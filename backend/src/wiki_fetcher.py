import logging
from pprint import pformat

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

TIMEOUT = (3.05, 20)


def _session():
    """One pooled session with bounded retries for transient HTTP failures."""
    s = requests.Session()
    s.mount("https://", HTTPAdapter(max_retries=Retry(
        total=4, backoff_factor=.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
    )))
    return s


def _get_json(session, url, params):
    response = session.get(url, params=params, timeout=TIMEOUT)
    response.raise_for_status()
    data = response.json()
    if "error" in data:
        raise RuntimeError(f"Wikipedia API error: {data['error']}")
    return data


def paginated_query(args, extractf, return_first_q=False, lang='en'):
    url = f"https://{lang}.wikipedia.org/w/api.php"
    continuation, first = {}, True
    with _session() as session:
        while continuation is not None:
            data = _get_json(session, url, {**args, **continuation, "redirects": ""})
            if first and return_first_q:
                yield data
            first = False
            continuation = data.get('continue')
            logging.debug(pformat(data, indent=2))
            yield from extractf(data)


def clean_search_query(s):
    return s.strip().lower()


def extract_q(data):
    pages = data.get("query", {}).get("pages", {}).values()
    return [link for page in pages for link in page.get('langlinks', [])]


def query_wiki_data(search, lang, description=None):
    logging.debug(description or f"searching '{search}' ({lang})")
    return paginated_query({
        "action": "query",
        "titles": clean_search_query(search),
        "prop": "langlinks",
        "format": "json",
        "lllimit": 500,
    }, extract_q, return_first_q=True, lang=lang)


def query_wiki_langs(search, lang="en", description=None):
    q = query_wiki_data(search, lang, description)
    query = next(q).get('query', {})
    normalized = query.get("normalized")
    origin = normalized[0]['to'] if normalized else search
    links = list(q)
    return {e['lang']: e['*'] for e in [{"lang": lang, "*": origin}, *links]} if links else None


def check_url_valid(url):
    try:
        return requests.get(url, timeout=TIMEOUT).status_code == 200
    except requests.RequestException:
        return False
