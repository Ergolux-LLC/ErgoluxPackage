from abc import ABC, abstractmethod
from typing import Optional
from app.interfaces.keyvalue.token_data_object import UserToken

class KeyValueRepository(ABC):
    @abstractmethod
    async def get_token(self, key: UserToken) -> Optional[str]:
        pass

    @abstractmethod
    async def set_token(self, key: UserToken, value: str, ex: Optional[int] = None) -> None:
        pass

    @abstractmethod
    async def delete_token(self, key: UserToken) -> None:
        pass
