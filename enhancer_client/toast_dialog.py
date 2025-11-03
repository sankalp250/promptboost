"""
Windows Toast Notifications with Action Buttons
Native, non-intrusive dialogs for Accept/Reject feedback
"""
import uuid
import pyperclip
from winotify import Notification, audio
from enhancer_client.enhancer.api_client import enhance_prompt_from_api, send_feedback_to_api
from enhancer_client.enhancer.config import settings
from enhancer_client.enhancer.state import set_last_session_id, set_last_prompts
from enhancer_client.enhancer.notifier import show_notification

# Store current enhancement data for callback
_current_enhancement = {
    'enhanced_text': None,
    'session_id': None,
    'original_prompt': None
}

def on_accept_click():
    """Callback when user clicks Accept button"""
    session_id = _current_enhancement.get('session_id')
    if session_id:
        print("✅ User ACCEPTED via toast notification")
        send_feedback_to_api(session_id, "accepted")
    else:
        print("⚠️ No session_id found for accept action")

def on_reject_click():
    """Callback when user clicks Reject button - get different enhancement"""
    session_id = _current_enhancement.get('session_id')
    original_prompt = _current_enhancement.get('original_prompt')
    
    if not session_id or not original_prompt:
        print("⚠️ No session data found for reject action")
        return
    
    print("🔄 User REJECTED via toast - requesting different enhancement")
    send_feedback_to_api(session_id, "rejected")
    
    # Get new enhancement
    user_id = settings.USER_ID
    new_session_id = uuid.uuid4()
    
    print("📤 Requesting different enhancement...")
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
        
        print("✅ Got different enhancement! Showing new toast...")
        show_notification("🔄 Different Enhancement!", "New version copied to clipboard")
        
        # Show new toast for the new enhancement
        show_toast_notification(new_enhanced_text, new_session_id, original_prompt)
    else:
        print("❌ Failed to get different enhancement")
        show_notification("🚫 Error", "Failed to get different enhancement")

def show_toast_notification(enhanced_text: str, session_id: uuid.UUID, original_prompt: str):
    """
    Show a Windows toast notification with Accept/Reject buttons.
    This is the main function to call when enhancement is ready.
    """
    # Store data for callbacks
    _current_enhancement['enhanced_text'] = enhanced_text
    _current_enhancement['session_id'] = session_id
    _current_enhancement['original_prompt'] = original_prompt
    
    try:
        # Create notification
        toast = Notification(
            app_id="PromptBoost",
            title="✨ Prompt Enhanced!",
            msg="Your enhanced prompt is now in the clipboard. Accept or get a different version?",
            duration="long",  # Stays visible longer
            icon=None  # You can add an icon path here if you have one
        )
        
        # Add action buttons
        toast.add_actions(
            label="✅ Accept",
            launch="accept"
        )
        toast.add_actions(
            label="🔄 Get Different",
            launch="reject"
        )
        
        # Set up click handlers
        toast.set_audio(audio.Default, loop=False)
        
        # Define what happens when buttons are clicked
        # Note: winotify has limitations - we'll use a simpler approach
        # The callbacks need to be handled differently
        
        # Show the notification
        toast.show()
        
        print("🔔 Toast notification displayed!")
        print(f"   Session: {session_id}")
        print(f"   Original: {original_prompt[:50]}...")
        
        # Note: For proper button handling, we need to set up action handlers
        # This is a limitation of winotify - buttons will open URLs or apps
        # We'll use a fallback approach with manual handling
        
    except Exception as e:
        print(f"❌ Failed to show toast notification: {e}")
        print("   Falling back to regular notification...")
        show_notification("✨ Prompt Enhanced!", "Enhancement copied to clipboard")

def show_simple_toast(title: str, message: str):
    """
    Show a simple toast notification without buttons (for confirmations).
    """
    try:
        toast = Notification(
            app_id="PromptBoost",
            title=title,
            msg=message,
            duration="short"
        )
        toast.show()
    except Exception as e:
        print(f"❌ Failed to show simple toast: {e}")
        # Fallback to plyer notification
        show_notification(title, message)