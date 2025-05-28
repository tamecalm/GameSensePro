"""
Auto-update feature utilities for the application.
"""

import json
import os
import zipfile
import shutil
import requests
import time
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.prompt import Confirm

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
            
            # Get latest release info with retry
            for attempt in range(3):
                try:
                    response = requests.get(f"{GITHUB_REPO}/releases/latest", headers=headers, timeout=10)
                    response.raise_for_status()
                    break
                except requests.exceptions.RequestException as e:
                    if attempt == 2:
                        raise e
                    time.sleep(2)
            
            latest = response.json()
            progress.update(task, advance=50)
            
            latest_version = latest["tag_name"].lstrip("v")
            needs_update, is_equal = compare_versions(CURRENT_VERSION, latest_version)
            
            update_info = {
                "current_version": CURRENT_VERSION,
                "latest_version": latest_version,
                "last_checked": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "update_available": needs_update
            }
            
            # Ensure directory exists for UPDATE_CHECK_FILE
            os.makedirs(os.path.dirname(UPDATE_CHECK_FILE), exist_ok=True)
            with open(UPDATE_CHECK_FILE, "w") as f:
                json.dump(update_info, f, indent=2)
            
            progress.update(task, advance=50)
            
            if needs_update:
                # Display shortened changelog if too long
                changelog = latest.get("body", "No changelog provided.")
                max_length = 200
                max_lines = 3
                lines = changelog.splitlines()
                if len(changelog) > max_length or len(lines) > max_lines:
                    short_changelog = "\n".join(lines[:max_lines])[:max_length] + "..."
                    console.print(f"[bold yellow][{datetime.now().strftime('%H:%M:%S')}] Update available: v{latest_version}[/]")
                    console.print("\nChangelog (shortened):")
                    console.print(short_changelog)
                    if Confirm.ask("[bold yellow]Would you like to view the full changelog?[/]"):
                        console.print("\nFull Changelog:")
                        console.print(changelog)
                else:
                    console.print(f"[bold yellow][{datetime.now().strftime('%H:%M:%S')}] Update available: v{latest_version}[/]")
                    console.print("\nChangelog:")
                    console.print(changelog)
                
                # Ask user if they want to update
                if Confirm.ask("\n[bold yellow]Would you like to download and install the update?[/]"):
                    if download_and_apply_update(latest):
                        console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] Update installed successfully! Please restart the application.[/]")
                        return True
                    else:
                        console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] Failed to install update. Please try again later.[/]")
                else:
                    console.print(f"[bold yellow][{datetime.now().strftime('%H:%M:%S')}] Update skipped. You can check for updates again later.[/]")
            else:
                console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] You're running the latest version (v{latest_version})!{' (same as current)' if is_equal else ''}[/]")
            
            return False
        except requests.exceptions.HTTPError as e:
            log_error(f"Update check failed: HTTP {e.response.status_code} - {e}")
            console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] ERROR: Failed to check for updates: {e}[/]")
            return False
        except Exception as e:
            log_error(f"Update check failed: {e}")
            console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] ERROR: Failed to check for updates: {e}[/]")
            return False
        finally:
            time.sleep(3)

def compare_versions(current, latest):
    """Compare version numbers, handling non-numeric tags."""
    try:
        # Clean and split version strings
        current_clean = current.lstrip("v")
        latest_clean = latest.lstrip("v")
        current_parts = [int(x) for x in current_clean.split(".") if x.isdigit()]
        latest_parts = [int(x) for x in latest_clean.split(".") if x.isdigit()]
        
        # Pad shorter version with zeros
        max_len = max(len(current_parts), len(latest_parts))
        current_parts.extend([0] * (max_len - len(current_parts)))
        latest_parts.extend([0] * (max_len - len(latest_parts)))
        
        for i in range(max_len):
            if latest_parts[i] > current_parts[i]:
                return True, False  # Update needed, not equal
            elif current_parts[i] > latest_parts[i]:
                return False, False  # No update, not equal
        return False, True  # No update, versions equal
    except ValueError as e:
        log_error(f"Version comparison failed: {e}")
        console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] ERROR: Invalid version format: current={current}, latest={latest}[/]")
        return False, False

def download_and_apply_update(latest):
    """Download and apply update."""
    clear_screen()
    console.print(Panel(
        f"[bold magenta]=== DOWNLOADING AND INSTALLING UPDATE ===[/]\n"
        f"[bold cyan][Started at {datetime.now().strftime('%H:%M:%S')}][/]",
        title="Update Download",
        border_style="magenta"
    ))
    
    with Progress() as progress:
        task = progress.add_task("[cyan]Processing update...", total=100)
        
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
            
            # Save the zip file
            update_file = "update.zip"
            with open(update_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            progress.update(task, advance=40)
            
            # Apply the update
            try:
                # Extract to a temporary directory
                temp_dir = "update_temp"
                os.makedirs(temp_dir, exist_ok=True)
                with zipfile.ZipFile(update_file, "r") as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Move files to current directory (customize based on your app structure)
                # Assumes zip contains a folder like "GameSensePro-1.0.4"
                extracted_folder = os.path.join(temp_dir, os.listdir(temp_dir)[0])
                for item in os.listdir(extracted_folder):
                    src = os.path.join(extracted_folder, item)
                    dst = os.path.join(".", item)
                    if os.path.isdir(src):
                        shutil.copytree(src, dst, dirs_exist_ok=True)
                    else:
                        shutil.copy2(src, dst)
                
                progress.update(task, advance=20)
                
                # Clean up
                shutil.rmtree(temp_dir)
                os.remove(update_file)
                console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] Cleaned up temporary files[/]")
                
                progress.update(task, advance=10)
                return True
            except Exception as e:
                log_error(f"Failed to apply update: {e}")
                console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] ERROR: Failed to apply update: {e}[/]")
                return False
        except requests.exceptions.HTTPError as e:
            log_error(f"Update download failed: HTTP {e.response.status_code} - {e}")
            console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] ERROR: Failed to download update: {e}[/]")
            return False
        except Exception as e:
            log_error(f"Update download failed: {e}")
            console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] ERROR: Failed to download update: {e}[/]")
            return False
        finally:
            # Clean up if update failed
            try:
                if os.path.exists("update.zip"):
                    os.remove("update.zip")
                if os.path.exists("update_temp"):
                    shutil.rmtree("update_temp")
            except:
                pass
            time.sleep(3)
