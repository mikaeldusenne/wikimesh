from pymongo import MongoClient
from pymongo import InsertOne, DeleteMany, ReplaceOne, UpdateOne
from bson.json_util import loads, dumps
import yaml
from os import environ
from pprint import pprint
from dotenv import load_dotenv

from backend.src.pytypes import conv, V
from backend.src import helpers as h


if not 'MONGO_INITDB_DATABASE' in environ.keys():
    print("................ mongo environment not loaded, loading ................")
    load_dotenv('mongo/.env', override=True)
    load_dotenv('mongo/.env.dev', override=True)

def connect(
        username=environ['MONGO_INITDB_ROOT_USERNAME'],
        password=environ['MONGO_INITDB_ROOT_PASSWORD']):
    global client, db, projects, users
    client = MongoClient(host=environ['MONGO_HOST'],
                         port=int(environ.get('MONGO_PORT', 27017)),
                         username=username,
                         password=password,
                         authSource=environ['MONGO_INITDB_DATABASE']
                         )
    db = client[environ['MONGO_INITDB_DATABASE']]
    return db


def get_mesh_links(m):
    return db.mesh.find_one({"_id": m['id']}, {"_id": 0, "links": 1})['links']


def get_mesh(id):
    ans = db.mesh.find_one({'_id': id})
    if ans is not None:
        return V.decode(ans)


def bulk_insert(col, l):
    col.bulk_write([InsertOne(e.toBsonDict()) for e in l])


def create_indexes():
    # db.mesh.create_index(
    #     [
    #         ("_id", 1),
    #         ("lang", 1),
    #     ],
    #     unique=True
    # )
    db.mesh.create_index(
        [
            ("langs.pt", 1),
        ],
    )
    db.wikimesh.create_index(
        [
            ("lang_match", 1),
        ],
    )
    db.wikimesh.create_index(
        [
            ("origin", 1),
        ],
    )
    
    


def create_views():
    db.command({
        "create": "mesh_view",
        "viewOn": "mesh", 
        "pipeline": [
            {
                "$lookup": {
                    "from": "wikimesh",
                    "localField": "_id",
                    "foreignField": "_id",
                    "as": "wikilangs",
                }
            },
            {
                "$unwind": "$wikilangs"
            }
        ]
    })
    # db.db.mesh_view.find_one()

connect()

if __name__ == "__main__":
    from sys import argv
    if argv[1] == "index":
        create_indexes()
