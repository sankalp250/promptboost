import uuid

# A global variable to hold the session ID of the last enhancement.
# We initialize it to None.
_last_session_id: uuid.UUID | None = None

def set_last_session_id(session_id: uuid.UUID):
    """
    Stores the ID of the most recent enhancement session.
    This is called by the clipboard monitor after a successful enhancement.
    """
    global _last_session_id
    print(f"State: Storing last session ID -> {session_id}")
    _last_session_id = session_id

def get_last_session_id() -> uuid.UUID | None:
    """
    Retrieves the ID of the most recent enhancement session.
    This is called by the feedback hotkey listener.
    """
    return _last_session_id

def clear_last_session_id():
    """
    Clears the session ID after feedback has been sent to prevent duplicates.
    """
    global _last_session_id
    if _last_session_id:
        print(f"State: Clearing last session ID -> {_last_session_id}")
        _last_session_id = None