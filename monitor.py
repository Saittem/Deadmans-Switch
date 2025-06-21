import os
import json
import time
import threading
from datetime import datetime, timedelta
from winotify import Notification, audio
from http.server import BaseHTTPRequestHandler, HTTPServer

CONFIG_PATH = "config.json"
CLICKED_FLAG = False

# loads config from config.json file
def load_config():
    default_config = {"start_time": "02:00", "notification_duration": 60, "notification_interval": 600}
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "w") as f:
            json.dump(default_config, f)
        return default_config
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

# handles click event in notification
class ClickHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global CLICKED_FLAG
        if self.path == "/click":
            CLICKED_FLAG = True
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Awake notification clicked.")
        else:
            self.send_response(204)
            self.end_headers()

def run_http_server():
    server = HTTPServer(("localhost", 8888), ClickHandler)
    server.serve_forever()

# waits until local time matches the one from config.json
def wait_until_time(target_str):
    target_hour, target_minute = map(int, target_str.split(":"))
    print(f"Waiting for start time: {target_str}")
    while True:
        now = datetime.now()
        if now.hour == target_hour and now.minute == target_minute:
            break
        time.sleep(20)  # check every 20 seconds

# sends notification
def send_notification():
    toast = Notification(app_id="Wake Check",
                         title="Are you awake?",
                         msg="Click the button or your PC will shut down in 1 minute.",
                         duration="long")
    toast.set_audio(audio.Default, loop=False)
    toast.add_actions(label="I'm Awake!", launch="http://localhost:8888/click")
    toast.show()

# main function that is called at the start of the script
def main():
    global CLICKED_FLAG
    config = load_config()
    start_time = (datetime.now() + timedelta(minutes=1)).strftime("%H:%M")
    #config["start_time"]
    duration = config["notification_duration"]
    interval = config["notification_interval"]

    # Start HTTP listener thread
    threading.Thread(target=run_http_server, daemon=True).start()

    wait_until_time(start_time)

    while True:
        CLICKED_FLAG = False
        send_notification()
        print("Notification sent. Waiting for click...")

        for _ in range(duration):
            if CLICKED_FLAG:
                print("User clicked the button. Waiting for interval.")
                time.sleep(interval)
                #
                # !!! when user click the button the localhost asks for favicon, FIX !!!
                # !!! the localhost doesn't close after the click event is handled, maybe it didn't because of the error above !!!
                #
                break
            time.sleep(1)
        else:
            print("No response. Shutting down.")
            os.system("shutdown /s /t 1")
            break

# calls main function
if __name__ == "__main__":
    main()
