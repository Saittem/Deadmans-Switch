from pystray import Icon, MenuItem, Menu
import threading

import utils as _utils
import monitor as _monitor
import settings_window as _settings

def on_awake_clicked():
    _utils.set_clicked_flag()
    _utils.log_click_time("tray menu")

def on_exit(icon):
    _utils.STOP_FLAG = True
    print("Tray icon stopped.")
    icon.stop()

def run_tray():
    threading.Thread(target=_monitor.monitor_loop, daemon=True).start()

    icon = Icon("WakeChecker", icon=_utils.create_icon_image(), menu=Menu(
        MenuItem("I'm Awake", on_awake_clicked),
        MenuItem("Settings", _settings.open_settings),
        MenuItem("Exit", on_exit)
    ))
    print("Tray icon running.")
    icon.run()
