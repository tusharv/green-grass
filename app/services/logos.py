"""Best-effort company logos from Wikidata and Wikimedia Commons.

Only employer names leave the app. Logo metadata is kept in a bounded,
short-lived memory cache, separate from the candidate's factual profile.
"""
from collections import OrderedDict
from threading import Lock
from time import monotonic
from urllib.parse import urlsplit
import re

import httpx

# Wikimedia returns 403 to clients whose User-Agent has no contact URL or email.
USER_AGENT = 'JobReady/1.0 (https://jobready.tech; company logo lookup)'


class CompanyLogos:
    def __init__(self, client=None):
        self.client = client
        self.cache = OrderedDict()
        self.lock = Lock()

    def lookup(self, company: str) -> dict | None:
        name = ' '.join(company.split())
        if not name or len(name) > 200:
            return None
        key = name.casefold()
        with self.lock:
            cached = self.cache.get(key)
            if cached and cached[0] > monotonic():
                self.cache.move_to_end(key)
                return cached[1]
        try:
            if self.client is not None:
                result = self._lookup(self.client, name)
            else:
                with httpx.Client(timeout=3.0, follow_redirects=False,
                                  headers={'User-Agent': USER_AGENT}) as client:
                    result = self._lookup(client, name)
        except (httpx.HTTPError, ValueError, KeyError, TypeError, AttributeError):
            result = None
        with self.lock:
            self.cache[key] = (monotonic() + (86400 if result else 300), result)
            self.cache.move_to_end(key)
            while len(self.cache) > 512:
                self.cache.popitem(last=False)
        return result

    @staticmethod
    def _get(client, host, **params):
        response = client.get(f'https://{host}/w/api.php', params={'format': 'json', **params})
        response.raise_for_status()
        return response.json()

    def _lookup(self, client, name):
        search = self._get(client, 'www.wikidata.org', action='wbsearchentities',
                           search=name, language='en', limit=10).get('search', [])
        matches = set()
        for item in search:
            labels = [item.get('label', ''), (item.get('match') or {}).get('text', '')]
            if any(' '.join(label.split()).casefold() == name.casefold() for label in labels):
                entity_id = item.get('id', '')
                if re.fullmatch(r'Q[1-9][0-9]*', entity_id):
                    matches.add(entity_id)
        if not matches:
            return None
        data = self._get(client, 'www.wikidata.org', action='wbgetentities',
                         ids='|'.join(sorted(matches)), props='claims')
        # Same-name items (a film, a river) rarely have both an official website and a
        # current logo; if more than one does, the name is ambiguous and gets no logo.
        candidates = [logos for entity in data.get('entities', {}).values()
                      if (logos := _current_logos(entity.get('claims', {})))]
        if len(candidates) != 1:
            return None
        filename = candidates[0][0]['mainsnak']['datavalue']['value']
        if not isinstance(filename, str) or len(filename) > 240:
            return None
        data = self._get(client, 'commons.wikimedia.org', action='query',
                         titles=f'File:{filename}', prop='imageinfo', iiprop='url', iiurlwidth=96)
        for page in data.get('query', {}).get('pages', {}).values():
            for info in page.get('imageinfo', []):
                url, source = info.get('thumburl', ''), info.get('descriptionurl', '')
                if (_trusted_url(url, 'upload.wikimedia.org', 'thumb.wikimedia.org')
                        and _trusted_url(source, 'commons.wikimedia.org')):
                    return {'url': url, 'source': source}
        return None


def _current_logos(claims):
    if not claims.get('P856'):  # Require an official website, not just a same-name item.
        return []
    logos = [claim for claim in claims.get('P154', [])
             if claim.get('rank') != 'deprecated' and not claim.get('qualifiers', {}).get('P582')]
    logos.sort(key=lambda claim: claim.get('rank') != 'preferred')
    return logos


def _trusted_url(url, *hosts):
    parsed = urlsplit(url)
    return parsed.scheme == 'https' and parsed.netloc in hosts
