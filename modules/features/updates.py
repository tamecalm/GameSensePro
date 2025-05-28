"""
Auto-update feature utilities for the application.
"""

import json
import os
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
            headers = {
                "User-Agent": "GameSensePro/1.0.0",
                "Accept": "application/vnd.github.v3+json"
            }
            
            # Get latest release info
            response = requests.get(f"{GITHUB_REPO}/releases/latest", headers=headers, timeout=10)
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
                
                if download_update(latest):
                    return True
            else:
                console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] You're running the latest version![/]")
            
            return False
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

def download_update(latest):
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
            headers = {
                "User-Agent": "GameSensePro/1.0.0",
                "Accept": "application/vnd.github.v3+json"
            }
            
            # Find the source code zip asset
            zip_asset = next(
                (asset for asset in latest["assets"] if asset["name"].endswith(".zip")),
                None
            )
            
            if not zip_asset:
                log_error("No zip asset found in release")
                console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] ERROR: No update package found[/]")
                return False
            
            progress.update(task, advance=30)
            
            # Download the zip file
            response = requests.get(
                zip_asset["browser_download_url"],
                headers=headers,
                stream=True,
                timeout=30
            )
            response.raise_for_status()
            
            progress.update(task, advance=40)
            
            # Save the zip file
            with open("update.zip", "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            progress.update(task, advance=30)
            
            console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] Update downloaded successfully![/]")
            
            # Clean up the downloaded file
            try:
                os.remove("update.zip")
                console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] Cleaned up temporary files[/]")
            except Exception as e:
                log_error(f"Failed to clean up update file: {e}")
                console.print(f"[bold yellow][{datetime.now().strftime('%H:%M:%S')}] WARNING: Failed to clean up temporary files[/]")
            
            return True
        except Exception as e:
            log_error(f"Update download failed: {e}")
            console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] ERROR: Failed to download update[/]")
            
            # Attempt to clean up if download failed
            try:
                if os.path.exists("update.zip"):
                    os.remove("update.zip")
            except:
                pass
            
            return False
        finally:
            time.sleep(3)