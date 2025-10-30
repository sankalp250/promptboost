from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
import uuid # Import uuid
import json # Import json for saving/loading the id

# --- NEW: Define where to save the user config ---
CLIENT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE_PATH = CLIENT_ROOT / ".env"
USER_CONFIG_PATH = CLIENT_ROOT / "user_config.json" # Our new config file

class Settings(BaseSettings):
    API_BASE_URL: str = "http://localhost:8000/api/v1"
    USER_ID: uuid.UUID | None = None # Add user_id to our settings

    model_config = SettingsConfigDict(env_file=ENV_FILE_PATH)

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