import os
from dotenv import dotenv_values, load_dotenv

class Config:
    _instance = None

    def __new__(cls, env_path: str):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, env_path: str):
        if self._initialized:
            return

        if not os.path.isfile(env_path):
            raise FileNotFoundError(f".env file not found at: {env_path}")
        
        self.env_path = env_path
        load_dotenv(dotenv_path=self.env_path)
        self._env_vars = dotenv_values(dotenv_path=self.env_path)
        self._initialized = True

    def get(self, key: str) -> str:
        value = self._env_vars.get(key)
        if value is None:
            raise KeyError(f"Environment variable '{key}' not found in {self.env_path}")
        return value
