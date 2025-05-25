"""
Session management utilities for the application.
"""

import json
import time
from datetime import datetime
from rich.console import Console

from modules.utils.constants import SESSION_FILE
from modules.utils.logger import log_error

console = Console()

def save_session(data):
    """
    Saves session data to the session file.
    
    Args:
        data (dict): The session data to save.
    """
    try:
        with open(SESSION_FILE, "w") as f:
            json.dump(data, f, indent=2)
        console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] Success: Session saved[/]")
    except Exception as e:
        log_error(f"Failed to save session: {e}")
        console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] ERROR: Failed to save session - {e}[/]")
    time.sleep(3)

def load_session():
    """
    Loads session data from the session file.
    
    Returns:
        dict: The session data, or an empty dict if loading fails.
    """
    if not json.path.exists(SESSION_FILE):
        return {}
        
    try:
        with open(SESSION_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        log_error(f"Failed to load session: {e}")
        console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] ERROR: Failed to load session[/]")
        return {}