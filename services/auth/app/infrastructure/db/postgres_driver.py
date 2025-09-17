from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from app.common.config import Config

class PostgresDriver:
    def __init__(self, config: Config):
        self._config = config
        self._engine = self._create_engine()
        self._SessionLocal = sessionmaker(bind=self._engine, autocommit=False, autoflush=False)

    def _create_engine(self) -> Engine:
        user = self._config.get("POSTGRES_USER")
        password = self._config.get("POSTGRES_PASSWORD")
        host = self._config.get("POSTGRES_HOST")
        port = self._config.get("POSTGRES_PORT")
        db = self._config.get("POSTGRES_DB")
        ssl_raw = self._config.get("POSTGRES_SSL")

        missing = [k for k, v in {
            "POSTGRES_USER": user,
            "POSTGRES_PASSWORD": password,
            "POSTGRES_HOST": host,
            "POSTGRES_PORT": port,
            "POSTGRES_DB": db,
            "POSTGRES_SSL": ssl_raw,
        }.items() if v is None]

        if missing:
            raise EnvironmentError(f"Missing required environment variables: {', '.join(missing)}")

        sslmode = "require" if ssl_raw.lower() == "true" else "disable"
        url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}?sslmode={sslmode}"
        return create_engine(url, echo=False, pool_pre_ping=True)

    def get_session(self) -> Session:
        return self._SessionLocal()
