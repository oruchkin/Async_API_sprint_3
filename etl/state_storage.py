import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict


class BaseStorage:
    def save_state(self, state: Dict[str, Any]) -> None:
        pass

    def retrieve_state(self) -> Dict[str, Any]:
        pass


class JsonFileStorage(BaseStorage):
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path

    def save_state(self, state: Dict[str, Any]) -> None:
        with open(self.file_path, 'w') as file:
            json.dump(state, file)

    def retrieve_state(self) -> Dict[str, Any]:
        if not os.path.exists(self.file_path):
            return {}
        with open(self.file_path, 'r') as file:
            return json.load(file)


class State:
    def __init__(self, storage: JsonFileStorage) -> None:
        self.storage = storage

    def set_state(self, key: str, value: str) -> None:
        value_dt = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')

        # Округляем до следующей полной секунды
        if value_dt.microsecond > 0:
            value_dt += timedelta(seconds=1)
            value_dt = value_dt.replace(microsecond=0)

        value_str = value_dt.strftime('%Y-%m-%dT%H:%M:%SZ')

        state = self.storage.retrieve_state()
        state[key] = value_str
        self.storage.save_state(state)

    def get_state(self, key: str, default=None) -> Any:
        state = self.storage.retrieve_state()
        return state.get(key, default)
