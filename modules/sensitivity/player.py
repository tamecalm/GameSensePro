"""
Player style utilities for the application.
"""

import time
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt

from modules.ui.display import clear_screen
from modules.utils.session import load_session, save_session

console = Console()

def get_player_style(translations):
    """
    Gets player style information from the user.
    
    Args:
        translations (dict): The translations dictionary.
        
    Returns:
        dict: Player style information.
    """
    # Get finger style
    clear_screen()
    console.print(Panel(
        f"[bold magenta]=== {translations.get('finger_style', 'FINGER STYLE')} ===[/]\n"
        f"[bold cyan][{translations.get('started_at', 'Started at')} {datetime.now().strftime('%H:%M:%S')}][/]\n"
        f"{translations.get('finger_options', '1. One Finger\n2. Two Fingers\n3. Three or More Fingers')}",
        title=translations.get('player_style', 'Player Style'),
        border_style="magenta"
    ))
    
    session = load_session()
    fingers = session.get("fingers") or IntPrompt.ask(
        f"[bold yellow]{translations.get('select_finger_prompt', 'Select finger style (1-3)')}[/]", 
        choices=["1", "2", "3"], 
        default=2
    )
    session["fingers"] = fingers
    
    console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] {translations.get('success', 'Success')}: {translations.get('selected', 'Selected')} {fingers} fingers[/]")
    time.sleep(3)
    
    # Get skill level
    clear_screen()
    console.print(Panel(
        f"[bold magenta]=== {translations.get('skill_level', 'SKILL LEVEL')} ===[/]\n"
        f"[bold cyan][{translations.get('continued_at', 'Continued at')} {datetime.now().strftime('%H:%M:%S')}][/]\n"
        f"{translations.get('skill_options', '1. Beginner\n2. Intermediate\n3. Advanced')}",
        title=translations.get('player_skill', 'Player Skill'),
        border_style="magenta"
    ))
    
    skill = session.get("skill") or IntPrompt.ask(
        f"[bold yellow]{translations.get('select_skill_prompt', 'Select skill level (1-3)')}[/]", 
        choices=["1", "2", "3"], 
        default=2
    )
    skill_map = {1: "beginner", 2: "intermediate", 3: "advanced"}
    session["skill"] = skill
    
    console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] {translations.get('success', 'Success')}: {translations.get('selected', 'Selected')} {skill_map[skill]} skill[/]")
    time.sleep(3)
    
    # Get aiming finger
    clear_screen()
    console.print(Panel(
        f"[bold magenta]=== {translations.get('aiming_finger', 'AIMING FINGER')} ===[/]\n"
        f"[bold cyan][{translations.get('continued_at', 'Continued at')} {datetime.now().strftime('%H:%M:%S')}][/]\n"
        f"{translations.get('aiming_options', '1. Thumb\n2. Index\n3. Other')}",
        title=translations.get('aiming_finger', 'Aiming Finger'),
        border_style="magenta"
    ))
    
    aiming_finger = session.get("aiming_finger") or IntPrompt.ask(
        f"[bold yellow]{translations.get('select_aiming_prompt', 'Select aiming finger (1-3)')}[/]", 
        choices=["1", "2", "3"], 
        default=1
    )
    aiming_map = {1: "thumb", 2: "index", 3: "other"}
    session["aiming_finger"] = aiming_finger
    
    console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] {translations.get('success', 'Success')}: {translations.get('selected', 'Selected')} {aiming_map[aiming_finger]} for aiming[/]")
    time.sleep(3)
    
    # Get claw grip (if applicable)
    claw_grip = None
    if int(fingers) == 3:
        clear_screen()
        console.print(Panel(
            f"[bold magenta]=== {translations.get('claw_grip', 'CLAW GRIP')} ===[/]\n"
            f"[bold cyan][{translations.get('continued_at', 'Continued at')} {datetime.now().strftime('%H:%M:%S')}][/]\n"
            f"{translations.get('yes_no', '1. Yes\n2. No')}",
            title=translations.get('claw_grip', 'Claw Grip'),
            border_style="magenta"
        ))
        
        claw_grip = session.get("claw_grip") or IntPrompt.ask(
            f"[bold yellow]{translations.get('select_prompt', 'Select (1-2)')}[/]", 
            choices=["1", "2"], 
            default=2
        )
        session["claw_grip"] = claw_grip
        
        yes_text = translations.get('yes', 'claw')
        no_text = translations.get('no', 'no claw')
        console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] {translations.get('success', 'Success')}: {translations.get('selected', 'Selected')} {yes_text if claw_grip == 1 else no_text} grip[/]")
        time.sleep(3)
    
    save_session(session)
    
    return {
        "fingers": int(fingers), 
        "skill": skill_map[int(skill)], 
        "aiming_finger": aiming_map[int(aiming_finger)], 
        "claw_grip": claw_grip == 1 if claw_grip else False
    }