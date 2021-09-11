import requests
import logging
from backend.src import helpers as h
import traceback
from pprint import pprint, pformat

def paginated_query(
        args,
        extractf,
        return_first_q=False,
        lang='en',
):
    url_api = f"https://{lang}.wikipedia.org/w/api.php"
    s = requests.Session()
    continuation = {}
    i = 0
    while continuation is not None:
        j = s.get(url_api, params={
            **args,
            **continuation
        }).json()
        if i == 0 and return_first_q:
            yield j
        i += 1
        continuation = j.get('continue')
        logging.debug(pformat(j, indent=2))
        for e in extractf(j):
            yield e


def clean_search_query(s):
    return s.strip().lower() # .replace(" ", "_")


def extract_q(j):
    try:
        return [ee for e in j["query"]["pages"].values() for ee in e['langlinks']]
    except:
        # traceback.print_exc()
        return None

def query_wiki_langs(search, lang="en"):
    try:
        q = paginated_query(
            args = {
                "action": "query",
                "titles": clean_search_query(search),
                "prop": "langlinks",
                "format": "json",
                "lllimit": 500
            },
            extractf=extract_q,
            return_first_q=True,
            lang=lang,
        )
        if q is not None:
            _normalized = next(q)['query'].get("normalized")
            if _normalized is not None:
                wikipage_orig = _normalized[0]['to']
            else:
                wikipage_orig = search
            l = [{"lang": lang, "*": wikipage_orig}] + list(q)
            return {e['lang']: e['*'] for e in l}
    except:
        # traceback.print_exc()
        return []


def test():
    
    requests.get("https://en.wikipedia.org/w/api.php?action=query&titles=Asthma&prop=langlinks&format=json").json()
