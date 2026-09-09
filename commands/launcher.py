import subprocess
import os
import re

def launch_app(command_text: str) -> str:
    """
    Launch desktop applications based on natural language user commands.
    Supports everyday apps like WhatsApp, Word, Excel, PowerPoint, Chrome, VS Code,
    Terminal, Calculator, Settings, Camera, Snipping Tool, Spotify, Telegram, Discord, Zoom, etc.
    """
    clean_cmd = command_text.lower().strip()
    clean_cmd = re.sub(r'^(open|launch|start|run|please open|please launch)\s+', '', clean_cmd).strip()
    
    apps_to_open = [app.strip() for app in re.split(r'\s+(?:and|,)\s+', clean_cmd) if app.strip()]
    opened_apps = []
    failed_apps = []
    
    for app in apps_to_open:
        # 1. Messaging & Social Apps
        if app in ["whatsapp", "whatsapp app"]:
            try:
                os.startfile("whatsapp:")
                opened_apps.append("WhatsApp")
            except Exception:
                try:
                    os.startfile("https://web.whatsapp.com")
                    opened_apps.append("WhatsApp Web")
                except Exception:
                    failed_apps.append("WhatsApp")

        elif app in ["telegram"]:
            try:
                os.startfile("telegram:")
                opened_apps.append("Telegram")
            except Exception:
                try:
                    os.startfile("https://web.telegram.org")
                    opened_apps.append("Telegram Web")
                except Exception:
                    failed_apps.append("Telegram")

        elif app in ["discord"]:
            try:
                os.startfile("discord:")
                opened_apps.append("Discord")
            except Exception:
                try:
                    os.startfile("https://discord.com/app")
                    opened_apps.append("Discord Web")
                except Exception:
                    failed_apps.append("Discord")

        elif app in ["zoom", "zoom meeting"]:
            try:
                os.startfile("zoommtg:")
                opened_apps.append("Zoom")
            except Exception:
                failed_apps.append("Zoom")

        elif app in ["teams", "microsoft teams", "ms teams"]:
            try:
                os.startfile("msteams:")
                opened_apps.append("Microsoft Teams")
            except Exception:
                failed_apps.append("Microsoft Teams")

        # 2. Office & Productivity Apps
        elif app in ["word", "microsoft word", "ms word", "doc", "docx"]:
            try:
                subprocess.Popen(["winword.exe"])
                opened_apps.append("Microsoft Word")
            except Exception:
                failed_apps.append("Microsoft Word")

        elif app in ["excel", "microsoft excel", "ms excel", "spreadsheet"]:
            try:
                subprocess.Popen(["excel.exe"])
                opened_apps.append("Microsoft Excel")
            except Exception:
                failed_apps.append("Microsoft Excel")

        elif app in ["powerpoint", "ppt", "microsoft powerpoint", "presentation"]:
            try:
                subprocess.Popen(["powerpnt.exe"])
                opened_apps.append("Microsoft PowerPoint")
            except Exception:
                failed_apps.append("Microsoft PowerPoint")

        elif app in ["onenote", "microsoft onenote"]:
            try:
                os.startfile("onenote:")
                opened_apps.append("OneNote")
            except Exception:
                failed_apps.append("OneNote")

        # 3. Web Browsers
        elif app in ["chrome", "google chrome", "browser"]:
            try:
                os.startfile("chrome")
                opened_apps.append("Chrome")
            except Exception:
                try:
                    subprocess.Popen(["cmd.exe", "/c", "start", "chrome"], shell=True)
                    opened_apps.append("Chrome")
                except Exception:
                    failed_apps.append("Chrome")

        elif app in ["edge", "microsoft edge", "msedge"]:
            try:
                os.startfile("msedge")
                opened_apps.append("Microsoft Edge")
            except Exception:
                failed_apps.append("Edge")

        elif app in ["firefox", "mozilla firefox"]:
            try:
                os.startfile("firefox")
                opened_apps.append("Firefox")
            except Exception:
                failed_apps.append("Firefox")

        elif app in ["brave", "brave browser"]:
            try:
                os.startfile("brave")
                opened_apps.append("Brave")
            except Exception:
                failed_apps.append("Brave")

        # 4. System & Developer Utilities
        elif app in ["terminal", "cmd", "command prompt", "command line"]:
            try:
                subprocess.Popen(["cmd.exe"])
                opened_apps.append("Terminal (Cmd)")
            except Exception:
                failed_apps.append("Terminal")

        elif app in ["powershell"]:
            try:
                subprocess.Popen(["powershell.exe"])
                opened_apps.append("PowerShell")
            except Exception:
                failed_apps.append("PowerShell")

        elif app in ["vscode", "code", "visual studio code", "code editor"]:
            try:
                subprocess.Popen(["code", "."], shell=True)
                opened_apps.append("VS Code")
            except Exception:
                failed_apps.append("VS Code")

        elif app in ["calculator", "calc"]:
            try:
                subprocess.Popen(["calc.exe"])
                opened_apps.append("Calculator")
            except Exception:
                failed_apps.append("Calculator")

        elif app in ["notepad", "text editor"]:
            try:
                subprocess.Popen(["notepad.exe"])
                opened_apps.append("Notepad")
            except Exception:
                failed_apps.append("Notepad")

        elif app in ["snipping tool", "snip", "snippingtool"]:
            try:
                subprocess.Popen(["snippingtool.exe"])
                opened_apps.append("Snipping Tool")
            except Exception:
                failed_apps.append("Snipping Tool")

        elif app in ["camera"]:
            try:
                os.startfile("microsoft.windows.camera:")
                opened_apps.append("Camera")
            except Exception:
                failed_apps.append("Camera")

        elif app in ["paint", "ms paint", "mspaint"]:
            try:
                subprocess.Popen(["mspaint.exe"])
                opened_apps.append("MS Paint")
            except Exception:
                failed_apps.append("Paint")

        elif app in ["settings", "system settings", "windows settings"]:
            try:
                os.startfile("ms-settings:")
                opened_apps.append("Settings")
            except Exception:
                failed_apps.append("Settings")

        elif app in ["control panel"]:
            try:
                subprocess.Popen(["control.exe"])
                opened_apps.append("Control Panel")
            except Exception:
                failed_apps.append("Control Panel")

        elif app in ["task manager", "taskmgr"]:
            try:
                subprocess.Popen(["taskmgr.exe"])
                opened_apps.append("Task Manager")
            except Exception:
                failed_apps.append("Task Manager")

        elif app in ["explorer", "file explorer", "my computer", "files"]:
            try:
                subprocess.Popen(["explorer.exe"])
                opened_apps.append("File Explorer")
            except Exception:
                failed_apps.append("File Explorer")

        elif app in ["spotify", "music player"]:
            try:
                os.startfile("spotify:")
                opened_apps.append("Spotify")
            except Exception:
                failed_apps.append("Spotify")

        elif app in ["vlc", "vlc media player"]:
            try:
                subprocess.Popen(["vlc.exe"])
                opened_apps.append("VLC Media Player")
            except Exception:
                failed_apps.append("VLC")

        else:
            # Fallback attempt via Windows shell
            try:
                os.startfile(app)
                opened_apps.append(app.capitalize())
            except Exception:
                try:
                    subprocess.Popen(f"start {app}", shell=True)
                    opened_apps.append(app.capitalize())
                except Exception:
                    failed_apps.append(app)
                
    if opened_apps:
        msg = f"Opened: {', '.join(opened_apps)}"
        if failed_apps:
            msg += f" (Could not launch: {', '.join(failed_apps)})"
        return msg
    return f"Could not find or launch requested application(s): {', '.join(failed_apps) if failed_apps else clean_cmd}"


