import tkinter as tk
import config

def open_settings():
    config.load_config()
    settings_window = tk.Tk()
    settings_window.title("Settings")

    def save():
        target_time = target_time_entry.get()
        notification_duration = notification_duration_entry.get()
        notification_interval = notification_interval_entry.get()
        config.save_config(target_time, notification_duration, notification_interval, "notification")
        settings_window.destroy()


    tk.Label(settings_window, text="Target Time:").grid(row=0, column=0)
    target_time_entry = tk.Entry(settings_window)
    target_time_entry.insert(0, config.CONFIG["target_time"])
    target_time_entry.grid(row=0, column=1)

    tk.Label(settings_window, text="Notification Duration:").grid(row=1, column=0)
    notification_duration_entry = tk.Entry(settings_window)
    notification_duration_entry.insert(0, config.CONFIG["notification_duration"])
    notification_duration_entry.grid(row=1, column=1)

    tk.Label(settings_window, text="Notification Interval:").grid(row=2, column=0)
    notification_interval_entry = tk.Entry(settings_window)
    notification_interval_entry.insert(0, config.CONFIG["notification_interval"])
    notification_interval_entry.grid(row=2, column=1)

    tk.Label(settings_window, text="Script Version:").grid(row=3, column=0)
    tk.Button(settings_window, text="Save", command=save).grid(row=3, column=0, columnspan=2)
    settings_window.mainloop()

if __name__ == "__main__":
    open_settings()