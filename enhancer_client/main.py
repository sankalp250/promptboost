import threading
from .enhancer.clipboard_monitor import start_monitoring, stop_monitoring
from pystray import Icon as pystrayIcon, MenuItem as item
from PIL import Image
import sys
from pathlib import Path

# --- TRAY ICON LOGIC ---

CLIENT_ROOT = Path(__file__).resolve().parent
ICON_PATH = CLIENT_ROOT / "assets" / "icon.png"

def on_quit_clicked(icon, item):
    """Function to handle the quit action."""
    print("Quit clicked. Shutting down...")
    stop_monitoring()
    icon.stop()

def run_tray_icon():
    """Creates and runs the system tray icon."""
    try:
        image = Image.open(ICON_PATH)
    except FileNotFoundError:
        print(f"Error: Icon file not found at {ICON_PATH}")
        sys.exit(1)

    menu = (item('Quit', on_quit_clicked),)
    icon = pystrayIcon("PromptBoost", image, "PromptBoost Enhancer", menu)
    print("✅ System tray icon is running.")
    icon.run()

def start_client_app():
    """
    This is the main function called by the external launcher.
    It sets up and runs the client application.
    """
    print("Starting PromptBoost Client...")
    
    monitor_thread = threading.Thread(target=start_monitoring, daemon=True)
    monitor_thread.start()
    
    run_tray_icon()
    
    print("Application has been shut down.")