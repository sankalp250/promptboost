import pyperclip
import logging

def get_clipboard_text() -> str:
    """Gets text from the system clipboard."""
    try:
        return pyperclip.paste()
    except pyperclip.PyperclipException as e:
        logging.error(f"Could not access clipboard: {e}")
        return ""

def set_clipboard_text(text: str):
    """Puts text onto the system clipboard."""
    try:
        pyperclip.copy(text)
    except pyperclip.PyperclipException as e:
        logging.error(f"Could not write to clipboard: {e}")