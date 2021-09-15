from flask import Flask, render_template, jsonify, redirect, flash, request, url_for, Response, Blueprint, send_from_directory
import flask
from flask_caching import Cache
import logging
from os.path import join, dirname
import json
import re
import numpy as np
import pandas as pd
import traceback
from pprint import pprint
from os import environ
import os

import backend.src.helpers as h
import backend.src.db as db
from backend.src import wiki_fetcher as ftc
from backend.src import mesh_parser
from backend.src import db_exporter

cache = Cache(config={
    # 'CACHE_TYPE': 'FileSystemCache', 'CACHE_DIR': '/.flask-cache', "CACHE_DEFAULT_TIMEOUT": 9999999
    'CACHE_TYPE': 'RedisCache',
    'CACHE_REDIS_URL': 'redis://redis',
    'CACHE_REDIS_PORT': '6379',
    "CACHE_DEFAULT_TIMEOUT": 9999999,
})


def logging_setup(path):
    loggingdest = os.path.join(path, "flask.log")
    print("setting logging to {}".format(loggingdest))

    logFormatter = logging.Formatter(
        "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    # format='%(asctime)s\t%(name)s\t%(funcName)s\t%(levelname)s\t%(message)s'
    rootLogger = logging.getLogger('wikimesh')
    rootLogger.setLevel(logging.DEBUG if os.environ.get(
        "PROD", False) else logging.WARNING)

    fileHandler = logging.FileHandler(loggingdest)
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)


logging_setup(".")

####################

# @cache.memoize(6000000)
# def query_wiki_langs(search):
#     return db.db.mesh.find_one({'title': search}).get("links", []) # ftc.query_wiki_langs(search)


# def gen_filled_mesh():
#     return list(sorted(
#         db.db.mesh.find(),
#         key=lambda e: ((0 if e["title"][0].lower() in "azertyuiopsqdfghjklmwxcvbn" else 1), e["title"])
#     ))

# filled_mesh = gen_filled_mesh()

####################

flsk = Blueprint(
    'bprnt', __name__,
    static_folder='./backend/static',
)

@cache.memoize(6000000)
def _get_mesh(filter_non_empty, start, n, search, langMatchFilter, ptsynfilter, langFilter, langMesh, langMeshType, langWiki):
    aggmatch = {}
    
    if filter_non_empty:
        aggmatch.update({"wikilangs.langs": {"$ne": None}})
    
    if search is not None and len(search) > 0:
        prepared_search = h.prepare_user_input_search_regex(search)
        print(prepared_search)
        search_re = re.compile(prepared_search, re.IGNORECASE)
        print(search_re)
        aggmatch.update({
            "$or": [
                {"langs": {"$elemMatch": {"pt": {'$regex': search_re}}}},
                {'_id': {"$regex": search_re}}
            ]
        })
    
    if langMatchFilter is not None:
        if langMatchFilter == "no-english":
            aggmatch.update({
                    "wikilangs.lang_match": {"$ne": "en"}
            })
        else:
            aggmatch.update({
                    "wikilangs.lang_match": langMatchFilter
            })

    if ptsynfilter is not None:
        aggmatch.update({
            "wikilangs.origin": ptsynfilter.lower()
        })

    if langFilter is not None:
        if langMesh != "all":
            d = {'$elemMatch': {'_id': langFilter}}
            if langMesh == "no":
                d = {'$not': d}
            aggmatch.update({
                "langs": d
            })
        if langWiki != "all":
            aggmatch.update({
                f"wikilangs.langs.{langFilter}": {'$exists': langWiki=="yes"}
            })
            

    print(aggmatch)
    n_documents = db.db.mesh_view.count_documents(aggmatch)
    
    agg = [
        {
            "$match": aggmatch
        },
        {
            "$skip": start
        },
        {
            "$limit": n
        }
    ]
    ans = list(db.db.mesh_view.aggregate(agg))
    
    print("TOTAL", n_documents)
    return {"count": n_documents, "data": ans}
    

@flsk.route("/api/mesh", methods=["GET"])
def get_mesh():
    args = dict(
        filter_non_empty=request.args.get('filterOnlyNonEmpty', "false") == "true",
        start=int(request.args.get('from', 0)),
        n=int(request.args.get('limit', 10)),
        
        search=request.args.get('search', ""),
        langMatchFilter=request.args.get('langMatchSearch'),
        ptsynfilter=request.args.get('ptsynMatchSearch'),
        
        langFilter=request.args.get('langSearch'),
        langMesh=request.args.get('langMesh'),
        langMeshType=request.args.get('langMeshType'),
        langWiki=request.args.get('langWiki'),
    )
    print("**************************")
    pprint(args)
    return jsonify(_get_mesh(**args))

    
@cache.cached(6000000)
@flsk.route("/api/languages", methods=["GET"])
def get_languages():
    return jsonify([e for e in list(db.db.wikimesh.find({}, {'_id': 0, 'lang_match': 1}).distinct("lang_match"))if e is not None])


@cache.memoize(6000000)
@flsk.route('/api/mesh-stats')
def mesh_stats():
    return jsonify(db_exporter.mesh_stats())


@flsk.route("/status", methods=["GET"])
def health_check():
    logging.debug("debug log")
    logging.info("info log")
    logging.warning("warning log")
    logging.error("error log")
    # logging.exception("exception log")
    return make_response("OK", 200)


@flsk.route('/', defaults={'path': ''})
@flsk.route('/<path:path>')
def index(path):
    return render_template('index.html')

root_url = os.path.join('/', "wikimesh")
static_url_path = os.path.join(root_url, "static")

app = Flask(__name__, static_url_path=static_url_path)
app.register_blueprint(flsk, url_prefix=root_url)
cache.init_app(app)


db.connect()
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app.run(host="0.0.0.0", debug=True)
else:
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(logging.DEBUG)
    logging = app.logger
