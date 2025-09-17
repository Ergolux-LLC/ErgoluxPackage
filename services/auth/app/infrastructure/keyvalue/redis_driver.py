import redis.asyncio as redis
from app.common.config import Config

class RedisDriver:
    _instance = None

    def __new__(cls, config: Config):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize(config)
        return cls._instance

    def _initialize(self, config: Config):
        self._config = config
        self._client = self._create_client()

    def _create_client(self) -> redis.Redis:
        host = self._config.get("REDIS_HOST")
        port = self._config.get("REDIS_PORT")
        db = self._config.get("REDIS_DB")
        password = self._config.get("REDIS_PASSWORD")
        ssl_raw = self._config.get("REDIS_SSL")

        missing = [k for k, v in {
            "REDIS_HOST": host,
            "REDIS_PORT": port,
            "REDIS_DB": db,
            "REDIS_SSL": ssl_raw,
        }.items() if v is None]

        if missing:
            raise EnvironmentError(f"Missing required environment variables: {', '.join(missing)}")

        ssl = ssl_raw.lower() == "true"
        return redis.Redis(
            host=host,
            port=int(port),
            db=int(db),
            password=password,
            ssl=ssl,
            decode_responses=True,
        )

    def get_client(self) -> redis.Redis:
        return self._client
