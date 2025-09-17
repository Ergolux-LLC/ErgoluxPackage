from typing import Dict
from app.common.config import Config

class NotificationAPIDriver:
    def __init__(self, config: Config):
        self._config = config
        self._connection_params = self._build_connection_params()

    def _build_connection_params(self) -> Dict[str, str]:
        base_url = self._config.get("NOTIFY_API_BASE_URL")
        api_key = self._config.get("NOTIFY_API_KEY")
        sender_id = self._config.get("NOTIFY_SENDER_ID")

        missing = [k for k, v in {
            "NOTIFY_API_BASE_URL": base_url,
            "NOTIFY_API_KEY": api_key,
            "NOTIFY_SENDER_ID": sender_id,
        }.items() if v is None]

        if missing:
            raise EnvironmentError(f"Missing required environment variables: {', '.join(missing)}")

        return {
            "base_url": base_url,
            "api_key": api_key,
            "sender_id": sender_id,
        }

    def get_connection_params(self) -> Dict[str, str]:
        return self._connection_params
