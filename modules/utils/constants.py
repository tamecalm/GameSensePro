"""
Constants used throughout the application.
"""

import os

# File paths
DATA_DIR = "data"
DEVICE_FILE = f"{DATA_DIR}/device_info.txt"
RESULT_TXT = f"{DATA_DIR}/sensitivity_result.txt"
RESULT_JSON = f"{DATA_DIR}/sensitivity_result.json"
FEEDBACK_FILE = f"{DATA_DIR}/feedback_log.json"
STATS_FILE = f"{DATA_DIR}/stats.json"
DEVICE_MAPPING_FILE = f"{DATA_DIR}/device_mapping.json"
SESSION_FILE = f"{DATA_DIR}/session.json"
LOG_FILE = f"{DATA_DIR}/logs.txt"

# Game settings with modes and max sensitivity
GAME_SETTINGS = {
    "Blood Strike": {"cap": 300, "modes": ["Battle Royale", "Team Deathmatch"]},
    "Free Fire": {"cap": 100, "modes": ["Battle Royale", "Clash Squad"]},
    "Call of Duty Mobile": {"cap": 300, "modes": ["Battle Royale", "Multiplayer"]},
    "Delta Force": {"cap": 200, "modes": ["Havoc Warfare", "Black Hawk Down"]},
    "PUBG Mobile": {"cap": 300, "modes": ["Classic Royale", "Team Deathmatch"]}
}

# Default language
DEFAULT_LANGUAGE = "en"

# Translation API URL (replace with actual translation API)
TRANSLATION_API_URL = "https://api.mymemory.translated.net/get"