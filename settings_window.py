import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import os

import config as _config
import utils as _utils
import tray as _tray

def open_settings():
    config = _config.load_config()

    def save():
        try:
            new_time = entry_target_time.get()
            duration = int(entry_notification_duration.get())
            interval = int(entry_notification_interval.get())
            version = combo_monitoring_variant.get()
            inactivity_threshold = int(entry_inactivity_threshold.get())

            old = _config.load_config()
            changed = (
                old["target_time"] != new_time or
                old["notification_duration"] != duration or
                old["notification_interval"] != interval or
                old["monitoring_variant"] != version or
                old["inactivity_threshold"] != inactivity_threshold
            )

            if changed:
                _config.save_config(new_time, duration, interval, version, inactivity_threshold)
                settings.destroy()
                
                # Restart monitoring with new variant
                _tray.restart_monitoring()
                print("Settings saved and monitoring restarted.")
            else:
                settings.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Invalid input: {e}")

    settings = tk.Tk()
    settings.title("Settings")
    settings.geometry("325x200")
    _utils.center_window(settings, 300, 200)

    if os.path.exists(_utils.ICON_PATH):
        settings.iconbitmap(_utils.ICON_PATH)

    # ---- Target Time ----
    label_target_time = tk.Label(settings, text="Target time:")
    label_target_time.grid(row=0, column=0, sticky="w", padx=10, pady=5)
    entry_target_time = tk.Entry(settings)
    entry_target_time.grid(row=0, column=1, padx=10, pady=5)
    entry_target_time.insert(0, config["target_time"])

    # ---- Notification Duration ----
    label_notification_duration = tk.Label(settings, text="Notification duration:")
    label_notification_duration.grid(row=1, column=0, sticky="w", padx=10, pady=5)
    entry_notification_duration = tk.Entry(settings)
    entry_notification_duration.grid(row=1, column=1, padx=10, pady=5)
    entry_notification_duration.insert(0, str(config["notification_duration"]))

    # ---- Notification Interval ----
    label_notification_interval = tk.Label(settings, text="Notification interval:")
    label_notification_interval.grid(row=2, column=0, sticky="w", padx=10, pady=5)
    entry_notification_interval = tk.Entry(settings)
    entry_notification_interval.grid(row=2, column=1, padx=10, pady=5)
    entry_notification_interval.insert(0, str(config["notification_interval"]))

    # ---- Monitoring Variant ----
    label_monitoring_variant = tk.Label(settings, text="Script version:")
    label_monitoring_variant.grid(row=3, column=0, sticky="w", padx=10, pady=5)
    combo_monitoring_variant = ttk.Combobox(settings, values=["notification", "activity"], state="readonly")
    combo_monitoring_variant.grid(row=3, column=1, padx=10, pady=5)
    combo_monitoring_variant.set(config["monitoring_variant"])

    # ---- Inactivity Threshold ----
    label_inactivity_threshold = tk.Label(settings, text="Inactivity threshold:")
    label_inactivity_threshold.grid(row=4, column=0, sticky="w", padx=10, pady=5)
    entry_inactivity_threshold = tk.Entry(settings)
    entry_inactivity_threshold.grid(row=4, column=1, padx=10, pady=5)
    entry_inactivity_threshold.insert(0, str(config["inactivity_threshold"]))

    # ---- Save Button ----
    save_button = tk.Button(settings, text="Save", command=save)
    save_button.grid(row=5, column=0, columnspan=2, pady=15)

    settings.mainloop()