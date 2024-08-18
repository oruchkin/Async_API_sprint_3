import json
import os
from typing import Any, cast

from .state_storage import BaseStorage


class JsonFileStorage(BaseStorage):
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path

    def save_state(self, state: dict[str, Any]) -> None:
        with open(self.file_path, "w") as file:
            json.dump(state, file)

    def retrieve_state(self) -> dict[str, Any]:
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as file:
                return cast(dict[str, Any], json.load(file))

        return {}
