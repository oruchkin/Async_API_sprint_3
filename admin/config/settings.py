# Django 4.2.5.


from dotenv import load_dotenv
from split_settings.tools import include

load_dotenv()

include(
    "components/auth_password_validators.py",
    "components/installed_apps.py",
    "components/configuration.py",
    "components/middleware.py",
    "components/templates.py",
    "components/database.py",
    "components/logging.py",
    "components/static.py",
    "components/file_storage.py",
)
