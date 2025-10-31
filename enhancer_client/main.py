import sys
import threading
from .enhancer.clipboard_monitor import start_monitoring, stop_monitoring
from .enhancer.feedback_hotkey import start_feedback_listener, stop_feedback_listener
from pystray import Icon as pystrayIcon, MenuItem as item
from PIL import Image
from pathlib import Path

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = Path(__file__).resolve().parent
    return Path(base_path) / relative_path

icon_instance = None
ICON_PATH = resource_path("assets/icon.png")

def on_quit_clicked(icon, item):
    """Function to handle the quit action."""
    print("Quit clicked. Shutting down...")
    stop_monitoring()
    stop_feedback_listener()
    icon.stop()

def run_tray_icon():
    """Creates and runs the system tray icon."""
    global icon_instance
    try:
        image = Image.open(ICON_PATH)
        print(f"Successfully loaded icon from: {ICON_PATH}")
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to load icon from {ICON_PATH}. Error: {e}")
        image = None
    menu = (item('Quit', on_quit_clicked),)
    icon_instance = pystrayIcon("PromptBoost", image, "PromptBoost Enhancer", menu)
    print("✅ System tray icon is running.")
    icon_instance.run()

def stop_tray_icon():
    """A dedicated function to allow external scripts to stop the tray icon."""
    if icon_instance:
        icon_instance.stop()

def start_client_app():
    """
    This is the main function called by the external launcher.
    """
    print("Starting PromptBoost Client...")
    monitor_thread = threading.Thread(target=start_monitoring, daemon=True)
    monitor_thread.start()
    feedback_thread = threading.Thread(target=start_feedback_listener, daemon=True)
    feedback_thread.start()
    tray_thread = threading.Thread(target=run_tray_icon)
    tray_thread.start()
    return tray_thread