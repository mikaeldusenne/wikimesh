from flask import Flask, render_template, jsonify, redirect, flash, request, url_for, Response, Blueprint, send_from_directory
import flask
from flask_caching import Cache
import logging
from os.path import join, dirname
import json
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

@cache.memoize(6000000)
def query_wiki_langs(search):
    return db.db.mesh.find_one({'title': search}).get("links", []) # ftc.query_wiki_langs(search)


def gen_filled_mesh():
    return list(sorted(
        db.db.mesh.find(),
        key=lambda e: ((0 if e["title"][0].lower() in "azertyuiopsqdfghjklmwxcvbn" else 1), e["title"])
    ))

filled_mesh = gen_filled_mesh()

####################

flsk = Blueprint(
    'bprnt', __name__,
    static_folder='./backend/static',
)

@flsk.route("/api/mesh", methods=["GET"])
def get_mesh():
    filter_non_empty = request.args.get('filterOnlyNonEmpty', False)
    start = int(request.args.get('from', 0))
    n = int(request.args.get('limit', 10))
    search = request.args.get('search')
    print("SEARCH", start, n, search)
    ans = filled_mesh
    
    if filter_non_empty:
        ans = [e for e in ans if len(e['links'])]
    
    if search is not None and len(search) > 0:
        ans = [
            e for e in ans
            if re.match(h.prepare_user_input_search_regex(search), e['title'], re.IGNORECASE)
            or re.match(h.prepare_user_input_search_regex(search), e['id'], re.IGNORECASE)
        ]

    print("TOTAL", len(ans))
    return jsonify({"count": len(ans), "data": ans[start: start+n]}), 200


@flsk.route('/pictures/<path:path>')
def send_pic(path):
    return send_from_directory('backend/pictures', path)


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
