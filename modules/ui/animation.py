"""
Animation utilities for the application.
"""

import time
from rich.console import Console
from rich.panel import Panel

from modules.ui.display import clear_screen

console = Console()

def display_logo_animation():
    """
    Displays the animated logo.
    """
    frames = [
        """
        [bold red]  ____  _     ___   ____  
        | __ )| |____/ _ \\ / ___|
        |  _ \\| |___| | | | |    
        | |_) | |   | |_| | |___ 
        |____/|_|    \\___/ \\____|
        [/]
        """,
        """
        [bold blue]  ____  _     ___   ____  
        | __ )| |____/ _ \\ / ___|
        |  _ \\| |___| | | | |    
        | |_) | |   | |_| | |___ 
        |____/|_|    \\___/ \\____|
        [/]
        """
    ]
    
    for _ in range(2):
        for frame in frames:
            clear_screen()
            console.print(Panel(frame, title="Sensitivity Toolkit", border_style="cyan"))
            time.sleep(0.5)
    
    clear_screen()