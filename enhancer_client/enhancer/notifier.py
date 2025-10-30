from plyer import notification

def show_notification(title: str, message: str):
    """Displays a desktop notification."""
    try:
        notification.notify(
            title=title,
            message=message,
            app_name='PromptBoost',
            timeout=5  # Notification will disappear after 5 seconds
        )
    except Exception as e:
        # If plyer fails, we can just print to the console
        print(f"NOTIFICATION: {title} - {message} (Plyer backend might be missing)")