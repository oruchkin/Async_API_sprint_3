import json
import logging

from flasgger import Swagger
from flask import Flask, request
from models.movie_progress import MovieProgress
from services.kafka_client import KafkaClient
from services.kafka_settings import KafkaSettings

app = Flask(__name__)

# Swagger available at /apidocs/
swagger = Swagger(app)


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


supported = ["movie_progress"]


@app.route("/event", methods=["POST"])
def post_event():
    """
    Endpoint to collect user generated events
    ---
    parameters:
      - in: body
        name: body
        required: true
        description: Request body
        example: { "type": "movie_progress", "user_id": "4518e644-1ff3-4003-a14e-99dfe3fdd7ab", "movie_id": "e9897504-9b73-40bb-a22e-815daf7a190d", "progress": 123 }
    requestBody:
        required: true
        content:
          application/json:
            $ref: '#/definitions/Event'
    definitions:
      Event:
        type: object
        properties:
          type: string
    responses:
      200:
        description: Doesn't return any results
    """

    settings = KafkaSettings()
    client = KafkaClient(settings)

    payload = request.json
    if not isinstance(payload, dict):
        return json.dumps({"success": False}), 400, {"ContentType": "application/json"}

    if payload.get("type") == "movie_progress":
        # For simplicity get user_id from the post body
        # For access_token decode use idp/src/core/verification.py
        model = MovieProgress.model_validate(payload)
        client.post_movie_progress(model)

    return json.dumps({"success": True}), 200, {"ContentType": "application/json"}


if __name__ == "__main__":
    app.run()
