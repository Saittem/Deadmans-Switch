import webview
import config

HTML_PATH = "web/index.html"
webview.create_window("Settings", HTML_PATH, width=400, height=300)

def open_settings():
    config.load_config()
    webview.start()

def save():
    target_time = webview.get_value("target_time")
    notification_duration = webview.get_value("notification_duration")
    notification_interval = webview.get_value("notification_interval")
    script_version = webview.get_value("script_version")
    config.save_config(target_time, notification_duration, notification_interval, config.CONFIG["script_version"])


if __name__ == "__main__":
    webview.start()