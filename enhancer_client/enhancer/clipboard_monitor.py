import pyperclip
import time
import logging
from .api_client import enhance_prompt_from_api
from .notifier import show_notification

# This is our magic string. The app will only trigger when it sees this at the end of copied text.
TRIGGER_SUFFIX = "!!e" 

# A variable to hold the last text we saw, to prevent re-processing the same text.
recent_text = ""

# A variable to stop the loop when the application quits.
monitoring_active = True

def process_clipboard():
    """Performs the check and enhancement of the clipboard content."""
    global recent_text
    
    try:
        current_text = pyperclip.paste()
    except pyperclip.PyperclipException:
        # If the clipboard is inaccessible (e.g., holding an image), just skip.
        return

    # Condition 1: Is there text?
    # Condition 2: Is it different from the last text we processed?
    # Condition 3: Does it end with our trigger phrase?
    if current_text and current_text != recent_text and current_text.endswith(TRIGGER_SUFFIX):
        
        print(f"✅ Trigger phrase detected!")
        
        # Keep a copy of the full triggered text so we don't re-process it
        recent_text = current_text
        
        # Remove the trigger phrase to get the actual prompt
        prompt_to_enhance = current_text.removesuffix(TRIGGER_SUFFIX).strip()
        
        if not prompt_to_enhance:
            print("No actual prompt text found before the trigger. Aborting.")
            return
            
        print(f"Sending to server: '{prompt_to_enhance[:50]}...'")
        
        # Send to the API
        enhanced_text = enhance_prompt_from_api(prompt_to_enhance)

        if enhanced_text:
            print("Successfully enhanced prompt. Updating clipboard.")
            pyperclip.copy(enhanced_text)
            # We update recent_text again with the new enhanced content, so if the user
            # copies the enhanced text, it won't trigger the process again.
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
        time.sleep(0.5) # Check the clipboard every 0.5 seconds

def stop_monitoring():
    """Signals the monitoring loop to stop."""
    global monitoring_active
    print("Stopping clipboard monitor...")
    monitoring_active = False