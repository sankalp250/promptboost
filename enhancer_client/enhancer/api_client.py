import httpx
from .config import settings
import logging
import uuid

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def enhance_prompt_from_api(prompt_text: str, user_id: uuid.UUID, session_id: uuid.UUID) -> str | None:
    """Sends a prompt to the backend API and returns the enhanced version."""
    enhance_url = f"{settings.API_BASE_URL}/enhance"
    
    payload = {
        "original_prompt": prompt_text,
        "user_id": str(user_id),
        "session_id": str(session_id)
    }

    try:
        logging.info(f"Sending prompt to API for user {user_id}: '{prompt_text[:50]}...'")
        response = httpx.post(enhance_url, json=payload, timeout=30.0)
        response.raise_for_status()
        data = response.json()
        enhanced_prompt = data.get("enhanced_prompt")
        logging.info(f"Received enhanced prompt. From cache: {data.get('from_cache')}")
        return enhanced_prompt
    except httpx.TimeoutException:
        logging.error(f"The request to {enhance_url!r} timed out. The server might be slow.")
        return None
    except httpx.RequestError as exc:
        logging.error(f"An error occurred while requesting {exc.request.url!r}: {exc}")
        return None
    except httpx.HTTPStatusError as exc:
        logging.error(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.")
        logging.error(f"Response body: {exc.response.text}")
        return None

# --- NEW FUNCTION FOR SENDING FEEDBACK ---
def send_feedback_to_api(session_id: uuid.UUID, action: str):
    """
    Sends feedback (e.g., 'rejected') for a given session_id to the server.
    This is a "fire-and-forget" call; we don't need a return value.
    """
    feedback_url = f"{settings.API_BASE_URL}/feedback"
    payload = {
        "session_id": str(session_id),
        "user_action": action
    }

    try:
        logging.info(f"Sending feedback for session {session_id}: '{action}'")
        with httpx.Client() as client:
            client.post(feedback_url, json=payload, timeout=5.0)
        logging.info("Feedback sent successfully.")
    except Exception as e:
        # We log the error but don't bother the user. This is a background task.
        logging.error(f"Failed to send feedback for session {session_id}: {e}")