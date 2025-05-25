"""
Statistics viewing utilities for the application.
"""

import json
import os
import time
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from modules.ui.display import clear_screen
from modules.utils.constants import STATS_FILE
from modules.utils.logger import log_error

console = Console()

def display_stats(translations):
    """
    Displays statistics about sensitivity calculations.
    
    Args:
        translations (dict): The translations dictionary.
    """
    clear_screen()
    console.print(Panel(
        f"[bold magenta]=== {translations.get('sensitivity_statistics', 'SENSITIVITY STATISTICS')} ===[/]\n"
        f"[bold cyan][{translations.get('displayed_at', 'Displayed at')} {datetime.now().strftime('%H:%M:%S')}][/]",
        title=translations.get('statistics', 'Statistics'),
        border_style="magenta"
    ))
    
    if not os.path.exists(STATS_FILE):
        console.print(f"[bold yellow][{datetime.now().strftime('%H:%M:%S')}] {translations.get('warning', 'WARNING')}: {translations.get('no_stats_available', 'No stats available')}[/]")
        time.sleep(1)
        return
    
    try:
        with open(STATS_FILE, "r") as f:
            stats = json.load(f)
        
        console.print(f"[bold green]{translations.get('total_calculations', 'Total Calculations')}: {len(stats['calculations'])}[/]")
        console.print(f"[bold green]{translations.get('feedback_submissions', 'Feedback Submissions')}: {stats['feedback_count']}[/]")
        
        if stats["calculations"]:
            recent = stats["calculations"][-1]
            
            # Device information table
            table = Table(title=translations.get('recent_calculation', 'Recent Calculation'), border_style="cyan")
            table.add_column(translations.get('field', 'Field'), style="bold green")
            table.add_column(translations.get('value', 'Value'), style="white")
            
            table.add_row(translations.get('timestamp', 'Timestamp'), recent["timestamp"])
            table.add_row(translations.get('device', 'Device'), recent["device"])
            table.add_row(translations.get('game', 'Game'), recent["game"])
            
            # Format player style
            player_style = (f"{recent['player_style']['fingers']} {translations.get('fingers', 'fingers')}, "
                           f"{recent['player_style']['skill']} {translations.get('skill', 'skill')}, "
                           f"{translations.get('aiming_with', 'aiming with')} {recent['player_style']['aiming_finger']}, "
                           f"{translations.get('claw', 'claw') if recent['player_style']['claw_grip'] else translations.get('no_claw', 'no claw')} {translations.get('grip', 'grip')}")
            
            table.add_row(translations.get('player_style', 'Player Style'), player_style)
            console.print(table)
            
            # Camera sensitivity table
            table = Table(title=translations.get('camera_sensitivity', 'Camera Sensitivity'), border_style="cyan")
            table.add_column(translations.get('scope', 'Scope'), style="bold green")
            table.add_column(translations.get('value', 'Value'), style="white")
            
            for k, v in recent["cam_sense"].items():
                table.add_row(k, str(v))
            
            console.print(table)
            
            # Firing sensitivity table
            table = Table(title=translations.get('firing_sensitivity', 'Firing Sensitivity'), border_style="cyan")
            table.add_column(translations.get('scope', 'Scope'), style="bold green")
            table.add_column(translations.get('value', 'Value'), style="white")
            
            for k, v in recent["fire_sense"].items():
                table.add_row(k, str(v))
            
            console.print(table)
            
            # Gyro sensitivity table
            table = Table(title=translations.get('gyro_sensitivity', 'Gyro Sensitivity'), border_style="cyan")
            table.add_column(translations.get('scope', 'Scope'), style="bold green")
            table.add_column(translations.get('value', 'Value'), style="white")
            
            if recent["gyro_sense"] == "Not Available":
                table.add_row("N/A", translations.get('not_available', 'Not Available'))
            else:
                for k, v in recent["gyro_sense"].items():
                    table.add_row(k, str(v))
            
            console.print(table)
    except Exception as e:
        log_error(f"Failed to display stats: {e}")
        console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] ERROR: {translations.get('display_stats_error', 'Failed to display stats')} - {e}[/]")
    
    time.sleep(3)