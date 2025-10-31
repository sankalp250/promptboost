import sys
import signal
from enhancer_client.main import start_client_app, stop_tray_icon

# --- The signal handler and __main__ block for the final version ---
# We remove the try...finally block as it was for debugging.

tray_icon_thread = None

def signal_handler(sig, frame):
    stop_tray_icon()
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    tray_icon_thread = start_client_app()
    if tray_icon_thread:
        tray_icon_thread.join()