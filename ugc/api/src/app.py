import logging

from flasgger import Swagger
from flask import Flask
from services.kafka_client import KafkaClient
from services.kafka_settings import KafkaSettings

app = Flask(__name__)

# Swagger available at /apidocs/
swagger = Swagger(app)


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@app.route("/hello-world")
def hello_world():
    """Example endpoint returning a list of colors by palette
    This is using docstrings for specifications.
    ---
    parameters:
      - name: palette
        in: path
        type: string
        enum: ['all', 'rgb', 'cmyk']
        required: true
        default: all
    definitions:
      Palette:
        type: object
        properties:
          palette_name:
            type: array
            items:
              $ref: '#/definitions/Color'
      Color:
        type: string
    responses:
      200:
        description: A list of colors (may be filtered by palette)
        schema:
          $ref: '#/definitions/Palette'
        examples:
          rgb: ['red', 'green', 'blue']
    """

    settings = KafkaSettings()
    client = KafkaClient(settings)
    client.ensure_topic("movies_progress")

    return "Hello, World!"


if __name__ == "__main__":
    app.run()
