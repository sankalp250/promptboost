import httpx
from .config import settings
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def enhance_prompt_from_api(prompt_text: str) -> str | None:
    """
    Sends a prompt to the backend API and returns the enhanced version.
    Returns None if the request fails.
    """
    enhance_url = f"{settings.API_BASE_URL}/enhance"
    try:
        logging.info(f"Sending prompt to API: '{prompt_text[:50]}...'")
        response = httpx.post(enhance_url, json={"original_prompt": prompt_text}, timeout=10.0)
        
        # Raise an exception for bad status codes (4xx or 5xx)
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