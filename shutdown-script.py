import os
from winotify import Notification
from datetime import datetime
import time

toast = Notification(app_id="Shutdown Script",
    title="Shutdown Script",
    msg="Spíš?",
    duration="short")

toast.add_actions(label="Jsem vzhůru", awake = True)

def shutdown():
    os.system("shutdown /s /t 0")

def check_time():
    now = datetime.now()
    if now.hour == 23 and now.minute == 59:
        return True
    else:
        return False
    
while True:
    if check_time():
        toast.show()
        time.sleep(60)
    time.sleep(1)
