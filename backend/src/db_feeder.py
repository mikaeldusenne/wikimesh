import logging
import multiprocessing as mp
from pprint import pprint
import argparse
from importlib import reload
from multiprocessing.pool import ThreadPool
from collections import Counter
from itertools import islice
from time import time

from backend.src import db
from backend.src.pytypes import V, Mesh
from backend.src import helpers as h
from backend.src import wiki_fetcher as ftc
from backend.src import mesh_parser
from backend.src import loggingManager


def info():
    logging.getLogger().setLevel(logging.INFO)
def normal():
    logging.getLogger().setLevel(logging.WARNING)
info()

def query_pt_and_syns(lang):
    to_query = [("pt", lang.pt)] + [("syn", e) for e in lang.syns]
    for origin, s in to_query:
        ans = ftc.query_wiki_langs(s, lang=lang.id)
        if len(ans):
            return origin, s, ans
    return None, None, None


def query_langs(mesh):
    # logging.info(f"query {str(mesh)}")
    which=["pt", "syn"]
    # which = ['ptsyn']
    def run(which=["pt", "syn"]):
        if len(which) == 0:
            # logging.info(f'no result for {str(mesh)}')
            return {
            "_id": mesh.id,
            "langs": None
        }
        # query all pts
        w, *ws = which
        # logging.info(f'\n-------- {str(mesh)} -> searching for {w} --------')
        l = []
        if "pt" in w:
            l = l + [(lang.pt, lang.id) for lang in mesh.langs]
            
        if "syn" in w:
            l = l + [
                (syn, lang.id)
                for lang in mesh.langs
                for syn in lang.syns
            ]
        # print(l)
        # logging.info(f'{len(l)} available: {l}')
        #pool = ThreadPool(processes=len(l))
        #ll = list(zip([e[0] for e in l], pool.starmap(ftc.query_wiki_langs, l)))
        #pool.close()
        #pool.join()
        # reload(ftc)
        ll = list(zip([e[0] for e in l], map(lambda e: ftc.query_wiki_langs(*e), l)))
        # pprint(ll)
        pts_resp = {k: v for k, v in ll if v is not None}
        # logging.info(f'{len(pts_resp)} successful queries: {pts_resp.keys()}')
        # pprint(pts_resp)

        ans = {}
        for lang in sorted(list(set(h.flatten(pts_resp.values())))):
            c = Counter(h.no_none([ee.get(lang) for ee in pts_resp.values()]))
            ans[lang] = c.most_common()[0][0]

        if len(ans):
            return {
                "_id": mesh.id,
                "identifier": mesh.identifier,
                "lang_match": None,
                "origin": w,
                "term_match": None,
                "langs": ans
            }
        else:
            return run(ws)
    return run(which)


# identifier = "EFMI"
# identifier = "MeSH"
def run(identifier="MeSH", force=False):
    agg_match_identifier = {'identifier': identifier}
    
    if not force:
        # find documents with no corresponding _id in the wikimesh collection
        aggregation = [
            {"$match": agg_match_identifier},
            {
                "$lookup": {
                    "from": "wikimesh",
                    "localField": "_id",
                    "foreignField": "_id",
                    "as": "matched"
                }
            },
            {
                "$match": { "matched": { "$eq": [] } }
            },
            {"$project": {"matched": 0}}
        ]
        try:
            # count these docs
            n_to_fetch = next(db.db.mesh.aggregate(aggregation + [{"$count": "n"}]))['n']
        except StopIteration:
            print('nothing to fetch, congratulations!')
            n_to_fetch = 0
            to_fetch = []
        else:
            to_fetch = db.db.mesh.aggregate(aggregation)
    else:
        to_fetch = db.db.mesh.find(agg_match_identifier)
        n_to_fetch = db.db.mesh.count_documents(agg_match_identifier)
        
    print(f"******** {n_to_fetch} / {db.db.mesh.count_documents({**agg_match_identifier})} {identifier} items to fetch ********")
    
    # len(list(h.process_by_chunk(add_mesh_links, mesh, len(mesh), chunk_size=max(10, int(len(mesh)/12)), display_progress=True)))
    n_workers = 12*5
    pool = mp.Pool(n_workers)
    to_fetch = list(to_fetch)
    total_len = len(to_fetch)
    starttime = time()
    i = 0
    for e in pool.imap_unordered(query_langs, map(V.decode, to_fetch), chunksize=20):
        # for mesh, lang, origin, origin_term, ans in l:
        # print(i)
        if i % 10 == 0:
            h.show_progress(i, total_len, eta_starttime=starttime, show_speed=True)
        i += 1
        
        if e is not None:
            db.db.wikimesh.insert_one(e)
            # "_id": mesh.id,
            # "identifier": mesh.identifier,
            # "lang_match": None,
            # "origin": w,
            # "term_match": None,
            # "langs": ans

            # logging.info(f'{e["_id"]}: [{e["origin"]}] - ({len(e["langs"])} langs found.')
        else:
            # logging.info(f'{mesh.id}: 0 langs found.')
            pass
    pool.close()
    pool.join()
    

def test():
    reload(h)
    # ftc.query_wiki_langs("anticorps", "fr")
    normal()
    test_meshs = "001249 055811 000906 007136 000009".split()
    test_meshs = "000029 000037 000081322".split()
    test_meshs = "000029".split()
    for id in test_meshs:
        mesh = db.get_mesh(id)
        print(mesh)
        ans = query_langs(mesh)['langs']
        print(
            id,
            h.find(lambda e: e.id=='fr', mesh.langs).pt,
            "--",
            ans.get('fr'), "/", ans.get('en')
        )
    reload(h)
    mesh
    query_langs(db.get_mesh("007136"))
    pprint(list(ftc.query_wiki_data('Immunoglobuline', 'fr')))
    ftc.query_wiki_langs(mesh.langs[4].pt, 'fr')

    query_langs(mesh)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--force', action='store_true', default=False)
    parser.add_argument('-i', '--identifier')
    args = parser.parse_args()
    run(**args.__dict__)
    
    print(db.db.wikimesh.count_documents({}))
