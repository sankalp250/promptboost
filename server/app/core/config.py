from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Manages application settings using Pydantic.
    It automatically reads environment variables from the specified .env file.
    """
    DATABASE_URL: str

    # Pydantic V2+ configuration.
    # This explicitly tells Pydantic where to look for the .env file.
    # It assumes that scripts are run from the project's root directory.
    model_config = SettingsConfigDict(env_file="server/.env")

settings = Settings()