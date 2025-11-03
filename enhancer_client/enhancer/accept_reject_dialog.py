import tkinter as tk
from tkinter import messagebox
import threading
from .api_client import enhance_prompt_from_api, send_feedback_to_api
from .state import get_last_session_id, get_last_original_prompt, set_last_session_id, set_last_prompts
from .config import settings
import uuid
import pyperclip


class AcceptRejectDialog:
    def __init__(self, enhanced_text: str, session_id: uuid.UUID, original_prompt: str):
        self.enhanced_text = enhanced_text
        self.session_id = session_id
        self.original_prompt = original_prompt
        self.result = None
        self.window = None
        
    def show(self):
        """Show the dialog directly in the current thread"""
        # Don't use threading as it causes the dialog to not appear
        self._show_dialog()
        
    def _show_dialog(self):
        """Create and show the dialog"""
        self.window = tk.Tk()
        self.window.title("PromptBoost - Accept or Reject?")
        self.window.geometry("600x400")
        self.window.resizable(True, True)
        
        # Make window stay on top
        self.window.attributes('-topmost', True)
        
        # Title
        title_label = tk.Label(
            self.window,
            text="✨ Prompt Enhanced!",
            font=("Arial", 16, "bold"),
            pady=10
        )
        title_label.pack()
        
        # Enhanced text preview (scrollable)
        text_frame = tk.Frame(self.window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget = tk.Text(
            text_frame,
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            font=("Consolas", 10),
            height=12
        )
        text_widget.insert(tk.END, self.enhanced_text)
        text_widget.config(state=tk.DISABLED)  # Read-only
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_widget.yview)
        
        # Instructions
        instructions = tk.Label(
            self.window,
            text="Click Accept to use this enhancement, or Reject to get a different version.",
            font=("Arial", 9),
            fg="gray",
            pady=5
        )
        instructions.pack()
        
        # Button frame
        button_frame = tk.Frame(self.window, pady=15)
        button_frame.pack()
        
        # Reject button (left) - triggers reroll
        reject_btn = tk.Button(
            button_frame,
            text="🔄 Reject & Get Different",
            font=("Arial", 11),
            bg="#ff6b6b",
            fg="white",
            padx=20,
            pady=10,
            command=self.on_reject,
            cursor="hand2"
        )
        reject_btn.pack(side=tk.LEFT, padx=10)
        
        # Accept button (right)
        accept_btn = tk.Button(
            button_frame,
            text="✅ Accept",
            font=("Arial", 11, "bold"),
            bg="#51cf66",
            fg="white",
            padx=30,
            pady=10,
            command=self.on_accept,
            cursor="hand2"
        )
        accept_btn.pack(side=tk.LEFT, padx=10)
        
        # Focus the window
        self.window.focus_force()
        
        # Center window on screen
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
        
        self.window.mainloop()
        
    def on_accept(self):
        """User accepted the enhancement"""
        print("✅ User accepted the enhancement")
        # Mark as accepted
        send_feedback_to_api(self.session_id, "accepted")
        self.result = "accepted"
        self.window.quit()
        self.window.destroy()
        
    def on_reject(self):
        """User rejected - get a different enhancement"""
        print("🔄 User rejected - requesting different enhancement")
        
        # Mark previous as rejected
        if self.session_id:
            send_feedback_to_api(self.session_id, "rejected")
        
        # Get a different enhancement
        previous_session_id = get_last_session_id()
        original_prompt = get_last_original_prompt()
        
        if not original_prompt:
            messagebox.showerror("Error", "Could not find original prompt. Please enhance again with !!e")
            self.window.quit()
            self.window.destroy()
            return
        
        # Close current dialog first
        self.window.quit()
        self.window.destroy()
        
        # Get new enhancement
        user_id = settings.USER_ID
        if not user_id:
            messagebox.showerror("Error", "User ID not found.")
            return
        
        new_session_id = uuid.uuid4()
        
        print("📤 Requesting different enhancement...")
        enhanced_text = enhance_prompt_from_api(
            prompt_text=self.enhanced_text,  # Current enhanced text (will be previous_enhancement)
            user_id=user_id,
            session_id=new_session_id,
            is_reroll=True,
            original_prompt=original_prompt
        )
        
        if enhanced_text:
            set_last_session_id(new_session_id)
            set_last_prompts(original_prompt, enhanced_text)
            
            # Update clipboard
            pyperclip.copy(enhanced_text)
            
            # Show dialog again with new enhancement
            new_dialog = AcceptRejectDialog(enhanced_text, new_session_id, original_prompt)
            new_dialog.show()
            self.result = "rerolled"
        else:
            messagebox.showerror("Error", "Failed to get different enhancement. Check server connection.")
            self.result = "failed"


def show_accept_reject_dialog(enhanced_text: str, session_id: uuid.UUID, original_prompt: str):
    """Show accept/reject dialog for enhancement"""
    dialog = AcceptRejectDialog(enhanced_text, session_id, original_prompt)
    dialog.show()
    return dialog.result

