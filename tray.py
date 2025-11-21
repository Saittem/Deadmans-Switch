from pystray import Icon, MenuItem, Menu
import threading

import utils as _utils
import monitor as _monitor
import activity_monitor as _activity
import settings_window as _settings
import config as _config

current_monitor_thread = None

def start_monitoring():
    global current_monitor_thread
    
    config = _config.load_config()
    variant = config["monitoring_variant"]
    
    if variant == "notification":
        current_monitor_thread = threading.Thread(target=_monitor.monitor_loop, daemon=True)
        current_monitor_thread.start()
        print("Started notification monitoring.")
    else:
        _activity.start_listeners()
        current_monitor_thread = threading.Thread(target=_activity.activity_watcher, daemon=True)
        current_monitor_thread.start()
        print("Started activity monitoring.")

def restart_monitoring():
    """Stop current monitoring and start the new variant"""
    _utils.STOP_FLAG = True
    _activity.stop_listeners()  # Stop activity listeners if they're running
    
    # Wait a moment for the current thread to stop
    if current_monitor_thread and current_monitor_thread.is_alive():
        current_monitor_thread.join(timeout=2)
    
    # Reset flag and start new monitoring
    _utils.STOP_FLAG = False
    start_monitoring()

def on_awake_clicked():
    _utils.set_clicked_flag()
    _utils.log_click_time("tray menu")

def on_exit(icon):
    _utils.STOP_FLAG = True
    _activity.stop_listeners()
    print("Tray icon stopped.")
    icon.stop()

def run_tray():
    start_monitoring()

    icon = Icon("WakeChecker", icon=_utils.create_icon_image(), menu=Menu(
        MenuItem("I'm Awake", on_awake_clicked),
        MenuItem("Settings", _settings.open_settings),
        MenuItem("Exit", on_exit)
    ))
    print("Tray icon running.")
    icon.run()