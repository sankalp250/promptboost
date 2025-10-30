import pyperclip
import time
import logging
import uuid # Import uuid
from .api_client import enhance_prompt_from_api
from .notifier import show_notification
from .config import settings # Import our settings which now holds the user_id

TRIGGER_SUFFIX = "!!e"
recent_text = ""
monitoring_active = True

def process_clipboard():
    """Performs the check and enhancement of the clipboard content."""
    global recent_text
    
    try:
        current_text = pyperclip.paste()
    except pyperclip.PyperclipException:
        return

    if current_text and current_text != recent_text and current_text.endswith(TRIGGER_SUFFIX):
        print(f"✅ Trigger phrase detected!")
        recent_text = current_text
        prompt_to_enhance = current_text.removesuffix(TRIGGER_SUFFIX).strip()
        
        if not prompt_to_enhance:
            print("No actual prompt text found before the trigger. Aborting.")
            return
            
        print(f"Sending to server: '{prompt_to_enhance[:50]}...'")

        # --- NEW LOGIC: PASS IDS TO API ---
        # Generate a new session_id for each unique interaction
        session_id = uuid.uuid4() 
        # Get the persistent user_id from our settings
        user_id = settings.USER_ID

        if not user_id:
            # This should ideally not happen if the config setup is correct
            print("CRITICAL: User ID not found. Aborting API call.")
            return

        enhanced_text = enhance_prompt_from_api(prompt_to_enhance, user_id=user_id, session_id=session_id)

        if enhanced_text:
            print("Successfully enhanced prompt. Updating clipboard.")
            pyperclip.copy(enhanced_text)
            recent_text = enhanced_text
            show_notification("✨ Prompt Enhanced!", "Ready to paste.")
        else:
            print("❌ Enhancement failed.")
            show_notification("🚫 Enhancement Failed", "Check server connection and logs.")

def start_monitoring():
    """Starts the clipboard monitoring loop."""
    print(f"✅ Clipboard monitor started. Copy text ending with '{TRIGGER_SUFFIX}' to enhance.")
    while monitoring_active:
        process_clipboard()
        time.sleep(0.5)

def stop_monitoring():
    """Signals the monitoring loop to stop."""
    global monitoring_active
    print("Stopping clipboard monitor...")
    monitoring_active = False