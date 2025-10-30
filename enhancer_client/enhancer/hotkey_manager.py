from pynput import keyboard
from .clipboard_manager import get_clipboard_text, set_clipboard_text
from .api_client import enhance_prompt_from_api
from .notifier import show_notification

# Define the hotkey combination
HOTKEY = {keyboard.Key.ctrl_l, keyboard.Key.shift, keyboard.KeyCode.from_char('e')}

# A set of currently pressed keys
current_keys = set()
listener = None

def on_hotkey_activated():
    """The main function that runs when the hotkey is triggered."""
    print("✨ Hotkey Activated!")
    
    original_text = get_clipboard_text()
    if not original_text or not original_text.strip():
        print("Clipboard is empty. Aborting.")
        return

    enhanced_text = enhance_prompt_from_api(original_text)
    
    if enhanced_text:
        set_clipboard_text(enhanced_text)
        show_notification("✨ Prompt Enhanced!", "Paste your new prompt with Ctrl+V.")
    else:
        show_notification("🚫 Enhancement Failed", "Check server connection and logs.")

def on_press(key):
    if key in HOTKEY:
        current_keys.add(key)
        if all(k in current_keys for k in HOTKEY):
            on_hotkey_activated()

def on_release(key):
    try:
        current_keys.remove(key)
    except KeyError:
        pass # If a key is released that wasn't in the set, ignore it

def start_listener():
    """Starts the keyboard listener."""
    global listener
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    print("Hotkey listener started. Press Ctrl+Shift+E to enhance clipboard text.")

def stop_listener():
    """Stops the keyboard listener."""
    if listener:
        listener.stop()
        print("Hotkey listener stopped.")

### **File 7: `enhancer_client/enhancer/tray_icon.py`**
from pystray import Icon as pystrayIcon, MenuItem as item
from PIL import Image
from .hotkey_manager import stop_listener
import sys

# This assumes you have an icon.png in the 'assets' folder
# The path is relative to where main.py will be.
ICON_PATH = "assets/icon.png" 

def on_quit_clicked(icon, item):
    """Function to handle the quit action."""
    print("Quit clicked. Shutting down...")
    stop_listener()
    icon.stop()

def create_and_run_tray_icon():
    """Creates and runs the system tray icon."""
    try:
        image = Image.open(ICON_PATH)
    except FileNotFoundError:
        print(f"Error: Icon file not found at {ICON_PATH}")
        print("Please ensure you have an 'icon.png' in the 'enhancer_client/assets/' directory.")
        # We exit here because without an icon, pystray will crash.
        sys.exit(1)

    # Define the menu for the tray icon
    menu = (item('Quit', on_quit_clicked),)

    # Create the icon
    icon = pystrayIcon("PromptBoost", image, "PromptBoost Enhancer", menu)

    print("System tray icon is running.")
    icon.run()