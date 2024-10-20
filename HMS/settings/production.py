import dj_database_url
from decouple import config
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL')
    )
}
SECURE_SSL_REDIRECT = False
DEBUG = False

STATICFILES_STORAGE = 'django.contrib.static.storage.StaticFilesStorage'
ALLOWED_HOSTS = ['powerful-garden-90023-0b97dae15c35.herokuapp.com', 'localhost', '127.0.0.1', 'https://powerful'
                                                                                               '-garden-90023'
                                                                                               '-0b97dae15c35'
                                                                                               '.herokuapp.com', '*', ]
