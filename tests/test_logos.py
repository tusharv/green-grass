import httpx
import pytest

from app.services.logos import CompanyLogos


def transport(search=None, claims=None, image=None):
    def respond(request):
        if request.url.host == 'www.wikidata.org':
            if request.url.params['action'] == 'wbsearchentities':
                return httpx.Response(200, json={'search': search if search is not None else [{'id': 'Q1', 'label': 'Acme'}]})
            return httpx.Response(200, json={'entities': {'Q1': {'claims': claims if claims is not None else {
                'P856': [{'mainsnak': {'datavalue': {'value': 'https://acme.example'}}}],
                'P154': [{'rank': 'normal', 'mainsnak': {'datavalue': {'value': 'Acme.svg'}}}],
            }}}})
        assert request.url.host == 'commons.wikimedia.org'
        return httpx.Response(200, json={'query': {'pages': {'1': {'imageinfo': [image or {
            'thumburl': 'https://upload.wikimedia.org/acme.png',
            'descriptionurl': 'https://commons.wikimedia.org/wiki/File:Acme.svg',
        }]}}}})
    return httpx.MockTransport(respond)


def test_resolves_existing_logo_and_caches_normalized_name():
    with httpx.Client(transport=transport()) as client:
        service = CompanyLogos(client=client)
        logo = service.lookup('Acme')
        assert logo == {'url': 'https://upload.wikimedia.org/acme.png', 'source': 'https://commons.wikimedia.org/wiki/File:Acme.svg'}
    # Cached results remain available without the network client.
    assert service.lookup('  ACME  ') == logo


@pytest.mark.parametrize('search', [[], [{'id': 'Q1', 'label': 'Acme products'}],
    [{'id': 'Q1', 'label': 'Acme'}, {'id': 'Q2', 'label': 'Acme'}]])
def test_missing_fuzzy_and_ambiguous_companies_have_no_logo(search):
    service = CompanyLogos(client=httpx.Client(transport=transport(search=search)))
    assert service.lookup('Acme') is None


@pytest.mark.parametrize('claims', [{}, {'P154': [{'mainsnak': {'datavalue': {'value': 'Acme.svg'}}}]}])
def test_missing_logo_or_official_website_has_no_logo(claims):
    assert CompanyLogos(client=httpx.Client(transport=transport(claims=claims))).lookup('Acme') is None


def test_provider_failure_is_cached_and_never_breaks_cv():
    calls = []
    def unavailable(request):
        calls.append(request)
        return httpx.Response(429)
    service = CompanyLogos(client=httpx.Client(transport=httpx.MockTransport(unavailable)))
    assert service.lookup('Acme') is None
    assert service.lookup('Acme') is None
    assert len(calls) == 1


def test_untrusted_image_url_is_rejected():
    service = CompanyLogos(client=httpx.Client(transport=transport(image={
        'thumburl': 'https://attacker.example/acme.svg',
        'descriptionurl': 'https://commons.wikimedia.org/wiki/File:Acme.svg',
    })))
    assert service.lookup('Acme') is None


def test_empty_and_overlong_company_names_do_not_call_provider():
    def unexpected(request):
        pytest.fail('Invalid company sent to provider')
    service = CompanyLogos(client=httpx.Client(transport=httpx.MockTransport(unexpected)))
    assert service.lookup(' ') is None
    assert service.lookup('a' * 201) is None
