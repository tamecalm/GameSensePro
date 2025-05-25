"""
Statistics management utilities for the application.
"""

import json
import os
import time
from datetime import datetime
from rich.console import Console
from rich.panel import Panel

from modules.ui.display import clear_screen
from modules.utils.constants import STATS_FILE, FEEDBACK_FILE
from modules.utils.logger import log_error

console = Console()

def update_stats(result):
    """
    Updates statistics with new calculation results.
    
    Args:
        result (dict): The calculation results.
    """
    # Initialize stats or load existing stats
    stats = {"calculations": [], "feedback_count": 0}
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r") as f:
                stats = json.load(f)
        except Exception as e:
            log_error(f"Failed to load stats: {e}")
    
    # Add new calculation
    stats["calculations"].append({
        "timestamp": result["timestamp"],
        "device": result["device"]["Device"],
        "game": result["game"],
        "player_style": result["player_style"],
        "cam_sense": result["camera_sensitivity"],
        "fire_sense": result["firing_sensitivity"],
        "gyro_sense": result["gyro_sensitivity"]
    })
    
    # Update feedback count
    stats["feedback_count"] += 1 if os.path.exists(FEEDBACK_FILE) else 0
    
    # Save stats
    try:
        with open(STATS_FILE, "w") as f:
            json.dump(stats, f, indent=2)
    except Exception as e:
        log_error(f"Failed to update stats: {e}")
        console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] ERROR: Failed to update stats - {e}[/]")

def clear_stats(translations):
    """
    Clears all statistics.
    
    Args:
        translations (dict): The translations dictionary.
    """
    clear_screen()
    console.print(Panel(
        f"[bold magenta]=== {translations.get('clearing_statistics', 'CLEARING STATISTICS')} ===[/]\n"
        f"[bold cyan][{translations.get('started_at', 'Started at')} {datetime.now().strftime('%H:%M:%S')}][/]",
        title=translations.get('clear_stats', 'Clear Stats'),
        border_style="magenta"
    ))
    
    if os.path.exists(STATS_FILE):
        try:
            os.remove(STATS_FILE)
            console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] {translations.get('success', 'Success')}: {translations.get('statistics_cleared', 'Statistics cleared')}[/]")
        except Exception as e:
            log_error(f"Failed to clear stats: {e}")
            console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] ERROR: {translations.get('clear_stats_error', 'Failed to clear stats')} - {e}[/]")
    else:
        console.print(f"[bold yellow][{datetime.now().strftime('%H:%M:%S')}] {translations.get('warning', 'WARNING')}: {translations.get('no_stats_file', 'No stats file to clear')}[/]")
    
    time.sleep(3)