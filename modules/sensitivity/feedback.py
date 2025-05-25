"""
Feedback collection utilities for the application.
"""

import json
import time
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt

from modules.ui.display import clear_screen
from modules.utils.constants import FEEDBACK_FILE
from modules.utils.logger import log_error

console = Console()

def collect_feedback(game, mode, translations):
    """
    Collects user feedback on sensitivity settings.
    
    Args:
        game (str): The selected game.
        mode (str): The selected game mode.
        translations (dict): The translations dictionary.
    """
    clear_screen()
    mode_display = f" ({mode})" if mode else ""
    
    console.print(Panel(
        f"[bold magenta]=== {translations.get('feedback_collection', 'FEEDBACK COLLECTION')} FOR {game.upper()}{mode_display} ===[/]\n"
        f"[bold cyan][{translations.get('started_at', 'Started at')} {datetime.now().strftime('%H:%M:%S')}][/]\n"
        f"{translations.get('test_settings', 'Test settings in')} {game}'s {translations.get('training_mode', 'Training Mode')}{mode_display}.\n"
        f"{translations.get('camera_feedback', 'Camera sensitivity feedback')}:\n"
        f"{translations.get('calibration_options', '1. Too High\n2. Too Low\n3. Just Right')}",
        title=translations.get('feedback', 'Feedback'),
        border_style="magenta"
    ))
    
    # Camera feedback
    cam_feedback = IntPrompt.ask(
        f"[bold yellow]{translations.get('select_prompt', 'Select (1-3)')}[/]", 
        choices=["1", "2", "3"], 
        default=3
    )
    
    console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] {translations.get('success', 'Success')}: {translations.get('camera_feedback_selected', 'Camera feedback selected')}[/]")
    time.sleep(3)
    
    # Firing feedback
    clear_screen()
    console.print(Panel(
        f"[bold magenta]=== {translations.get('feedback_collection', 'FEEDBACK COLLECTION')} ===[/]\n"
        f"[bold cyan][{translations.get('continued_at', 'Continued at')} {datetime.now().strftime('%H:%M:%S')}][/]\n"
        f"{translations.get('firing_feedback', 'Firing sensitivity feedback')}\n"
        f"{translations.get('calibration_options', '1. Too High\n2. Too Low\n3. Just Right')}",
        title=translations.get('feedback', 'Feedback'),
        border_style="magenta"
    ))
    
    fire_feedback = IntPrompt.ask(
        f"[bold yellow]{translations.get('select_prompt', 'Select (1-3)')}[/]", 
        choices=["1", "2", "3"], 
        default=3
    )
    
    console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] {translations.get('success', 'Success')}: {translations.get('firing_feedback_selected', 'Firing feedback selected')}[/]")
    time.sleep(3)
    
    # Gyro feedback
    clear_screen()
    console.print(Panel(
        f"[bold magenta]=== {translations.get('feedback_collection', 'FEEDBACK COLLECTION')} ===[/]\n"
        f"[bold cyan][{translations.get('continued_at', 'Continued at')} {datetime.now().strftime('%H:%M:%S')}][/]\n"
        f"{translations.get('gyro_feedback', 'Gyro sensitivity (skip if not applicable)')}:\n"
        f"{translations.get('calibration_options', '1. Too High\n2. Too Low\n3. Just Right')}\n4. {translations.get('skip', 'Skip')}",
        title=translations.get('feedback', 'Feedback'),
        border_style="magenta"
    ))
    
    gyro_feedback = IntPrompt.ask(
        f"[bold yellow]{translations.get('select_prompt', 'Select (1-4)')}[/]", 
        choices=["1", "2", "3", "4"], 
        default=4
    )
    
    console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] {translations.get('success', 'Success')}: {translations.get('gyro_feedback_selected', 'Gyro feedback selected')}[/]")
    time.sleep(3)
    
    # Process feedback
    feedback = {"cam_adjust": 1.0, "fire_adjust": 1.0, "gyro_adjust": 1.0}
    
    if int(cam_feedback) == 1:
        feedback["cam_adjust"] = 0.9
    elif int(cam_feedback) == 2:
        feedback["cam_adjust"] = 1.1
    
    if int(fire_feedback) == 1:
        feedback["fire_adjust"] = 0.9
    elif int(fire_feedback) == 2:
        feedback["fire_adjust"] = 1.1
    
    if int(gyro_feedback) in [1, 2, 3]:
        if int(gyro_feedback) == 1:
            feedback["gyro_adjust"] = 0.9
        elif int(gyro_feedback) == 2:
            feedback["gyro_adjust"] = 1.1
    
    # Save feedback
    try:
        with open(FEEDBACK_FILE, "w") as f:
            json.dump(feedback, f, indent=2)
        console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] {translations.get('success', 'Success')}: {translations.get('feedback_saved', 'Feedback saved')}[/]")
    except Exception as e:
        log_error(f"Failed to save feedback: {e}")
        console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] ERROR: {translations.get('feedback_save_error', 'Failed to save feedback')} - {e}[/]")
    
    time.sleep(3)