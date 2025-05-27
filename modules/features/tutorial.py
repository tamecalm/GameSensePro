"""
Interactive tutorial mode utilities.
"""

import json
import time
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

from modules.utils.constants import GAME_SETTINGS
from modules.utils.logger import log_error
from modules.ui.display import clear_screen

console = Console()

TUTORIAL_STEPS = [
    {
        "title": "Welcome",
        "content": "Welcome to the Game Sense Pro toolkit! This tutorial will guide you through the main features.",
        "action": None
    },
    {
        "title": "Device Information",
        "content": "First, we'll gather information about your device. This helps calculate optimal sensitivity settings.",
        "action": "get_device_info"
    },
    {
        "title": "Game Selection",
        "content": "Next, select your game. Each game has specific sensitivity ranges and recommended settings.",
        "action": "select_game"
    },
    {
        "title": "Player Style",
        "content": "Tell us about your play style. This affects sensitivity calculations.",
        "action": "get_player_style"
    },
    {
        "title": "Sensitivity Calculation",
        "content": "We'll calculate your optimal sensitivity settings based on your device and preferences.",
        "action": "calculate_sensitivity"
    },
    {
        "title": "Applying Settings",
        "content": "Learn how to apply these settings in your game.",
        "action": "show_application_guide"
    },
    {
        "title": "Fine-tuning",
        "content": "After testing, you can provide feedback to fine-tune your settings.",
        "action": "explain_feedback"
    }
]

def run_tutorial():
    """Run the interactive tutorial."""
    clear_screen()
    console.print(Panel(
        f"[bold magenta]=== TUTORIAL MODE ===[/]\n"
        f"[bold cyan][Started at {datetime.now().strftime('%H:%M:%S')}][/]",
        title="Tutorial",
        border_style="magenta"
    ))
    
    for step in TUTORIAL_STEPS:
        display_tutorial_step(step)
        if not Confirm.ask("[bold yellow]Continue to next step?[/]"):
            break
    
    console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] Tutorial completed![/]")
    time.sleep(3)

def display_tutorial_step(step):
    """Display a tutorial step."""
    clear_screen()
    console.print(Panel(
        f"[bold magenta]=== {step['title'].upper()} ===[/]\n"
        f"[bold cyan][Step at {datetime.now().strftime('%H:%M:%S')}][/]\n\n"
        f"{step['content']}",
        title=f"Tutorial - {step['title']}",
        border_style="magenta"
    ))
    time.sleep(2)

def show_application_guide(game):
    """Show guide for applying settings in a specific game."""
    settings = GAME_SETTINGS[game]
    
    clear_screen()
    console.print(Panel(
        f"[bold magenta]=== APPLYING SETTINGS IN {game.upper()} ===[/]\n"
        f"[bold cyan][Guide at {datetime.now().strftime('%H:%M:%S')}][/]\n\n"
        f"1. Open {settings['menu_path']}\n"
        "2. Apply the calculated sensitivity values\n"
        "\nRecommended Settings:\n" +
        "\n".join(f"- {k}: {v}" for k, v in settings['recommended_settings'].items()),
        title="Application Guide",
        border_style="magenta"
    ))
    time.sleep(3)

def explain_feedback():
    """Explain the feedback system."""
    clear_screen()
    console.print(Panel(
        f"[bold magenta]=== FEEDBACK SYSTEM ===[/]\n"
        f"[bold cyan][Guide at {datetime.now().strftime('%H:%M:%S')}][/]\n\n"
        "After testing your settings:\n"
        "1. Select 'Provide Feedback' from the main menu\n"
        "2. Rate the sensitivity for camera, firing, and gyro\n"
        "3. Your feedback will be used to improve future calculations",
        title="Feedback Guide",
        border_style="magenta"
    ))
    time.sleep(3)