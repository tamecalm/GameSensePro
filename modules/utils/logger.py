"""
Logging utilities for the application.
"""

from datetime import datetime
import os
from modules.utils.constants import LOG_FILE

def log_error(message):
    """
    Logs an error message to the log file.
    
    Args:
        message (str): The error message to log.
    """
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    with open(LOG_FILE, "a") as log:
        log.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERROR: {message}\n")

def log_info(message):
    """
    Logs an info message to the log file.
    
    Args:
        message (str): The info message to log.
    """
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    with open(LOG_FILE, "a") as log:
        log.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] INFO: {message}\n")

def log_warning(message):
    """
    Logs a warning message to the log file.
    
    Args:
        message (str): The warning message to log.
    """
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    with open(LOG_FILE, "a") as log:
        log.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] WARNING: {message}\n")