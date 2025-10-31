from pynput import keyboard
from .state import get_last_session_id, clear_last_session_id
from .api_client import send_feedback_to_api
from .notifier import show_notification

# A separate listener for our feedback hotkey
feedback_listener = None

# Define the hotkey combination for rejecting a suggestion
REJECT_HOTKEY = {keyboard.Key.ctrl_l, keyboard.Key.shift, keyboard.KeyCode.from_char('x')}
current_feedback_keys = set()

def on_rejection_hotkey_activated():
    """
    This function runs when the user presses the rejection hotkey.
    It sends a 'rejected' signal for the last known enhancement.
    """
    print("🔥 Rejection hotkey activated!")

    last_session_id = get_last_session_id()

    if last_session_id is None:
        print("No recent enhancement found to reject. Ignoring.")
        return

    # Send the feedback to the server
    send_feedback_to_api(session_id=last_session_id, action="rejected")

    # Show a notification to the user
    show_notification("Feedback Sent", "Thanks for helping us improve!")

    # IMPORTANT: Clear the session ID immediately after sending feedback
    # to prevent the user from rejecting the same enhancement twice.
    clear_last_session_id()


def on_press(key):
    if key in REJECT_HOTKEY:
        current_feedback_keys.add(key)
        if all(k in current_feedback_keys for k in REJECT_HOTKEY):
            on_rejection_hotkey_activated()

def on_release(key):
    try:
        current_feedback_keys.remove(key)
    except KeyError:
        pass

def start_feedback_listener():
    """Starts the keyboard listener for the feedback hotkey."""
    global feedback_listener
    feedback_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    feedback_listener.start()
    print(f"✅ Feedback hotkey listener started. Press Ctrl+Shift+X to reject a suggestion.")

def stop_feedback_listener():
    """Stops the keyboard listener."""
    if feedback_listener:
        feedback_listener.stop()