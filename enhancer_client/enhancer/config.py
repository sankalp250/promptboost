from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
import uuid # Import uuid
import json # Import json for saving/loading the id
import sys
import os

# --- NEW: Define where to save the user config ---
# Handle PyInstaller frozen exe paths
def get_app_dir():
    """Get the directory where the application/exe is located."""
    if getattr(sys, 'frozen', False):
        # Running as compiled exe - use the exe's directory
        return Path(sys.executable).parent
    else:
        # Running as script - use the enhancer_client directory
        return Path(__file__).resolve().parent.parent

APP_DIR = get_app_dir()
CLIENT_ROOT = Path(__file__).resolve().parent.parent if not getattr(sys, 'frozen', False) else APP_DIR

# For bundled resources (.env), check in the bundle first, then app directory
def get_env_file_path():
    """Get the path to .env file, checking bundle first."""
    if getattr(sys, 'frozen', False):
        # Check if .env exists next to the exe
        exe_env = APP_DIR / ".env"
        if exe_env.exists():
            return exe_env
        # Check in enhancer_client folder next to exe
        client_env = APP_DIR / "enhancer_client" / ".env"
        if client_env.exists():
            return client_env
        # Default to exe directory
        return exe_env
    else:
        return CLIENT_ROOT / ".env"

ENV_FILE_PATH = get_env_file_path()
USER_CONFIG_PATH = APP_DIR / "user_config.json"  # Always save user config next to exe/script

class Settings(BaseSettings):
    API_BASE_URL: str = "http://localhost:8000/api/v1"
    USER_ID: uuid.UUID | None = None # Add user_id to our settings

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding='utf-8-sig',  # utf-8-sig handles BOM automatically
        case_sensitive=False,
        extra='ignore'  # Ignore extra fields in .env file
    )

def load_or_create_user_id() -> uuid.UUID:
    """
    Loads the persistent user_id from user_config.json.
    If the file or ID doesn't exist, it creates a new one and saves it.
    """
    try:
        with open(USER_CONFIG_PATH, 'r') as f:
            data = json.load(f)
            user_id = uuid.UUID(data['user_id'])
            print(f"Loaded existing user ID: {user_id}")
            return user_id
    except (FileNotFoundError, KeyError, json.JSONDecodeError):
        print("No valid user ID found. Creating a new one.")
        new_user_id = uuid.uuid4()
        try:
            with open(USER_CONFIG_PATH, 'w') as f:
                json.dump({'user_id': str(new_user_id)}, f)
            print(f"Saved new user ID: {new_user_id}")
            return new_user_id
        except IOError as e:
            print(f"CRITICAL ERROR: Could not write user config file at {USER_CONFIG_PATH}: {e}")
            # If we can't save, we'll just use the ID for this session.
            return new_user_id


settings = Settings()
# --- NEW: Load the user ID when the application starts ---
settings.USER_ID = load_or_create_user_id()