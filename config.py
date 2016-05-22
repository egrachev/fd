# -*- coding: utf-8 -*-

import os
from logging import config


BASE_DIR = os.path.abspath(os.path.dirname(__name__))
LOG_DIR = os.path.join(BASE_DIR, 'logs')
CASCADES_DIR = os.path.join(BASE_DIR, 'cascades')
FONTS_DIR = os.path.join(BASE_DIR, 'fonts')

USER_IMAGES_DIR = os.path.join(BASE_DIR, 'user_images')
USER_FEATURES_DIR_NAME = 'features'

OVERLAYS_DIR = os.path.join(BASE_DIR, 'overlays')

# detect params
FEATURE_SCALE = 1.3
FEATURE_MIN_NEIGHBORS = 10

DB_HOST = ''
DB_USER = 'postgres'
DB_PASS = ''
DB_NAME = 'fd'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(asctime)s [%(levelname)s][%(name)s:%(lineno)d]: %(message)s'
        },
    },
    'handlers': {
        'file_handler': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'bot.log'),
            'formatter': 'simple',
            'when': 'h',
            'interval': 24,
            'backupCount': 7,

        },
        'console_handler': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'simple',
            'stream': 'ext://sys.stdout',
        },
    },
    'loggers': {
        'bot': {
            'handlers': ['file_handler', 'console_handler'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'detect': {
            'handlers': ['file_handler', 'console_handler'],
            'propagate': True,
            'level': 'DEBUG',
        },

        'pony.orm': {
            'handlers': ['console_handler'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'pony.orm.sql': {
            'handlers': ['console_handler'],
            'propagate': True,
            'level': 'DEBUG',
        },

    }
}

config.dictConfig(LOGGING)


# consts
POSITION_UPPER_TOP = 0
POSITION_TOP = 1
POSITION_CENTER = 2
POSITION_BOTTOM = 3
POSITION_LOWER_BOTTOM = 4
POSITION_LEFT = 5
POSITION_RIGHT = 6

STATUS_OPEN = 0
STATUS_CLOSE = 1
STATUS_CURRENT = 2
