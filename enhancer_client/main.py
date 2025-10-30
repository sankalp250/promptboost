import threading
from enhancer.hotkey_manager import start_listener
from enhancer.tray_icon import create_and_run_tray_icon

if __name__ == "__main__":
    print("Starting PromptBoost Client...")
    
    # Run the keyboard listener in a separate thread so it doesn't
    # block the system tray icon's main loop.
    listener_thread = threading.Thread(target=start_listener, daemon=True)
    listener_thread.start()
    
    # The tray icon must run on the main thread. This will block
    # until the user clicks "Quit".
    create_and_run_tray_icon()
    
    print("Application has been shut down.")