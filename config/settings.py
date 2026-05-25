import dj_database_url
from pathlib import Path
import os
from app_modules.quiz.log_filters import InfoOrErrorFilter

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-ny+!$q8y65e54a^ekhck7a8^1)!uzqk7z&+t_zbmp8r!lk-g$e'

DEBUG = False

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'prismteam-backend.onrender.com',
    '*.onrender.com',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'corsheaders',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'channels',
    'app_modules.quiz',
    'app_modules.quiz_sessions',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
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

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    }
}

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

DATABASES = {
    'default': dj_database_url.config(default='sqlite:///db.sqlite3')
}

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

LOG_DIR = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": '{asctime} - {levelname} - {message}',
            "style": "{",
        },
        "verbose": {
            "format": '[{asctime}] {levelname} {name} ({filename}:{lineno}): {message}',
            "style": "{",
        },
    },
    "filters": {
        "info_or_error": {
            "()": InfoOrErrorFilter,
        }
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "ws_file": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, 'websocket.log'),
            "formatter": "verbose",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 3,
        },
        "app_file": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, 'app.log'),
            "formatter": "verbose",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
        },
        "error_file": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, 'error.log'),
            "formatter": "verbose",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 3,
        },
    },
    'loggers': {
        "login_log": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "quiz_log": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "ws": {
            "handlers": ["ws_file", "app_file", "console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["error_file", "app_file"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'

AUTH_USER_MODEL = 'quiz.User'

CORS_ALLOWED_ORIGINS = [
    "https://prismteam-frontend.onrender.com",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}