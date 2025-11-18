import tkinter as tk
from tkinter import ttk
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
            new_time = entry_target_time.get()
            duration = int(entry_notification_duration.get())
            interval = int(entry_notification_interval.get())
            version = combo_monitoring_variant.get()

            old = load_config()
            changed = (
                old["target_time"] != new_time or
                old["notification_duration"] != duration or
                old["notification_interval"] != interval or
                old["monitoring_variant"] != version
            )

            if changed:
                save_config(new_time, duration, interval, version)
                STOP_FLAG = True
                settings.destroy()
                threading.Thread(target=restart_monitor_loop_after_delay, daemon=True).start()
            else:
                settings.destroy()

        except Exception:
            messagebox.showerror("Error", "Invalid input.")


    settings = tk.Tk()
    settings.title("Settings")
    settings.geometry("325x175")
    center_window(settings, 300, 175)

    if os.path.exists(ICON_PATH):
        settings.iconbitmap(ICON_PATH)

    # ---- Target Time ----
    label_target_time = tk.Label(settings, text="Target time:")
    label_target_time.grid(row=0, column=0, sticky="w", padx=10, pady=5)
    entry_target_time = tk.Entry(settings)
    entry_target_time.grid(row=0, column=1, padx=10, pady=5)
    entry_target_time.insert(0, "02:00")

    # ---- Notification Duration ----
    label_notification_duration = tk.Label(settings, text="Notification duration:")
    label_notification_duration.grid(row=1, column=0, sticky="w", padx=10, pady=5)
    entry_notification_duration = tk.Entry(settings)
    entry_notification_duration.grid(row=1, column=1, padx=10, pady=5)
    entry_notification_duration.insert(0, "60")

    # ---- Notification Interval ----
    label_notification_interval = tk.Label(settings, text="Notification interval:")
    label_notification_interval.grid(row=2, column=0, sticky="w", padx=10, pady=5)
    entry_notification_interval = tk.Entry(settings)
    entry_notification_interval.grid(row=2, column=1, padx=10, pady=5)
    entry_notification_interval.insert(0, "600")

    # ---- Monitoring Variant ----
    label_monitoring_variant = tk.Label(settings, text="Script version:")
    label_monitoring_variant.grid(row=3, column=0, sticky="w", padx=10, pady=5)
    combo_monitoring_variant = ttk.Combobox(settings, values=["notification", "activity"], state="readonly")
    combo_monitoring_variant.grid(row=3, column=1, padx=10, pady=5)
    combo_monitoring_variant.current(0)

    # ---- Save Button ----
    save_button = tk.Button(settings, text="Save", command=save)
    save_button.grid(row=4, column=0, columnspan=2, pady=15)

    settings.mainloop()
