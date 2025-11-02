import uuid

_last_session_id: uuid.UUID | None = None
_last_original_prompt: str | None = None
_last_enhanced_prompt: str | None = None

def set_last_session_id(session_id: uuid.UUID):
    global _last_session_id
    print(f"!!!! CLIENT STATE: Storing last session ID -> {session_id} !!!!")
    _last_session_id = session_id

def get_last_session_id() -> uuid.UUID | None:
    return _last_session_id

def clear_last_session_id():
    global _last_session_id, _last_original_prompt, _last_enhanced_prompt
    if _last_session_id:
        print(f"!!!! CLIENT STATE: Clearing last session data !!!!")
        _last_session_id = None
        _last_original_prompt = None
        _last_enhanced_prompt = None

def set_last_prompts(original: str, enhanced: str):
    """Store the original and enhanced prompts for reroll detection."""
    global _last_original_prompt, _last_enhanced_prompt
    _last_original_prompt = original
    _last_enhanced_prompt = enhanced
    print(f"!!!! CLIENT STATE: Stored prompts for reroll detection !!!!")

def get_last_original_prompt() -> str | None:
    return _last_original_prompt

def is_reroll_attempt(text: str) -> bool:
    """Detect if the text being enhanced is actually a previously enhanced prompt."""
    global _last_enhanced_prompt, _last_original_prompt
    text_stripped = text.strip()
    
    # Primary check: Does text exactly match our last enhanced prompt?
    if _last_enhanced_prompt:
        if text_stripped == _last_enhanced_prompt.strip():
            print(f"🔄 REROLL DETECTED: Text matches last enhanced prompt!")
            return True
        # Also check if text is similar (handles whitespace differences)
        if len(text_stripped) > 20 and _last_enhanced_prompt.strip() in text_stripped:
            print(f"🔄 REROLL DETECTED: Text contains last enhanced prompt!")
            return True
    
    # Secondary check: Does text look like an enhanced prompt but is NOT the original?
    # (This catches cases where state wasn't tracked properly)
    if _last_original_prompt:
        if text_stripped.startswith("Act as") and len(text_stripped) > 50:
            if text_stripped != _last_original_prompt.strip():
                print(f"🔄 REROLL DETECTED: Text looks like enhanced prompt (starts with 'Act as')!")
                return True
    
    return False