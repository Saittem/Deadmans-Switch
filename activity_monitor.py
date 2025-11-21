from pynput import keyboard, mouse
import time

import notifier as _notifier
import config as _config
import utils as _utils

last_activity = time.time()
inactive = False
listeners = []

def update_activity(*_):
    global last_activity, inactive
    last_activity = time.time()

    # If the user was inactive and now active again
    if inactive:
        print("User active again.")
        inactive = False

def activity_watcher():
    global inactive
    while not _utils.STOP_FLAG:
        time.sleep(1)
        if not inactive and (time.time() - last_activity > _config.load_config()["inactivity_threshold"]):
            inactive = True
            _notifier.send_notification()
    
    print("Activity watcher stopped.")
    stop_listeners()

def start_listeners():
    global listeners
    stop_listeners()  # Stop any existing listeners first
    
    kb_listener = keyboard.Listener(on_press=update_activity, on_release=update_activity)
    mouse_listener = mouse.Listener(on_move=update_activity, on_click=update_activity, on_scroll=update_activity)
    
    kb_listener.start()
    mouse_listener.start()
    
    listeners = [kb_listener, mouse_listener]
    print("Activity listeners started.")

def stop_listeners():
    global listeners
    for listener in listeners:
        listener.stop()
    listeners = []
    if listeners:
        print("Activity listeners stopped.")