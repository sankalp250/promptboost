import httpx
from .config import settings
import logging
import uuid # Import the UUID library

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def enhance_prompt_from_api(prompt_text: str, user_id: uuid.UUID, session_id: uuid.UUID) -> str | None:
    """
    Sends a prompt to the backend API and returns the enhanced version.
    Now includes user and session identifiers for A/B testing.
    """
    enhance_url = f"{settings.API_BASE_URL}/enhance"
    
    # --- NEW PAYLOAD ---
    # We now send a more detailed JSON body to the server
    payload = {
        "original_prompt": prompt_text,
        "user_id": str(user_id),       # Convert UUIDs to strings for JSON
        "session_id": str(session_id)
    }

    try:
        logging.info(f"Sending prompt to API for user {user_id}: '{prompt_text[:50]}...'")
        response = httpx.post(enhance_url, json=payload, timeout=10.0)
        
        response.raise_for_status()
        
        data = response.json()
        enhanced_prompt = data.get("enhanced_prompt")
        logging.info(f"Received enhanced prompt. From cache: {data.get('from_cache')}")
        return enhanced_prompt

    except httpx.RequestError as exc:
        logging.error(f"An error occurred while requesting {exc.request.url!r}: {exc}")
        return None
    except httpx.HTTPStatusError as exc:
        logging.error(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.")
        logging.error(f"Response body: {exc.response.text}")
        return None