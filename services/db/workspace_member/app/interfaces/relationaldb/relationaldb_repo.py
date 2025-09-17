from abc import ABC, abstractmethod
from typing import Any, List

class RelationalDBRepo(ABC):
    @abstractmethod
    def get_all(self) -> List[Any]:
        pass

    @abstractmethod
    def get_by_id(self, item_id: int) -> Any:
        pass

    @abstractmethod
    def create(self, data: Any) -> Any:
        pass

    @abstractmethod
    def update(self, item_id: int, data: Any) -> Any:
        pass

    @abstractmethod
    def delete(self, item_id: int) -> bool:
        pass