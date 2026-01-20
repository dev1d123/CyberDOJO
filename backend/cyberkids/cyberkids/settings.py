

from pathlib import Path
import dj_database_url
from dotenv import load_dotenv
import os

import cloudinary

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GOOGLE_GENAI_API_KEY = GEMINI_API_KEY

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-change-this-in-production-cyberkids-2024'

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']



INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    # Third-party apps
    'rest_framework',
    'drf_yasg',
    
    # CyberKids Apps
    'apps.cyberUser',          # User Core: user, country, risk_level
    'apps.simulation',         # Social Engineering Simulation
    'apps.pets',               # Emotional Feedback System
    'apps.minigames',          # Gamified Events
    'apps.progression',        # Progression and Economy
    'apps.onboarding',         # Initial Risk Identification

    'cloudinary',
    'cloudinary_storage',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'cyberkids.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'cyberkids.wsgi.application'


# Database

DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    # Producción
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=True,
        )
    }
else:
    # Desarrollo local (SQLite)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }



# Password validation

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Django REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'apps.cyberUser.auth_backend.JWTCustomAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# JWT Configuration
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    "USER_ID_FIELD": "user_id",
    "USER_ID_CLAIM": "user_id",
}

# CORS Configuration
CORS_ALLOW_ALL_ORIGINS = True
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

# Hosts permitidos
ALLOWED_HOSTS = ['*']

CLOUDINARY_CLOUD_NAME = 'dsvynqyq5'
CLOUDINARY_API_KEY = '537782675375588'
CLOUDINARY_API_SECRET = '9tbhQfQOxFjU1Xb-yZZiyXvM72I'

import os
PYTHONANYWHERE_DOMAIN = os.environ.get('PYTHONANYWHERE_DOMAIN')

cloudinary_config = {
    'cloud_name': 'dsvynqyq5',
    'api_key': '537782675375588',
    'api_secret': '9tbhQfQOxFjU1Xb-yZZiyXvM72I',
}

if PYTHONANYWHERE_DOMAIN:
    PYTHONANYWHERE_PROXY = 'http://proxy.server:3128'
    os.environ['HTTP_PROXY'] = PYTHONANYWHERE_PROXY
    os.environ['HTTPS_PROXY'] = PYTHONANYWHERE_PROXY
    cloudinary_config['api_proxy'] = PYTHONANYWHERE_PROXY

cloudinary.config(**cloudinary_config)
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

CSRF_TRUSTED_ORIGINS = [
    "https://cyberdojo-production.up.railway.app",
]