"""
Sensitivity storage utilities for the application.
"""

import json
import time
from datetime import datetime
from rich.console import Console

from modules.utils.constants import GAMES_DIR
from modules.utils.logger import log_error
from modules.stats.manager import update_stats

console = Console()

def save_results(info, cam, fire, gyro, player_style, game, mode):
    """
    Saves sensitivity results to files.
    
    Args:
        info (dict): Device information.
        cam (dict): Camera sensitivity values.
        fire (dict): Firing sensitivity values.
        gyro (dict): Gyro sensitivity values.
        player_style (dict): Player style information.
        game (str): The selected game.
        mode (str): The selected game mode.
    """
    try:
        mode_display = f" ({mode})" if mode else ""
        game_dir = GAMES_DIR[game]
        result_txt = f"{game_dir}/sensitivity_result.txt"
        result_json = f"{game_dir}/sensitivity_result.json"
        
        # Save as text file
        with open(result_txt, "w") as f:
            f.write(f"=== {game.upper()}{mode_display} SENSITIVITY SETTINGS ===\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write(f"Device Information:\n")
            for k, v in info.items():
                f.write(f"  {k}: {v}\n")
            
            f.write(f"\nPlayer Style: {player_style['fingers']} fingers, {player_style['skill']} skill, "
                   f"aiming with {player_style['aiming_finger']}, {'claw' if player_style['claw_grip'] else 'no claw'} grip\n")
            
            f.write("\n=== Camera Sensitivity ===\n")
            for k, v in cam.items():
                f.write(f"{k}: {v}\n")
            
            f.write("\n=== Firing Sensitivity ===\n")
            for k, v in fire.items():
                f.write(f"{k}: {v}\n")
            
            if gyro:
                f.write("\n=== Gyro Sensitivity ===\n")
                for k, v in gyro.items():
                    f.write(f"{k}: {v}\n")
        
        # Save as JSON file
        result = {
            "device": info,
            "player_style": player_style,
            "game": game,
            "mode": mode,
            "camera_sensitivity": cam,
            "firing_sensitivity": fire,
            "gyro_sensitivity": gyro if gyro else "Not Available",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open(result_json, "w") as f:
            json.dump(result, f, indent=2)
        
        # Update statistics
        update_stats(result)
        
        console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] Success: Results saved to {result_txt} and {result_json}[/]")
    except Exception as e:
        log_error(f"Failed to save results: {e}")
        console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] ERROR: Failed to save results - {e}[/]")
    
    time.sleep(3)