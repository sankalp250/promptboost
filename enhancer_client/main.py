# module-level imports and constants
import pyperclip
import time
import logging
import uuid
import tkinter as tk
from tkinter import messagebox
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
# ... existing code ...

def display_dialog(enhanced_text, session_id, original_prompt):
    """Display a modal Accept/Reject dialog and handle reroll inside the dialog."""
    try:
        root = tk.Tk()
        root.title("PromptBoost - Accept or Reject?")
        root.geometry("600x400")
        root.resizable(True, True)
        root.attributes('-topmost', True)
        root.lift()
        root.focus_force()

        title_label = tk.Label(root, text="✨ Prompt Enhanced!", font=("Arial", 16, "bold"), pady=10)
        title_label.pack()

        text_frame = tk.Frame(root)
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
            root,
            text="Choose Accept to keep this enhancement or Reject to get a different version.",
            font=("Arial", 9), fg="gray", pady=5
        )
        instructions.pack()

        button_frame = tk.Frame(root, pady=15)
        button_frame.pack()

        def on_accept():
            print("✅ User accepted the enhancement")
            send_feedback_to_api(session_id, "accepted")
            root.quit()
            root.destroy()

        def on_reject():
            print("🔄 User rejected - requesting different enhancement")
            send_feedback_to_api(session_id, "rejected")

            user_id = settings.USER_ID
            if not user_id:
                messagebox.showerror("Error", "User ID not found.")
                return

            new_session_id = uuid.uuid4()
            print("📤 Requesting different enhancement...")
            
            # -----------------------------------------------------------------
            # ▼▼▼ THE FIX ▼▼▼
            # The 'prompt_text' should be the 'original_prompt', not the
            # 'enhanced_text' that the user just rejected.
            # -----------------------------------------------------------------
            new_enhanced_text = enhance_prompt_from_api(
                prompt_text=original_prompt,  # <-- CORRECTED
                user_id=user_id,
                session_id=new_session_id,
                is_reroll=True,
                original_prompt=original_prompt
            )
            # -----------------------------------------------------------------
            # ▲▲▲ END OF FIX ▲▲▲
            # -----------------------------------------------------------------

            if new_enhanced_text:
                set_last_session_id(new_session_id)
                set_last_prompts(original_prompt, new_enhanced_text)
                pyperclip.copy(new_enhanced_text)
                # restart modal dialog with new content
                root.quit()
                root.destroy()
                display_dialog(new_enhanced_text, new_session_id, original_prompt)
                show_notification("🔄 Different Enhancement!", "Previous marked as rejected.")
            else:
                messagebox.showerror("Error", "Failed to get different enhancement.")

        def on_close():
            print("Window closed - treating as accept")
            send_feedback_to_api(session_id, "accepted")
            root.quit()
            root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_close)
        root.bind("<Escape>", lambda e: on_close())
        root.bind("<Return>", lambda e: on_accept())

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

        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f"{width}x{height}+{x}+{y}")

        root.mainloop()
        return True

    except Exception as e:
        print(f"❌ ERROR showing dialog: {e}")
        show_notification("✨ Prompt Enhanced!", "Dialog failed to show. Enhancement is in clipboard.")
        return False
# ... existing code ...

def process_clipboard():
    # ... (rest of your process_clipboard function) ...
    # This part looks correct.
    global recent_text
    try:
        current_text = pyperclip.paste()
    except Exception as e:
        # Handle clipboard errors, e.g., on remote desktop
        # print(f"Clipboard error: {e}")
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

            # Show Accept/Reject modal dialog
            print("💡 Showing Accept/Reject dialog...")
            display_dialog(enhanced_text, session_id, prompt_to_enhance)
        else:
            print("❌ Enhancement failed.")
            show_notification("🚫 Enhancement Failed", "Check server connection and logs.")
            recent_text = ""
        return
    # ... (rest of your function) ...

def start_monitoring():
    # ... existing code ...
    print("Clipboard monitoring started...")
    while monitoring_active:
        process_clipboard()
        time.sleep(0.5)
    print("Clipboard monitoring stopped.")

# (Your other functions like stop_monitoring)