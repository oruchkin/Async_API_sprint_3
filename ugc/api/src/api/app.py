import logging

import sentry_sdk
from flasgger import Swagger
from flask import Flask
from .logging_config import logger

sentry_sdk.init(
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for tracing.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)

app = Flask(__name__)

# Swagger available at /apidocs/
swagger = Swagger(app)


# Логирование
@app.before_request
def log_request_info():
    logger.info(
        "Processing request", extra={"path": request.path, "method": request.method}
    )


from .events import *  # noqa: F403, F401, E402
