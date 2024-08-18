from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseStorage(ABC):
    @abstractmethod
    def save_state(self, state: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def retrieve_state(self) -> dict[str, Any]:
        pass
