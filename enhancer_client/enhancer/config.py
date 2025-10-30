from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

# Absolute path to the .env file in the enhancer_client directory
CLIENT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE_PATH = CLIENT_ROOT / ".env"

class Settings(BaseSettings):
    API_BASE_URL: str = "http://localhost:8000/api/v1"

    model_config = SettingsConfigDict(env_file=ENV_FILE_PATH)

settings = Settings()