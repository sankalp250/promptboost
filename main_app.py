import sys
import signal
from enhancer_client.main import start_client_app, stop_tray_icon

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    print("\n\n🛑 Received interrupt signal. Shutting down...")
    stop_tray_icon()
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    print("=" * 60)
    print("   PromptBoost - AI-Powered Prompt Enhancement Tool")
    print("=" * 60)
    
    try:
        # This blocks until the user quits via tray icon or Ctrl+C
        start_client_app()
    except KeyboardInterrupt:
        print("\n\n🛑 Application interrupted.")
        stop_tray_icon()
    except Exception as e:
        print(f"\n\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        stop_tray_icon()
        sys.exit(1)