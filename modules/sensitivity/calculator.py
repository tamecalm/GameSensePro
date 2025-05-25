"""
Sensitivity calculation utilities for the application.
"""

import math
import time
import os
import json
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt

from modules.ui.display import clear_screen
from modules.utils.constants import GAME_SETTINGS, FEEDBACK_FILE
from modules.utils.logger import log_error
from modules.sensitivity.news import fetch_game_news

console = Console()

def calculate_sensitivity(info, player_style, game, mode):
    """
    Calculates sensitivity settings based on device info and player style.
    
    Args:
        info (dict): Device information.
        player_style (dict): Player style information.
        game (str): The selected game.
        mode (str): The selected game mode.
        
    Returns:
        tuple: Camera, firing, and gyro sensitivity settings.
    """
    clear_screen()
    mode_display = f" ({mode})" if mode else ""
    
    console.print(Panel(
        f"[bold magenta]=== CALCULATING SENSITIVITY FOR {game.upper()}{mode_display} ===[/]\n"
        f"[bold cyan][Started at {datetime.now().strftime('%H:%M:%S')}][/]",
        title="Sensitivity Calculation",
        border_style="magenta"
    ))
    
    try:
        # Base constants
        BASE_SENS = 150
        DPI_SCALE = max(0.5, min(2.0, info["DPI"] / 440))
        REFRESH_SCALE = max(0.8, min(1.5, info["RefreshRate"] / 120))
        SCREEN_SCALE = max(0.7, min(1.3, info["ScreenSize"] / 6.67))
        MAX_SENS = GAME_SETTINGS[game]["cap"]
        
        # Adjustment factors based on player style
        finger_adjust = {
            1: 1.1, 
            2: 1.0, 
            3: 0.9 if player_style["claw_grip"] else 0.85
        }
        
        aiming_adjust = {
            "thumb": 1.1, 
            "index": 1.0, 
            "other": 0.95
        }
        
        skill_adjust = {
            "beginner": 0.9, 
            "intermediate": 1.0, 
            "advanced": 1.15
        }
        
        # Combined adjustment factor
        style_adjust = (finger_adjust[player_style["fingers"]] * 
                       aiming_adjust[player_style["aiming_finger"]] * 
                       skill_adjust[player_style["skill"]])
        
        # Calculate base sensitivity
        adjusted_base = BASE_SENS * (1 / DPI_SCALE) * REFRESH_SCALE * SCREEN_SCALE * style_adjust
        adjusted_base = max(50, min(MAX_SENS * 0.9, adjusted_base))
        
        # Calculate camera sensitivities
        cam_sense = {
            "No ADS": round(adjusted_base, 1),
            "Iron Sight": round(adjusted_base * 0.8, 1),
            "2x Scope": round(adjusted_base * 0.7, 1),
            "3x Scope": round(adjusted_base * 0.65, 1),
            "4x Scope": round(adjusted_base * 0.6, 1),
            "6x Scope": round(adjusted_base * 0.55, 1),
            "8x Scope": round(adjusted_base * 0.5, 1)
        }
        
        # Calculate firing sensitivities
        fire_sense = {
            "No ADS": round(adjusted_base * 1.1, 1),
            "Iron Sight": round(adjusted_base * 0.85, 1),
            "2x Scope": round(adjusted_base * 0.75, 1),
            "3x Scope": round(adjusted_base * 0.7, 1),
            "4x Scope": round(adjusted_base * 0.65, 1),
            "6x Scope": round(adjusted_base * 0.6, 1),
            "8x Scope": round(adjusted_base * 0.55, 1)
        }
        
        # Calculate gyro sensitivities (if applicable)
        gyro_sense = None
        if info["GyroRange"] is not None:
            GYRO_SCALE = min(1.5, max(0.5, math.log1p(info["GyroRange"]) / 2))
            gyro_sense = {
                "No ADS": round(adjusted_base * 0.9 * GYRO_SCALE, 1),
                "Iron Sight": round(adjusted_base * 0.75 * GYRO_SCALE, 1),
                "2x Scope": round(adjusted_base * 0.65 * GYRO_SCALE, 1),
                "3x Scope": round(adjusted_base * 0.6 * GYRO_SCALE, 1),
                "4x Scope": round(adjusted_base * 0.55 * GYRO_SCALE, 1),
                "6x Scope": round(adjusted_base * 0.5 * GYRO_SCALE, 1),
                "8x Scope": round(adjusted_base * 0.45 * GYRO_SCALE, 1)
            }
        
        # Adjust based on game news
        news_adjust = fetch_game_news(game, mode)
        for scope in cam_sense:
            cam_sense[scope] = round(min(cam_sense[scope] * news_adjust.get("cam_adjust", 1.0), MAX_SENS), 1)
            fire_sense[scope] = round(min(fire_sense[scope] * news_adjust.get("fire_adjust", 1.0), MAX_SENS), 1)
            if gyro_sense:
                gyro_sense[scope] = round(min(gyro_sense[scope] * news_adjust.get("gyro_adjust", 1.0), MAX_SENS), 1)
        
        # Apply feedback adjustments if available
        if os.path.exists(FEEDBACK_FILE):
            try:
                with open(FEEDBACK_FILE, "r") as f:
                    feedback = json.load(f)
                for scope in cam_sense:
                    cam_sense[scope] = round(min(cam_sense[scope] * feedback.get("cam_adjust", 1.0), MAX_SENS), 1)
                    fire_sense[scope] = round(min(fire_sense[scope] * feedback.get("fire_adjust", 1.0), MAX_SENS), 1)
                    if gyro_sense:
                        gyro_sense[scope] = round(min(gyro_sense[scope] * feedback.get("gyro_adjust", 1.0), MAX_SENS), 1)
            except Exception as e:
                log_error(f"Failed to apply feedback: {e}")
                console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] ERROR: Failed to apply feedback - {e}[/]")
        
        # Preview and calibrate sensitivities
        cam_sense, fire_sense, gyro_sense = preview_sensitivity(cam_sense, fire_sense, gyro_sense, game)
        cam_sense, fire_sense, gyro_sense = calibrate_sensitivity(cam_sense, fire_sense, gyro_sense, game)
        
        console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] Success: Sensitivity calculated[/]")
        time.sleep(3)
        
        return cam_sense, fire_sense, gyro_sense
    except Exception as e:
        log_error(f"Failed to calculate sensitivity: {e}")
        console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] ERROR: Failed to calculate sensitivity - {e}[/]")
        return None, None, None

def preview_sensitivity(cam, fire, gyro, game):
    """
    Allows the user to preview and adjust sensitivity values.
    
    Args:
        cam (dict): Camera sensitivity values.
        fire (dict): Firing sensitivity values.
        gyro (dict): Gyro sensitivity values.
        game (str): The selected game.
        
    Returns:
        tuple: Adjusted camera, firing, and gyro sensitivity settings.
    """
    clear_screen()
    console.print(Panel(
        f"[bold magenta]=== SENSITIVITY PREVIEW FOR {game.upper()} ===[/]\n"
        f"[bold cyan][Displayed at {datetime.now().strftime('%H:%M:%S')}][/]\n"
        "Review the calculated sensitivities. Enter a percentage to adjust (e.g., 110 for +10%, 90 for -10%) or 100 to keep as is.",
        title="Preview",
        border_style="magenta"
    ))
    
    adjustments = {}
    for scope in cam:
        gyro_text = f", Gyro: {gyro[scope]}" if gyro else ""
        adjustment = IntPrompt.ask(
            f"For {scope} (Camera: {cam[scope]}, Fire: {fire[scope]}{gyro_text}): ",
            default=100
        )
        adjustments[scope] = adjustment / 100.0
    
    for scope in cam:
        cam[scope] = round(min(cam[scope] * adjustments[scope], GAME_SETTINGS[game]["cap"]), 1)
        fire[scope] = round(min(fire[scope] * adjustments[scope], GAME_SETTINGS[game]["cap"]), 1)
        if gyro:
            gyro[scope] = round(min(gyro[scope] * adjustments[scope], GAME_SETTINGS[game]["cap"]), 1)
    
    console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] Success: Sensitivities adjusted[/]")
    time.sleep(3)
    
    return cam, fire, gyro

def calibrate_sensitivity(cam, fire, gyro, game):
    """
    Allows the user to calibrate sensitivity values.
    
    Args:
        cam (dict): Camera sensitivity values.
        fire (dict): Firing sensitivity values.
        gyro (dict): Gyro sensitivity values.
        game (str): The selected game.
        
    Returns:
        tuple: Calibrated camera, firing, and gyro sensitivity settings.
    """
    clear_screen()
    console.print(Panel(
        f"[bold magenta]=== SENSITIVITY CALIBRATION FOR {game.upper()} ===[/]\n"
        f"[bold cyan][Started at {datetime.now().strftime('%H:%M:%S')}][/]\n"
        f"After testing in {game}, do you find the sensitivity:\n1. Too High\n2. Too Low\n3. Just Right",
        title="Calibration",
        border_style="magenta"
    ))
    
    feedback = IntPrompt.ask("[bold yellow]Select (1-3)[/]", choices=["1", "2", "3"], default=3)
    
    adjust = 1.0
    if feedback == 1:
        adjust = 0.9
    elif feedback == 2:
        adjust = 1.1
    
    for scope in cam:
        cam[scope] = round(min(cam[scope] * adjust, GAME_SETTINGS[game]["cap"]), 1)
        fire[scope] = round(min(fire[scope] * adjust, GAME_SETTINGS[game]["cap"]), 1)
        if gyro:
            gyro[scope] = round(min(gyro[scope] * adjust, GAME_SETTINGS[game]["cap"]), 1)
    
    console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] Success: Calibration applied[/]")
    time.sleep(3)
    
    return cam, fire, gyro