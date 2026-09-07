import json
import os
import webbrowser
import subprocess
from pathlib import Path

# Path to the configuration file
CONFIG_PATH = Path(__file__).parent.parent / "config" / "workspaces.json"

def open_workspace(command_text: str) -> str:
    """
    Open a workspace defined in workspaces.json.
    Example command: 'open dsa workspace'
    """
    command_text = command_text.lower()
    
    # Extract the workspace name (e.g., 'dsa' from 'open dsa workspace')
    # Expected format: open <name> workspace
    parts = command_text.split()
    if len(parts) >= 3 and parts[-1] == "workspace":
        workspace_name = " ".join(parts[1:-1])
    else:
        return "Invalid workspace command. Try 'open <name> workspace'."

    if not CONFIG_PATH.exists():
        return "workspaces.json not found."
        
    try:
        with open(CONFIG_PATH, "r") as f:
            workspaces = json.load(f)
    except Exception as e:
        return f"Error reading config: {e}"

    if workspace_name not in workspaces:
        return f"Workspace '{workspace_name}' not found."
        
    workspace = workspaces[workspace_name]
    
    # Open URLs
    urls = workspace.get("urls", [])
    for url in urls:
        webbrowser.open(url)
        
    # Open Apps
    apps = workspace.get("apps", [])
    for app in apps:
        if app == "code":
            subprocess.Popen(["code", "."], shell=True)
        elif app == "chrome":
            # Just start chrome, although webbrowser.open might already do this
            os.startfile("chrome")
        else:
            # Try to start it natively
            try:
                os.startfile(app)
            except Exception:
                pass
                
    return f"Launched workspace: {workspace_name.capitalize()}"
