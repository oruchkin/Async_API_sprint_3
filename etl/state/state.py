from datetime import datetime, timedelta
from typing import Any

from state.state_storage import BaseStorage


class State:
    def __init__(self, storage: BaseStorage) -> None:
        self._storage = storage

    def set_state(self, key: str, value: str) -> None:
        # FIXME: Зачем мы тут парсим время?
        value_dt = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")

        # FIXME: Это неправильно, ничего нельзя округлять - мы так пропускам данные
        # Округляем до следующей полной секунды
        if value_dt.microsecond > 0:
            value_dt += timedelta(seconds=1)
            value_dt = value_dt.replace(microsecond=0)

        value_str = value_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        state = self._storage.retrieve_state()
        state[key] = value_str
        self._storage.save_state(state)

    def get_state(self, key: str, default=None) -> Any:
        state = self._storage.retrieve_state()
        return state.get(key, default)
