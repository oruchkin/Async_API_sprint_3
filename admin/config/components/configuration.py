import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = os.environ.get("DEBUG", False) == "True"
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "*"]

LANGUAGE_CODE = "ru-RU"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
SECRET_KEY = os.environ.get("ADMIN_SECRET_KEY")

LOCALE_PATHS = [os.path.join(BASE_DIR, "locale")]


INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
]
