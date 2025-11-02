import httpx
from .config import settings
import logging
import uuid

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def enhance_prompt_from_api(
    prompt_text: str,
    user_id: uuid.UUID,
    session_id: uuid.UUID,
    is_reroll: bool = False,
    original_prompt: str | None = None
) -> str | None:
    enhance_url = f"{settings.API_BASE_URL}/enhance"
    payload = {
        "original_prompt": prompt_text,
        "user_id": str(user_id),
        "session_id": str(session_id),
        "is_reroll": is_reroll,
        "true_original_prompt": original_prompt if is_reroll and original_prompt else None
    }
    try:
        logging.info(f"Sending prompt to API for user {user_id}: '{prompt_text[:50]}...' (reroll: {is_reroll})")
        response = httpx.post(enhance_url, json=payload, timeout=30.0)
        response.raise_for_status()
        data = response.json()
        return data.get("enhanced_prompt")
    except httpx.TimeoutException:
        logging.error("Request to enhancement API timed out.")
        return None
    except Exception as exc:
        logging.error(f"Error during enhancement request: {exc}")
        return None

def send_feedback_to_api(session_id: uuid.UUID, action: str) -> bool:
    """
    Sends feedback (e.g., 'rejected') for a given session_id to the server.
    Returns True if successful, False otherwise.
    """
    feedback_url = f"{settings.API_BASE_URL}/feedback"
    payload = {"session_id": str(session_id), "user_action": action}
    try:
        print(f"\n{'='*60}")
        print(f"🔄 CLIENT: Sending feedback for session {session_id}: '{action}'")
        print(f"{'='*60}")
        logging.info(f"Sending feedback for session {session_id}: '{action}'")
        
        response = httpx.post(feedback_url, json=payload, timeout=15.0)
        response.raise_for_status()
        result = response.json()
        
        status = result.get('status', 'unknown')
        message = result.get('message', 'No message')
        
        print(f"✅ CLIENT: Server response received!")
        print(f"   Status: {status}")
        print(f"   Message: {message}")
        print(f"{'='*60}\n")
        
        logging.info(f"Feedback sent and server confirmed receipt. Status: {status}")
        
        if status == 'success':
            return True
        elif status == 'warning':
            print(f"⚠️ CLIENT: Server warning - {message}")
            print(f"   The session_id might not have been found, but continuing...")
            return False  # Not a success, but not a fatal error
        else:
            print(f"⚠️ CLIENT: Unexpected status - {status}")
            return False
            
    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP {e.response.status_code}"
        try:
            error_body = e.response.json()
            error_msg += f": {error_body}"
            print(f"❌ CLIENT: HTTP Error - {error_msg}")
        except:
            error_text = e.response.text[:200]
            error_msg += f": {error_text}"
            print(f"❌ CLIENT: HTTP Error - {error_msg}")
        logging.error(f"FATAL: Failed to send feedback for session {session_id}: {error_msg}")
        return False
    except Exception as e:
        print(f"❌ CLIENT: Failed to send feedback - {str(e)}")
        logging.error(f"FATAL: Failed to send feedback for session {session_id}: {e}")
        return False