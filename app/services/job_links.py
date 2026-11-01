"""Import public job pages without exposing the server's private network."""
import http.client
import ipaddress
import json
import socket
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Timer

_DNS_POOL = ThreadPoolExecutor(max_workers=4, thread_name_prefix="job-link-dns")
from html.parser import HTMLParser
from urllib.parse import urlsplit, urlunsplit, urljoin


class JobLinkError(ValueError):
    pass


def validate_job_url(value: str) -> str:
    value = value.strip()
    try:
        parts = urlsplit(value)
        if (len(value) > 2048 or parts.scheme not in ('http', 'https') or not parts.hostname
                or parts.username or parts.password or parts.port not in (None, 80, 443)
                or any(ord(c) < 33 for c in value)):
            raise ValueError()
        host = parts.hostname.encode('idna').decode('ascii')
        if ':' in host:
            host = f'[{host}]'
        return urlunsplit((parts.scheme, host + (f':{parts.port}' if parts.port else ''), parts.path or '/', parts.query, ''))
    except (ValueError, UnicodeError):
        raise JobLinkError('Enter a valid public http or https job link.') from None


class PageText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.text = []
        self.scripts = []
        self.script = None
        self.hidden = 0
        self.title = False
        self.titles = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ('script', 'style', 'nav', 'footer', 'header', 'noscript', 'svg'):
            self.hidden += 1
        if tag == 'script' and attrs.get('type', '').lower() == 'application/ld+json':
            self.script = []
        if tag == 'title':
            self.title = True
        if tag in ('p', 'div', 'br', 'li', 'h1', 'h2', 'h3', 'section'):
            self.text.append('\n')

    def handle_endtag(self, tag):
        if tag == 'script' and self.script is not None:
            self.scripts.append(''.join(self.script))
            self.script = None
        if tag in ('script', 'style', 'nav', 'footer', 'header', 'noscript', 'svg'):
            self.hidden = max(0, self.hidden - 1)
        if tag == 'title':
            self.title = False
        if tag in ('p', 'div', 'li', 'section'):
            self.text.append('\n')

    def handle_data(self, data):
        if self.script is not None:
            self.script.append(data)
        if self.title:
            self.titles.append(data)
        elif not self.hidden:
            self.text.append(data)

    def plain(self):
        return '\n'.join(line for part in ''.join(self.text).splitlines() if (line := ' '.join(part.split())))


def extract_job(html):
    page = PageText()
    page.feed(html)
    title = ''.join(page.titles).strip()
    description = page.plain()
    def postings(node):
        if isinstance(node, list):
            for item in node:
                yield from postings(item)
        elif isinstance(node, dict):
            kind = node.get('@type', [])
            if kind == 'JobPosting' or isinstance(kind, list) and 'JobPosting' in kind:
                yield node
            for value in node.values():
                if isinstance(value, (dict, list)):
                    yield from postings(value)
    for script in page.scripts:
        try:
            for job in postings(json.loads(script)):
                if isinstance(job.get('description'), str):
                    body = PageText()
                    body.feed(job['description'])
                    if len(body.plain()) >= 40:
                        return {'role_title': str(job.get('title') or title)[:200], 'job_description': body.plain()[:20000]}
        except (ValueError, RecursionError):
            continue
    if len(description) < 40:
        raise JobLinkError('No readable job description was found. Paste it below instead.')
    return {'role_title': title[:200], 'job_description': description[:20000]}


def fetch_job_link(value):
    url = validate_job_url(value)
    deadline = time.monotonic() + 20
    try:
        for _ in range(4):
            parts = urlsplit(url)
            port = parts.port or (443 if parts.scheme == 'https' else 80)
            lookup = _DNS_POOL.submit(socket.getaddrinfo, parts.hostname, port, type=socket.SOCK_STREAM)
            try:
                addresses = lookup.result(timeout=max(0.01, deadline - time.monotonic()))
            finally:
                lookup.cancel()
            ips = [entry[4][0] for entry in addresses]
            if not ips or any(not ipaddress.ip_address(ip).is_global for ip in ips):
                raise JobLinkError('Use a public job posting link. Private network addresses are not supported.')
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError()
            timeout = min(6, remaining)
            cls = http.client.HTTPSConnection if parts.scheme == 'https' else http.client.HTTPConnection
            conn = cls(parts.hostname, port, timeout=timeout)
            # Pin the validated IP; HTTPS still verifies the original hostname and uses its SNI.
            conn._create_connection = lambda address, timeout, source_address=None: socket.create_connection((ips[0], port), timeout, source_address)
            transport = [None]
            def expire():
                sock = transport[0] or conn.sock
                if sock is not None:
                    try:
                        sock.shutdown(socket.SHUT_RDWR)
                    except OSError:
                        pass
                    sock.close()
            timer = Timer(max(0.01, deadline - time.monotonic()), expire)
            timer.daemon = True
            timer.start()
            try:
                conn.request('GET', urlunsplit(('', '', parts.path or '/', parts.query, '')),
                             headers={'User-Agent': 'JobReady/1.0 (job description import)', 'Accept': 'text/html,text/plain', 'Accept-Encoding': 'identity'})
                transport[0] = conn.sock
                if time.monotonic() >= deadline:
                    raise TimeoutError()
                response = conn.getresponse()
                if response.status in (301, 302, 303, 307, 308):
                    url = validate_job_url(urljoin(url, response.getheader('Location', '')))
                    continue
                if response.status != 200:
                    raise JobLinkError('This site could not be fetched. Paste the job description below; you can still save its link.')
                if response.getheader('Content-Encoding', 'identity') != 'identity':
                    raise JobLinkError('This page could not be read. Paste its job description below instead.')
                content_type = response.getheader('Content-Type', '').split(';')[0].lower()
                if content_type not in ('text/html', 'application/xhtml+xml', 'text/plain'):
                    raise JobLinkError('That link is not a readable job page. Paste the description below instead.')
                chunks = []
                size = 0
                while True:
                    if time.monotonic() > deadline:
                        raise TimeoutError()
                    chunk = response.read1(16384)
                    if not chunk:
                        break
                    size += len(chunk)
                    if size > 1_000_000:
                        raise JobLinkError('That page is too large. Paste its job description below instead.')
                    chunks.append(chunk)
                return {**extract_job(b''.join(chunks).decode('utf-8', errors='replace')), 'job_url': value.strip()}
            finally:
                timer.cancel()
                conn.close()
        raise JobLinkError('That link redirects too many times. Paste the description below instead.')
    except JobLinkError:
        raise
    except (OSError, http.client.HTTPException, ValueError, UnicodeError):
        raise JobLinkError('Could not fetch this page. Paste the job description below; you can still save its link.') from None
