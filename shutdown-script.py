import os
from winotify import Notification

toast = Notification(app_id="Shutdown Script",
    title="Shutdown Script",
    msg="Spíš?",
    duration="short")

toast.add_actions(label="Jsem vzhůru")

def shutdown():
    os.system("shutdown /s /t 0")

toast.show()