from pathlib import Path
import os

# Lee variables de entorno desde .env si existe (solo local)
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# DB URL parser (Postgres/SQLite) mediante DATABASE_URL
try:
    import dj_database_url
except Exception:
    dj_database_url = None

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Seguridad / modo
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'dev-secret-key-change-me')
DEBUG = os.getenv('DJANGO_DEBUG', 'True').lower() == 'true'
ALLOWED_HOSTS = [h.strip() for h in os.getenv('DJANGO_ALLOWED_HOSTS', '*').split(',') if h.strip()]

# HTTPS/CSRF detrás de proxy del PaaS
CSRF_TRUSTED_ORIGINS = [o.strip() for o in os.getenv('CSRF_TRUSTED_ORIGINS','').split(',') if o.strip()]
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# --- Apps
INSTALLED_APPS = [
    'django.contrib.admin','django.contrib.auth','django.contrib.contenttypes',
    'django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles',
    'expenses',
]

# --- Middleware (Whitenoise debe ir inmediatamente después de SecurityMiddleware)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'absl_expenses.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ],},
}]

WSGI_APPLICATION = 'absl_expenses.wsgi.application'

# --- Database
DEFAULT_DB = f"sqlite:///{BASE_DIR / 'db.sqlite3'}"
if dj_database_url:
    DATABASES = {
        'default': dj_database_url.parse(os.getenv('DATABASE_URL', DEFAULT_DB), conn_max_age=600)
    }
else:
    # Fallback: sin dj-database-url
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# --- Locale
LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'America/Los_Angeles'
USE_I18N = True
USE_TZ = True

# --- Static / Media
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'            # donde collectstatic agrupa todo para prod
STATICFILES_DIRS = [BASE_DIR / 'static']          # tu carpeta de assets fuente (dev)

# Whitenoise: sirve estáticos comprimidos y con hash en prod (no hace falta S3 para static)
STORAGES = {
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'                   # dónde se guardan fotos subidas (dev/staging simple)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'
