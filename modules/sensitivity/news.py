"""
Game news and community feedback utilities for the application.
"""

import time
from datetime import datetime
from rich.console import Console
from rich.panel import Panel

from modules.ui.display import clear_screen

console = Console()

def fetch_game_news(game, mode):
    """
    Fetches and displays game news and community feedback.
    
    Args:
        game (str): The selected game.
        mode (str): The selected game mode.
        
    Returns:
        dict: Adjustment factors based on community sentiment.
    """
    clear_screen()
    mode_display = f" ({mode})" if mode else ""
    
    console.print(Panel(
        f"[bold magenta]=== FETCHING NEWS FOR {game.upper()}{mode_display} ===[/]\n"
        f"[bold cyan][Started at {datetime.now().strftime('%H:%M:%S')}][/]\n"
        "Fetching community posts for 15 seconds...",
        title="News Fetch",
        border_style="magenta"
    ))
    
    # Mock community posts (replace with real API, e.g., X API)
    mock_news = {
        "Blood Strike": {
            "Battle Royale": [
                {"text": "New BR map update improves loot spawns!", "sentiment": "positive", "timestamp": "2025-05-25"},
                {"text": "BR mode lag issues reported on low-end devices", "sentiment": "negative", "timestamp": "2025-05-24"},
                {"text": "Community loves the new BR weapon balance", "sentiment": "positive", "timestamp": "2025-05-23"}
            ],
            "Team Deathmatch": [
                {"text": "TDM now has faster respawns!", "sentiment": "positive", "timestamp": "2025-05-25"},
                {"text": "TDM matchmaking needs improvement", "sentiment": "negative", "timestamp": "2025-05-24"}
            ]
        },
        "Free Fire": {
            "Battle Royale": [
                {"text": "BR ranked mode gets new rewards!", "sentiment": "positive", "timestamp": "2025-05-25"},
                {"text": "BR mode hitreg issues persist", "sentiment": "negative", "timestamp": "2025-05-24"},
                {"text": "New BR character skills are OP", "sentiment": "positive", "timestamp": "2025-05-23"}
            ],
            "Clash Squad": [
                {"text": "Clash Squad meta favors snipers", "sentiment": "neutral", "timestamp": "2025-05-25"},
                {"text": "Clash Squad map rotation updated", "sentiment": "positive", "timestamp": "2025-05-24"}
            ]
        },
        "Call of Duty Mobile": {
            "Battle Royale": [
                {"text": "BR mode gets Black Ops 6 integration", "sentiment": "positive", "timestamp": "2025-05-25"},
                {"text": "BR server issues during peak hours", "sentiment": "negative", "timestamp": "2025-05-24"}
            ],
            "Multiplayer": [
                {"text": "New MP maps are a hit!", "sentiment": "positive", "timestamp": "2025-05-25"},
                {"text": "MP aim assist needs tweaking", "sentiment": "negative", "timestamp": "2025-05-24"}
            ]
        },
        "Delta Force": {
            "Havoc Warfare": [
                {"text": "Havoc Warfare mode adds artillery strikes", "sentiment": "positive", "timestamp": "2025-05-25"},
                {"text": "Havoc Warfare balance issues with vehicles", "sentiment": "negative", "timestamp": "2025-05-24"},
                {"text": "Community praises Havoc Warfare operators", "sentiment": "positive", "timestamp": "2025-05-23"}
            ],
            "Black Hawk Down": [
                {"text": "Solo mode added to Black Hawk Down!", "sentiment": "positive", "timestamp": "2025-05-22"},
                {"text": "Black Hawk Down campaign pacing too slow", "sentiment": "negative", "timestamp": "2025-05-21"}
            ]
        },
        "PUBG Mobile": {
            "Classic Royale": [
                {"text": "Classic mode gets new anti-cheat measures", "sentiment": "positive", "timestamp": "2025-05-25"},
                {"text": "Classic Royale lag in high-ping regions", "sentiment": "negative", "timestamp": "2025-05-24"},
                {"text": "New Classic Royale skins released", "sentiment": "positive", "timestamp": "2025-05-23"}
            ],
            "Team Deathmatch": [
                {"text": "TDM mode now has faster pacing", "sentiment": "positive", "timestamp": "2025-05-25"},
                {"text": "TDM weapon balance needs work", "sentiment": "negative", "timestamp": "2025-05-24"}
            ]
        }
    }
    
    # Get news for the selected game
    if mode and mode in mock_news.get(game, {}):
        news_items = mock_news[game][mode][:7]  # Max 7 items for 15 seconds
    elif game in mock_news:
        # If mode is not found or empty, combine all news for the game
        news_items = []
        for mode_news in mock_news[game].values():
            news_items.extend(mode_news)
        news_items = news_items[:7]  # Max 7 items
    else:
        news_items = []
    
    if not news_items:
        console.print(f"[bold yellow][{datetime.now().strftime('%H:%M:%S')}] WARNING: No news found for {game}{mode_display}[/]")
        time.sleep(3)
        return {"cam_adjust": 1.0, "fire_adjust": 1.0, "gyro_adjust": 1.0}
    
    # Display news and calculate sentiment adjustment
    start_time = time.time()
    sentiment_sum = 0
    count = 0
    
    for item in news_items:
        if time.time() - start_time > 15:
            break
        
        clear_screen()
        console.print(Panel(
            f"[bold magenta]=== COMMUNITY NEWS FOR {game.upper()}{mode_display} ===[/]\n"
            f"[bold cyan][Time: {datetime.now().strftime('%H:%M:%S')}][/]\n"
            f"Post: {item['text']}\n"
            f"Sentiment: {item['sentiment'].capitalize()}\n"
            f"Date: {item['timestamp']}",
            title="News Update",
            border_style="magenta"
        ))
        
        sentiment = {"positive": 0.05, "neutral": 0.0, "negative": -0.05}.get(item["sentiment"], 0.0)
        sentiment_sum += sentiment
        count += 1
        
        time.sleep(2)  # Display each for 2 seconds
    
    # Calculate adjustment factor based on sentiment
    adjust = 1.0 + (sentiment_sum / count) if count > 0 else 1.0
    
    console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] Success: News fetched, sensitivity adjust: {adjust:.2f}x[/]")
    time.sleep(3)
    
    return {"cam_adjust": adjust, "fire_adjust": adjust, "gyro_adjust": adjust}