from pynput import keyboard
import threading

# Use a threading lock for consistency, though it's no longer used
feedback_lock = threading.Lock()
feedback_listener = None

# --- HOTKEYS REMOVED ---
# All hotkey definitions have been removed.
REJECT_HOTKEY = set()
REROLL_HOTKEY = set()
current_feedback_keys = set()
current_reroll_keys = set()

def on_reroll_hotkey_activated():
    """Reroll hotkey is disabled. This function will not be called."""
    print("Hotkey (Ctrl+Shift+R) is disabled. Use the 'Reject' button in the dialog.")

def on_rejection_hotkey_activated():
    """Rejection hotkey is disabled. This function will not be called."""
    print("Hotkey (Ctrl+Shift+X) is disabled. Use the 'Reject' button in the dialog.")


def on_press(key):
    """
    Listener function is now empty and does nothing.
    """
    pass

def on_release(key):
    """
    Listener function is now empty and does nothing.
    """
    pass

def start_feedback_listener():
    """
    Starts the keyboard listener.
    ---
    UPDATE: This function has been modified to NOT start the listener,
    effectively disabling all hotkeys.
    """
    global feedback_listener
    if feedback_listener:
        return
        
    print("✅ Feedback hotkey listener is DISABLED.")
    print("   Please use the dialog box to Accept or Reject suggestions.")
    
    # The following lines are commented out to disable the listener
    # feedback_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    # feedback_listener.start()
    # print(f"✅ Feedback hotkey listener started.")
    # print(f"   Press Ctrl+Shift+X to reject a suggestion")
    # print(f"   Press Ctrl+Shift+R to reroll (get different enhancement)")

def stop_feedback_listener():
    """Stops the keyboard listener."""
    if feedback_listener:
        feedback_listener.stop()