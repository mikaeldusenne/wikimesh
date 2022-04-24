import os
from backend.src import helpers as h
from functools import cache
import csv
from typing import List
from pprint import pprint

import attr
import cattr
from itertools import groupby
import argparse

from backend.src.pytypes import conv, V, Row, Mesh, MeshLang
from backend.src import db
from backend.src import helpers as h


def parser_julien(path, identifier):
    with open(path, encoding="utf-8") as f:
        csvreader = csv.reader(f, delimiter=',', quotechar='"')
        columns = [e.lower() for e in next(csvreader)]
        columns[0] = "id"
        
        def strct(e):
            d = dict(zip(columns, e))
            if identifier != "MeSH":
                d['id'] = f"{identifier}_{d['id']}"
            return conv.structure(d, Row)
        
        for i, (id, _rows) in enumerate(groupby(map(strct, csvreader), lambda e: e.id)):
            # if i > maxn: break
            rows = sorted(_rows, key=lambda e: ((0 if e.lang=="en" else 1), e.lang))

            m = Mesh(id, identifier=identifier, langs=[])

            for lang, [pt, *syns] in groupby(filter(lambda e: e.lang != "N/A", rows), lambda e: e.lang):
                m.langs.append(MeshLang(
                    id=lang,
                    pt=pt.label,
                    syns=[e.label for e in syns]
                ))
            # pprint(m)
            # print("--------")
            
            db.db.mesh.insert_one(m.toBsonDict())
            if i % 100 == 0:
                h.show_progress(i)


def parser_flavien(path, identifier, lang="fr", *args, **kwargs):
    with open(path, encoding="utf-8") as f:
        csvreader = csv.reader(f, delimiter=',', quotechar='"')
        
        for i, row in enumerate(csvreader):
            [id, pt, *syns] = row
            m = Mesh(id, identifier=identifier, langs=[])
            
            m.langs.append(MeshLang(
                id=lang,
                pt=pt,
                syns=syns
            ))
            
            db.db.mesh.insert_one(m.toBsonDict())
            if i % 100 == 0:
                h.show_progress(i)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # parser.add_argument('-f', '--force', action='store_true', default=False)
    parser.add_argument('-i', '--identifier')
    parser.add_argument('path', help='path to file')
    parser.add_argument('--source', default="julien")
    args = parser.parse_args()

    parser_flavien(
        path="./backend/data/EFMI_wikimesh.csv",
        identifier="EFMIMO",
    )
    
    db.connect()
    print(db.db)
    
    dict(
        julien=parser_julien,
        flavien=parser_flavien,
    )[args.source](**vars(args))
    
    # print(args)
    # db.client
    # filepath = "backend/data/mesh_descr_ml.csv"

# V.decode(db.db.mesh.find_one())
# print(db.db.mesh.count_documents({}))
# 1        

# f = open(filepath, encoding="utf-8")

# next(f)

# line = next(f).strip()


# def search(it, f, extract=lambda e: e.split('=')[-1].strip()):
#     try:
#         while not f((line:=next(it))):
#             pass
#         return extract(line)
#     except StopIteration:
#         return None


# def parse_mesh():
#     with open(filepath, encoding="utf-8") as f:
#         while search(f, lambda e: e == "*NEWRECORD\n", extract=lambda e: e) is not None:
#             heading = search(f, lambda e: e.startswith('MH ='))
#             id = search(f, lambda e: e.startswith('UI ='))
#             yield heading, id


# def generate_mesh():
#     mesh_data = [
#         {"id": id, "title": title}
#         for title, id in
#         sorted(
#             parse_mesh(),
#             key=lambda e: ((0 if e[0][0].lower() in "azertyuiopsqdfghjklmwxcvbn" else 1), e[0])
#         )
#     ]
#     h.save_pickle(picklepath, mesh_data)
#     return mesh_data
    

# @cache
# def get_mesh():
#     try:
#         mesh_data = h.load_pickle(picklepath)
#     except:
#         mesh_data = generate_mesh()
#     return mesh_data


# if __name__ == "__main__":
#     generate_mesh()
