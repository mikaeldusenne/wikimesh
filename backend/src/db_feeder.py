import logging
import multiprocessing as mp
from pprint import pprint

from backend.src import db
from backend.src.pytypes import V, Mesh
from backend.src import helpers as h
from backend.src import wiki_fetcher as ftc
from backend.src import mesh_parser
from backend.src import loggingManager

# from importlib import reload
# reload(ftc)
# # logging.getLogger().setLevel('INFO')
# mesh = [V.decode(e) for e in db.db.mesh.find({'langs.0.pt': {"$regex": ".*sthm.*"}})][6]
# mesh
# list(db.db.wikimesh.find())
# add_mesh_links(mesh)

# db.db.wikimesh


def query_pt_and_syns(lang):
    to_query = [("pt", lang.pt)] + [("syn", e) for e in lang.syns]
    for origin, s in to_query:
        ans =  h.retry_with_delay(
            lambda: ftc.query_wiki_langs(s, lang=lang.id),
            message_prefix=f"fetching wiki ({lang.id}): {s}"
        )
        if len(ans):
            # logging.info(f'[{origin}] - "{s}" - {len(ans)} langs found.')
            return origin, s, ans
    return None, None, None


def query_langs(mesh):
    for lang in mesh.langs:
        # logging.info(f"**** {mesh.id} -- ({lang.id}) {lang.pt}")
        origin, origin_term, ans = query_pt_and_syns(lang)
        # yield lang, origin, origin_term, ans
        if origin is not None:
            return lang.id, origin, origin_term, ans
    return None, None, None, None


def add_mesh_links(mesh: Mesh):
    db.connect()
    logging.info(f"******** {mesh.id} -- {mesh.langs[0].pt} ********")
    lang, origin, origin_term, ans = list(query_langs(mesh))
    if ans is not None:
        db.db.wikimesh.insert_one({
            "_id": mesh.id,
            "origin": origin,
            "lang_match": lang,
            "term_match": origin_term,
            "langs": ans
        })
    else:
        db.db.wikimesh.insert_one({
            "_id": mesh.id,
            "langs": None
        })
    return mesh, lang, origin, origin_term, ans
        

def run():
    from sys import argv
    
    if not (len(argv)>1 and argv[1]=="force"):
        aggregation = [
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
        n_to_fetch = next(db.db.mesh.aggregate(aggregation + [{"$count": "n"}]))['n']
        to_fetch = db.db.mesh.aggregate(aggregation)
    else:
        to_fetch = db.db.mesh.find()
        
    print(f"******** {n_to_fetch} / {db.db.mesh.count_documents({})} MeSH items to fetch ********")
    
    # len(list(h.process_by_chunk(add_mesh_links, mesh, len(mesh), chunk_size=max(10, int(len(mesh)/12)), display_progress=True)))
    n_workers = 12*10
    pool = mp.Pool(n_workers)
    i = 0
    for l in pool.map(add_mesh_links, map(V.decode, to_fetch), chunksize=100):
        for mesh, lang, origin, origin_term, ans in l:
            i+=1
            if i % 100 == 0:
                h.display_progress(i)
            if ans is not None:
                logging.info(f'{mesh.id}: [{origin}] - ({lang}) "{origin_term}" - {len(ans)} langs found.')
            else:
                logging.info(f'{mesh.id}: 0 langs found.')
    pool.close()
    pool.join()
    

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    run()
    db.db.wikimesh.count_documents({})
