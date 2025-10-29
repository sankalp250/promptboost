from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Manages application settings using Pydantic.
    It automatically reads environment variables from a .env file.
    """
    DATABASE_URL: str

    class Config:
        env_file = ".env"

settings = Settings()