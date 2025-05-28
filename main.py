#!/usr/bin/env python3
"""
Main entry point for the Sensitivity Toolkit application.
This script initializes the application and handles the main program flow.
"""

import os
import time
from rich.console import Console
from rich.prompt import Prompt

from modules.utils.setup import ensure_data_folder
from modules.ui.animation import display_logo_animation
from modules.ui.banner import banner
from modules.language.manager import select_language, load_language
from modules.device.info import get_device_info
from modules.sensitivity.player import get_player_style
from modules.sensitivity.calculator import calculate_sensitivity
from modules.ui.display import display_results
from modules.sensitivity.storage import save_results
from modules.ui.menus import menu
from modules.sensitivity.feedback import collect_feedback
from modules.stats.viewer import display_stats
from modules.stats.manager import clear_stats
from modules.features.benchmark import run_benchmark
from modules.features.community import display_community_stats
from modules.features.updates import check_for_updates
from modules.features.tutorial import run_tutorial

# Initialize rich console
console = Console()

def main():
    """Main function that orchestrates the program flow."""
    # Ensure data directory exists
    ensure_data_folder()
    
    # Display logo animation
    display_logo_animation()
    
    # Select language
    language_code = select_language()
    translations = load_language(language_code)
    
    # Get game selection
    game = get_game_selection(translations)
    mode = ""  # Empty mode as the feature is removed
    
    # Display banner
    banner(game)
    
    # Main application loop
    while True:
        choice = menu(translations)
        
        if choice == "1":
            # Calculate sensitivity
            info = get_device_info()
            player_style = get_player_style(translations)
            cam, fire, gyro = calculate_sensitivity(info, player_style, game, mode)
            
            if cam and fire:
                display_results(info, cam, fire, gyro, game, mode)
                save_results(info, cam, fire, gyro, player_style, game, mode)
            
            Prompt.ask(f"[bold grey]{translations.get('press_enter', 'Press Enter to return to menu...')}[/]")
        
        elif choice == "2":
            # Collect feedback
            collect_feedback(game, mode, translations)
            Prompt.ask(f"[bold grey]{translations.get('press_enter', 'Press Enter to return to menu...')}[/]")
        
        elif choice == "3":
            # Display stats
            display_stats(translations)
            Prompt.ask(f"[bold grey]{translations.get('press_enter', 'Press Enter to return to menu...')}[/]")
        
        elif choice == "4":
            # Clear stats
            clear_stats(translations)
            Prompt.ask(f"[bold grey]{translations.get('press_enter', 'Press Enter to return to menu...')}[/]")
        
        elif choice == "5":
            # Run benchmark
            results = run_benchmark()
            if results:
                console.print(f"[bold green]Benchmark Score: {results['performance_score']}[/]")
            Prompt.ask(f"[bold grey]{translations.get('press_enter', 'Press Enter to return to menu...')}[/]")
        
        elif choice == "6":
            # View community settings
            display_community_stats()
            Prompt.ask(f"[bold grey]{translations.get('press_enter', 'Press Enter to return to menu...')}[/]")
        
        elif choice == "7":
            # Check for updates
            if check_for_updates():
                console.print("[bold yellow]Update available! Please restart the application to apply updates.[/]")
            Prompt.ask(f"[bold grey]{translations.get('press_enter', 'Press Enter to return to menu...')}[/]")
        
        elif choice == "8":
            # Start tutorial
            run_tutorial()
            Prompt.ask(f"[bold grey]{translations.get('press_enter', 'Press Enter to return to menu...')}[/]")
        
        elif choice == "9":
            # Exit program
            from modules.ui.display import clear_screen
            from rich.panel import Panel
            from datetime import datetime
            
            clear_screen()
            console.print(Panel(
                f"[bold magenta]=== {translations.get('exiting', 'EXITING')} ===[/]\n"
                f"[bold cyan][{translations.get('exited_at', 'Exited at')} {datetime.now().strftime('%H:%M:%S')}][/]\n"
                f"[bold green]{translations.get('stay_sharp', 'STAY SHARP, SOLDIER!')}[/]",
                title=translations.get('exit', 'Exit'),
                border_style="magenta"
            ))
            time.sleep(1)
            break

def get_game_selection(translations):
    """Get game selection from user."""
    from rich.panel import Panel
    from rich.prompt import IntPrompt
    from datetime import datetime
    from modules.ui.display import clear_screen
    from modules.utils.constants import GAME_SETTINGS
    
    clear_screen()
    console.print(Panel(
        f"[bold magenta]=== {translations.get('select_game', 'SELECT GAME')} ===[/]\n"
        f"[bold cyan][{translations.get('started_at', 'Started at')} {datetime.now().strftime('%H:%M:%S')}][/]\n"
        "1. Blood Strike\n2. Free Fire\n3. Call of Duty Mobile\n4. Delta Force\n5. PUBG Mobile",
        title=translations.get('game_selection', 'Game Selection'),
        border_style="magenta"
    ))
    
    game_choice = IntPrompt.ask(
        f"[bold yellow]{translations.get('select_game_prompt', 'Select game (1-5)')}[/]", 
        choices=["1", "2", "3", "4", "5"], 
        default=1
    )
    
    games = list(GAME_SETTINGS.keys())
    game = games[game_choice - 1]
    
    console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] {translations.get('success', 'Success')}: {translations.get('selected', 'Selected')} {game}[/]")
    time.sleep(3)
    
    return game

if __name__ == "__main__":
    main()