"""
Community-driven sensitivity database utilities.
"""

import json
import time
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from modules.utils.constants import COMMUNITY_DB_FILE
from modules.utils.logger import log_error
from modules.ui.display import clear_screen

console = Console()

def save_to_community_db(settings, anonymous=True):
    """Save sensitivity settings to community database."""
    try:
        db = load_community_db()
        
        # Remove personal info if anonymous
        if anonymous:
            settings = anonymize_settings(settings)
        
        db["settings"].append(settings)
        
        with open(COMMUNITY_DB_FILE, "w") as f:
            json.dump(db, f, indent=2)
        
        console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] Success: Settings shared with community[/]")
    except Exception as e:
        log_error(f"Failed to save to community database: {e}")
        console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] ERROR: Failed to share settings[/]")

def load_community_db():
    """Load community database."""
    try:
        with open(COMMUNITY_DB_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"settings": []}
    except Exception as e:
        log_error(f"Failed to load community database: {e}")
        return {"settings": []}

def get_community_recommendations(device, game, skill_level):
    """Get community-recommended settings."""
    db = load_community_db()
    
    # Filter settings by device, game and skill level
    recommendations = [
        s for s in db["settings"]
        if s["device"] == device and s["game"] == game and s["skill_level"] == skill_level
    ]
    
    if not recommendations:
        return None
    
    # Calculate average settings
    avg_settings = calculate_average_settings(recommendations)
    return avg_settings

def anonymize_settings(settings):
    """Remove personal information from settings."""
    anonymous = settings.copy()
    if "device_id" in anonymous:
        del anonymous["device_id"]
    if "user_id" in anonymous:
        del anonymous["user_id"]
    return anonymous

def calculate_average_settings(settings_list):
    """Calculate average sensitivity values from multiple settings."""
    if not settings_list:
        return None
    
    total = {}
    for settings in settings_list:
        for scope, value in settings["sensitivity"].items():
            if scope not in total:
                total[scope] = 0
            total[scope] += value
    
    return {
        scope: round(value / len(settings_list), 1)
        for scope, value in total.items()
    }

def display_community_stats():
    """Display community database statistics."""
    clear_screen()
    db = load_community_db()
    
    console.print(Panel(
        f"[bold magenta]=== COMMUNITY STATISTICS ===[/]\n"
        f"[bold cyan][Displayed at {datetime.now().strftime('%H:%M:%S')}][/]",
        title="Community Stats",
        border_style="magenta"
    ))
    
    table = Table(title="Community Database Stats")
    table.add_column("Metric", style="bold green")
    table.add_column("Value", style="white")
    
    table.add_row("Total Contributions", str(len(db["settings"])))
    table.add_row("Unique Games", str(len(set(s["game"] for s in db["settings"]))))
    table.add_row("Unique Devices", str(len(set(s["device"] for s in db["settings"]))))
    
    console.print(table)
    time.sleep(3)