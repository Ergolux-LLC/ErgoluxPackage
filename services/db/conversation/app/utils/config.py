import os
from dotenv import load_dotenv

class Config:
    def __init__(self, env_file: str = None):
        if env_file:
            load_dotenv(dotenv_path=env_file)
        else:
            load_dotenv()

    def get(self, key: str) -> str:
        value = os.getenv(key)
        if value is None:
            raise EnvironmentError(f"Required environment variable '{key}' not found.")
        return value