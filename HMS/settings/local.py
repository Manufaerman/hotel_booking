from .common import *

DEBUG = True
ALLOWED_HOSTS = []
SECRET_KEY ='2+@xo)m=q)mg0eauo^b6)n$63i^dio+2-((oy%ugok7q6j8xro'
DATABASES = {
        'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

STATIC_URL = '/static/'

django_heroku.settings(locals())