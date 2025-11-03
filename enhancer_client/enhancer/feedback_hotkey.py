from pynput import keyboard
from .state import get_last_session_id, clear_last_session_id
from .api_client import send_feedback_to_api
from .notifier import show_notification
import threading

# Use a threading lock to prevent race conditions
feedback_lock = threading.Lock()
feedback_listener = None

REJECT_HOTKEY = {keyboard.Key.ctrl_l, keyboard.Key.shift_l, keyboard.KeyCode.from_char('x')}
REROLL_HOTKEY = {keyboard.Key.ctrl_l, keyboard.Key.shift_l, keyboard.KeyCode.from_char('r')}
current_feedback_keys = set()
current_reroll_keys = set()

def on_reroll_hotkey_activated():
    """Trigger reroll with keyboard shortcut Ctrl+Shift+R"""
    if not feedback_lock.acquire(blocking=False):
        return
    try:
        print("🔄 REROLL HOTKEY: Ctrl+Shift+R activated!")
        from .state import get_last_original_prompt, get_last_session_id
        from .api_client import enhance_prompt_from_api
        from .config import settings
        from .notifier import show_notification
        import pyperclip
        import uuid
        
        previous_session_id = get_last_session_id()
        original_prompt = get_last_original_prompt()
        
        if not original_prompt:
            print("❌ No previous enhancement found. Use !!e first.")
            show_notification("⚠️ Reroll Failed", "Use !!e first to enhance a prompt.")
            return
        
        if previous_session_id:
            print(f"📤 Marking previous as rejected (session: {previous_session_id})")
            send_feedback_to_api(previous_session_id, "rejected")
        
        # Get current clipboard as the enhanced text we're rejecting
        try:
            current_enhanced = pyperclip.paste()
        except:
            current_enhanced = ""
        
        session_id = uuid.uuid4()
        user_id = settings.USER_ID
        
        if not user_id:
            print("❌ User ID not found.")
            return
        
        print(f"📤 Requesting different enhancement...")
        enhanced_text = enhance_prompt_from_api(
            prompt_text=current_enhanced if current_enhanced else original_prompt,
            user_id=user_id,
            session_id=session_id,
            is_reroll=True,
            original_prompt=original_prompt
        )
        
        if enhanced_text:
            from .state import set_last_session_id, set_last_prompts
            set_last_session_id(session_id)
            set_last_prompts(original_prompt, enhanced_text)
            
            pyperclip.copy(enhanced_text)
            print("✅ Got different enhancement! Updated clipboard.")
            show_notification("🔄 Different Enhancement!", "Previous marked as rejected.")
        else:
            print("❌ Reroll failed.")
            show_notification("🚫 Reroll Failed", "Check server connection.")
    finally:
        threading.Timer(1.0, feedback_lock.release).start()

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
    
    # Handle reroll hotkey
    if normalized_key in REROLL_HOTKEY:
        current_reroll_keys.add(normalized_key)
        if all(k in current_reroll_keys for k in REROLL_HOTKEY):
            on_reroll_hotkey_activated()

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
    
    try:
        current_reroll_keys.remove(normalized_key)
    except KeyError:
        pass

def start_feedback_listener():
    """Starts the keyboard listener for the feedback hotkey."""
    global feedback_listener
    feedback_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    feedback_listener.start()
    print(f"✅ Feedback hotkey listener started.")
    print(f"   Press Ctrl+Shift+X to reject a suggestion")
    print(f"   Press Ctrl+Shift+R to reroll (get different enhancement)")

def stop_feedback_listener():
    """Stops the keyboard listener."""
    if feedback_listener:
        feedback_listener.stop()