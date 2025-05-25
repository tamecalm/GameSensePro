"""
Device information utilities for the application.
"""

import subprocess
import re
import math
import time
from datetime import datetime
import os
import json
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.progress import Progress
import requests
from bs4 import BeautifulSoup

from modules.ui.display import clear_screen
from modules.device.gyro import get_gyro_data, test_gyro
from modules.utils.constants import DEVICE_FILE
from modules.utils.logger import log_error
from modules.utils.session import load_session, save_session

console = Console()

def normalize_device_name(brand, model):
    """
    Normalizes device name for display.
    
    Args:
        brand (str): The device brand.
        model (str): The device model.
        
    Returns:
        str: The normalized device name.
    """
    try:
        normalized_model = dynamically_map_device(model)
        device_name = f"{brand} {normalized_model}".strip()
        if device_name.lower().startswith("redmi redmi"):
            device_name = device_name[len("redmi "):]
        return device_name
    except Exception:
        return f"{brand} {model}".strip()

def dynamically_map_device(model):
    """
    Maps device model to full device name using a mapping file or GSMArena.
    
    Args:
        model (str): The device model.
        
    Returns:
        str: The mapped device name or the model if mapping fails.
    """
    from modules.utils.constants import DEVICE_MAPPING_FILE
    
    with open(DEVICE_MAPPING_FILE, "r") as f:
        mapping = json.load(f)
    
    # Return cached mapping if available and not expired
    if model in mapping and (datetime.now().timestamp() - mapping[model]["timestamp"]) < 30 * 24 * 3600:
        return mapping[model]["name"]
    
    console.print(f"[bold cyan][{datetime.now().strftime('%H:%M:%S')}] DEBUG: Model {model} not in cache or expired. Searching GSMArena...[/]")
    
    with Progress() as progress:
        task = progress.add_task("[cyan]Fetching device data...", total=100)
        progress.update(task, advance=20)
        
        try:
            search_url = f"https://www.gsmarena.com/results.php3?sQuickSearch=yes&sName={model}"
            headers = {"User-Agent": "Mozilla/5.0 (Linux; Android 12; SM-G991B)"}
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            progress.update(task, advance=50)
            
            soup = BeautifulSoup(response.text, "html.parser")
            device_link = soup.find("div", class_="makers").find("a")
            
            if not device_link:
                log_error(f"Could not find device for model {model}")
                console.print(f"[bold yellow][{datetime.now().strftime('%H:%M:%S')}] WARNING: Could not find device for model {model}[/]")
                return model
            
            device_name = device_link.find("span").text.strip()
            mapping[model] = {"name": device_name, "timestamp": datetime.now().timestamp()}
            
            with open(DEVICE_MAPPING_FILE, "w") as f:
                json.dump(mapping, f, indent=2)
            
            console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] Success: Cached {model} -> {device_name}[/]")
            progress.update(task, advance=100)
            time.sleep(3)
            
            return device_name
        except Exception as e:
            log_error(f"Failed to map device: {e}")
            console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] ERROR: Failed to map device - {e}[/]")
            return model

def fetch_resolution_from_gsmarena(brand, model):
    """
    Fetches device resolution from GSMArena.
    
    Args:
        brand (str): The device brand.
        model (str): The device model.
        
    Returns:
        str: The device resolution or None if fetching fails.
    """
    with Progress() as progress:
        task = progress.add_task("[cyan]Fetching resolution...", total=100)
        progress.update(task, advance=20)
        
        try:
            device_name = normalize_device_name(brand, model)
            console.print(f"[bold cyan][{datetime.now().strftime('%H:%M:%S')}] DEBUG: Searching GSMArena for {device_name}[/]")
            
            search_url = f"https://www.gsmarena.com/results.php3?sQuickSearch=yes&sName={device_name.replace(' ', '+')}"
            headers = {"User-Agent": "Mozilla/5.0 (Linux; Android 12; SM-G991B)"}
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            progress.update(task, advance=50)
            
            soup = BeautifulSoup(response.text, "html.parser")
            device_url_pattern = f"{brand.lower().replace(' ', '_')}_.*\\.php"
            links = soup.find_all("a", href=True)
            device_url = next((link['href'] for link in links if re.search(device_url_pattern, link['href'])), None)
            
            if not device_url:
                log_error(f"Could not find device page for {device_name}")
                console.print(f"[bold yellow][{datetime.now().strftime('%H:%M:%S')}] WARNING: Could not find device page[/]")
                return None
            
            device_page_url = f"https://www.gsmarena.com/{device_url}"
            response = requests.get(device_page_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            display_section = soup.find("div", id="specs-list")
            
            if display_section:
                for table in display_section.find_all("table"):
                    if "Display" in table.text:
                        for row in table.find_all("tr"):
                            cells = row.find_all("td")
                            if len(cells) >= 2 and "Resolution" in cells[0].text:
                                resolution_text = cells[1].text.strip()
                                res_match = re.search(r'(\d+)\s*x\s*(\d+)', resolution_text)
                                
                                if res_match:
                                    console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] Success: Resolution via GSMArena: {res_match.group(1)}x{res_match.group(2)}[/]")
                                    progress.update(task, advance=100)
                                    return f"{res_match.group(1)}x{res_match.group(2)}"
            
            log_error(f"Resolution not found for {device_name}")
            console.print(f"[bold yellow][{datetime.now().strftime('%H:%M:%S')}] WARNING: Resolution not found[/]")
            return None
        except Exception as e:
            log_error(f"GSMArena error: {e}")
            console.print(f"[bold yellow][{datetime.now().strftime('%H:%M:%S')}] WARNING: GSMArena error - {e}[/]")
            return None
        finally:
            time.sleep(3)

def get_manual_resolution():
    """
    Gets resolution input manually from the user.
    
    Returns:
        str: The user-provided resolution.
    """
    clear_screen()
    console.print(Panel(
        f"[bold magenta]=== MANUAL RESOLUTION INPUT ===[/]\n"
        f"[bold cyan][Started at {datetime.now().strftime('%H:%M:%S')}][/]\n"
        "[yellow]All methods to detect resolution failed. Please input your device's resolution manually.[/]\n"
        "[yellow]Format: WIDTHxHEIGHT (e.g., 1080x2400)[/]",
        title="Manual Input",
        border_style="magenta"
    ))
    
    session = load_session()
    
    while True:
        resolution = Prompt.ask("[bold yellow]Enter resolution[/]").strip()
        if re.match(r'^\d+x\d+$', resolution):
            session["resolution"] = resolution
            save_session(session)
            console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] Success: Manual resolution: {resolution}[/]")
            time.sleep(3)
            return resolution
        console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] ERROR: Invalid format[/]")

def get_manual_dpi():
    """
    Gets DPI input manually from the user.
    
    Returns:
        int: The user-provided DPI.
    """
    clear_screen()
    console.print(Panel(
        f"[bold magenta]=== MANUAL DPI INPUT ===[/]\n"
        f"[bold cyan][Started at {datetime.now().strftime('%H:%M:%S')}][/]\n"
        "[yellow]All methods to detect DPI failed. Please input your device's DPI manually.[/]\n"
        "[yellow]Example: 440[/]",
        title="Manual Input",
        border_style="magenta"
    ))
    
    session = load_session()
    
    while True:
        dpi = IntPrompt.ask("[bold yellow]Enter DPI[/]", default=440)
        if dpi > 0:
            session["dpi"] = dpi
            save_session(session)
            console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] Success: Manual DPI: {dpi}[/]")
            time.sleep(3)
            return dpi
        console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] ERROR: DPI must be positive[/]")

def get_manual_refresh_rate():
    """
    Gets refresh rate input manually from the user.
    
    Returns:
        float: The user-provided refresh rate.
    """
    clear_screen()
    console.print(Panel(
        f"[bold magenta]=== MANUAL REFRESH RATE INPUT ===[/]\n"
        f"[bold cyan][Started at {datetime.now().strftime('%H:%M:%S')}][/]\n"
        "[yellow]All methods to detect refresh rate failed. Please input your device's refresh rate manually.[/]\n"
        "[yellow]Example: 120[/]",
        title="Manual Input",
        border_style="magenta"
    ))
    
    session = load_session()
    
    while True:
        refresh_rate = Prompt.ask("[bold yellow]Enter refresh rate (in Hz)[/]").strip()
        try:
            refresh_rate = float(refresh_rate)
            if refresh_rate > 0:
                session["refresh_rate"] = refresh_rate
                save_session(session)
                console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] Success: Manual refresh rate: {refresh_rate}[/]")
                time.sleep(3)
                return refresh_rate
            console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] ERROR: Refresh rate must be positive[/]")
        except ValueError:
            console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] ERROR: Invalid input[/]")

def get_device_info():
    """
    Gathers comprehensive device information.
    
    Returns:
        dict: Device information including model, brand, resolution, DPI, etc.
    """
    clear_screen()
    console.print(Panel(
        f"[bold magenta]=== GATHERING DEVICE INFORMATION ===[/]\n"
        f"[bold cyan][Started at {datetime.now().strftime('%H:%M:%S')}][/]",
        title="Device Info",
        border_style="magenta"
    ))
    
    session = load_session()
    
    try:
        # Get device model
        model = session.get("model") or subprocess.getoutput("getprop ro.product.model").strip()
        if not model:
            raise ValueError("Device model not found")
        session["model"] = model
        
        # Get device brand
        brand = session.get("brand") or subprocess.getoutput("getprop ro.product.brand").strip()
        if not brand:
            raise ValueError("Device brand not found")
        session["brand"] = brand
        
        # Get Android version
        android = session.get("android") or subprocess.getoutput("getprop ro.build.version.release").strip()
        if not android:
            raise ValueError("Android version not found")
        session["android"] = android
        
        # Get screen resolution
        resolution = session.get("resolution")
        if not resolution:
            # Try wm size
            res_output = subprocess.getoutput("wm size").strip()
            res_match = re.search(r'(\d+)x(\d+)', res_output)
            
            if res_match:
                resolution = f"{res_match.group(1)}x{res_match.group(2)}"
                console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] Success: Resolution via wm size: {resolution}[/]")
            else:
                # Try GSMArena
                console.print(f"[bold yellow][{datetime.now().strftime('%H:%M:%S')}] WARNING: wm size failed. Trying GSMArena...[/]")
                resolution = fetch_resolution_from_gsmarena(brand, model)
                
                if not resolution:
                    # Try dumpsys
                    console.print(f"[bold yellow][{datetime.now().strftime('%H:%M:%S')}] WARNING: GSMArena failed. Trying dumpsys...[/]")
                    res_output = subprocess.getoutput("dumpsys display | grep mBaseDisplayInfo").strip()
                    res_match = re.search(r'width=(\d+), height=(\d+)', res_output)
                    
                    if res_match:
                        resolution = f"{res_match.group(1)}x{res_match.group(2)}"
                        console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] Success: Resolution via dumpsys: {resolution}[/]")
                    else:
                        # Get manual input
                        resolution = get_manual_resolution()
            
            session["resolution"] = resolution
        
        # Get DPI
        dpi = session.get("dpi")
        if not dpi:
            # Try wm density
            dpi_output = subprocess.getoutput("wm density").strip()
            dpi_match = re.search(r'Physical density: (\d+)', dpi_output)
            
            if dpi_match:
                dpi = int(dpi_match.group(1))
                console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] Success: DPI via wm density: {dpi}[/]")
            else:
                # Try getprop
                console.print(f"[bold yellow][{datetime.now().strftime('%H:%M:%S')}] WARNING: wm density failed. Trying getprop...[/]")
                dpi_output = subprocess.getoutput("getprop ro.sf.lcd_density").strip()
                
                if dpi_output.isdigit():
                    dpi = int(dpi_output)
                    console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] Success: DPI via getprop: {dpi}[/]")
                else:
                    # Try dumpsys
                    console.print(f"[bold yellow][{datetime.now().strftime('%H:%M:%S')}] WARNING: getprop failed. Trying dumpsys...[/]")
                    dpi_output = subprocess.getoutput("dumpsys display | grep density").strip()
                    dpi_match = re.search(r'density (\d+)', dpi_output)
                    
                    if dpi_match:
                        dpi = int(dpi_match.group(1))
                        console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] Success: DPI via dumpsys: {dpi}[/]")
                    else:
                        # Get manual input
                        dpi = get_manual_dpi()
            
            session["dpi"] = dpi
        
        # Get refresh rate
        refresh_rate = session.get("refresh_rate")
        if not refresh_rate:
            # Try dumpsys
            refresh_output = subprocess.getoutput("dumpsys display | grep refreshRate").strip()
            refresh_match = re.search(r'refreshRate=(\d+\.\d+)', refresh_output)
            
            if refresh_match:
                refresh_rate = float(refresh_match.group(1))
                console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] Success: Refresh rate via dumpsys: {refresh_rate}[/]")
            else:
                # Try alternative dumpsys
                console.print(f"[bold yellow][{datetime.now().strftime('%H:%M:%S')}] WARNING: dumpsys refreshRate failed. Trying alternative...[/]")
                refresh_output = subprocess.getoutput("dumpsys display").strip()
                refresh_match = re.search(r'refresh\s*rate:?\s*(\d+\.?\d*)', refresh_output, re.IGNORECASE)
                
                if refresh_match:
                    refresh_rate = float(refresh_match.group(1))
                    console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] Success: Refresh rate via dumpsys alternative: {refresh_rate}[/]")
                else:
                    # Try getprop
                    console.print(f"[bold yellow][{datetime.now().strftime('%H:%M:%S')}] WARNING: dumpsys alternative failed. Trying getprop...[/]")
                    refresh_output = subprocess.getoutput("getprop persist.sys.display.refresh_rate").strip()
                    
                    if refresh_output.replace('.', '', 1).isdigit():
                        refresh_rate = float(refresh_output)
                        console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] Success: Refresh rate via getprop: {refresh_rate}[/]")
                    else:
                        # Get manual input
                        refresh_rate = get_manual_refresh_rate()
            
            session["refresh_rate"] = refresh_rate
        
        # Calculate screen size
        width, height = map(int, resolution.split('x'))
        screen_size = round(math.sqrt(width**2 + height**2) / dpi, 2)
        
        # Get gyro data
        gyro_range = get_gyro_data()
        if gyro_range and test_gyro():
            console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] Success: Gyro test confirmed[/]")
        else:
            gyro_range = None
            console.print(f"[bold yellow][{datetime.now().strftime('%H:%M:%S')}] WARNING: Gyro unavailable or test failed[/]")
        
        # Compile device information
        info = {
            "Device": model,
            "Brand": brand,
            "Android": android,
            "Resolution": resolution,
            "DPI": dpi,
            "RefreshRate": refresh_rate,
            "ScreenSize": screen_size,
            "GyroRange": gyro_range
        }
        
        # Save device information
        with open(DEVICE_FILE, "w") as f:
            for k, v in info.items():
                f.write(f"{k}: {v}\n")
        
        save_session(session)
        console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] Success: Device information saved[/]")
        time.sleep(3)
        
        return info
    except Exception as e:
        log_error(f"Device info error: {e}")
        console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] ERROR: {e}[/]\n"
                     f"[bold red]CRITICAL: Cannot proceed without device information[/]")
        exit(1)