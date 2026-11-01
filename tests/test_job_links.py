import json
import socket

import pytest

from app.services import job_links
from app.services.job_links import JobLinkError, extract_job, fetch_job_link, validate_job_url
from tests.test_api import _client, _register, _csrf, _headers, _docx, ScriptedModel, REWRITE
from tests.samples import suitable_job


@pytest.mark.parametrize('url', ['file:///etc/passwd', 'javascript:alert(1)', 'https://user:pass@example.com', 'https://example.com:8000', 'https://example.com/\nprivate', 'not a url'])
def test_reject_unsafe_urls(url):
    with pytest.raises(JobLinkError):
        validate_job_url(url)


def test_extract_structured_job_ignores_navigation():
    job = {'@graph': [{'@type':'JobPosting', 'title':'Python engineer', 'description':'<p>Build reliable Python services for customers.</p><ul><li>Required: SQL and Python.</li></ul>'}]}
    result = extract_job('<nav>Unrelated careers menu</nav><script type="application/ld+json">' + json.dumps(job) + '</script>')
    assert result['role_title'] == 'Python engineer'
    assert result['job_description'] == 'Build reliable Python services for customers.\nRequired: SQL and Python.'


def test_fallback_plain_text_and_length():
    result = extract_job('<title>Engineer</title><style>hidden css</style><p>' + 'Build customer services. ' * 2000 + '</p>')
    assert result['role_title'] == 'Engineer'
    assert 'hidden css' not in result['job_description']
    assert len(result['job_description']) == 20000
    with pytest.raises(JobLinkError):
        extract_job('<script>window.loadJob()</script>')


@pytest.mark.parametrize('ip', ['127.0.0.1', '10.1.2.3', '169.254.169.254', '::1', '192.168.1.1', '::ffff:127.0.0.1'])
def test_private_networks_never_requested(monkeypatch, ip):
    monkeypatch.setattr(socket, 'getaddrinfo', lambda *a, **k: [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (ip, 443))])
    with pytest.raises(JobLinkError, match='public job'):
        fetch_job_link('https://example.com/job')


def test_redirect_is_revalidated_and_ip_is_pinned(monkeypatch):
    monkeypatch.setattr(socket, 'getaddrinfo', lambda host, *a, **k: [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('93.184.216.34' if host=='example.com' else '127.0.0.1', 443))])
    calls = []
    class Connection:
        sock = None
        def __init__(self, host, port, timeout): calls.append(host)
        def request(self, *a, **k):
            monkeypatch.setattr(socket, 'create_connection', lambda addr, *a: calls.append(addr))
            self._create_connection(('example.com', 443), 6)
        def getresponse(self): return self
        status = 302
        def getheader(self, name, default=''): return 'https://internal.test/job'
        def close(self): pass
    monkeypatch.setattr(job_links.http.client, 'HTTPSConnection', Connection)
    with pytest.raises(JobLinkError): fetch_job_link('https://example.com/job')
    assert calls == ['example.com', ('93.184.216.34', 443)]


def test_import_requires_auth_csrf_and_does_not_call_model(tmp_path, monkeypatch):
    model = ScriptedModel(suitable_job().model_dump(), rewrite=REWRITE)
    with _client(tmp_path, model) as client:
        assert client.post('/api/job-description', json={'url':'https://example.com/job'}).status_code in (401,403)
        _register(client)
        assert client.post('/api/job-description', json={'url':'https://example.com/job'}).status_code == 403
        monkeypatch.setattr('app.main.fetch_job_link', lambda value: {'role_title':'Engineer','job_description':'Python required','job_url':value})
        response = client.post('/api/job-description', headers=_headers(_csrf(client)), json={'url':'https://example.com/job'})
        assert response.status_code == 200
        assert response.json()['job_description'] == 'Python required'
        assert not model.calls


def test_link_persisted_without_fetching_and_not_public(tmp_path):
    with _client(tmp_path, ScriptedModel(suitable_job().model_dump(), rewrite=REWRITE)) as client:
        _register(client)
        headers = _headers(_csrf(client))
        cv = client.post('/api/cvs', headers=headers, files={'file':('cv.docx',_docx())}).json()
        response = client.post('/api/applications', headers=headers, json={'cv_id':cv['id'], 'role_title':'Engineer', 'job_description':'Python and SQL required', 'job_url':'https://example.com/jobs/123'})
        assert response.status_code == 201, response.text
        row = response.json()
        assert row['job_url'] == 'https://example.com/jobs/123'
        assert client.get(f"/api/applications/{row['id']}").json()['job_url'] == row['job_url']
        share = client.post(f"/api/applications/{row['id']}/profile", headers=headers).json()
        assert 'job_url' not in client.get('/api' + share['share_path']).json()


def test_slow_headers_are_interrupted_by_deadline(monkeypatch):
    from threading import Event, Timer as RealTimer
    monkeypatch.setattr(socket, 'getaddrinfo', lambda *a, **k: [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('93.184.216.34', 443))])
    stopped = Event()
    class Sock:
        def shutdown(self, how): stopped.set()
        def close(self): pass
    class Connection:
        def __init__(self, *a, **k): self.sock = Sock()
        def request(self, *a, **k): pass
        def getresponse(self):
            assert stopped.wait(1), 'Deadline did not stop header parsing'
            raise OSError('closed by deadline')
        def close(self): pass
    monkeypatch.setattr(job_links.http.client, 'HTTPSConnection', Connection)
    monkeypatch.setattr(job_links, 'Timer', lambda seconds, callback: RealTimer(.02, callback))
    with pytest.raises(JobLinkError, match='Could not fetch'):
        fetch_job_link('https://example.com/job')


def test_existing_database_gets_optional_link_column(tmp_path):
    from app.database import make_engine, ensure_schema
    from sqlalchemy import text, inspect
    engine = make_engine(f"sqlite:///{tmp_path / 'legacy.db'}")
    with engine.begin() as conn:
        conn.execute(text('CREATE TABLE users (id INTEGER PRIMARY KEY, is_admin BOOLEAN)'))
        conn.execute(text('CREATE TABLE applications (id INTEGER PRIMARY KEY)'))
        conn.execute(text('INSERT INTO applications (id) VALUES (1)'))
    ensure_schema(engine)
    ensure_schema(engine)
    assert 'job_url' in {col['name'] for col in inspect(engine).get_columns('applications')}
    with engine.connect() as conn:
        assert conn.execute(text('SELECT job_url FROM applications')).scalar() is None
