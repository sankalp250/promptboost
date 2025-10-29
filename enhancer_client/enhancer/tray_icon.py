from pystray import Icon as pystrayIcon, MenuItem as item
from PIL import Image
from .hotkey_manager import stop_listener
import sys
from pathlib import Path # Import the Path object

# --- ROBUST ICON PATH LOGIC ---
# This creates a reliable, absolute path to the icon file.
# It finds the directory of this script and navigates from there.
CLIENT_ROOT = Path(__file__).resolve().parent.parent
ICON_PATH = CLIENT_ROOT / "assets" / "icon.png" 

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
        print(f"Error: Icon file not found at the expected path: {ICON_PATH}")
        print("Please ensure you have an 'icon.png' in the 'enhancer_client/assets/' directory.")
        # We exit here because without an icon, pystray will crash.
        sys.exit(1)

    # Define the menu for the tray icon
    menu = (item('Quit', on_quit_clicked),)

    # Create the icon
    icon = pystrayIcon("PromptBoost", image, "PromptBoost Enhancer", menu)

    print("System tray icon is running.")
    icon.run()