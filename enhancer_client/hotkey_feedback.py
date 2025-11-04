"""
Keyboard Shortcut Feedback System
Reliable Accept/Reject via hotkeys - No finicky toast buttons!
"""
import uuid
import pyperclip
from pynput import keyboard
import threading
from enhancer_client.enhancer.api_client import enhance_prompt_from_api, send_feedback_to_api
from enhancer_client.enhancer.config import settings
from enhancer_client.enhancer.state import set_last_session_id, set_last_prompts
from enhancer_client.enhancer.notifier import show_notification

# Store current enhancement data
_current_enhancement = {
    'enhanced_text': None,
    'session_id': None,
    'original_prompt': None,
    'awaiting_feedback': False
}

_hotkey_listener = None
_hotkey_lock = threading.Lock()

def on_accept_hotkey():
    """Handle Ctrl+Shift+A - Accept enhancement"""
    with _hotkey_lock:
        if not _current_enhancement.get('awaiting_feedback'):
            return
        
        session_id = _current_enhancement.get('session_id')
        if session_id:
            print("\n" + "="*60)
            print("✅ User ACCEPTED via Ctrl+Shift+A")
            print("="*60)
            send_feedback_to_api(session_id, "accepted")
            show_notification("✅ Accepted!", "Enhancement accepted")
            _current_enhancement['awaiting_feedback'] = False
        else:
            print("⚠️ No session_id found for accept action")

def on_reject_hotkey():
    """Handle Ctrl+Shift+R - Reject and get different"""
    with _hotkey_lock:
        if not _current_enhancement.get('awaiting_feedback'):
            return
        
        session_id = _current_enhancement.get('session_id')
        original_prompt = _current_enhancement.get('original_prompt')
        
        if not session_id or not original_prompt:
            print("⚠️ No session data found for reject action")
            return
        
        print("\n" + "="*60)
        print("🔄 User REJECTED via Ctrl+Shift+R - Getting different version")
        print("="*60)
        
        send_feedback_to_api(session_id, "rejected")
        
        # Get new enhancement
        user_id = settings.USER_ID
        new_session_id = uuid.uuid4()
        
        print("📤 Requesting different enhancement...")
        show_notification("🔄 Getting Different...", "Please wait...")
        
        new_enhanced_text = enhance_prompt_from_api(
            prompt_text=original_prompt,
            user_id=user_id,
            session_id=new_session_id,
            is_reroll=True,
            original_prompt=original_prompt
        )
        
        if new_enhanced_text:
            set_last_session_id(new_session_id)
            set_last_prompts(original_prompt, new_enhanced_text)
            pyperclip.copy(new_enhanced_text)
            
            print("✅ Got different enhancement!")
            show_notification("🔄 Different Version!", "New enhancement copied to clipboard\nCtrl+Shift+A=Accept | Ctrl+Shift+R=Reject")
            
            # Update current enhancement
            _current_enhancement['enhanced_text'] = new_enhanced_text
            _current_enhancement['session_id'] = new_session_id
            _current_enhancement['original_prompt'] = original_prompt
            _current_enhancement['awaiting_feedback'] = True
        else:
            print("❌ Failed to get different enhancement")
            show_notification("🚫 Error", "Failed to get different enhancement")
            _current_enhancement['awaiting_feedback'] = False

def show_enhancement_notification(enhanced_text: str, session_id: uuid.UUID, original_prompt: str):
    """
    Show notification and activate hotkey listening.
    This is the main function to call when enhancement is ready.
    """
    # Store data for hotkeys
    _current_enhancement['enhanced_text'] = enhanced_text
    _current_enhancement['session_id'] = session_id
    _current_enhancement['original_prompt'] = original_prompt
    _current_enhancement['awaiting_feedback'] = True
    
    print("\n" + "="*60)
    print("🎹 HOTKEYS ACTIVE:")
    print("   Ctrl+Shift+A = ✅ Accept")
    print("   Ctrl+Shift+R = 🔄 Reject & Get Different")
    print("="*60)
    
    # Show notification with instructions
    show_notification(
        "✨ Enhanced! (In Clipboard)",
        "Ctrl+Shift+A=Accept | Ctrl+Shift+R=Reject\nOr just paste to use!"
    )

def start_hotkey_listener():
    """Start listening for feedback hotkeys"""
    global _hotkey_listener
    
    if _hotkey_listener is not None:
        return  # Already running
    
    # Define hotkey combinations
    accept_combo = {keyboard.Key.ctrl_l, keyboard.Key.shift, keyboard.KeyCode.from_char('a')}
    reject_combo = {keyboard.Key.ctrl_l, keyboard.Key.shift, keyboard.KeyCode.from_char('r')}
    
    # Track currently pressed keys
    current_keys = set()
    
    def on_press(key):
        # Add key to current set
        try:
            current_keys.add(key)
        except:
            pass
        
        # Check if hotkey combo is pressed
        if accept_combo.issubset(current_keys):
            on_accept_hotkey()
        elif reject_combo.issubset(current_keys):
            on_reject_hotkey()
    
    def on_release(key):
        # Remove key from current set
        try:
            current_keys.discard(key)
        except:
            pass
    
    # Start listener
    _hotkey_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    _hotkey_listener.start()
    
    print("✅ Feedback hotkeys enabled:")
    print("   Ctrl+Shift+A = Accept")
    print("   Ctrl+Shift+R = Reject & Get Different")

def stop_hotkey_listener():
    """Stop the hotkey listener"""
    global _hotkey_listener
    if _hotkey_listener:
        _hotkey_listener.stop()
        _hotkey_listener = None
        print("❌ Feedback hotkeys disabled")