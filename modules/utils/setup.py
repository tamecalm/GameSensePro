"""
Setup utilities for the application.
"""

import os
import json
import subprocess
from datetime import datetime
from rich.console import Console

from modules.utils.constants import DATA_DIR, DEVICE_MAPPING_FILE, GAMES_DIR
from modules.utils.logger import log_error

console = Console()

def ensure_data_folder():
    """
    Ensures that the data folder and required files exist.
    Creates initial device mapping if it doesn't exist.
    """
    # Create main data directory
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Create game-specific directories
    for game_dir in GAMES_DIR.values():
        os.makedirs(game_dir, exist_ok=True)
    
    if not os.path.exists(DEVICE_MAPPING_FILE):
        # Initial device mapping
        initial_mapping = {
            "M2101K6G": {"name": "Redmi Note 10 Pro", "timestamp": datetime.now().timestamp()},
            "M2003J15SC": {"name": "Redmi 9", "timestamp": datetime.now().timestamp()},
            "M2010J19SG": {"name": "Redmi 9A", "timestamp": datetime.now().timestamp()},
            "SM-G960F": {"name": "Galaxy S9", "timestamp": datetime.now().timestamp()}
        }
        
        with open(DEVICE_MAPPING_FILE, "w") as f:
            json.dump(initial_mapping, f, indent=2)
        
        console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] Success: Initialized device_mapping.json[/]")

def check_dependencies():
    """
    Checks if required dependencies are installed.
    Installs missing dependencies.
    """
    try:
        # Check if requests and BeautifulSoup are available
        import requests
        from bs4 import BeautifulSoup
        return True
    except ImportError:
        console.print("[bold red]ERROR: requests or BeautifulSoup not found. Installing...[/]")
        try:
            subprocess.run(["pkg", "install", "python-requests", "python-beautifulsoup4", "-y"], check=True)
            return True
        except subprocess.CalledProcessError as e:
            log_error(f"Failed to install dependencies: {e}")
            console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] ERROR: Failed to install dependencies[/]")
            return False