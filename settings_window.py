import tkinter as tk
from tkinter import messagebox
import threading
import os

from config import load_config, save_config
from utils import center_window, ICON_PATH, STOP_FLAG
from monitor import restart_monitor_loop_after_delay

def open_settings():
    config = load_config()

    def save():
        global STOP_FLAG

        try:
            new_time = start_time_entry.get()
            duration = int(duration_entry.get())
            interval = int(interval_entry.get())

            old = load_config()
            changed = (
                old["start_time"] != new_time or
                old["notification_duration"] != duration or
                old["notification_interval"] != interval
            )

            if changed:
                save_config(new_time, duration, interval)
                STOP_FLAG = True
                settings.destroy()
                threading.Thread(target=restart_monitor_loop_after_delay, daemon=True).start()
            else:
                settings.destroy()

        except Exception:
            messagebox.showerror("Error", "Invalid input.")

    settings = tk.Tk()
    settings.title("Wake Check Settings")
    center_window(settings, 300, 200)

    if os.path.exists(ICON_PATH):
        settings.iconbitmap(ICON_PATH)

    tk.Label(settings, text="Start Time (HH:MM):").grid(row=0, column=0)
    start_time_entry = tk.Entry(settings)
    start_time_entry.insert(0, config["start_time"])
    start_time_entry.grid(row=0, column=1)

    tk.Label(settings, text="Duration (sec):").grid(row=1, column=0)
    duration_entry = tk.Entry(settings)
    duration_entry.insert(0, config["notification_duration"])
    duration_entry.grid(row=1, column=1)

    tk.Label(settings, text="Interval (sec):").grid(row=2, column=0)
    interval_entry = tk.Entry(settings)
    interval_entry.insert(0, config["notification_interval"])
    interval_entry.grid(row=2, column=1)

    tk.Button(settings, text="Save", command=save).grid(row=3, columnspan=2, pady=10)

    settings.mainloop()
