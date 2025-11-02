import pyperclip
import time
import logging
import uuid
from .api_client import enhance_prompt_from_api, send_feedback_to_api
from .notifier import show_notification
from .config import settings
from .state import (
    set_last_session_id,
    set_last_prompts,
    get_last_original_prompt,
    is_reroll_attempt,
    get_last_session_id
)

TRIGGER_SUFFIX_ENHANCE = "!!e"
TRIGGER_SUFFIX_REROLL = "!!d"  # "dislike" or "different" - triggers reroll
recent_text = ""
monitoring_active = True

def process_clipboard():
    """Performs the check and enhancement of the clipboard content."""
    global recent_text
    
    try:
        current_text = pyperclip.paste()
    except pyperclip.PyperclipException:
        return

    # Check for enhancement trigger (!!e)
    if current_text and current_text != recent_text and current_text.endswith(TRIGGER_SUFFIX_ENHANCE):
        print(f"✅ Enhancement trigger detected (!!e)!")
        recent_text = current_text
        prompt_to_enhance = current_text.removesuffix(TRIGGER_SUFFIX_ENHANCE).strip()
        
        if not prompt_to_enhance:
            print("No actual prompt text found. Aborting.")
            return
        
        print(f"✓ New prompt detected - sending for enhancement")
        print(f"Sending to server: '{prompt_to_enhance[:50]}...'")

        session_id = uuid.uuid4() 
        user_id = settings.USER_ID

        if not user_id:
            print("CRITICAL: User ID not found.")
            return

        enhanced_text = enhance_prompt_from_api(
            prompt_text=prompt_to_enhance,
            user_id=user_id,
            session_id=session_id,
            is_reroll=False,
            original_prompt=prompt_to_enhance
        )

        if enhanced_text:
            # Store session info for future rerolls
            print(f"💾 CLIENT: Storing session_id {session_id} for future rerolls")
            set_last_session_id(session_id)
            set_last_prompts(prompt_to_enhance, enhanced_text)
            
            # Debug: verify storage
            stored_id = get_last_session_id()
            if stored_id != session_id:
                print(f"⚠️ CLIENT WARNING: Session ID mismatch! Stored: {stored_id}, Expected: {session_id}")
            else:
                print(f"✅ CLIENT: Session ID stored correctly: {stored_id}")

            print("Successfully enhanced prompt. Updating clipboard.")
            pyperclip.copy(enhanced_text)
            recent_text = enhanced_text
            show_notification("✨ Prompt Enhanced!", "Ready to paste.")
        else:
            print("❌ Enhancement failed.")
            show_notification("🚫 Enhancement Failed", "Check server connection and logs.")
    
    # Check for reroll trigger (!!d - "dislike" or "different")
    elif current_text and current_text != recent_text and current_text.endswith(TRIGGER_SUFFIX_REROLL):
        print(f"\n{'='*60}")
        print(f"🔄 REROLL TRIGGER DETECTED (!!d)!")
        print(f"{'='*60}")
        recent_text = current_text
        prompt_to_enhance = current_text.removesuffix(TRIGGER_SUFFIX_REROLL).strip()
        
        if not prompt_to_enhance:
            print("No actual prompt text found. Aborting.")
            return
        
        # Get the original prompt and session_id from previous enhancement
        previous_session_id = get_last_session_id()
        original_prompt_for_api = get_last_original_prompt()
        
        print(f"Previous session_id: {previous_session_id}")
        print(f"Previous original prompt: {original_prompt_for_api[:60] if original_prompt_for_api else 'None'}...")
        print(f"Current enhanced text (being rerolled): {prompt_to_enhance[:60]}...")
        print(f"{'='*60}\n")
        
        # FIRST: Mark previous enhancement as rejected BEFORE getting new one
        if previous_session_id:
            print(f"📤 Step 1: Sending rejection feedback for session {previous_session_id}...")
            feedback_success = send_feedback_to_api(previous_session_id, "rejected")
            if feedback_success:
                print(f"✅ Step 1: Rejection feedback successfully saved!")
            else:
                print(f"⚠️ Step 1: Rejection feedback may not have been saved (check server logs)")
        else:
            print(f"⚠️ WARNING: No previous session_id found. Cannot mark as rejected.")
            print(f"   This might be a first enhancement or state was lost.")
            print(f"   Use manual_feedback.py script to manually mark rejections.")
        
        # SECOND: Get a new different enhancement
        if original_prompt_for_api:
            print(f"📤 Step 2: Requesting different enhancement for original prompt...")
            
            session_id = uuid.uuid4() 
            user_id = settings.USER_ID

            if not user_id:
                print("CRITICAL: User ID not found.")
                return

            enhanced_text = enhance_prompt_from_api(
                prompt_text=prompt_to_enhance,  # Send the enhanced text, but server uses original
                user_id=user_id,
                session_id=session_id,
                is_reroll=True,
                original_prompt=original_prompt_for_api
            )

            if enhanced_text:
                # Store new session info
                print(f"💾 CLIENT: Storing NEW session_id {session_id}")
                set_last_session_id(session_id)
                set_last_prompts(original_prompt_for_api, enhanced_text)

                print("✅ Successfully got different enhancement. Updating clipboard.")
                pyperclip.copy(enhanced_text)
                recent_text = enhanced_text
                show_notification("🔄 Different Enhancement!", "Previous marked as rejected.")
            else:
                print("❌ Reroll enhancement failed.")
                show_notification("🚫 Reroll Failed", "Check server connection and logs.")
        else:
            print(f"❌ CRITICAL: No original prompt found. Cannot perform reroll.")
            print(f"   Please use !!e first to get an initial enhancement.")

def start_monitoring():
    """Starts the clipboard monitoring loop."""
    print(f"✅ Clipboard monitor started.")
    print(f"   Use '{TRIGGER_SUFFIX_ENHANCE}' to enhance a prompt")
    print(f"   Use '{TRIGGER_SUFFIX_REROLL}' on an enhanced result to reject and get a different one")
    while monitoring_active:
        process_clipboard()
        time.sleep(0.5)

def stop_monitoring():
    """Signals the monitoring loop to stop."""
    global monitoring_active
    print("Stopping clipboard monitor...")
    monitoring_active = False