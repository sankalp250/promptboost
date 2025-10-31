import sys
import threading
from .enhancer.clipboard_monitor import start_monitoring, stop_monitoring
from pystray import Icon as pystrayIcon, MenuItem as item
from PIL import Image
from pathlib import Path

# --- NEW: ROBUST RESOURCE PATH FUNCTION ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # If not running as a PyInstaller bundle, use the normal script path
        base_path = Path(__file__).resolve().parent.parent # Go up to the enhancer_client root
    
    return Path(base_path) / relative_path

# --- GLOBAL ICON INSTANCE (Unchanged) ---
icon_instance = None

# --- USE THE NEW FUNCTION TO DEFINE THE ICON PATH ---
ICON_PATH = resource_path("assets/icon.png")

# --- on_quit_clicked function (Unchanged) ---
def on_quit_clicked(icon, item):
    print("Quit clicked. Shutting down...")
    stop_monitoring()
    icon.stop()

# --- run_tray_icon function (Unchanged, but now uses correct ICON_PATH) ---
def run_tray_icon():
    global icon_instance
    try:
        image = Image.open(ICON_PATH)
        print(f"Successfully loaded icon from: {ICON_PATH}") # Add a debug print
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to load icon from {ICON_PATH}. Error: {e}")
        # Even if the icon fails, we can still try to run the tray icon
        # It will just show a default icon.
        image = None # This will cause pystray to use a default icon

    menu = (item('Quit', on_quit_clicked),)
    # Pystray can handle a None image, which is good for fallback.
    icon_instance = pystrayIcon("PromptBoost", image, "PromptBoost Enhancer", menu)
    print("✅ System tray icon is running.")
    icon_instance.run()

# --- stop_tray_icon and start_client_app functions (Unchanged) ---
def stop_tray_icon():
    if icon_instance:
        icon_instance.stop()

def start_client_app():
    print("Starting PromptBoost Client...")
    monitor_thread = threading.Thread(target=start_monitoring, daemon=True)
    monitor_thread.start()
    tray_thread = threading.Thread(target=run_tray_icon)
    tray_thread.start()
    return tray_thread