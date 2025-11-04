"""
PromptBoost Client - Windows Toast Notification Version
Native, non-intrusive notifications with action buttons!
"""
import pyperclip
import time
import logging
import uuid
import threading
from PIL import Image, ImageDraw
import pystray
import sys
import platform

# Import from other modules
from enhancer_client.enhancer.api_client import enhance_prompt_from_api, send_feedback_to_api
from enhancer_client.enhancer.notifier import show_notification
from enhancer_client.enhancer.config import settings
from enhancer_client.enhancer.state import (
    set_last_session_id,
    set_last_prompts,
)

# Import hotkey feedback system
from enhancer_client.hotkey_feedback import (
    show_enhancement_notification, 
    start_hotkey_listener, 
    stop_hotkey_listener
)

# Constants
TRIGGER_SUFFIX_ENHANCE = "!!e"
recent_text = ""
monitoring_active = True
tray_icon = None
TOAST_AVAILABLE = False  # Set to False by default as fallback notification is implemented

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_clipboard():
    """Process clipboard for enhancement triggers."""
    global recent_text
    
    try:
        current_text = pyperclip.paste()
    except Exception as e:
        return
        
    if not isinstance(current_text, str):
        return
        
    current_stripped = current_text.strip()
    recent_stripped = recent_text.strip()

    if current_stripped != recent_stripped and current_stripped.endswith(TRIGGER_SUFFIX_ENHANCE):
        recent_text = current_text
        prompt_to_enhance = current_stripped.removesuffix(TRIGGER_SUFFIX_ENHANCE).strip()
        
        if not prompt_to_enhance:
            return

        print(f"\n{'='*60}")
        print(f"✅ Enhancement trigger detected!")
        print(f"{'='*60}")
        
        session_id = uuid.uuid4()
        user_id = settings.USER_ID
        if not user_id:
            print("CRITICAL: User ID not found.")
            return

        print("📤 Sending to server for enhancement...")
        enhanced_text = enhance_prompt_from_api(
            prompt_text=prompt_to_enhance,
            user_id=user_id,
            session_id=session_id,
            is_reroll=False,
            original_prompt=prompt_to_enhance
        )

        if enhanced_text:
            set_last_session_id(session_id)
            set_last_prompts(prompt_to_enhance, enhanced_text)
            print("✅ Successfully enhanced prompt!")
            
            # Update clipboard FIRST (so it's ready to paste)
            pyperclip.copy(enhanced_text)
            recent_text = enhanced_text
            
            # Check if server bypassed (code detection)
            if enhanced_text.strip() == prompt_to_enhance.strip():
                print("--- Server bypassed enhancement (likely code). ---")
                show_notification("✨ Code Detected", "Prompt unchanged (code bypass)")
                return

            # Show toast notification with Accept/Reject buttons
            print("🔔 Showing toast notification...")
            if TOAST_AVAILABLE:
                show_toast_notification(enhanced_text, session_id, prompt_to_enhance)
            else:
                # Fallback to regular notification if toast not available
                show_notification("✨ Prompt Enhanced!", "Enhancement copied to clipboard")
                print("⚠️ Toast notifications not available - using fallback")
            
        else:
            print("❌ Enhancement failed.")
            show_notification("🚫 Enhancement Failed", "Check server connection")
            recent_text = ""


def clipboard_monitor_loop():
    """Background thread function that monitors clipboard."""
    global monitoring_active
    print("\n" + "="*60)
    print("📋 Clipboard monitoring started")
    print(f"   Trigger: Copy text ending with '{TRIGGER_SUFFIX_ENHANCE}'")
    print("="*60 + "\n")
    
    while monitoring_active:
        try:
            process_clipboard()
            time.sleep(0.5)
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"ERROR in monitor loop: {e}")
            time.sleep(2)
    
    print("\n📋 Clipboard monitoring stopped.")


def create_icon_image():
    """Create a simple icon for the system tray."""
    width = 64
    height = 64
    color1 = "#4CAF50"
    color2 = "#45a049"
    
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        (width // 4, height // 4, width * 3 // 4, height * 3 // 4),
        fill=color2
    )
    
    return image


def on_quit_tray(icon, item):
    """Handle quit from tray menu."""
    global monitoring_active, tray_icon
    print("\n" + "="*60)
    print("🛑 Shutting down PromptBoost...")
    print("="*60)
    monitoring_active = False
    if icon:
        icon.stop()
    sys.exit(0)


def setup_tray_icon():
    """Setup and return the system tray icon."""
    icon_image = create_icon_image()
    
    menu_items = [
        pystray.MenuItem("PromptBoost is running", lambda: None, enabled=False),
        pystray.MenuItem(f"Trigger: {TRIGGER_SUFFIX_ENHANCE}", lambda: None, enabled=False),
    ]
    
    # Add toast status to menu
    if TOAST_AVAILABLE:
        menu_items.append(pystray.MenuItem("✅ Toast notifications enabled", lambda: None, enabled=False))
    else:
        menu_items.append(pystray.MenuItem("⚠️ Toast notifications unavailable", lambda: None, enabled=False))
    
    menu_items.extend([
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quit", on_quit_tray)
    ])
    
    menu = pystray.Menu(*menu_items)
    icon = pystray.Icon("PromptBoost", icon_image, "PromptBoost", menu)
    return icon


def start_client_app():
    """
    Main entry point to start the PromptBoost client.
    """
    global tray_icon, monitoring_active
    
    if not settings.USER_ID:
        print("❌ CRITICAL: User ID not found. Cannot start application.")
        return None
    
    print("\n" + "="*60)
    print("   PromptBoost - AI Prompt Enhancement Tool")
    print("="*60)
    print(f"👤 User ID: {settings.USER_ID}")
    print(f"🌐 API URL: {settings.API_BASE_URL}")
    print(f"💻 OS: {platform.system()}")
    
    if TOAST_AVAILABLE:
        print("🔔 Toast Notifications: ENABLED ✅")
    else:
        print("🔔 Toast Notifications: UNAVAILABLE ⚠️")
        print("   (Fallback: System notifications)")
    
    print("="*60 + "\n")
    
    # Start clipboard monitoring in background thread
    monitor_thread = threading.Thread(target=clipboard_monitor_loop, daemon=True)
    monitor_thread.start()
    
    # Setup and run tray icon in main thread
    tray_icon = setup_tray_icon()
    
    print("✅ PromptBoost is now running!")
    print(f"📋 Copy text ending with '{TRIGGER_SUFFIX_ENHANCE}' to enhance")
    if TOAST_AVAILABLE:
        print("🔔 Toast notification will appear when ready")
    else:
        print("🔔 System notification will appear when ready")
    print("❌ Right-click tray icon → Quit to exit\n")
    
    # Run the tray icon (blocks until quit)
    tray_icon.run()
    
    return monitor_thread


def stop_tray_icon():
    """Stop the tray icon and cleanup."""
    global monitoring_active, tray_icon
    monitoring_active = False
    if tray_icon:
        tray_icon.stop()


# For standalone testing
if __name__ == "__main__":
    try:
        print("Starting PromptBoost in standalone mode...")
        start_client_app()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
        stop_tray_icon()