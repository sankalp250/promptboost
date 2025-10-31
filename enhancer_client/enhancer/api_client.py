import httpx
from .config import settings
import logging
import uuid

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def enhance_prompt_from_api(prompt_text: str, user_id: uuid.UUID, session_id: uuid.UUID) -> str | None:
    """
    Sends a prompt to the backend API and returns the enhanced version.
    Includes user and session identifiers for A/B testing.
    """
    enhance_url = f"{settings.API_BASE_URL}/enhance"
    
    payload = {
        "original_prompt": prompt_text,
        "user_id": str(user_id),
        "session_id": str(session_id)
    }

    try:
        logging.info(f"Sending prompt to API for user {user_id}: '{prompt_text[:50]}...'")
        
        # --- THE FIX IS ON THE LINE BELOW ---
        # Increase the timeout to 30 seconds to allow the LLM more time to process complex prompts.
        response = httpx.post(enhance_url, json=payload, timeout=30.0)
        
        response.raise_for_status()
        
        data = response.json()
        enhanced_prompt = data.get("enhanced_prompt")
        logging.info(f"Received enhanced prompt. From cache: {data.get('from_cache')}")
        return enhanced_prompt

    except httpx.TimeoutException:
        # We can add a more specific error message for timeouts.
        logging.error(f"The request to {enhance_url!r} timed out after 30 seconds. The server might be slow.")
        return None
    except httpx.RequestError as exc:
        logging.error(f"An error occurred while requesting {exc.request.url!r}: {exc}")
        return None
    except httpx.HTTPStatusError as exc:
        logging.error(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.")
        logging.error(f"Response body: {exc.response.text}")
        return None