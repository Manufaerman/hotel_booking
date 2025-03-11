import dj_database_url
from decouple import config
from pathlib import Path
from .base import *


BASE_DIR = Path(__file__).resolve().parent.parent
ALLOWED_HOSTS = ['*', 'www.smartagency.es', 'smartagency.es', '46.202.175.212']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'hotelina',
        'user': 'manuel',
        'PASSWORD': 'Prometheus',
        'PORT': 5432,
        'HOST': 'localhost',

    }
}
SECURE_SSL_REDIRECT = False
DEBUG = False

STATICFILES_STORAGE = 'django.contrib.static.storage.StaticFilesStorage'
ALLOWED_HOSTS = ['', 'localhost', '127.0.0.1', ''
                                                                                               '-garden-90023'
                                                                                               '-0b97dae15c35'
                                                                                               '.herokuapp.com', '*','46.202.175.212']
