import time
import threading
from datetime import datetime, timedelta
import os

from config import load_config
from utils import CLICKED_FLAG, STOP_FLAG
from notifier import send_notification

def wait_until_time(target):
    hour, minute = map(int, target.split(":"))
    now = datetime.now()
    target_dt = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

    if target_dt <= now:
        target_dt += timedelta(days=1)

    while datetime.now() < target_dt and not STOP_FLAG:
        time.sleep(1)

def monitor_loop():
    global CLICKED_FLAG
    config = load_config()

    wait_until_time(config["target_time"])

    while not STOP_FLAG:
        CLICKED_FLAG = False
        send_notification()

        if not CLICKED_FLAG and not STOP_FLAG:
            os.system("shutdown /s /t 15")
            break

        time.sleep(config["notification_interval"])

def restart_monitor_loop_after_delay():
    global STOP_FLAG
    time.sleep(1)
    STOP_FLAG = False
    threading.Thread(target=monitor_loop, daemon=True).start()
