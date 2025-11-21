import time
import threading
from datetime import datetime, timedelta

import config as _config
import utils as _ituls
import notifier as _notifier

def wait_until_time(target):
    hour, minute = map(int, target.split(":"))
    now = datetime.now()
    target_dt = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

    print(f"Waiting until {target}")

    if target_dt <= now:
        target_dt += timedelta(days=1)

    while datetime.now() < target_dt and not _ituls.STOP_FLAG:
        time.sleep(1)

def monitor_loop():
    config = _config.load_config()

    #wait_until_time(config["target_time"])
    wait_until_time((datetime.now() + timedelta(minutes=1)).strftime("%H:%M"))

    while not _ituls.STOP_FLAG:
        _ituls.CLICKED_FLAG = False
        _notifier.send_notification()

        if not _ituls.CLICKED_FLAG and not _ituls.STOP_FLAG:
            print("Shutting down...")
            #os.system("shutdown /s /t 15")
            break

        time.sleep(config["notification_interval"])
    
    print("Monitor loop stopped.")

def restart_monitor_loop_after_delay():
    time.sleep(1)
    _ituls.STOP_FLAG = False
    threading.Thread(target=monitor_loop, daemon=True).start()