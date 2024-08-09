import logging

from flasgger import Swagger
from flask import Flask

app = Flask(__name__)

# Swagger available at /apidocs/
swagger = Swagger(app)


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

from .events import *
