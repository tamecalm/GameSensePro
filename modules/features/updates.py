"""
Auto-update feature utilities.
"""

import json
import requests
import time
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress

from modules.utils.constants import GITHUB_REPO, CURRENT_VERSION, UPDATE_CHECK_FILE
from modules.utils.logger import log_error
from modules.ui.display import clear_screen

console = Console()

def check_for_updates():
    """Check for available updates."""
    clear_screen()
    console.print(Panel(
        f"[bold magenta]=== CHECKING FOR UPDATES ===[/]\n"
        f"[bold cyan][Started at {datetime.now().strftime('%H:%M:%S')}][/]",
        title="Update Check",
        border_style="magenta"
    ))
    
    with Progress() as progress:
        task = progress.add_task("[cyan]Checking for updates...", total=100)
        
        try:
            # Get latest release info
            response = requests.get(f"{GITHUB_REPO}/releases/latest")
            response.raise_for_status()
            latest = response.json()
            
            progress.update(task, advance=50)
            
            latest_version = latest["tag_name"].lstrip("v")
            needs_update = compare_versions(CURRENT_VERSION, latest_version)
            
            update_info = {
                "current_version": CURRENT_VERSION,
                "latest_version": latest_version,
                "last_checked": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "update_available": needs_update
            }
            
            with open(UPDATE_CHECK_FILE, "w") as f:
                json.dump(update_info, f, indent=2)
            
            progress.update(task, advance=50)
            
            if needs_update:
                console.print(f"[bold yellow][{datetime.now().strftime('%H:%M:%S')}] Update available: v{latest_version}[/]")
                console.print("\nChangelog:")
                console.print(latest["body"])
            else:
                console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] You're running the latest version![/]")
            
            return needs_update
        except Exception as e:
            log_error(f"Update check failed: {e}")
            console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] ERROR: Failed to check for updates[/]")
            return False
        finally:
            time.sleep(3)

def compare_versions(current, latest):
    """Compare version numbers."""
    current_parts = [int(x) for x in current.split(".")]
    latest_parts = [int(x) for x in latest.split(".")]
    
    for i in range(max(len(current_parts), len(latest_parts))):
        current_part = current_parts[i] if i < len(current_parts) else 0
        latest_part = latest_parts[i] if i < len(latest_parts) else 0
        
        if latest_part > current_part:
            return True
        elif current_part > latest_part:
            return False
    
    return False

def download_update():
    """Download and apply update."""
    clear_screen()
    console.print(Panel(
        f"[bold magenta]=== DOWNLOADING UPDATE ===[/]\n"
        f"[bold cyan][Started at {datetime.now().strftime('%H:%M:%S')}][/]",
        title="Update Download",
        border_style="magenta"
    ))
    
    with Progress() as progress:
        task = progress.add_task("[cyan]Downloading update...", total=100)
        
        try:
            # Get latest release assets
            response = requests.get(f"{GITHUB_REPO}/releases/latest")
            response.raise_for_status()
            latest = response.json()
            
            progress.update(task, advance=30)
            
            # Download new version
            asset_url = latest["assets"][0]["browser_download_url"]
            response = requests.get(asset_url)
            response.raise_for_status()
            
            progress.update(task, advance=40)
            
            # Save new version
            with open("update.zip", "wb") as f:
                f.write(response.content)
            
            progress.update(task, advance=30)
            
            console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] Update downloaded successfully![/]")
            console.print("[bold yellow]Please restart the application to apply the update.[/]")
            return True
        except Exception as e:
            log_error(f"Update download failed: {e}")
            console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] ERROR: Failed to download update[/]")
            return False
        finally:
            time.sleep(3)