"""
Device performance benchmarking utilities.
"""

import time
import json
import subprocess
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress

from modules.utils.constants import BENCHMARK_FILE
from modules.utils.logger import log_error
from modules.ui.display import clear_screen

console = Console()

def measure_frame_rate():
    """Measure device frame rate under load."""
    try:
        # Simulate game-like load
        frame_times = []
        start_time = time.time()
        frames = 0
        
        while time.time() - start_time < 5:  # 5-second test
            frame_start = time.time()
            # Simulate frame rendering with basic computation
            for _ in range(10000):
                _ = 1 + 1
            frame_time = time.time() - frame_start
            frame_times.append(frame_time)
            frames += 1
        
        avg_fps = frames / 5
        return avg_fps
    except Exception as e:
        log_error(f"Frame rate measurement failed: {e}")
        return None

def measure_touch_latency():
    """Measure touch input latency."""
    try:
        # Use dumpsys input to get touch stats
        output = subprocess.getoutput("dumpsys input")
        if "TouchLatency" in output:
            latency_lines = [line for line in output.split("\n") if "TouchLatency" in line]
            if latency_lines:
                # Extract average latency value
                latency = float(latency_lines[0].split()[-1])
                return latency
        return None
    except Exception as e:
        log_error(f"Touch latency measurement failed: {e}")
        return None

def run_benchmark():
    """Run complete device benchmark."""
    clear_screen()
    console.print(Panel(
        f"[bold magenta]=== DEVICE BENCHMARKING ===[/]\n"
        f"[bold cyan][Started at {datetime.now().strftime('%H:%M:%S')}][/]\n"
        "Running performance tests...",
        title="Benchmark",
        border_style="magenta"
    ))
    
    with Progress() as progress:
        task = progress.add_task("[cyan]Running benchmark...", total=100)
        
        # Measure frame rate
        progress.update(task, advance=30)
        fps = measure_frame_rate()
        
        # Measure touch latency
        progress.update(task, advance=30)
        latency = measure_touch_latency()
        
        # Calculate performance score
        progress.update(task, advance=40)
        score = calculate_performance_score(fps, latency)
        
        results = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "fps": fps,
            "touch_latency": latency,
            "performance_score": score
        }
        
        try:
            with open(BENCHMARK_FILE, "w") as f:
                json.dump(results, f, indent=2)
            console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}] Success: Benchmark results saved[/]")
        except Exception as e:
            log_error(f"Failed to save benchmark results: {e}")
            console.print(f"[bold red][{datetime.now().strftime('%H:%M:%S')}] ERROR: Failed to save benchmark results[/]")
        
        return results

def calculate_performance_score(fps, latency):
    """Calculate overall performance score."""
    if fps is None or latency is None:
        return None
    
    # Normalize FPS (60-120 range)
    fps_score = min(100, max(0, (fps - 60) / 0.6))
    
    # Normalize latency (0-100ms range)
    latency_score = min(100, max(0, 100 - latency))
    
    # Combined score (0-100)
    return round((fps_score + latency_score) / 2, 2)

def get_sensitivity_adjustment(score):
    """Get sensitivity adjustment based on performance score."""
    if score is None:
        return 1.0
    
    # Adjust sensitivity based on performance
    if score >= 80:
        return 1.1  # Higher sensitivity for better performance
    elif score <= 40:
        return 0.9  # Lower sensitivity for worse performance
    return 1.0