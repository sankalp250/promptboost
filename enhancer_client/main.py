import threading
from .enhancer.clipboard_manager import start_monitoring, stop_monitoring
from pystray import Icon as pystrayIcon, MenuItem as item
from PIL import Image
import sys
from pathlib import Path

# --- TRAY ICON LOGIC IS NOW IN MAIN.PY FOR SIMPLICITY ---

CLIENT_ROOT = Path(__file__).resolve().parent
ICON_PATH = CLIENT_ROOT / "assets" / "icon.png"

def on_quit_clicked(icon, item):
    """Function to handle the quit action."""
    print("Quit clicked. Shutting down...")
    stop_monitoring() # Signal the thread to stop
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

if __name__ == "__main__":
    print("Starting PromptBoost Client...")
    
    # Run the clipboard monitor in a separate thread.
    # It's a daemon thread so it will exit when the main app exits.
    monitor_thread = threading.Thread(target=start_monitoring, daemon=True)
    monitor_thread.start()
    
    # The tray icon must run on the main thread. This blocks until "Quit" is clicked.
    run_tray_icon()
    
    print("Application has been shut down.")