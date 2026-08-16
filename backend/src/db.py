from pymongo import MongoClient
from pymongo import InsertOne, DeleteMany, ReplaceOne, UpdateOne
from bson.json_util import loads, dumps
import yaml
from os import environ
from pprint import pprint
from threading import Lock
from dotenv import load_dotenv

from backend.src.pytypes import conv, V
from backend.src import helpers as h


if not 'MONGO_INITDB_DATABASE' in environ.keys():
    print("................ mongo environment not loaded, loading ................")
    load_dotenv('mongo/.env', override=True)
    load_dotenv('mongo/.env.dev', override=True)

client = db = None
_credentials = None
_connect_lock = Lock()


def connect(username=None, password=None):
    """Connect on first use; explicit credential changes still reconnect."""
    global client, db, _credentials
    username = username or environ['MONGO_INITDB_ROOT_USERNAME']
    password = password or environ['MONGO_INITDB_ROOT_PASSWORD']
    credentials = (username, password)

    if db is None or credentials != _credentials:
        with _connect_lock:
            if db is None or credentials != _credentials:
                client = MongoClient(host=environ['MONGO_HOST'],
                                     port=int(environ.get('MONGO_PORT', 27017)),
                                     username=username,
                                     password=password,
                                     authSource=environ['MONGO_INITDB_DATABASE'],
                                     serverSelectionTimeoutMS=5000
                                     )
                db = client[environ['MONGO_INITDB_DATABASE']]
                _credentials = credentials
    return db


def get_mesh_links(m):
    return connect().mesh.find_one({"_id": m['id']}, {"_id": 0, "links": 1})['links']


def get_mesh(id):
    ans = connect().mesh.find_one({'_id': id})
    if ans is not None:
        return V.decode(ans)


def bulk_insert(col, l):
    col.bulk_write([InsertOne(e.toBsonDict()) for e in l])


def create_indexes():
    database = connect()
    # db.mesh.create_index(
    #     [
    #         ("_id", 1),
    #         ("lang", 1),
    #     ],
    #     unique=True
    # )
    database.mesh.create_index(
        [
            ("langs.pt", 1),
        ],
    )
    database.wikimesh.create_index(
        [
            ("lang_match", 1),
        ],
    )
    database.wikimesh.create_index(
        [
            ("origin", 1),
        ],
    )
    
    


def create_views():
    connect().command({
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


if __name__ == "__main__":
    from sys import argv
    if argv[1] == "index":
        create_indexes()
