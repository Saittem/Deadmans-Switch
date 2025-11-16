import os
import json

CONFIG_PATH = "config.json"

default_config = {
    "start_time": "02:00",
    "notification_duration": 60,
    "notification_interval": 600
}

def load_config():
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "w") as f:
            json.dump(default_config, f)
        return default_config
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def save_config(start_time, duration, interval):
    config = {
        "start_time": start_time,
        "notification_duration": int(duration),
        "notification_interval": int(interval)
    }
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f)
