"""
Gyroscope utilities for the application.
"""

import subprocess
import json
import time
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt, FloatPrompt

from modules.ui.display import clear_screen
from modules.utils.logger import log_error

console = Console()

def check_and_install_termux_api():
    """
    Checks if Termux:API is installed and permissions are granted, installs if needed.
    
    Returns:
        bool: True if Termux:API is available and permissions are granted, False otherwise.
    """
    try:
        # Check if termux-sensor is available
        result = subprocess.run(
            ["termux-sensor", "-h"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] Success: Termux:API is installed[/]")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        console.print(f"[bold yellow][{datetime.now().strftime('%H:%M:%S')}] WARNING: Termux:API not found. Installing...[/]")
        
        try:
            # Install Termux:API
            subprocess.run(["pkg", "install", "termux-api", "-y"], check=True)
            console.print(f"[bold yellow][{datetime.now().strftime('%H:%M:%S')}] Installed Termux:API. Please grant sensor permissions.[/]")
            subprocess.run(["termux-toast", "Please grant sensor permissions"], check=True)
            
            # Retry checking permissions
            result = subprocess.run(
                ["termux-sensor", "-h"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] Success: Termux:API ready[/]")
            return True
        except subprocess.CalledProcessError as e:
            log_error(f"Failed to install Termux:API: {e}")
            console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] ERROR: Failed to install Termux:API. Please install manually using 'pkg install termux-api'.[/]")
            return False
        except FileNotFoundError as e:
            log_error(f"Termux environment not properly set up: {e}")
            console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] ERROR: Termux environment issue. Ensure Termux is installed correctly.[/]")
            return False

def check_gyro_availability():
    """
    Checks if a gyroscope sensor is available on the device.
    
    Returns:
        bool: True if gyroscope is available, False otherwise.
    """
    try:
        # Check via dumpsys
        output = subprocess.getoutput("dumpsys sensorservice")
        if "gyroscope" in output.lower():
            console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] Success: Gyroscope sensor detected via dumpsys[/]")
            return True
        
        # Fallback: check termux-sensor list
        if check_and_install_termux_api():
            output = subprocess.getoutput("termux-sensor -l")
            if "gyroscope" in output.lower():
                console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] Success: Gyroscope sensor detected via termux-sensor[/]")
                return True
        
        console.print(f"[bold yellow][{datetime.now().strftime('%H:%M:%S')}] WARNING: No gyroscope sensor detected[/]")
        return False
    except Exception as e:
        log_error(f"Failed to check gyro availability: {e}")
        console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] ERROR: Failed to check gyro availability: {e}[/]")
        return False

def get_gyro_data():
    """
    Gets gyroscope data or prompts user for manual range input.
    
    Returns:
        float: Gyroscope range (radians/second) or None if unavailable.
    """
    if not check_and_install_termux_api():
        console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] ERROR: Termux:API unavailable. Cannot access gyroscope.[/]")
        return None
    
    has_gyro = check_gyro_availability()
    if not has_gyro:
        console.print(f"[bold yellow][{datetime.now().strftime('%H:%M:%S')}] WARNING: Gyroscope not detected automatically.[/]")
    
    clear_screen()
    console.print(Panel(
        f"[bold magenta]=== GYRO CALIBRATION ===[/]\n"
        f"[bold cyan][Started at {datetime.now().strftime('%H:%M:%S')}][/]\n"
        "Please rotate your device in all directions (pitch, roll, yaw) for 5 seconds to calibrate the gyroscope.",
        title="Gyro Calibration",
        border_style="magenta"
    ))
    
    # Calibration period
    time.sleep(5)
    
    try:
        output = subprocess.getoutput("termux-sensor -s GYROSCOPE -n 1 -d 100")
        data = json.loads(output)
        
        if "GYROSCOPE" in data and data["GYROSCOPE"] and len(data["GYROSCOPE"]) > 0:
            values = data["GYROSCOPE"][0]["values"]
            if len(values) >= 3 and any(abs(v) > 0.1 for v in values):
                console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] Success: Gyroscope detected with values: {values}[/]")
                time.sleep(3)
                return max(abs(min(values)), abs(max(values)))
        
        console.print(f"[bold yellow][{datetime.now().strftime('%H:%M:%S')}] WARNING: No valid gyroscope data detected[/]")
    except json.JSONDecodeError as e:
        log_error(f"Invalid gyroscope data format: {e}")
        console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] ERROR: Invalid gyroscope data format: {e}[/]")
    except subprocess.CalledProcessError as e:
        log_error(f"Failed to fetch gyro data: {e}")
        console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] ERROR: Failed to fetch gyro data: {e}[/]")
    except Exception as e:
        log_error(f"Unexpected error fetching gyro data: {e}")
        console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] ERROR: Unexpected error: {e}[/]")
    
    # Prompt user for manual input
    clear_screen()
    console.print(Panel(
        f"[bold magenta]=== GYRO CONFIRMATION ===[/]\n"
        f"[bold cyan][Continued at {datetime.now().strftime('%H:%M:%S')}][/]\n"
        "Automatic gyroscope detection failed. Does your device have a working gyroscope?\n1. Yes\n2. No\n\n"
        "To determine your device's gyroscope range, we recommend:\n"
        "1. Install 'Sensor Kinetics' from Google Play:\n"
        "   - Open the app, select the gyroscope sensor.\n"
        "   - Rotate your device in all directions and note the maximum angular velocity (in radians/second).\n"
        "   - Enter this value below.\n"
        "2. Alternatively, connect your device to a PC and run:\n"
        "   - adb shell dumpsys sensorservice\n"
        "   - Look for the gyroscope sensor and its maximum range (in radians/second).\n"
        "   - Enter this value below.",
        title="Gyro Confirmation",
        border_style="magenta"
    ))
    
    choice = IntPrompt.ask("[bold yellow]Select (1-2)[/]", choices=["1", "2"], default=2)
    
    if choice == 1:
        console.print(f"[bold yellow][{datetime.now().strftime('%H:%M:%S')}] Please enter your device's gyroscope range (in radians/second).[/]")
        console.print(f"[bold yellow]Typical range is 5.0 to 20.0. Use Sensor Kinetics or adb to confirm.[/]")
        range_value = FloatPrompt.ask("[bold yellow]Enter gyro range[/]", default=10.0)
        
        if range_value <= 0:
            console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] ERROR: Gyro range must be positive[/]")
            time.sleep(3)
            return None
        
        console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] Success: Using user-provided gyro range: {range_value}[/]")
        time.sleep(3)
        return range_value
    
    console.print(f"[bold yellow][{datetime.now().strftime('%H:%M:%S')}] WARNING: Gyroscope unavailable[/]")
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