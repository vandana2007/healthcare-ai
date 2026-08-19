"""
settings.py
==============================================
This is Django's central configuration file.
==============================================
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url
# --------------------------------------------------
# STEP 1: Load environment variables from .env
# --------------------------------------------------
load_dotenv()

# --------------------------------------------------
# STEP 2: Base directory of the project
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------------------------------------
# STEP 3: Security settings (from .env — never hardcoded)
# --------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.getenv("DEBUG", "False") == "True"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")

# --------------------------------------------------
# STEP 4: Installed apps
# --------------------------------------------------
INSTALLED_APPS = [
    # --- Django built-in apps ---
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",

    # --- Third-party apps ---
    "rest_framework",
    "corsheaders",

    # --- Our custom apps ---
    "chatbot",
    "appointments",
    "reminders",
    "reports",
    "accounts",
    "hospitals",
    "doctors",
    "cloudinary_storage",
    "django.contrib.staticfiles",
    "cloudinary",
]

# --------------------------------------------------
# STEP 5: Middleware
# --------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# --------------------------------------------------
# STEP 6: URL configuration entry point
# --------------------------------------------------
ROOT_URLCONF = "healthcare_project.urls"

# --------------------------------------------------
# STEP 7: Template configuration
# --------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "healthcare_project.context_processors.vapid_key",
            ],
        },
    },
]

WSGI_APPLICATION = "healthcare_project.wsgi.application"

# --------------------------------------------------
# STEP 8: Database configuration (PostgreSQL)
# --------------------------------------------------
DATABASES = {
    "default": dj_database_url.config(
        default=f"postgresql://{os.getenv('DB_USER', 'postgres')}:{os.getenv('DB_PASSWORD', '')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'healthcare_ai')}",
        conn_max_age=600,
    )
}

# --------------------------------------------------
# STEP 9: Password validation
# --------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --------------------------------------------------
# STEP 10: Internationalization
# --------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

# --------------------------------------------------
# STEP 11: Static & media files
# --------------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# --------------------------------------------------
# STEP 12: Default primary key field type
# --------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --------------------------------------------------
# STEP 13: CORS settings
# --------------------------------------------------
CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]

# --------------------------------------------------
# STEP 14: Django REST Framework settings
# --------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
}

# --------------------------------------------------
# STEP 15: Custom setting — our supported chat languages
# --------------------------------------------------
SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "te": "Telugu",
}

# --------------------------------------------------
# STEP 16: Authentication redirect settings
# --------------------------------------------------
LOGIN_URL = "login_view"
LOGIN_REDIRECT_URL = "chat_view"
LOGOUT_REDIRECT_URL = "login_view"

# --------------------------------------------------
# STEP 17: Geocoding configuration
# --------------------------------------------------
# Nominatim (OpenStreetMap) requires a unique app identifier
# in every request — this is their usage policy, not optional.
GEOCODING_USER_AGENT = "ai_healthcare_assistant_app"
#added
# -----------------------------
# Web Push (VAPID)
# -----------------------------
VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY")
VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY")
VAPID_CLAIMS = {
    "sub": os.getenv("VAPID_CLAIMS_EMAIL")
}
# --------------------------------------------------
# Web Push (VAPID) configuration
# --------------------------------------------------
VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY", "").replace("\\n", "\n")
VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY", "")
VAPID_CLAIMS_EMAIL = os.getenv("VAPID_CLAIMS_EMAIL", "mailto:admin@example.com")

# --------------------------------------------------
# Email configuration (Gmail SMTP)
# --------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
# --------------------------------------------------
# Cloudinary — persistent cloud storage for uploaded
# files (profile pics, reports), since Render's free
# tier has no persistent disk.
# --------------------------------------------------
CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.getenv("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": os.getenv("CLOUDINARY_API_KEY"),
    "API_SECRET": os.getenv("CLOUDINARY_API_SECRET"),
}
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"