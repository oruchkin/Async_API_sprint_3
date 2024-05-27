import json
import os
from typing import Any

from state.state_storage import BaseStorage


class JsonFileStorage(BaseStorage):
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path

    def save_state(self, state: dict[str, Any]) -> None:
        with open(self.file_path, "w") as file:
            json.dump(state, file)

    def retrieve_state(self) -> dict[str, Any]:
        if not os.path.exists(self.file_path):
            return {}
        with open(self.file_path, "r") as file:
            return json.load(file)
