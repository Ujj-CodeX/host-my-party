"""
Django settings for config project.
"""
from dotenv import load_dotenv
import os
load_dotenv()
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-f)hmm7n!2bzbqin)o8ye-w7jdgk2e*-st)35$-507#_5izqr-u'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Our custom User (accounts app) replaces Django's built-in one entirely —
# must be set before any migrations touching auth-related tables run.
AUTH_USER_MODEL = "account.User"

# Silences the W042 warning and gives new models a 64-bit primary key by
# default instead of the older 32-bit AutoField.
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Django needs this to know which callable serves HTTP vs WebSocket —
# daphne (in INSTALLED_APPS below) reads this to make `runserver` ASGI-aware.
ASGI_APPLICATION = "config.asgi.application"
WSGI_APPLICATION = "config.wsgi.application"


# Application definition

INSTALLED_APPS = [
    'daphne',  # MUST be first — makes runserver ASGI/WebSocket-aware
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',

    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',

    'account',
    'party',
    'order',
    'core',
    'ai',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# Database — Supabase Postgres via DATABASE_URL in .env.
# conn_max_age reuses connections for 10 min instead of reconnecting on
# every request (Supabase is remote, unlike the old local SQLite file).
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # VueJS default port
]


# DRF — every view authenticates via JWT unless it explicitly overrides
# authentication_classes (like the GuestSession-authenticated endpoints).
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": os.getenv("JWT_SECRET_KEY"),
}

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")


# Channels — realtime host-dashboard sync (Section 5.3.3), backed by
# Redis (running via Docker locally — see hostmyparty-redis container).
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [{
                "address": os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0"),
                "socket_timeout": None,
            }],
        },
    },
}

# Celery — late-arrival order firing (Section 5.3.6), backed by the same
# Redis instance CHANNEL_LAYERS already uses.
CELERY_BROKER_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
CELERY_RESULT_BACKEND = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'



GROQ_API_KEY = os.getenv("GROQ_API_KEY")