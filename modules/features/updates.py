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

from modules.utils.constants import GITHUB_REPO, UPDATE_CHECK_FILE, get_current_version
from modules.utils.logger import log_error
from modules.ui.display import clear_screen

console = Console()

def check_for_updates():
    """Check for available updates."""
    clear_screen()
    current_version = get_current_version()
    console.print(Panel(
        f"[bold magenta]=== CHECKING FOR UPDATES ===[/]\n"
        f"[bold cyan][Started at {datetime.now().strftime('%H:%M:%S')}][/]\n"
        f"Current version: {current_version}",
        title="Update Check",
        border_style="magenta"
    ))
    
    try:
        headers = {
            "User-Agent": "GameSensePro/1.0.0",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Run progress bar for update check
        with Progress() as progress:
            task = progress.add_task("[cyan]Checking for updates...", total=100)
            
            # Simulate real-time checking
            progress.update(task, advance=10)
            time.sleep(0.3)
            
            # Get latest release info with retry
            for attempt in range(3):
                try:
                    response = requests.get(f"{GITHUB_REPO}/releases/latest", headers=headers, timeout=10)
                    response.raise_for_status()
                    break
                except requests.exceptions.RequestException as e:
                    if attempt == 2:
                        raise e
                    progress.update(task, advance=10)
                    time.sleep(1)
            
            latest = response.json()
            progress.update(task, advance=30)
            
            latest_version = latest["tag_name"].lstrip("v")
            needs_update, is_equal = compare_versions(current_version, latest_version)
            progress.update(task, advance=20)
            
            # Validate UPDATE_CHECK_FILE
            update_file = UPDATE_CHECK_FILE if UPDATE_CHECK_FILE else "./update_info.json"
            if not update_file:
                raise ValueError("UPDATE_CHECK_FILE is empty or invalid")
            
            # Save update info
            update_info = {
                "current_version": current_version,
                "latest_version": latest_version,
                "last_checked": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "update_available": needs_update
            }
            
            update_dir = os.path.dirname(update_file) or "."
            os.makedirs(update_dir, exist_ok=True)
            with open(update_file, "w", encoding="utf-8") as f:
                json.dump(update_info, f, indent=2)
            
            progress.update(task, advance=30)
        
        # Display changelog and prompt after progress bar closes
        if needs_update:
            # Display changelog
            changelog = latest.get("body", "No changelog provided.")
            max_length = 200
            max_lines = 3
            lines = changelog.splitlines()
            if len(changelog) > max_length or len(lines) > max_lines:
                short_changelog = "\n".join(lines[:max_lines])[:max_length] + "..."
                console.print(f"[bold yellow][{datetime.now().strftime('%H:%M:%S')}] Update available: v{latest_version}[/]")
                console.print("\nChangelog (shortened):")
                console.print(short_changelog)
                try:
                    if Confirm.ask("[bold yellow]Would you like to view the full changelog?[/]"):
                        console.print("\nFull Changelog:")
                        console.print(changelog)
                except Exception as e:
                    log_error(f"Changelog prompt failed: {e}")
                    console.print(f"[bold yellow][{datetime.now().strftime('%H:%M:%S')}] WARNING: Unable to show changelog prompt, proceeding with update prompt[/]")
            else:
                console.print(f"[bold yellow][{datetime.now().strftime('%H:%M:%S')}] Update available: v{latest_version}[/]")
                console.print("\nChangelog:")
                console.print(changelog)
            
            # Prompt for update
            try:
                if Confirm.ask("\n[bold yellow]Would you like to download and install the update?[/]"):
                    clear_screen()
                    if download_and_apply_update(latest):
                        console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] Update installed successfully! Please restart the application.[/]")
                        return True
                    else:
                        console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] Failed to install update. Please try again later.[/]")
                else:
                    console.print(f"[bold yellow][{datetime.now().strftime('%H:%M:%S')}] Update skipped. You can check for updates again later.[/]")
            except Exception as e:
                log_error(f"Update prompt failed: {e}")
                console.print(f"[bold yellow][{datetime.now().strftime('%H:%M:%S')}] WARNING: Unable to show update prompt, skipping update[/]")
        else:
            console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] You're running the latest version (v{latest_version})!{' (same as current)' if is_equal else ''}[/]")
        
        return False
    except requests.exceptions.HTTPError as e:
        log_error(f"Update check failed: HTTP {e.response.status_code} - {e}")
        console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] ERROR: Failed to check for updates: {e}[/]")
        return False
    except (OSError, ValueError) as e:
        log_error(f"Failed to save update info: {e}")
        console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] ERROR: Failed to save update info: {e}[/]")
        return False
    except Exception as e:
        log_error(f"Update check failed: {e}")
        console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] ERROR: Failed to check for updates: {e}[/]")
        return False
    finally:
        console.input("Press Enter to return to menu...")

def compare_versions(current, latest):
    """Compare version numbers, handling non-numeric tags."""
    try:
        current_clean = current.lstrip("v")
        latest_clean = latest.lstrip("v")
        current_parts = [int(x) for x in current_clean.split(".") if x.isdigit()]
        latest_parts = [int(x) for x in latest_clean.split(".") if x.isdigit()]
        
        max_len = max(len(current_parts), len(latest_parts))
        current_parts.extend([0] * (max_len - len(current_parts)))
        latest_parts.extend([0] * (max_len - len(latest_parts)))
        
        for i in range(max_len):
            if latest_parts[i] > current_parts[i]:
                return True, False
            elif current_parts[i] > latest_parts[i]:
                return False, False
        return False, True
    except ValueError as e:
        log_error(f"Version comparison failed: {e}")
        console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] ERROR: Invalid version format: current={current}, latest={latest}[/]")
        return False, False

def download_and_apply_update(latest):
    """Download and apply update using GitHub's auto-generated source code zip."""
    console.print(Panel(
        f"[bold magenta]=== DOWNLOADING AND INSTALLING UPDATE ===[/]\n"
        f"[bold cyan][Started at {datetime.now().strftime('%H:%M:%S')}][/]\n"
        f"Installing version: {latest['tag_name'].lstrip('v')}",
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
            
            # Use the auto-generated source code zip
            zipball_url = latest.get("zipball_url")
            latest_version = latest["tag_name"].lstrip("v")
            if not zipball_url:
                log_error("No zipball_url found in release")
                console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] ERROR: No update package found[/]")
                return False
            
            progress.update(task, advance=30)
            
            # Download the zip file
            response = requests.get(
                zipball_url,
                headers=headers,
                stream=True,
                timeout=30
            )
            response.raise_for_status()
            
            update_file = "update.zip"
            with open(update_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            progress.update(task, advance=40)
            
            # Apply the update
            try:
                temp_dir = "update_temp"
                os.makedirs(temp_dir, exist_ok=True)
                with zipfile.ZipFile(update_file, "r") as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Find the extracted folder (e.g., GameSensePro-1.0.10-xxxx)
                extracted_folder = os.path.join(temp_dir, os.listdir(temp_dir)[0])
                for item in os.listdir(extracted_folder):
                    src = os.path.join(extracted_folder, item)
                    dst = os.path.join(".", item)
                    if os.path.isdir(src):
                        shutil.copytree(src, dst, dirs_exist_ok=True)
                    else:
                        shutil.copy2(src, dst)
                
                progress.update(task, advance=20)
                
                # Update UPDATE_CHECK_FILE with new current_version
                update_dir = os.path.dirname(UPDATE_CHECK_FILE) or "."
                os.makedirs(update_dir, exist_ok=True)
                update_info = {
                    "current_version": latest_version,
                    "latest_version": latest_version,
                    "last_checked": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "update_available": False
                }
                with open(UPDATE_CHECK_FILE, "w", encoding="utf-8") as f:
                    json.dump(update_info, f, indent=2)
                
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
            try:
                if os.path.exists("update.zip"):
                    os.remove("update.zip")
                if os.path.exists("update_temp"):
                    shutil.rmtree("update_temp")
            except:
                pass
            console.input("Press Enter to return to menu...")