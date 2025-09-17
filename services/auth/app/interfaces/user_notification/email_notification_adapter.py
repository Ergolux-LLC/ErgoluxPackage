import logging
from app.interfaces.user_notification.user_notification_repo import Notifier  # ABC
from app.infrastructure.apis.email_api import NotificationAPIDriver
from app.common.config import Config

import requests

logger = logging.getLogger(__name__)

class EmailNotifierAdapter(Notifier):
    def __init__(self, config: Config):
        logger.info("Initializing EmailNotifierAdapter")
        driver = NotificationAPIDriver(config)
        params = driver.get_connection_params()

        self.sender_id = params["sender_id"]
        self.api_key = params["api_key"]
        self.base_url = params["base_url"]
        self.session = None

    def connect(self):
        logger.debug("Establishing session for EmailNotifierAdapter")
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })

    def notify(self, recipient_id: str, subject: str, message: str):
        if not self.session:
            raise RuntimeError("Session not initialized. Call connect() first.")
        
        payload = {
            "sender": self.sender_id,
            "recipient": recipient_id,
            "subject": subject,
            "message": message
        }

        logger.info("FAKE: Simulating notification to %s", recipient_id)
        logger.debug("FAKE PAYLOAD: %s", payload)

        # Real notification logic — to be re-enabled when service is ready
        # try:
        #     response = self.session.post(f"https://{self.base_url}/send", json=payload)
        #     response.raise_for_status()
        #     logger.debug("Notification sent successfully: %s", response.status_code)
        # except requests.RequestException as e:
        #     logger.error("Failed to send notification: %s", e)
        #     raise

    def disconnect(self):
        if self.session:
            logger.debug("Closing session for EmailNotifierAdapter")
            self.session.close()
            self.session = None
