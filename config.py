import json
import os

CONFIG_PATH = "config.json"

def load_config():

    global CONFIG

    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            CONFIG = json.load(f)
    else:
        CONFIG = {
            "target_time": "02:00",
            "notification_duration": 60,
            "notification_interval": 600,
            "script_version": "notification"
        }
        with open(CONFIG_PATH, "w") as f:
            json.dump(CONFIG, f, indent=4)


