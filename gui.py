import webview
import pystray
from PIL import Image, ImageDraw
import config

HTML_PATH = "web/index.html"


def create_image(width, height, color1, color2):
    # Generate an image and draw a pattern
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        (width // 2, 0, width, height // 2),
        fill=color2)
    dc.rectangle(
        (0, height // 2, width // 2, height),
        fill=color2)

    return image

def run_tray():
    print("Running tray...")

    icon = pystray.Icon(
        'test name',
        icon=create_image(64, 64, 'black', 'white')
    )

    menu = pystray.Menu(
        pystray.MenuItem('Open settings', lambda: open_settings()),
        pystray.MenuItem('Exit', lambda: icon.stop())
    )

    icon.menu = menu
    icon.run()


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
    run_tray()
