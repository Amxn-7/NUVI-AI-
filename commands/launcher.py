import subprocess
import os

def launch_app(command_text: str) -> str:
    """
    Launch standard apps like chrome, vscode based on the text command.
    Example: 'open chrome' or 'open vscode and chrome'
    """
    command_text = command_text.lower().replace("open ", "").strip()
    
    # Split by 'and' to open multiple apps if requested
    apps_to_open = [app.strip() for app in command_text.split(" and ")]
    opened_apps = []
    
    for app in apps_to_open:
        # Simple mapping for common apps
        # On Windows, os.startfile or subprocess with shell=True can launch apps if they are in PATH or known
        if app in ["chrome", "google chrome"]:
            try:
                os.startfile("chrome")
                opened_apps.append("Chrome")
            except Exception:
                return "Failed to open Chrome."
        elif app in ["vscode", "code"]:
            try:
                subprocess.Popen(["code", "."], shell=True)
                opened_apps.append("VS Code")
            except Exception:
                return "Failed to open VS Code."
        elif app in ["notepad"]:
            try:
                subprocess.Popen(["notepad.exe"])
                opened_apps.append("Notepad")
            except Exception:
                return "Failed to open Notepad."
        else:
            # Try generic start
            try:
                os.startfile(app)
                opened_apps.append(app.capitalize())
            except Exception:
                return f"Could not find or launch '{app}'."
                
    if opened_apps:
        return f"Opened: {', '.join(opened_apps)}"
    return "No applications matched or opened."
