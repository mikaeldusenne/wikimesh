import requests
import logging
from backend.src import helpers as h



def paginated_query(args, extractf):
    url_api = "https://en.wikipedia.org/w/api.php"
    s = requests.Session()
    continuation = {}
    while continuation is not None:
        j = s.get(url_api, params={
            **args,
            **continuation
        }).json()
        continuation = j.get('continue')
        # pprint(j)
        for e in extractf(j):
            yield e

def clean_search_query(s):
    return s.strip().lower().replace(" ", "_")

def query_wiki_langs(search):
    try:
        l = list(paginated_query(
            args = {
                "action": "query",
                "titles": clean_search_query(search),
                "prop": "langlinks",
                "format": "json",
                "lllimit": 500
            },
            extractf=lambda e: list(e["query"]["pages"].values())[0]['langlinks']
        ))
        return {e['lang']: e['*'] for e in l}
    except:
        return {}


