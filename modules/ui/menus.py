"""
Menu utilities for the application.
"""

import time
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt

from modules.ui.display import clear_screen
from modules.features.updates import check_for_updates
from modules.features.benchmark import run_benchmark
from modules.features.tutorial import run_tutorial

console = Console()

def menu(translations):
    """
    Displays the main menu and returns the user's choice.
    
    Args:
        translations (dict): The translations dictionary.
        
    Returns:
        str: The user's menu choice.
    """
    clear_screen()
    console.print(Panel(
        f"[bold magenta]=== {translations.get('menu', 'MENU')} ===[/]\n"
        f"[bold cyan][{translations.get('displayed_at', 'Displayed at')} {datetime.now().strftime('%H:%M:%S')}][/]\n"
        f"1. {translations.get('calculate_sensitivity', 'Calculate Sensitivity')}\n"
        f"2. {translations.get('provide_feedback', 'Provide Feedback')}\n"
        f"3. {translations.get('view_stats', 'View Stats')}\n"
        f"4. {translations.get('clear_stats', 'Clear Stats')}\n"
        f"5. {translations.get('run_benchmark', 'Run Performance Benchmark')}\n"
        f"6. {translations.get('view_community', 'View Community Settings')}\n"
        f"7. {translations.get('check_updates', 'Check for Updates')}\n"
        f"8. {translations.get('start_tutorial', 'Start Tutorial')}\n"
        f"9. {translations.get('exit', 'Exit')}",
        title=translations.get('menu', 'Menu'),
        border_style="magenta"
    ))
    
    choice = IntPrompt.ask(
        f"[bold yellow]{translations.get('choose_option', 'Choose an option (1-9)')}[/]", 
        choices=["1", "2", "3", "4", "5", "6", "7", "8", "9"], 
        default=1
    )
    
    time.sleep(1)
    return str(choice)