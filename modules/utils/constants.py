"""
Constants used throughout the application.
"""

import os
import json
from datetime import datetime

# File paths
DATA_DIR = "data"
GAMES_DIR = {
    "Blood Strike": f"{DATA_DIR}/blood_strike",
    "Free Fire": f"{DATA_DIR}/free_fire",
    "Call of Duty Mobile": f"{DATA_DIR}/cod_mobile",
    "Delta Force": f"{DATA_DIR}/delta_force",
    "PUBG Mobile": f"{DATA_DIR}/pubg_mobile"
}

# Common files
DEVICE_FILE = f"{DATA_DIR}/device_info.txt"
DEVICE_MAPPING_FILE = f"{DATA_DIR}/device_mapping.json"
SESSION_FILE = f"{DATA_DIR}/session.json"
LOG_FILE = f"{DATA_DIR}/logs.txt"
BENCHMARK_FILE = f"{DATA_DIR}/benchmark_results.json"
COMMUNITY_DB_FILE = f"{DATA_DIR}/community_settings.json"
UPDATE_CHECK_FILE = f"{DATA_DIR}/update_info.json"
FEEDBACK_FILE = f"{DATA_DIR}/feedback.json"
RESULT_TXT = f"{DATA_DIR}/sensitivity_result.txt"
RESULT_JSON = f"{DATA_DIR}/sensitivity_result.json"
STATS_FILE = f"{DATA_DIR}/stats.json"

# Game-specific file paths
def get_game_path(game):
    """Get file paths for a specific game."""
    game_dir = GAMES_DIR[game]
    return {
        "device": f"{game_dir}/device_info.txt",
        "result_txt": f"{game_dir}/sensitivity_result.txt",
        "result_json": f"{game_dir}/sensitivity_result.json",
        "feedback": f"{game_dir}/feedback_log.json",
        "stats": f"{game_dir}/stats.json",
        "benchmark": f"{game_dir}/benchmark.json",
        "tutorial": f"{game_dir}/tutorial_progress.json"
    }

# Game settings with max sensitivity
GAME_SETTINGS = {
    "Blood Strike": {
        "cap": 300,
        "menu_path": "Settings > Controls > Sensitivity",
        "recommended_settings": {
            "aim_assist": "Enhanced",
            "gyro_mode": "Always On",
            "fire_mode": "Automatic"
        }
    },
    "Free Fire": {
        "cap": 100,
        "menu_path": "Settings > Sensitivity",
        "recommended_settings": {
            "aim_assist": "On",
            "precise_on_scope": "On",
            "quick_weapon_switch": "On"
        }
    },
    "Call of Duty Mobile": {
        "cap": 300,
        "menu_path": "Settings > Sensitivity",
        "recommended_settings": {
            "aim_assist": "On",
            "perspective": "FPS",
            "ads_mode": "Hold"
        }
    },
    "Delta Force": {
        "cap": 200,
        "menu_path": "Options > Controls > Sensitivity",
        "recommended_settings": {
            "aim_assist": "Standard",
            "auto_sprint": "On",
            "tactical_sprint": "Double Tap"
        }
    },
    "PUBG Mobile": {
        "cap": 300,
        "menu_path": "Settings > Sensitivity",
        "recommended_settings": {
            "aim_assist": "On",
            "peek_mode": "Hold",
            "gyro_mode": "Scope On"
        }
    }
}

# GitHub repository info for updates
GITHUB_REPO = "https://api.github.com/repos/tamecalm/gamesensepro"

def get_current_version():
    """Read the current version from UPDATE_CHECK_FILE or return default."""
    default_version = "1.0.9"
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        if os.path.exists(UPDATE_CHECK_FILE):
            with open(UPDATE_CHECK_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                version = data.get("current_version")
                if version and isinstance(version, str) and version.count(".") == 2:
                    return version
        # Initialize UPDATE_CHECK_FILE with default version
        with open(UPDATE_CHECK_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "current_version": default_version,
                "last_checked": datetime.now().isoformat()
            }, f, indent=2)
        return default_version
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error reading version: {e}. Using default version {default_version}")
        return default_version

CURRENT_VERSION = get_current_version()

# Translation API URL
TRANSLATION_API_URL = "https://api.mymemory.translated.net/get"

# Default language
DEFAULT_LANGUAGE = "en"

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