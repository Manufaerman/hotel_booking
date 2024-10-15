
import os
import environ
import dj_database_url
from decouple import config
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

ALLOWED_HOSTS = ['*']

SITE_ID = 1
SECRET_KEY = config('SECRET_KEY', default='2+@xo)m=q)mg0eauo^b6)n$63i^dio+2-((oy%ugok7q6j8xro')
DEBUG = config('DJANGO_DEBUG', default=True, cast=bool)


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}





SOCIALACCOUNT_PROVIDERS = {
    'github': {
        # For each OAuth based provider, either add a ''SocialApp''
        # (''socialaccount'' app) containing the required client
        # credentials, or list them here:
        'APP': {
            'client_id': 'Ov23liRvpwTwvywBCeAR',
            'secret': '4fe3c71433355e657b3a2a2023bd69eb5d595112',
            'key': ''
        }
    }
}

# redirect after log in and sing up
ACCOUNT_SIGNUP_REDIRECT_URL = "thanks/"
LOGIN_REDIRECT_URL = "/dashboard/"

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'hotel',
    'hotel.booking_functions',
    'django_extensions',
    'user_profile',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.github',
    'whitenoise.runserver_nostatic',
    'crispy_forms',
    'crispy_bootstrap4',
    'rest_framework',

]
CRISPY_TEMPLATE_PACK = 'bootstrap4'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    "allauth.account.middleware.AccountMiddleware",
    'whitenoise.middleware.WhiteNoiseMiddleware'
]

ROOT_URLCONF = 'HMS.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates', 'hotel/templates/hotel', 'user_profile/templates/user_profile'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'HMS.wsgi.application'



# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

SITE_ID = 1

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')  # here is where Nginx will search my files in deployment

STATICFILES_DIRS = [
    # to collect aditional files
]


MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# importat to add when you are adding email authentication
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
ACCOUNT_EMAIL_VERIFICATION = "none"

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTHENTICATION_BACKENDS = [

    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by email
    'allauth.account.auth_backends.AuthenticationBackend',

]

if config('DJANGO_PRODUCTION', default=False, cast=bool):
    DATABASES = {
        'default': dj_database_url.config(
            default=config('DATABASE_URL')
        )
    }

