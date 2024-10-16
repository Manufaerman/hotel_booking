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