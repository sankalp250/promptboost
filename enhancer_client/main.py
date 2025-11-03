# module-level imports and constants
import pyperclip
import time
import logging
import uuid
import tkinter as tk
from tkinter import messagebox
import queue
import threading
from .api_client import enhance_prompt_from_api, send_feedback_to_api
from .notifier import show_notification
from .config import settings
from .state import (
    set_last_session_id,
    set_last_prompts,
    get_last_original_prompt,
    get_last_session_id
)

TRIGGER_SUFFIX_ENHANCE = "!!e"
recent_text = ""
monitoring_active = True

# --- FIX: THREAD-SAFE QUEUE ---
# Queue to pass dialog requests from background thread to main thread
dialog_queue = queue.Queue()

# --- FIX 1: THE TKINTER ROOT ---
# Create a single, hidden, persistent root window for tkinter.
# This solves the bug where the dialog only appears once.
try:
    root = tk.Tk()
    root.withdraw()  # Hide the main window
except Exception as e:
    print(f"CRITICAL: Failed to initialize tkinter. Is a display available? {e}")
    # Handle environments where tkinter can't run (e.g., SSH session)
    root = None

def display_dialog(enhanced_text, session_id, original_prompt):
    """Display a modal Accept/Reject dialog and handle reroll inside the dialog."""
    
    if not root:
        print("ERROR: tkinter root window not initialized. Cannot show dialog.")
        show_notification("✨ Prompt Enhanced!", "Enhancement copied to clipboard.")
        return

    try:
        # --- FIX 1 (Continued): Use Toplevel ---
        # Create a Toplevel window, which is a child of the main 'root'.
        dialog = tk.Toplevel(root)
        dialog.title("PromptBoost - Accept or Reject?")
        dialog.geometry("600x400")
        dialog.resizable(True, True)
        
        # Make this dialog stay on top and grab focus
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
                prompt_text=original_prompt,  # Correct logic: send original prompt
                user_id=user_id,
                session_id=new_session_id,
                is_reroll=True,
                original_prompt=original_prompt
            )
            
            # First, destroy the current dialog
            dialog.quit()
            dialog.destroy()

            if new_enhanced_text:
                set_last_session_id(new_session_id)
                set_last_prompts(original_prompt, new_enhanced_text)
                pyperclip.copy(new_enhanced_text)
                
                show_notification("🔄 Different Enhancement!", "Previous marked as rejected.")
                # Recursively call display_dialog for the new enhancement
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

        # Use wait_window to make it a modal dialog
        dialog.wait_window()
        return True

    except Exception as e:
        print(f"❌ ERROR showing dialog: {e}")
        show_notification("✨ Prompt Enhanced!", "Dialog failed to show. Enhancement is in clipboard.")
        return False

def process_clipboard():
    # --- FIX 2: GLOBAL VARIABLE ---
    # We must use 'global' to modify the 'recent_text'
    # variable in the module's scope.
    global recent_text
    
    try:
        current_text = pyperclip.paste()
    except Exception as e:
        # print(f"Clipboard error: {e}")
        return
        
    if not isinstance(current_text, str):
        return
        
    current_stripped = current_text.strip()
    recent_stripped = recent_text.strip()

    if current_stripped != recent_stripped and current_stripped.endswith(TRIGGER_SUFFIX_ENHANCE):
        # This assignment now correctly updates the global variable
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
            
            # This assignment also updates the global variable
            recent_text = enhanced_text
            
            # --- CHECK FOR BYPASS ---
            # If the server bypassed (returned original text), don't show dialog.
            if enhanced_text.strip() == prompt_to_enhance.strip():
                print("--- Server bypassed enhancement (likely code). Dialog skipped. ---")
                return

            # --- FIX: USE QUEUE INSTEAD OF DIRECT CALL ---
            # Put the dialog request in the queue for the main thread to handle
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
        return

def check_dialog_queue():
    """
    Check if there are any dialog requests in the queue and show them.
    MUST be called from the main thread (where the tray icon runs).
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

def start_monitoring():
    """
    Start the clipboard monitoring loop in a background thread.
    This should be called to initialize the monitoring.
    """
    print("Clipboard monitoring started...")
    print(f"   Use '{TRIGGER_SUFFIX_ENHANCE}' to enhance a prompt")
    
    def monitor_loop():
        global monitoring_active
        while monitoring_active:
            try:
                process_clipboard()
                time.sleep(0.5)
            except KeyboardInterrupt:
                print("\nStopping monitor...")
                stop_monitoring()
            except Exception as e:
                print(f"ERROR in monitor loop: {e}")
                time.sleep(2)  # Prevent rapid-fire errors
    
    # Start monitoring in a daemon thread
    monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
    monitor_thread.start()
    print("✅ Clipboard monitoring thread started")

def stop_monitoring():
    global monitoring_active
    monitoring_active = False
    print("Clipboard monitoring stopped.")

# --- FOR STANDALONE TESTING ONLY ---
# If you run this file directly (not from tray), it will start a simple tkinter loop
if __name__ == "__main__":
    try:
        start_monitoring()
        print("Running standalone - press Ctrl+C to stop")
        
        # Simple main loop that checks the queue
        while monitoring_active:
            if root:
                check_dialog_queue()
                root.update()
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        stop_monitoring()
        if root:
            root.destroy()