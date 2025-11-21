import os
import json

CONFIG_PATH = "config.json"

default_config = {
    "target_time": "02:00",
    "notification_duration": 60,
    "notification_interval": 600,
    "monitoring_variant": "notification",
    "inactivity_threshold": 900
}

def load_config():
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "w") as f:
            json.dump(default_config, f)
        print("Loaded default config.")
        return default_config
    with open(CONFIG_PATH, "r") as f:
        print("Loaded config.")
        return json.load(f)

def save_config(start_time, duration, interval, version, inactivity_threshold):
    config = {
        "target_time": start_time,
        "notification_duration": int(duration),
        "notification_interval": int(interval),
        "monitoring_variant": version,
        "inactivity_threshold": int(inactivity_threshold)
    }
    with open(CONFIG_PATH, "w") as f:
        print("Saved config.")
        json.dump(config, f)