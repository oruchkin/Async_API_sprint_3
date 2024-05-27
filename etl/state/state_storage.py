from typing import Any, Dict


class BaseStorage:
    def save_state(self, state: Dict[str, Any]) -> None: ...

    def retrieve_state(self) -> dict[str, Any]: ...
