import logging
import multiprocessing as mp

from backend.src import db
from backend.src import helpers as h
from backend.src import wiki_fetcher as ftc
from backend.src import mesh_parser

def add_mesh_links(mesh):
    db.connect()
    
    def f(e):
        return {
            "_id": e['id'],
            "title": e["title"],
            "links": h.retry_with_delay(lambda: ftc.query_wiki_langs(e['title']), message_prefix=f"fetching wiki {e['title']}"),
        }
    
    for e in map(f, mesh):
        logging.info(f"{e['title']}: {len(e['links'])}")
        # db.db.mesh.replace_one({"_id": ans['_id']}, ans, upsert=True)
        db.db.mesh.insert_one(e)


def run():
    from sys import argv
    db.connect()
    mesh = mesh_parser.get_mesh()
    original_n = len(mesh)
    if not (len(argv)>1 and argv[1]=="force"):
        existing = [e['_id'] for e in db.db.mesh.find({}, {'_id': 1})]
        mesh_to_fetch = list(set([e["id"] for e in mesh]).difference(set(existing)))
        mesh = [e for e in mesh if e['id'] in mesh_to_fetch]
        
    print(f"******** {len(mesh)} / {original_n} MeSH items to fetch ********")
    
    # len(list(h.process_by_chunk(add_mesh_links, mesh, len(mesh), chunk_size=max(10, int(len(mesh)/12)), display_progress=True)))
    n_workers = 12
    pool = mp.Pool(n_workers)
    pool.map(add_mesh_links, h.chunk(mesh, 250), chunksize=24)
    pool.close()
    pool.join()
    

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    run()

