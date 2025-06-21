import os
import json
import time
import threading
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
from pystray import Icon, MenuItem, Menu
from winotify import Notification, audio
from PIL import Image, ImageDraw

CONFIG_PATH = "config.json"
CLICKED_FLAG = False
STOP_FLAG = False

# ------------------- Config Functions ------------------- #
def load_config():
    default_config = {"start_time": "02:00", "notification_duration": 60, "notification_interval": 600}
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "w") as f:
            json.dump(default_config, f)
        return default_config
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def save_config(start_time, duration, interval):
    config = {
        "start_time": start_time,
        "notification_duration": int(duration),
        "notification_interval": int(interval)
    }
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f)

# ------------------- Tray Image ------------------- #
def create_icon_image():
    image = Image.new("RGB", (64, 64), "blue")
    draw = ImageDraw.Draw(image)
    draw.ellipse((16, 16, 48, 48), fill="white")
    return image

# ------------------- Notification ------------------- #
def send_notification():
    toast = Notification(app_id="Wake Check",
                         title="Are you awake?",
                         msg="Click 'I’m Awake' from the tray or your PC will shut down.",
                         duration="long")
    toast.set_audio(audio.Default, loop=False)
    toast.show()

# ------------------- Wait Until Time ------------------- #
def wait_until_time(target_str):
    target_hour, target_minute = map(int, target_str.split(":"))
    print(f"Waiting until {target_str} to start monitoring...")
    while True:
        now = datetime.now()
        if now.hour == target_hour and now.minute == target_minute:
            break
        if STOP_FLAG:
            return
        time.sleep(20)

# ------------------- Monitoring Thread ------------------- #
def monitor_loop():
    global CLICKED_FLAG
    config = load_config()
    wait_until_time(config["start_time"])

    while not STOP_FLAG:
        CLICKED_FLAG = False
        send_notification()
        print("Notification sent. Waiting for tray confirmation...")

        for _ in range(config["notification_duration"]):
            if CLICKED_FLAG or STOP_FLAG:
                break
            time.sleep(1)

        if not CLICKED_FLAG and not STOP_FLAG:
            print("No response. Shutting down.")
            os.system("shutdown /s /t 1")
            break

        print(f"User confirmed. Sleeping for {config['notification_interval']} seconds.")
        time.sleep(config["notification_interval"])

# ------------------- Tray Menu Handlers ------------------- #
def on_awake_clicked(icon, item):
    global CLICKED_FLAG
    print("User clicked 'I'm Awake'")
    CLICKED_FLAG = True

def on_exit(icon, item):
    global STOP_FLAG
    STOP_FLAG = True
    icon.stop()
    print("Exiting...")

def open_settings(icon=None, item=None):
    config = load_config()

    def save():
        try:
            save_config(start_time_entry.get(), duration_entry.get(), interval_entry.get())
            messagebox.showinfo("Saved", "Settings saved.")
            settings_window.destroy()
        except ValueError:
            messagebox.showerror("Error", "Invalid input.")

    settings_window = tk.Tk()
    settings_window.title("Wake Check Settings")

    tk.Label(settings_window, text="Start Time (HH:MM 24hr):").grid(row=0, column=0)
    start_time_entry = tk.Entry(settings_window)
    start_time_entry.insert(0, config["start_time"])
    start_time_entry.grid(row=0, column=1)

    tk.Label(settings_window, text="Notification Duration (seconds):").grid(row=1, column=0)
    duration_entry = tk.Entry(settings_window)
    duration_entry.insert(0, str(config["notification_duration"]))
    duration_entry.grid(row=1, column=1)

    tk.Label(settings_window, text="Interval After Click (seconds):").grid(row=2, column=0)
    interval_entry = tk.Entry(settings_window)
    interval_entry.insert(0, str(config["notification_interval"]))
    interval_entry.grid(row=2, column=1)

    tk.Button(settings_window, text="Save", command=save).grid(row=3, columnspan=2, pady=10)

    settings_window.mainloop()

# ------------------- Run Tray App ------------------- #
def run_tray():
    icon = Icon("WakeChecker")
    icon.icon = create_icon_image()
    icon.menu = Menu(
        MenuItem("I'm Awake", on_awake_clicked),
        MenuItem("Settings", open_settings),
        MenuItem("Exit", on_exit)
    )

    monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
    monitor_thread.start()

    icon.run()

if __name__ == "__main__":
    run_tray()