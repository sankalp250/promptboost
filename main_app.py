import sys
import os
import threading
import signal
from pathlib import Path

# --- IMPORTANT SCRIPT SETUP ---
# When packaged by PyInstaller, the script's base directory can be a temporary folder.
# This code correctly finds the 'enhancer_client' directory whether we are running
# as a normal script or as a frozen .exe.
if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True.
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).resolve().parent

# We need to add the parent directory of enhancer_client to the Python path
# so our imports work correctly in all scenarios.
sys.path.append(str(BASE_DIR))
# --- END IMPORTANT SCRIPT SETUP ---

from enhancer_client.main import start_client_app, stop_tray_icon

tray_icon_thread = None

def signal_handler(sig, frame):
    """Handles Ctrl+C for a graceful shutdown."""
    print("\nCtrl+C detected! Shutting down client...")
    stop_tray_icon()
    sys.exit(0)

if __name__ == "__main__":
    # Register the signal handler for Ctrl+C.
    signal.signal(signal.SIGINT, signal_handler)

    print("Application entry point reached. Starting client...")
    
    # Start the client application.
    tray_icon_thread = start_client_app()
    
    # Keep the main thread alive, waiting for the tray icon thread to finish.
    if tray_icon_thread:
        tray_icon_thread.join()
    
    print("Application has been shut down successfully.")