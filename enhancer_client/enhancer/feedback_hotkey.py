from pynput import keyboard
from .state import get_last_session_id, clear_last_session_id
from .api_client import send_feedback_to_api
from .notifier import show_notification
import threading

# Use a threading lock to prevent race conditions
feedback_lock = threading.Lock()
feedback_listener = None

REJECT_HOTKEY = {keyboard.Key.ctrl_l, keyboard.Key.shift_l, keyboard.KeyCode.from_char('x')}
current_feedback_keys = set()

def on_rejection_hotkey_activated():
    if not feedback_lock.acquire(blocking=False):
        return
    try:
        print("!!!! CLIENT HOTKEY: Rejection hotkey activated! !!!!")
        last_session_id = get_last_session_id()
        if last_session_id is None:
            print("!!!! CLIENT HOTKEY: No session ID found. Bailing. !!!!")
            return
        
        # --- DEBUG ---
        print(f"!!!! CLIENT HOTKEY: Found session ID {last_session_id}. Handing off to API client. !!!!")

        feedback_thread = threading.Thread(target=send_feedback_to_api, args=(last_session_id, "rejected"), daemon=True)
        feedback_thread.start()
        show_notification("Feedback Sent", "Thanks for helping us improve!")
        clear_last_session_id()
    finally:
        threading.Timer(1.0, feedback_lock.release).start()


def on_press(key):
    # Normalize modifiers to handle both left and right keys
    normalized_key = key
    if key in {keyboard.Key.ctrl_r, keyboard.Key.shift_r}:
        normalized_key = {
            keyboard.Key.ctrl_r: keyboard.Key.ctrl_l,
            keyboard.Key.shift_r: keyboard.Key.shift_l
        }.get(key, key)

    if normalized_key in REJECT_HOTKEY:
        current_feedback_keys.add(normalized_key)
        if all(k in current_feedback_keys for k in REJECT_HOTKEY):
            on_rejection_hotkey_activated()

def on_release(key):
    normalized_key = key
    if key in {keyboard.Key.ctrl_r, keyboard.Key.shift_r}:
        normalized_key = {
            keyboard.Key.ctrl_r: keyboard.Key.ctrl_l,
            keyboard.Key.shift_r: keyboard.Key.shift_l
        }.get(key, key)
    
    try:
        current_feedback_keys.remove(normalized_key)
    except KeyError:
        pass

def start_feedback_listener():
    """Starts the keyboard listener for the feedback hotkey."""
    global feedback_listener
    feedback_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    feedback_listener.start()
    print(f"✅ Feedback hotkey listener started. Press Left Ctrl+Left Shift+X to reject a suggestion.")

def stop_feedback_listener():
    """Stops the keyboard listener."""
    if feedback_listener:
        feedback_listener.stop()