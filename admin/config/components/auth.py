import os

AUTH_USER_MODEL = "movies.User"

AUTHENTICATION_BACKENDS = [
    "movies.auth.CustomBackend",
    # "django.contrib.auth.backends.ModelBackend",
]

# Fails while collectstatic run
AUTH_API_LOGIN_URL = f"{os.environ['IDP_URL']}/api/v1" if "IDP_URL" in os.environ else None
