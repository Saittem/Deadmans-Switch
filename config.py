import os
import json
from datetime import datetime

CONFIG = None
CONFIG_PATH = "config.json"
LOG_FILE_PATH = "wake_log.txt"

# ------------------- Config Functions ------------------- #
def load_config():
    """   
    Loads configuration settings from a JSON file (config.json).
    If the file does not exist, it creates it with default settings.
    Default settings include a start time, notification duration, and interval.
    """

    global CONFIG

    default_config = {"start_time": "02:00", "notification_duration": 60, "notification_interval": 600}
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "w") as f:
            json.dump(default_config, f)
        return default_config
    with open(CONFIG_PATH, "r") as f:
        CONFIG = json.load(f)

def save_config(start_time, duration, interval):
    """
    Saves the provided configuration settings (start time, notification duration, and interval)
    to the config.json file in JSON format.
    """

    global CONFIG

    CONFIG = {
        "start_time": start_time,
        "notification_duration": int(duration),
        "notification_interval": int(interval)
    }
    with open(CONFIG_PATH, "w") as f:
        json.dump(CONFIG, f)

# ------------------- Logging Function ------------------- #
def log_click_time(source="notification"):
    """
    Logs the current timestamp to the log file (wake_log.txt), indicating
    when the user confirmed being "Awake".
    Types of sources include "notification" and "tray menu".
    """

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] User clicked 'I'm Awake' via {source}.\n"
    try:
        with open(LOG_FILE_PATH, "a") as f:
            f.write(log_message)
        print(f"Logged: {log_message.strip()}")
    except Exception as e:
        print(f"Error writing to log file: {e}")