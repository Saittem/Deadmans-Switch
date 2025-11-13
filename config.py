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

def save_config(target_time, notification_duration, notification_interval, script_version):

    global CONFIG

    CONFIG["target_time"] = target_time
    CONFIG["notification_duration"] = int(notification_duration)
    CONFIG["notification_interval"] = int(notification_interval)
    CONFIG["script_version"] = script_version

    with open(CONFIG_PATH, "w") as f:
        json.dump(CONFIG, f, indent=4)

