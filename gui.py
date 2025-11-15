import webview
import config

HTML_PATH = "web/index.html"

def open_settings():
    config.load_config()
    webview.start()

class Api:

    def save(self, target_time_value, notification_duration_value, notification_interval_value, script_version_value):
        print("Saving settings...")
        target_time = target_time_value
        notification_duration = notification_duration_value
        notification_interval = notification_interval_value
        script_version = script_version_value
        config.save_config(target_time, notification_duration, notification_interval, script_version)

api = Api()
webview.create_window(
    title="Settings",
    url=HTML_PATH,
    width=400,
    height=300,
    js_api=api
)

if __name__ == "__main__":
    webview.start()