from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-tne!4+=5cizkx=!7pt^l#0ksv%ralt2f!zpger#ubkm)4=pi@d'
DEBUG = True

ALLOWED_HOSTS = ['bbd.pythonanywhere.com', 'localhost', '127.0.0.1']
CSRF_TRUSTED_ORIGINS = [
    'https://bbd.pythonanywhere.com',
    'http://localhost',
    'http://127.0.0.1', 
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'market',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bbdolx.urls'

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
                'market.context_processors.notifications_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'bbdolx.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
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

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# -------- Static & media (PythonAnywhere) --------
# URL that the browser will use
STATIC_URL = '/static/'

# Extra folders with your custom static files (optional but you already use it)
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Folder where collectstatic will put everything (admin CSS, etc.)
# This MUST match the directory in the PythonAnywhere "Static files" config
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# -------- Login / Logout redirects --------
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/accounts/login/'

# -------- Apps Script OTP mailer --------
APPS_SCRIPT_OTP_URL = "https://script.google.com/macros/s/AKfycbyXt0lL1BqgnDQkk0zcfb1ndMxJYDvESQyM-nu-vNkUIDEmqeKa9GcWRphtnUij21xk/exec"
APPS_SCRIPT_OTP_SECRET = "02478162820713575730"
