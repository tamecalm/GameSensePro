"""
Banner utilities for the application.
"""

import time
from datetime import datetime
from rich.console import Console
from rich.panel import Panel

from modules.ui.display import clear_screen

console = Console()

def banner(game):
    """
    Displays the application banner.
    
    Args:
        game (str): The selected game.
    """
    clear_screen()
    console.print(Panel(
        f"[bold magenta]=== {game.upper()} DYNAMIC SENSITIVITY TOOLKIT ===[/]\n"
        f"[bold green]REMO773 : (14.4.2021)[/]\n"
        f"[bold cyan][Started at {datetime.now().strftime('%H:%M:%S')}][/]",
        title="Toolkit Banner",
        border_style="magenta"
    ))
    time.sleep(3)