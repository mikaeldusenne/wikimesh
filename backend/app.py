from flask import Flask, render_template, jsonify, redirect, flash, request, url_for, Response, Blueprint, send_from_directory
import flask
from flask_caching import Cache
from redis import Redis
import logging
from os.path import join, dirname
import json
import re
import traceback
from pprint import pprint
from os import environ
import os

import backend.src.helpers as h
import backend.src.db as db
from backend.src import wiki_fetcher as ftc
from backend.src import mesh_parser
from backend.src import db_exporter

REDIS_URL = 'redis://redis'
cache = Cache(config={
    # 'CACHE_TYPE': 'FileSystemCache', 'CACHE_DIR': '/.flask-cache', "CACHE_DEFAULT_TIMEOUT": 9999999
    'CACHE_TYPE': 'RedisCache',
    'CACHE_REDIS_URL': REDIS_URL,
    'CACHE_REDIS_PORT': '6379',
    "CACHE_DEFAULT_TIMEOUT": 9999999,
})
redis_client = Redis.from_url(REDIS_URL, socket_connect_timeout=2, socket_timeout=2)


def logging_setup(path):
    loggingdest = os.path.join(path, "flask.log")
    print("setting logging to {}".format(loggingdest))

    logFormatter = logging.Formatter(
        "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    # Production defaults to warnings; development stays verbose.
    rootLogger = logging.getLogger('wikimesh')
    rootLogger.setLevel(logging.WARNING if os.environ.get(
        "PROD", False) else logging.DEBUG)

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

flsk = Blueprint('bprnt', __name__)


def _int_arg(name, default, minimum=0, maximum=None):
    try:
        value = int(request.args.get(name, default))
    except (TypeError, ValueError):
        raise ValueError(f"{name} must be an integer") from None
    if value < minimum or maximum is not None and value > maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum if maximum is not None else '∞'}")
    return value


def _choice_arg(name, default, choices):
    value = request.args.get(name, default)
    if value not in choices:
        raise ValueError(f"{name} must be one of {', '.join(choices)}")
    return value


@cache.memoize()
def _get_mesh(filter_non_empty, start, n, search, langMatchFilter, ptsynfilter, langFilter, langMesh, langWiki, identifier=None):
    aggmatch = {}
    
    if identifier is not None:
        aggmatch.update({"identifier": identifier})
    
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
                {'_id': {'$regex': search_re}}
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
    try:
        args = dict(
            filter_non_empty=request.args.get('filterOnlyNonEmpty', "false") == "true",
            start=_int_arg('from', 0),
            n=_int_arg('limit', 10, 1, 100),
            
            search=request.args.get('search', "").strip()[:75],
            langMatchFilter=request.args.get('langMatchSearch'),
            ptsynfilter=request.args.get('ptsynMatchSearch'),
            
            langFilter=request.args.get('langSearch'),
            langMesh=_choice_arg('langMesh', 'all', ('yes', 'no', 'all')),
            langWiki=_choice_arg('langWiki', 'all', ('yes', 'no', 'all')),
            
            identifier=request.args.get('identifier'),
        )
    except ValueError as error:
        return jsonify(error=str(error)), 400
    return jsonify(_get_mesh(**args))

    
@flsk.route("/api/languages", methods=["GET"])
@cache.cached()
def get_languages():
    return jsonify([e for e in list(db.db.wikimesh.find({}, {'_id': 0, 'lang_match': 1}).distinct("lang_match"))if e is not None])


@flsk.route("/api/identifiers", methods=["GET"])
@cache.cached()
def get_identifiers():
    return jsonify(db.db.mesh.distinct("identifier"))


@flsk.route('/api/mesh-stats')
@cache.cached()
def mesh_stats():
    return jsonify(db_exporter.mesh_stats())


@flsk.route("/status", methods=["GET"])
def health_check():
    return "OK", 200


@flsk.route("/ready", methods=["GET"])
def readiness_check():
    try:
        db.connect().command("ping")
        redis_client.ping()
        return "OK", 200
    except Exception:
        logging.exception("readiness check failed")
        return "NOT READY", 503


@flsk.route('/', defaults={'path': ''})
@flsk.route('/<path:path>')
def index(path):
    return render_template('index.html')

app = Flask(__name__, static_url_path="/static")
app.register_blueprint(flsk)
cache.init_app(app)


@app.before_request
def ensure_db():
    # Health endpoints own their dependency checks.
    if request.endpoint not in {'bprnt.health_check', 'bprnt.readiness_check'}:
        db.connect()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app.run(host="0.0.0.0", debug=True)
else:
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(logging.WARNING if os.environ.get("PROD") else logging.DEBUG)
    logging = app.logger
