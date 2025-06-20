import json
import tkinter as tk
from tkinter import messagebox

CONFIG_PATH = "config.json"

# loads config from config.json file, if it doesn't exist or work, returns default
def load_config():
    default = {"start_time": "02:00", "notification_duration": 60, "notification_interval": 600}
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except:
        return default

# saves config to config.json
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

# !!! EXPERIMENTAL FEATURE !!!
# makes the monitor.py script run in the background
def run_in_background():
    import subprocess
    subprocess.call(['pythonw', 'monitor.py'])

# !!! EXPERIMENTAL FEATURE !!!
# stops the monitor.py script from running in the background
def stop_in_background():
    import subprocess
    subprocess.call(['taskkill', '/im', 'python.exe', '/fi', 'windowtitle eq Sleeping man\'s script'])

config = load_config()

# title
root = tk.Tk()
root.title("Sleeping man's script")

# notification display time, label and textbox
tk.Label(root, text="Notification display time (HH:MM 24hr):").grid(row=0, column=0)
start_time_entry = tk.Entry(root)
start_time_entry.insert(0, config["start_time"])
start_time_entry.grid(row=0, column=1)

# duration of the notification, label and textbox
tk.Label(root, text="Notification Duration (seconds):").grid(row=1, column=0)
duration_entry = tk.Entry(root)
duration_entry.insert(0, str(config["notification_duration"]))
duration_entry.grid(row=1, column=1)

# interval for the next notification after click, label and textbox
tk.Label(root, text="Interval After Click (seconds):").grid(row=2, column=0)
interval_entry = tk.Entry(root)
interval_entry.insert(0, str(config["notification_interval"]))
interval_entry.grid(row=2, column=1)

# button that calls run_in_background
run_button = tk.Button(root, text="Run in background", command=run_in_background)
run_button.grid(row=3, columnspan=2, pady=10)

# button that calls stop_in_background
stop_button = tk.Button(root, text="Stop background process", command=stop_in_background)
stop_button.grid(row=4, columnspan=2, pady=10)

# button that calls save_config
save_button = tk.Button(root, text="Save", command=save_config)
save_button.grid(row=5, columnspan=2, pady=10)

root.mainloop()