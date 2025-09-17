import logging
from typing import Optional

from app.infrastructure.keyvalue.redis_driver import RedisDriver
from app.interfaces.keyvalue.keyvalue_repo import KeyValueRepository
from app.interfaces.keyvalue.token_data_object import UserToken
from app.common.config import Config

logger = logging.getLogger(__name__)

class RedisAdapter(KeyValueRepository):
    def __init__(self, config: Config):
        driver = RedisDriver(config)
        self._client = driver.get_client()
        logger.info("RedisAdapter initialized")

    async def get_token(self, key: UserToken) -> Optional[str]:
        key_str = str(key)
        logger.debug("GET %s", key_str)
        value = await self._client.get(key_str)
        logger.debug("-> %s", value)
        return value

    async def set_token(self, key: UserToken, value: str, ex: Optional[int] = None) -> None:
        key_str = str(key)
        logger.debug("SET %s = %s (ex=%s)", key_str, value, ex)
        await self._client.set(key_str, value, ex=ex)

    async def delete_token(self, key: UserToken) -> None:
        key_str = str(key)
        logger.debug("DEL %s", key_str)
        await self._client.delete(key_str)
