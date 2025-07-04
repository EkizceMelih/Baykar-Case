import os
from pathlib import Path
import environ


BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env(
    DEBUG=(bool, False)
)

environ.Env.read_env(os.path.join(BASE_DIR, '.env'))


SECRET_KEY = env('SECRET_KEY')
DEBUG      = env('DEBUG')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

# ---------- INSTALLED APPS -------------
INSTALLED_APPS = [
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # third party eklediklerim
    'rest_framework',
    'rest_framework.authtoken',
    'drf_yasg',
    'django_filters',
    'widget_tweaks',          
    'django_datatables_view',  


    # Yerel uygulamalar
    'users',
    'inventory',
    'assembly',
]
# --------------------------------------

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'aircraft_production.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],   # ← Proje kökündeki templates klasörü
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

WSGI_APPLICATION = 'aircraft_production.wsgi.application'

#DATABASE KISMI
DATABASES = {
    'default': env.db_url('DATABASE_URL')
}


AUTH_USER_MODEL = 'users.User'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
}

# ------ Internationalization -------
LANGUAGE_CODE = 'en-us'
TIME_ZONE    = 'Europe/Istanbul'
USE_I18N     = True
USE_L10N     = True
USE_TZ       = True

# ------ Static & Media Files ------
STATIC_URL   = '/static/'
STATIC_ROOT  = BASE_DIR / 'static'

MEDIA_URL    = '/media/'
MEDIA_ROOT   = BASE_DIR / 'media'

# ---------- Default PK field ----------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
