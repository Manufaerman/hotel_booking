import dj_database_url
from decouple import config
from pathlib import Path
from .base import *

import sys

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'ERROR',
    },
}

BASE_DIR = Path(__file__).resolve().parent.parent
ALLOWED_HOSTS = ['*', 'www.smartagency.es', 'smartagency.es', '46.202.175.212', 'localhost']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'hotelina',
        'USER': 'manuel',
        'PASSWORD': 'Prometheus',
        'PORT': '5432',
        'HOST': 'localhost',
    }
}

SECURE_SSL_REDIRECT = False
DEBUG = False


