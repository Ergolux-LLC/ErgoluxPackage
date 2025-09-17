from abc import ABC, abstractmethod

class Notifier(ABC):
    def __init__(self, sender_id: str, api_key: str):
        self.sender_id = sender_id
        self.api_key = api_key

    @abstractmethod
    def connect(self):
        """Authenticate or prepare the connection to the external notification API."""
        pass

    @abstractmethod
    def notify(self, recipient_id: str, subject: str, message: str):
        """Send a notification via the external API."""
        pass

    @abstractmethod
    def disconnect(self):
        """Clean up any persistent connections or sessions."""
        pass
