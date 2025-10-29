from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Manages application settings using Pydantic.
    It automatically reads environment variables from the specified .env file.
    """
    DATABASE_URL: str
    GROQ_API_KEY: str
    GOOGLE_API_KEY: str
    PROJECT_NAME: str = "PromptBoost"
    PROJECT_DESCRIPTION: str = "Prompt Enhancement Service"

    model_config = SettingsConfigDict(env_file="server/.env")

settings = Settings()