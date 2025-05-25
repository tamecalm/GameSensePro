"""
Gyroscope utilities for the application.
"""

import subprocess
import json
import time
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt

from modules.ui.display import clear_screen
from modules.utils.logger import log_error

console = Console()

def check_and_install_termux_api():
    """
    Checks if Termux:API is installed and installs it if not.
    
    Returns:
        bool: True if Termux:API is available, False otherwise.
    """
    try:
        subprocess.run(["termux-sensor", "-h"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(["termux-toast", "Termux:API is installed"], check=True)
        return True
    except subprocess.CalledProcessError:
        console.print(f"[bold yellow][{datetime.now().strftime('%H:%M:%S')}] WARNING: Termux:API not found. Installing...[/]")
        
        try:
            subprocess.run(["pkg", "install", "termux-api", "-y"], check=True)
            subprocess.run(["termux-toast", "Please grant sensor permissions"], check=True)
            console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] Success: Termux:API installed[/]")
            return True
        except subprocess.CalledProcessError as e:
            log_error(f"Failed to install Termux:API: {e}")
            console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] ERROR: Failed to install Termux:API[/]")
            return False

def check_gyro_availability():
    """
    Checks if gyroscope is available on the device.
    
    Returns:
        bool: True if gyroscope is available, False otherwise.
    """
    try:
        output = subprocess.getoutput("dumpsys sensorservice")
        if "gyroscope" in output.lower():
            console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] Success: Gyroscope sensor detected via dumpsys[/]")
            return True
        return False
    except Exception as e:
        log_error(f"Failed to check gyro availability: {e}")
        return False

def get_gyro_data():
    """
    Gets gyroscope data from the device.
    
    Returns:
        float: Gyroscope range or None if unavailable.
    """
    if not check_and_install_termux_api():
        log_error("Termux:API unavailable")
        console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] ERROR: Termux:API unavailable[/]")
        return None
    
    if not check_gyro_availability():
        log_error("No gyroscope sensor detected via dumpsys")
        console.print(f"[bold yellow][{datetime.now().strftime('%H:%M:%S')}] WARNING: No gyroscope sensor detected[/]")
    
    clear_screen()
    console.print(Panel(
        f"[bold magenta]=== GYRO CALIBRATION ===[/]\n"
        f"[bold cyan][Started at {datetime.now().strftime('%H:%M:%S')}][/]\n"
        "Please rotate your device in all directions for 10 seconds to initialize the gyroscope.",
        title="Gyro Calibration",
        border_style="magenta"
    ))
    
    # Extended initialization
    time.sleep(10)
    
    try:
        output = subprocess.getoutput("termux-sensor -s GYROSCOPE -n 1 -d 100")
        data = json.loads(output)
        
        if "GYROSCOPE" in data and data["GYROSCOPE"] and len(data["GYROSCOPE"]) > 0:
            values = data["GYROSCOPE"][0]["values"]
            
            if len(values) >= 3 and any(abs(v) > 0.1 for v in values):
                console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] Success: Gyroscope detected with values: {values}[/]")
                time.sleep(3)
                return max(abs(min(values)), abs(max(values)))
        
        log_error("No valid gyroscope data")
        console.print(f"[bold yellow][{datetime.now().strftime('%H:%M:%S')}] WARNING: No valid gyroscope data[/]")
    except json.JSONDecodeError as e:
        log_error(f"Invalid gyroscope data format: {e}")
        console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] ERROR: Invalid gyroscope data format[/]")
    except Exception as e:
        log_error(f"Failed to fetch gyro data: {e}")
        console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] ERROR: Failed to fetch gyro data - {e}[/]")
    
    # Manual confirmation
    clear_screen()
    console.print(Panel(
        f"[bold magenta]=== GYRO CONFIRMATION ===[/]\n"
        f"[bold cyan][Continued at {datetime.now().strftime('%H:%M:%S')}][/]\n"
        "Gyroscope detection failed. Does your device have a working gyroscope?\n1. Yes\n2. No",
        title="Gyro Confirmation",
        border_style="magenta"
    ))
    
    choice = IntPrompt.ask("[bold yellow]Select (1-2)[/]", choices=["1", "2"], default=2)
    
    if choice == 1:
        console.print(f"[bold yellow][{datetime.now().strftime('%H:%M:%S')}] WARNING: Assuming gyro is present with default range[/]")
        time.sleep(3)
        return 10.0  # Default range
    
    console.print(f"[bold yellow][{datetime.now().strftime('%H:%M:%S')}] WARNING: Gyro unavailable[/]")
    time.sleep(3)
    return None

def test_gyro():
    """
    Tests if gyroscope is working correctly.
    
    Returns:
        bool: True if gyroscope is working, False otherwise.
    """
    clear_screen()
    console.print(Panel(
        f"[bold magenta]=== GYRO TEST ===[/]\n"
        f"[bold cyan][Started at {datetime.now().strftime('%H:%M:%S')}][/]\n"
        "Tilt your device left and right for 3 seconds.",
        title="Gyro Test",
        border_style="magenta"
    ))
    
    time.sleep(3)
    
    try:
        output = subprocess.getoutput("termux-sensor -s GYROSCOPE -n 1 -d 100")
        data = json.loads(output)
        
        if "GYROSCOPE" in data and data["GYROSCOPE"] and len(data["GYROSCOPE"]) > 0:
            values = data["GYROSCOPE"][0]["values"]
            
            if len(values) >= 3 and any(abs(v) > 0.1 for v in values):
                console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] Success: Gyro test passed[/]")
                time.sleep(3)
                return True
        
        log_error("Gyro test failed: No valid data")
        console.print(f"[bold yellow][{datetime.now().strftime('%H:%M:%S')}] WARNING: Gyro test failed[/]")
        return False
    except Exception as e:
        log_error(f"Gyro test error: {e}")
        console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] ERROR: Gyro test error - {e}[/]")
        return False
    finally:
        time.sleep(3)