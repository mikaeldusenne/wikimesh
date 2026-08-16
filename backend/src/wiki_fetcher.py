import logging
from pprint import pformat

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

LOGGER = logging.getLogger(__name__)
TIMEOUT = (3.05, 20)
RETRYABLE_STATUSES = (429, 500, 502, 503, 504)
USER_AGENT = "WikiMeSH/0.2 (https://github.com/mikaeldusenne/wikimesh)"


def _retry():
    return Retry(
        total=4,
        connect=4,
        read=4,
        status=4,
        other=0,
        backoff_factor=.5,
        backoff_max=8,
        backoff_jitter=.25,
        status_forcelist=RETRYABLE_STATUSES,
        allowed_methods=("GET",),
        raise_on_status=False,
        respect_retry_after_header=True,
    )


def _session():
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    session.mount("https://", HTTPAdapter(max_retries=_retry()))
    return session


def _get_json(session, url, params):
    try:
        response = session.get(url, params=params, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError) as error:
        LOGGER.warning("Wikipedia request failed for %s: %s", url, error)
        raise

    if not isinstance(data, dict):
        raise ValueError("Wikipedia API returned non-object JSON")
    if error := data.get("error"):
        raise RuntimeError(f"Wikipedia API error: {error}")
    return data


def paginated_query(args, extractf, return_first_q=False, lang="en"):
    url = f"https://{lang}.wikipedia.org/w/api.php"
    continuation, first = {}, True

    with _session() as session:
        while continuation is not None:
            data = _get_json(
                session,
                url,
                {**args, **continuation, "redirects": ""},
            )
            if first and return_first_q:
                yield data
            first = False
            continuation = data.get("continue")
            LOGGER.debug(pformat(data, indent=2))
            yield from extractf(data)


def clean_search_query(search):
    return search.strip().lower()


def extract_q(data):
    pages = data["query"]["pages"].values()
    return [
        link
        for page in pages
        for link in page.get("langlinks", ())
    ]


def query_wiki_data(search, lang, description=None):
    LOGGER.debug(description or f"searching '{search}' ({lang})")
    return paginated_query(
        {
            "action": "query",
            "titles": clean_search_query(search),
            "prop": "langlinks",
            "format": "json",
            "lllimit": 500,
        },
        extract_q,
        return_first_q=True,
        lang=lang,
    )


def query_wiki_langs(search, lang="en", description=None):
    query = query_wiki_data(search, lang, description)
    first = next(query)["query"]
    normalized = first.get("normalized", ())
    origin = normalized[0]["to"] if normalized else search
    links = list(query)
    if not links:
        return None
    return {
        lang: origin,
        **{link["lang"]: link["*"] for link in links},
    }
