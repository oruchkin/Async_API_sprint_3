import sys
from http import HTTPStatus

from flask import jsonify, request
from models.movie_progress import MovieProgress
from pydantic_core import ValidationError
from services.kafka_client import KafkaClient
from services.kafka_settings import KafkaSettings

from .app import app

settings = KafkaSettings()


@app.route("/event", methods=["POST"])
async def post_event():
    """
    Endpoint to collect user generated events
    ---
    parameters:
      - in: body
        name: body
        required: true
        description: Request body
        example: {
          "type": "movie_progress",
          "user_id": "4518e644-1ff3-4003-a14e-99dfe3fdd7ab",
          "movie_id": "e9897504-9b73-40bb-a22e-815daf7a190d",
          "progress": 123
        }
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

    client = KafkaClient(settings)

    payload = request.json
    if not isinstance(payload, dict):
        return jsonify({"success": False}), HTTPStatus.BAD_REQUEST

    if payload.get("type") == "movie_progress":
        # For simplicity get user_id from the post body
        # For access_token decode use idp/src/core/verification.py
        try:
            model = MovieProgress.model_validate(payload)
            await client.post_movie_progress(model)
        except ValidationError as err:
            return (
                jsonify({"success": False, "message": "Invalid format", "validation": err.errors()}),
                HTTPStatus.BAD_REQUEST,
            )
    else:
        return (jsonify({"success": False, "message": "Unkown even type"}), HTTPStatus.BAD_REQUEST)

    return jsonify({"success": True}), HTTPStatus.OK
