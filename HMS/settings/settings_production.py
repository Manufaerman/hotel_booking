import dj_database_url
from decouple import config
DEBUG: False
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'powerful-garden-90023-0b97dae15c35.herokuapp.com', 'herokuapp.com']


DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL')
    )
}
