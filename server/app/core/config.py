from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# This creates an absolute path to the 'server' directory, where this file lives.
# It makes the .env file discovery independent of where you run the script from.
# __file__ -> app/core/config.py
# .parent -> app/core
# .parent -> app
# .parent -> server
SERVER_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_FILE_PATH = SERVER_ROOT / ".env"

class Settings(BaseSettings):
    """
    Manages application settings using Pydantic.
    It automatically reads environment variables from the .env file found at ENV_FILE_PATH.
    """
    DATABASE_URL: str
    GROQ_API_KEY: str
    GOOGLE_API_KEY: str
    PROJECT_NAME: str = "PromptBoost"
    PROJECT_DESCRIPTION: str = "Prompt Enhancement Service"

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        extra='ignore'  # Ignore extra fields from .env file (like POSTGRES_USER, etc.)
    )

settings = Settings()