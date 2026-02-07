from pathlib import Path
from datetime import timedelta
import os

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env if present (dev and prod)
load_dotenv(BASE_DIR / ".env")

# -------------------- Core --------------------
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-insecure-change-me")
DEBUG = os.getenv("DJANGO_DEBUG", "1") == "1"

# Comma-separated hosts: "example.com,.example.com,localhost,127.0.0.1"
ALLOWED_HOSTS = [h.strip() for h in os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",") if h.strip()]

# Dev default
if DEBUG and not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# Prod safety default (agar env qo'ymagan bo'lsangiz ham ishlasin)
if not DEBUG and not ALLOWED_HOSTS:
    ALLOWED_HOSTS = [".railway.app"]

# -------------------- Apps --------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "corsheaders",
    "rest_framework",

    "users",
    "academics",
    "messaging",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "users.middleware.UpdateLastSeenMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# -------------------- Database --------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Uses DATABASE_URL if provided (recommended in production)
db_url = os.getenv("DATABASE_URL")
if db_url:
    import dj_database_url
    DATABASES["default"] = dj_database_url.parse(db_url, conn_max_age=600, ssl_require=not DEBUG)

# -------------------- Auth & REST --------------------
AUTH_USER_MODEL = "users.User"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}

# -------------------- i18n --------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Tashkent"
USE_I18N = True
USE_TZ = True

# -------------------- Static & Media --------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -------------------- CORS / CSRF --------------------
# Comma-separated origins: "https://app.example.com,http://localhost:5173"
# -------------------- CORS / CSRF --------------------
# Comma-separated origins: "https://app.example.com,http://localhost:5173"
cors_origins = [o.strip() for o in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",") if o.strip()]

if cors_origins:
    CORS_ALLOWED_ORIGINS = cors_origins
else:
    # Dev default
    CORS_ALLOWED_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]

# Netlify preview domains uchun (xohlasangiz yoqing)
CORS_ALLOW_ALL_ORIGINS = os.getenv("CORS_ALLOW_ALL_ORIGINS", "0") == "1"

# JWT bo'lsa credential shart emas, lekin kerak bo'lsa env bilan yoqiladi
CORS_ALLOW_CREDENTIALS = os.getenv("CORS_ALLOW_CREDENTIALS", "0") == "1"

# CSRF trusted origins (cookies ishlatsa kerak bo'ladi; hozir JWT bo'lsa ham zarar qilmaydi)
csrf_trusted = [o.strip() for o in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()]
if csrf_trusted:
    CSRF_TRUSTED_ORIGINS = csrf_trusted
else:
    # Dev default
    CSRF_TRUSTED_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]

# -------------------- Security for production --------------------
# -------------------- Security for production --------------------
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

    # Railway/Netlify'da ko'pincha redirect kerak emas (Netlify allaqachon https beradi),
    # lekin xohlasangiz env orqali yoqib qo'yasiz:
    SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "0") == "1"

    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # Static/media uchun xavfsiz
    SECURE_REFERRER_POLICY = "same-origin"

    # HSTS (avval 0, keyin asta-sekin oshiring)
    SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "0"))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
