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
            **continuation,
            **{"redirects": ""}
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
    # print("extract", j)
    try:
        ans = [ee for e in j["query"]["pages"].values() for ee in e['langlinks']]
    except:
        # print("exception:")
        # traceback.print_exc()
        ans = []
    # print("returning", ans)
    return ans


def query_wiki_data(search, lang, description=None):
    if description is None:
        description=f"searching '{search}' ({lang})"
    return h.retry_with_delay(lambda: paginated_query(
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
        ), message_prefix=description)


def query_wiki_langs(search, lang="en", description=None):
    try:
        q = query_wiki_data(search, lang, description)
        
        if q is not None:
            qq = next(q)['query']
            _normalized = qq.get("normalized")
            _redirects = qq.get('redirects')
            
            # if _redirects is not None:
            #     return query_wiki_langs(_redirects[0]["to"])
            qq
            _normalized
            if _normalized is not None:
                wikipage_orig = _normalized[0]['to']
            else:
                wikipage_orig = search
            ll = list(q)
            len(ll)
            # print(ll)
            if len(ll):
                l = [{"lang": lang, "*": wikipage_orig}] + ll
                return {e['lang']: e['*'] for e in l}
            else:
                return None
    except:
        # traceback.print_exc()
        return None


def check_url_valid(url):
    try:
        return requests.get(url).status_code == 200
    except:
        return False

def test():
    search = 'abréviations comme sujet'
    search = 'anticorps'
    search = 'immunoglobuline'
    ans = query_wiki_langs(
        search=search,
        lang='fr',
        description=None,
    )
    # assert all([check_url_valid(h.mk_wikipedia_link(lang, term)) for lang, term in ans.items()])
    for lang, term in ans.items():
        lnk = h.mk_wikipedia_link(lang, term)
        print(lnk)
        assert check_url_valid(lnk)
        
                
    check_url_valid('https://fr.wikipedia.org/wiki/Immunoglobulinefrezg')
    
    print(ans)
    reload(h)
    
    h.mk_wikipedia_link('fr', 'Immunoglobuline')
    # requests.get("https://en.wikipedia.org/w/api.php?action=query&titles=Asthma&prop=langlinks&format=json").json()
