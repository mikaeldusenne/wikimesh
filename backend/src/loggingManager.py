import logging
from logging.config import dictConfig
import requests
from os import environ

from backend.src import helpers as h


debug = False


dictConfig({
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "default": {
            "format": f"[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
        },
        "access": {
            "format": "%(message)s",
        }
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
        "log_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "default",
            # "filename": "/var/log/gunicorn.error.log",
            "filename": "./logs/logs.log",
            "maxBytes": 100000,
            "backupCount": 2,
            "delay": "True",
        },
        "error_file_flask": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "default",
            # "filename": "/var/log/gunicorn.error.log",
            "filename": "./logs/flask.error.log",
            "maxBytes": 100000,
            "backupCount": 2,
            "delay": "True",
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "default",
            "filename": "./logs/error.log",
            "maxBytes": 100000,
            "backupCount": 2,
            "delay": "True",
        },
        "events_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "default",
            "filename": "./logs/events.log",
            "maxBytes": 100000,
            "backupCount": 2,
            "delay": "True",
        },
        "access_file_flask": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "access",
            "filename": "./logs/flask.access.log",
            "maxBytes": 100000,
            "backupCount": 2,
            "delay": "True",
        }
    },
    "loggers": {
        "errors": {
            "handlers": ["console", "error_file"],
            "level": "INFO",
            "propagate": False,
        },
        "gunicorn.error": {
            "handlers": ["console", "error_file_flask"],
            "level": "INFO",
            "propagate": False,
        },
        "gunicorn.access": {
            "handlers": ["console", "access_file_flask"],
            "level": "INFO",
            "propagate": False,
        },
    },
    "root": {
        "level": "DEBUG" if debug else "INFO",
        "handlers": ["console", "log_file"],
    }
})
