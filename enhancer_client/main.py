"""
Complete client-side implementation with tray icon and dialog support.
This file contains all the necessary components for the PromptBoost client.
"""
import pyperclip
import time
import logging
import uuid
import tkinter as tk
from tkinter import messagebox
import queue
import threading
from PIL import Image, ImageDraw
import pystray
import sys

# Import from other modules
from enhancer_client.enhancer.api_client import enhance_prompt_from_api, send_feedback_to_api
from enhancer_client.enhancer.notifier import show_notification
from enhancer_client.enhancer.config import settings
from enhancer_client.enhancer.state import (
    set_last_session_id,
    set_last_prompts,
    get_last_original_prompt,
    get_last_session_id
)

# Constants
TRIGGER_SUFFIX_ENHANCE = "!!e"
recent_text = ""
monitoring_active = True
tray_icon = None

# --- THREAD-SAFE QUEUE ---
dialog_queue = queue.Queue()

# --- TKINTER ROOT ---
try:
    root = tk.Tk()
    root.withdraw()
except Exception as e:
    print(f"CRITICAL: Failed to initialize tkinter. Is a display available? {e}")
    root = None


def display_dialog(enhanced_text, session_id, original_prompt):
    """Display a modal Accept/Reject dialog and handle reroll inside the dialog."""
    
    if not root:
        print("ERROR: tkinter root window not initialized. Cannot show dialog.")
        show_notification("✨ Prompt Enhanced!", "Enhancement copied to clipboard.")
        return

    try:
        dialog = tk.Toplevel(root)
        dialog.title("PromptBoost - Accept or Reject?")
        dialog.geometry("600x400")
        dialog.resizable(True, True)
        
        dialog.attributes('-topmost', True)
        dialog.lift()
        dialog.focus_force()

        title_label = tk.Label(dialog, text="✨ Prompt Enhanced!", font=("Arial", 16, "bold"), pady=10)
        title_label.pack()

        text_frame = tk.Frame(dialog)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        text_widget = tk.Text(
            text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set,
            font=("Consolas", 11), padx=10, pady=10, height=12
        )
        text_widget.insert(tk.END, enhanced_text)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_widget.yview)

        instructions = tk.Label(
            dialog,
            text="Choose Accept to keep this enhancement or Reject to get a different version.",
            font=("Arial", 9), fg="gray", pady=5
        )
        instructions.pack()

        button_frame = tk.Frame(dialog, pady=15)
        button_frame.pack()

        def on_accept():
            print("✅ User accepted the enhancement")
            send_feedback_to_api(session_id, "accepted")
            dialog.quit()
            dialog.destroy()

        def on_reject():
            print("🔄 User rejected - requesting different enhancement")
            send_feedback_to_api(session_id, "rejected")

            user_id = settings.USER_ID
            if not user_id:
                messagebox.showerror("Error", "User ID not found.")
                return

            new_session_id = uuid.uuid4()
            print("📤 Requesting different enhancement...")
            
            new_enhanced_text = enhance_prompt_from_api(
                prompt_text=original_prompt,
                user_id=user_id,
                session_id=new_session_id,
                is_reroll=True,
                original_prompt=original_prompt
            )
            
            dialog.quit()
            dialog.destroy()

            if new_enhanced_text:
                set_last_session_id(new_session_id)
                set_last_prompts(original_prompt, new_enhanced_text)
                pyperclip.copy(new_enhanced_text)
                
                show_notification("🔄 Different Enhancement!", "Previous marked as rejected.")
                display_dialog(new_enhanced_text, new_session_id, original_prompt)
            else:
                messagebox.showerror("Error", "Failed to get different enhancement.")

        def on_close():
            print("Window closed - treating as accept")
            send_feedback_to_api(session_id, "accepted")
            dialog.quit()
            dialog.destroy()

        dialog.protocol("WM_DELETE_WINDOW", on_close)
        dialog.bind("<Escape>", lambda e: on_close())
        dialog.bind("<Return>", lambda e: on_accept())

        reject_btn = tk.Button(
            button_frame, text="🔄 Reject & Get Different",
            font=("Arial", 11), bg="#ff6b6b", fg="white",
            padx=20, pady=10, command=on_reject, cursor="hand2"
        )
        reject_btn.pack(side=tk.LEFT, padx=10)

        accept_btn = tk.Button(
            button_frame, text="✅ Accept",
            font=("Arial", 11, "bold"), bg="#51cf66", fg="white",
            padx=30, pady=10, command=on_accept, cursor="hand2"
        )
        accept_btn.pack(side=tk.LEFT, padx=10)

        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")

        dialog.wait_window()
        return True

    except Exception as e:
        print(f"❌ ERROR showing dialog: {e}")
        show_notification("✨ Prompt Enhanced!", "Dialog failed to show. Enhancement is in clipboard.")
        return False


def process_clipboard():
    """Process clipboard for enhancement triggers."""
    global recent_text
    
    try:
        current_text = pyperclip.paste()
    except Exception as e:
        return
        
    if not isinstance(current_text, str):
        return
        
    current_stripped = current_text.strip()
    recent_stripped = recent_text.strip()

    if current_stripped != recent_stripped and current_stripped.endswith(TRIGGER_SUFFIX_ENHANCE):
        recent_text = current_text
        prompt_to_enhance = current_stripped.removesuffix(TRIGGER_SUFFIX_ENHANCE).strip()
        
        if not prompt_to_enhance:
            return

        print(f"✅ Enhancement trigger detected (!!e)!")
        session_id = uuid.uuid4()
        user_id = settings.USER_ID
        if not user_id:
            print("CRITICAL: User ID not found.")
            return

        enhanced_text = enhance_prompt_from_api(
            prompt_text=prompt_to_enhance,
            user_id=user_id,
            session_id=session_id,
            is_reroll=False,
            original_prompt=prompt_to_enhance
        )

        if enhanced_text:
            set_last_session_id(session_id)
            set_last_prompts(prompt_to_enhance, enhanced_text)
            print("✅ Successfully enhanced prompt. Updating clipboard.")
            pyperclip.copy(enhanced_text)
            recent_text = enhanced_text
            
            if enhanced_text.strip() == prompt_to_enhance.strip():
                print("--- Server bypassed enhancement (likely code). Dialog skipped. ---")
                return

            print("💡 Queuing dialog request for main thread...")
            dialog_queue.put({
                'enhanced_text': enhanced_text,
                'session_id': session_id,
                'original_prompt': prompt_to_enhance
            })
        else:
            print("❌ Enhancement failed.")
            show_notification("🚫 Enhancement Failed", "Check server connection and logs.")
            recent_text = ""


def check_dialog_queue():
    """
    Check if there are any dialog requests in the queue and show them.
    MUST be called from the main thread.
    """
    try:
        while not dialog_queue.empty():
            dialog_request = dialog_queue.get_nowait()
            display_dialog(
                dialog_request['enhanced_text'],
                dialog_request['session_id'],
                dialog_request['original_prompt']
            )
    except queue.Empty:
        pass
    except Exception as e:
        print(f"❌ ERROR processing dialog queue: {e}")


def clipboard_monitor_loop():
    """Background thread function that monitors clipboard."""
    global monitoring_active
    print("Clipboard monitoring started...")
    print(f"   Use '{TRIGGER_SUFFIX_ENHANCE}' to enhance a prompt")
    
    while monitoring_active:
        try:
            process_clipboard()
            time.sleep(0.5)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"ERROR in monitor loop: {e}")
            time.sleep(2)
    
    print("Clipboard monitoring stopped.")


def create_icon_image():
    """Create a simple icon for the system tray."""
    width = 64
    height = 64
    color1 = "#4CAF50"
    color2 = "#45a049"
    
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        (width // 4, height // 4, width * 3 // 4, height * 3 // 4),
        fill=color2
    )
    
    return image


def on_quit_tray(icon, item):
    """Handle quit from tray menu."""
    global monitoring_active, tray_icon
    print("\n🛑 Shutting down PromptBoost...")
    monitoring_active = False
    if icon:
        icon.stop()
    if root:
        try:
            root.quit()
        except:
            pass
    sys.exit(0)


def setup_tray_icon():
    """Setup and return the system tray icon."""
    icon_image = create_icon_image()
    menu = pystray.Menu(
        pystray.MenuItem("PromptBoost is running", lambda: None, enabled=False),
        pystray.MenuItem(f"Trigger: {TRIGGER_SUFFIX_ENHANCE}", lambda: None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quit", on_quit_tray)
    )
    
    icon = pystray.Icon("PromptBoost", icon_image, "PromptBoost", menu)
    return icon


def tray_icon_main_loop(icon):
    """
    Main loop for the tray icon. This runs in the main thread and
    periodically checks the dialog queue.
    """
    icon.visible = True
    print("\n✅ PromptBoost is running in the system tray!")
    print(f"📋 Copy text ending with '{TRIGGER_SUFFIX_ENHANCE}' to enhance it")
    print("🔔 A dialog will appear when enhancement is ready")
    print("❌ Right-click the tray icon and select 'Quit' to exit\n")
    
    while monitoring_active and icon.visible:
        try:
            # Check for dialog requests (CRITICAL!)
            check_dialog_queue()
            
            # Update tkinter
            if root:
                root.update()
            
            time.sleep(0.1)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"ERROR in main loop: {e}")
            time.sleep(1)


def start_client_app():
    """
    Main entry point to start the PromptBoost client.
    Returns the monitor thread.
    """
    global tray_icon, monitoring_active
    
    if not settings.USER_ID:
        print("❌ CRITICAL: User ID not found. Cannot start application.")
        return None
    
    print(f"👤 User ID: {settings.USER_ID}")
    print(f"🌐 API URL: {settings.API_BASE_URL}")
    
    # Start clipboard monitoring in background thread
    monitor_thread = threading.Thread(target=clipboard_monitor_loop, daemon=True)
    monitor_thread.start()
    
    # Setup and run tray icon in main thread
    tray_icon = setup_tray_icon()
    
    # Run the tray icon with our custom loop
    tray_icon.run(setup=tray_icon_main_loop)
    
    return monitor_thread


def stop_tray_icon():
    """Stop the tray icon and cleanup."""
    global monitoring_active, tray_icon
    monitoring_active = False
    if tray_icon:
        tray_icon.stop()
    if root:
        try:
            root.quit()
            root.destroy()
        except:
            pass


# For standalone testing
if __name__ == "__main__":
    try:
        print("Starting PromptBoost in standalone mode...")
        start_client_app()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
        stop_tray_icon()