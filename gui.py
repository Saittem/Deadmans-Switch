import json
import tkinter as tk
from tkinter import messagebox

CONFIG_PATH = "config.json"

def load_config():
    default = {"start_time": "02:00", "notification_duration": 60, "notification_interval": 600}
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except:
        return default

def save_config():
    try:
        config = {
            "start_time": start_time_entry.get(),
            "notification_duration": int(duration_entry.get()),
            "notification_interval": int(interval_entry.get())
        }
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f)
        messagebox.showinfo("Saved", "Configuration saved successfully.")
    except ValueError:
        messagebox.showerror("Error", "Please enter valid values (HH:MM and integers).")

config = load_config()

root = tk.Tk()
root.title("Wake Check Config")

tk.Label(root, text="Start Time (HH:MM 24hr):").grid(row=0, column=0)
start_time_entry = tk.Entry(root)
start_time_entry.insert(0, config["start_time"])
start_time_entry.grid(row=0, column=1)

tk.Label(root, text="Notification Duration (seconds):").grid(row=1, column=0)
duration_entry = tk.Entry(root)
duration_entry.insert(0, str(config["notification_duration"]))
duration_entry.grid(row=1, column=1)

tk.Label(root, text="Interval After Click (seconds):").grid(row=2, column=0)
interval_entry = tk.Entry(root)
interval_entry.insert(0, str(config["notification_interval"]))
interval_entry.grid(row=2, column=1)

save_button = tk.Button(root, text="Save", command=save_config)
save_button.grid(row=3, columnspan=2, pady=10)

root.mainloop()