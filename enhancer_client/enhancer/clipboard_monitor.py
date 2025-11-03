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
            new_enhanced_text = enhance_prompt_from_api(
                prompt_text=enhanced_text,
                user_id=user_id,
                session_id=new_session_id,
                is_reroll=True,
                original_prompt=original_prompt
            )

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

def process_clipboard():
    """Performs the check and enhancement of the clipboard content."""
    global recent_text
    
    try:
        current_text = pyperclip.paste()
    except Exception:
        return

    if not current_text:
        return

    # Normalize for comparison - strip trailing whitespace
    current_stripped = current_text.rstrip()
    recent_stripped = recent_text.rstrip() if recent_text else ""

    # ALWAYS log when we see trigger suffix - this helps debug
    if current_stripped.endswith(TRIGGER_SUFFIX_ENHANCE):
        print(f"🔍 DEBUG: Clipboard ends with !!e")
        print(f"   Current != Recent: {current_stripped != recent_stripped}")
        print(f"   Current length: {len(current_stripped)}, Recent length: {len(recent_stripped)}")
        if current_stripped[-10:]: print(f"   Last 10 chars: {repr(current_stripped[-10:])}")
    
    if current_stripped.endswith(TRIGGER_SUFFIX_REROLL):
        print(f"🔍 DEBUG: Clipboard ends with !!d")
        print(f"   Current != Recent: {current_stripped != recent_stripped}")
        print(f"   Current length: {len(current_stripped)}, Recent length: {len(recent_stripped)}")
        if current_stripped[-10:]: print(f"   Last 10 chars: {repr(current_stripped[-10:])}")
        print(f"   Will trigger: {current_stripped != recent_stripped and current_stripped.endswith(TRIGGER_SUFFIX_REROLL)}")

    # Check for enhancement trigger (!!e)
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

    # Reroll trigger (!!d) disabled to avoid conflicts with dialog-driven reroll
    # if current_stripped.endswith("!!d"): pass
    if current_stripped.endswith(TRIGGER_SUFFIX_REROLL):
        # Only process if it's actually different from recent (prevents duplicate processing)
        if current_stripped != recent_stripped:
            # Set recent_text BEFORE processing to prevent duplicate triggers
            recent_text = current_text
            prompt_to_enhance = current_stripped.removesuffix(TRIGGER_SUFFIX_REROLL).strip()
            
            if not prompt_to_enhance:
                print("⚠️ Reroll detected but no text after removing !!d")
                return
            
            print(f"🔄 Reroll trigger detected (!!d)!")
            print(f"Enhanced text being rerolled: '{prompt_to_enhance[:100]}...'")
            
            previous_session_id = get_last_session_id()
            original_prompt_for_api = get_last_original_prompt()
            
            print(f"🔍 State check:")
            print(f"   Previous session_id: {previous_session_id}")
            print(f"   Original prompt: {'Found' if original_prompt_for_api else 'NOT FOUND'}")
            
            if not original_prompt_for_api:
                print("❌ CRITICAL: No original prompt found in state!")
                print("   This means the previous enhancement didn't store state properly.")
                print("   Please use !!e first to get an initial enhancement.")
                show_notification("⚠️ Reroll Failed", "No previous enhancement found. Use !!e first.")
                return
            
            if previous_session_id:
                print(f"📤 Marking previous enhancement as rejected (session: {previous_session_id})")
                send_feedback_to_api(previous_session_id, "rejected")
            
            session_id = uuid.uuid4() 
            user_id = settings.USER_ID

            if not user_id:
                print("❌ CRITICAL: User ID not found.")
                return

            print(f"📤 Requesting different enhancement for original prompt...")
            enhanced_text = enhance_prompt_from_api(
                prompt_text=prompt_to_enhance,
                user_id=user_id,
                session_id=session_id,
                is_reroll=True,
                original_prompt=original_prompt_for_api
            )

            if enhanced_text:
                set_last_session_id(session_id)
                set_last_prompts(original_prompt_for_api, enhanced_text)

                print("✅ Successfully got different enhancement. Updating clipboard.")
                pyperclip.copy(enhanced_text)
                recent_text = enhanced_text
                show_notification("🔄 Different Enhancement!", "Previous marked as rejected.")
            else:
                print("❌ Reroll enhancement failed - no response from API.")
                show_notification("🚫 Reroll Failed", "Check server connection and logs.")
        else:
            print(f"⚠️ DEBUG: !!d detected but text matches recent_text (duplicate prevention)")

def start_monitoring():
    """Starts the clipboard monitoring loop."""
    print(f"✅ Clipboard monitor started.")
    print(f"   Use '{TRIGGER_SUFFIX_ENHANCE}' to enhance a prompt")
    print(f"   Use '{TRIGGER_SUFFIX_REROLL}' on an enhanced result to reject and get a different one")
    while monitoring_active:
        process_clipboard()
        time.sleep(0.5)

def stop_monitoring():
    """Signals the monitoring loop to stop."""
    global monitoring_active
    print("Stopping clipboard monitor...")
    monitoring_active = False
