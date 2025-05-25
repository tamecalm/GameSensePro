"""
Language manager for the application.
Handles language selection and loading translations.
"""

import json
import requests
import time
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt
from rich.progress import Progress

from modules.ui.display import clear_screen
from modules.utils.constants import DEFAULT_LANGUAGE, TRANSLATION_API_URL
from modules.utils.logger import log_error, log_info

console = Console()

# Available languages
LANGUAGES = {
    1: {"code": "en", "name": "English"},
    2: {"code": "es", "name": "Spanish"},
    3: {"code": "fr", "name": "French"},
    4: {"code": "de", "name": "German"},
    5: {"code": "zh", "name": "Chinese"},
    6: {"code": "ja", "name": "Japanese"},
    7: {"code": "ru", "name": "Russian"},
    8: {"code": "ar", "name": "Arabic"},
    9: {"code": "hi", "name": "Hindi"},
    10: {"code": "pt", "name": "Portuguese"}
}

# Base strings to translate for each language
BASE_STRINGS = {
    "success": "Success",
    "error": "Error",
    "warning": "Warning",
    "select_game": "SELECT GAME",
    "select_game_prompt": "Select game (1-5)",
    "finger_style": "FINGER STYLE",
    "finger_options": "1. One Finger\n2. Two Fingers\n3. Three or More Fingers",
    "skill_level": "SKILL LEVEL",
    "skill_options": "1. Beginner\n2. Intermediate\n3. Advanced",
    "aiming_finger": "AIMING FINGER",
    "aiming_options": "1. Thumb\n2. Index\n3. Other",
    "claw_grip": "CLAW GRIP",
    "yes_no": "1. Yes\n2. No",
    "press_enter": "Press Enter to return to menu...",
    "selected": "Selected",
    "exiting": "EXITING",
    "exited_at": "Exited at",
    "stay_sharp": "STAY SHARP, SOLDIER!",
    "exit": "Exit",
    "game_selection": "Game Selection",
    "preview_prompt": "For {scope} (Camera: {cam}, Fire: {fire}{gyro_text}): ",
    "calibration_prompt": "After testing in {game}, do you find the sensitivity:",
    "calibration_options": "1. Too High\n2. Too Low\n3. Just Right"
}

def select_language():
    """
    Displays language selection menu and returns the selected language code.
    
    Returns:
        str: The selected language code.
    """
    clear_screen()
    console.print(Panel(
        "[bold magenta]=== SELECT LANGUAGE ===[/]\n"
        f"[bold cyan][Started at {datetime.now().strftime('%H:%M:%S')}][/]\n"
        "\n".join([f"{i}. {lang['name']}" for i, lang in LANGUAGES.items()]),
        title="Language Selection",
        border_style="magenta"
    ))
    
    language_choice = IntPrompt.ask(
        "[bold yellow]Select language[/]",
        choices=[str(i) for i in LANGUAGES.keys()],
        default=1
    )
    
    selected_language = LANGUAGES[language_choice]["code"]
    selected_language_name = LANGUAGES[language_choice]["name"]
    
    console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] Success: Selected {selected_language_name}[/]")
    time.sleep(3)
    
    return selected_language

def translate_text(text, target_lang, source_lang="en"):
    """
    Translates text using an external API.
    
    Args:
        text (str): The text to translate.
        target_lang (str): The target language code.
        source_lang (str): The source language code.
        
    Returns:
        str: The translated text or the original text if translation fails.
    """
    if target_lang == source_lang:
        return text
    
    try:
        params = {
            'q': text,
            'langpair': f'{source_lang}|{target_lang}'
        }
        
        response = requests.get(TRANSLATION_API_URL, params=params, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        if data['responseStatus'] == 200:
            return data['responseData']['translatedText']
        return text
    except Exception as e:
        log_error(f"Translation error: {e}")
        return text

def generate_translations(lang_code):
    """
    Generates translations for the base strings using the translation API.
    
    Args:
        lang_code (str): The language code to translate to.
        
    Returns:
        dict: A dictionary of translated strings.
    """
    if lang_code == DEFAULT_LANGUAGE:
        return BASE_STRINGS
    
    translations = {}
    
    with Progress() as progress:
        task = progress.add_task("[cyan]Translating...", total=len(BASE_STRINGS))
        
        for key, value in BASE_STRINGS.items():
            translations[key] = translate_text(value, lang_code)
            progress.update(task, advance=1)
            time.sleep(0.2)  # Small delay to avoid overwhelming the API
    
    return translations

def load_language(lang_code):
    """
    Loads translations for the specified language.
    
    Args:
        lang_code (str): The language code to load.
        
    Returns:
        dict: A dictionary of translated strings.
    """
    try:
        clear_screen()
        console.print(Panel(
            f"[bold magenta]=== LOADING {lang_code.upper()} LANGUAGE ===[/]\n"
            f"[bold cyan][Started at {datetime.now().strftime('%H:%M:%S')}][/]",
            title="Language Loading",
            border_style="magenta"
        ))
        
        translations = generate_translations(lang_code)
        
        console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] Success: Language loaded[/]")
        time.sleep(3)
        
        return translations
    except Exception as e:
        log_error(f"Failed to load language {lang_code}: {e}")
        console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] ERROR: Failed to load language - {e}[/]")
        console.print(f"[bold yellow][{datetime.now().strftime('%H:%M:%S')}] WARNING: Falling back to English[/]")
        time.sleep(3)
        
        return BASE_STRINGS