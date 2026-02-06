"""
Dialog-based feedback system for PromptBoost
Shows Accept/Reject dialog after enhancement
"""
import uuid
import tkinter as tk
from tkinter import messagebox
import threading
import pyperclip
from enhancer_client.enhancer.api_client import enhance_prompt_from_api, send_feedback_to_api
from enhancer_client.enhancer.config import settings
from enhancer_client.enhancer.state import set_last_session_id, set_last_prompts
from enhancer_client.enhancer.notifier import show_notification

# Store current enhancement data
_current_enhancement = {
    'enhanced_text': None,
    'session_id': None,
    'original_prompt': None,
    'dialog_open': False
}

def show_dialog_on_main_thread(enhanced_text: str, session_id: uuid.UUID, original_prompt: str):
    """Show the Accept/Reject dialog (must run on main thread for tkinter)"""
    if _current_enhancement.get('dialog_open'):
        print("⚠️ Dialog already open, skipping...")
        return
    
    _current_enhancement['dialog_open'] = True
    _current_enhancement['enhanced_text'] = enhanced_text
    _current_enhancement['session_id'] = session_id
    _current_enhancement['original_prompt'] = original_prompt
    
    # Create the dialog window
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    # Configure dialog appearance
    dialog = tk.Toplevel(root)
    dialog.title("✨ Prompt Enhanced!")
    # REPLACED: dialog.geometry("500x250") -> Smaller/Shorter as requested
    dialog.geometry("480x280") 
    dialog.resizable(False, False)
    
    # Make dialog stay on top
    dialog.attributes('-topmost', True)
    dialog.focus_force()
    
    # Header
    header = tk.Label(
        dialog, 
        text="✨ Your prompt has been enhanced!",
        font=("Arial", 12, "bold"), # Slightly smaller font
        pady=5
    )
    header.pack()
    
    # Info text
    info = tk.Label(
        dialog,
        text="The result is in your clipboard.",
        font=("Arial", 9),
        fg="#555",
        pady=2
    )
    info.pack()
    
    # Text Area Frame (for scrolling)
    text_frame = tk.Frame(dialog)
    text_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
    
    # Scrollbar
    scrollbar = tk.Scrollbar(text_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Editable Text Area (Read-only behavior handled below)
    text_area = tk.Text(
        text_frame,
        height=5, # Short height to keep dialog small
        font=("Consolas", 9),
        wrap=tk.WORD,
        yscrollcommand=scrollbar.set,
        bg="#f5f5f5",
        bd=1,
        relief=tk.SOLID
    )
    text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Insert text and make read-only
    text_area.insert(tk.END, enhanced_text)
    text_area.config(state=tk.DISABLED) # Prevent editing
    
    # Link scrollbar
    scrollbar.config(command=text_area.yview)
    
    # Button frame
    button_frame = tk.Frame(dialog)
    button_frame.pack(pady=20)
    
    def on_accept():
        """Handle Accept button"""
        print("\n" + "="*60)
        print("✅ User ACCEPTED via dialog button")
        print("="*60)
        send_feedback_to_api(session_id, "accepted")
        show_notification("✅ Accepted!", "Enhancement accepted")
        _current_enhancement['dialog_open'] = False
        dialog.destroy()
        root.quit()
    
    def on_reject():
        """Handle Reject button - get different enhancement"""
        print("\n" + "="*60)
        print("🔄 User REJECTED via dialog button - Getting different version")
        print("="*60)
        
        send_feedback_to_api(session_id, "rejected")
        
        # Close current dialog
        dialog.destroy()
        
        # Show "getting different version" message
        show_notification("🔄 Getting Different...", "Please wait...")
        
        # Get new enhancement
        user_id = settings.USER_ID
        new_session_id = uuid.uuid4()
        
        print("📤 Requesting different enhancement...")
        
        new_enhanced_text = enhance_prompt_from_api(
            prompt_text=original_prompt,
            user_id=user_id,
            session_id=new_session_id,
            is_reroll=True,
            original_prompt=original_prompt
        )
        
        if new_enhanced_text:
            set_last_session_id(new_session_id)
            set_last_prompts(original_prompt, new_enhanced_text)
            pyperclip.copy(new_enhanced_text)
            
            print("✅ Got different enhancement!")
            
            # Show new dialog with different version
            _current_enhancement['dialog_open'] = False
            root.quit()
            
            # Show new dialog in a new thread
            show_enhancement_dialog(new_enhanced_text, new_session_id, original_prompt)
        else:
            print("❌ Failed to get different enhancement")
            show_notification("🚫 Error", "Failed to get different enhancement")
            _current_enhancement['dialog_open'] = False
            root.quit()
    
    def on_close():
        """Handle window close (X button) - treat as Accept"""
        print("\n" + "="*60)
        print("✅ User closed dialog (treating as Accept)")
        print("="*60)
        send_feedback_to_api(session_id, "accepted")
        _current_enhancement['dialog_open'] = False
        dialog.destroy()
        root.quit()
    
    # Accept button (green)
    accept_btn = tk.Button(
        button_frame,
        text="✅ Accept",
        command=on_accept,
        width=15,
        height=2,
        bg="#4CAF50",
        fg="white",
        font=("Arial", 11, "bold"),
        cursor="hand2"
    )
    accept_btn.pack(side=tk.LEFT, padx=10)
    
    # Reject button (orange)
    reject_btn = tk.Button(
        button_frame,
        text="🔄 Reject (Get Different)",
        command=on_reject,
        width=20,
        height=2,
        bg="#FF9800",
        fg="white",
        font=("Arial", 11, "bold"),
        cursor="hand2"
    )
    reject_btn.pack(side=tk.LEFT, padx=10)
    
    # Handle window close button
    dialog.protocol("WM_DELETE_WINDOW", on_close)
    
    # Center the dialog on screen
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
    y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
    dialog.geometry(f"+{x}+{y}")
    
    # Run the dialog
    root.mainloop()

def show_enhancement_dialog(enhanced_text: str, session_id: uuid.UUID, original_prompt: str):
    """
    Show the Accept/Reject dialog.
    This function spawns a new thread to avoid blocking the main application.
    """
    print("\n" + "="*60)
    print("🔔 Showing Accept/Reject dialog...")
    print("="*60)
    
    # Run dialog in a separate thread to avoid blocking clipboard monitor
    dialog_thread = threading.Thread(
        target=show_dialog_on_main_thread,
        args=(enhanced_text, session_id, original_prompt),
        daemon=True
    )
    dialog_thread.start()