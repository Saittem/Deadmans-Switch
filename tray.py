from pystray import Icon, MenuItem, Menu
from utils import create_icon_image, set_clicked_flag, log_click_time, STOP_FLAG
from monitor import monitor_loop
from settings_window import open_settings
import threading

def on_awake_clicked():
    set_clicked_flag()
    log_click_time("tray menu")

def on_exit(icon):
    global STOP_FLAG
    STOP_FLAG = True
    icon.stop()

def run_tray():
    threading.Thread(target=monitor_loop, daemon=True).start()

    icon = Icon("WakeChecker", icon=create_icon_image(), menu=Menu(
        MenuItem("I'm Awake", on_awake_clicked),
        MenuItem("Settings", open_settings),
        MenuItem("Exit", on_exit)
    ))
    icon.run()
