"""
Display utilities for the application.
"""

import time
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from modules.utils.constants import GAME_SETTINGS

console = Console()

def clear_screen():
    """
    Clears the console screen.
    """
    console.clear()

def display_results(info, cam, fire, gyro, game, mode):
    """
    Displays the calculated sensitivity results.
    
    Args:
        info (dict): Device information.
        cam (dict): Camera sensitivity values.
        fire (dict): Firing sensitivity values.
        gyro (dict): Gyro sensitivity values.
        game (str): The selected game.
        mode (str): The selected game mode.
    """
    clear_screen()
    mode_display = f" ({mode})" if mode else ""
    
    console.print(Panel(
        f"[bold magenta]=== SENSITIVITY RESULTS FOR {game.upper()}{mode_display} ===[/]\n"
        f"[bold cyan][Displayed at {datetime.now().strftime('%H:%M:%S')}][/]",
        title="Results",
        border_style="magenta"  # Changed from 'badge' to 'magenta'
    ))
    
    # Device information table
    table = Table(title="Device Information", show_header=False, border_style="cyan")
    table.add_column("Field", style="bold green")
    table.add_column("Value", style="white")
    
    for k, v in info.items():
        table.add_row(k, str(v))
    
    console.print(table)
    
    # Camera sensitivity table
    table = Table(title="Camera Sensitivity", border_style="cyan")
    table.add_column("Scope", style="bold green")
    table.add_column("Value", style="white")
    
    for k, v in cam.items():
        table.add_row(k, str(v))
    
    console.print(table)
    
    # Firing sensitivity table
    table = Table(title="Firing Sensitivity", border_style="cyan")
    table.add_column("Scope", style="bold green")
    table.add_column("Value", style="white")
    
    for k, v in fire.items():
        table.add_row(k, str(v))
    
    console.print(table)
    
    # Gyro sensitivity table (if available)
    if gyro:
        table = Table(title="Gyro Sensitivity", border_style="cyan")
        table.add_column("Scope", style="bold green")
        table.add_column("Value", style="white")
        
        for k, v in gyro.items():
            table.add_row(k, str(v))
        
        console.print(table)
    else:
        console.print("[bold yellow] Gyro Sensitivity: Not Available[/]")
    
    # Instructions
    mode_instructions = f" {mode} mode" if mode else ""
    console.print(f"[bold yellow] INSTRUCTIONS: Apply these values in {game}'s Settings > Sensitivity and test in{mode_instructions}.[/]")
    time.sleep(1)