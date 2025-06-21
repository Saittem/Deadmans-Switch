import json
import tkinter as tk
from tkinter import messagebox
import os
import shutil
import subprocess
import psutil
import ctypes
from ctypes import wintypes


CONFIG_PATH = "config.json"
SCRIPT = "monitor.py"


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


def get_startup_folder():
    SHGFP_TYPE_CURRENT = 0
    CSIDL_STARTUP = 7

    buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_STARTUP, None, SHGFP_TYPE_CURRENT, buf)
    return buf.value


def get_script_path():  
    startup_folder = get_startup_folder()

    # Define the destination path
    destination_path = os.path.join(startup_folder, SCRIPT)

    print(f"Destination path: {destination_path}")

    return destination_path


# !!! EXPERIMENTAL FEATURE !!!
# makes the monitor.py script run in the background
def run_in_background():
    # returns the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Constructs the path to the monitor.py script
    script_path = os.path.join(current_dir, SCRIPT)

    destination_path = get_script_path()

    if not os.path.exists(script_path):
        # Copies the script to the startup folder
        shutil.copy(script_path, destination_path)
        print(f"Copied {SCRIPT} to Startup folder.")
    else:
        print(f"{SCRIPT} already exists in Startup folder.")

    start_process(destination_path)


def start_process(process_path):
    try:
        subprocess.Popen(["python", process_path], shell=True)
        print("Script launched.")
    except Exception as e:
        print("Failed to launch script:", e)


# !!! EXPERIMENTAL FEATURE !!!
# stops the monitor.py script from running in the background
def stop_in_background():
    startup_path = get_script_path()

    if os.path.exists(startup_path):
        os.remove(startup_path)
        print("Script removed from Startup.")
    else:
        print("Script not found in Startup folder.")

    kill_process("monitor.py")


def kill_process(process_name):
    for process in psutil.process_iter():
        if process.name() == process_name:
            process.kill()


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
stop_button = tk.Button(root, text="Stop background process", command=get_script_path)
stop_button.grid(row=4, columnspan=2, pady=10)

# button that calls save_config
save_button = tk.Button(root, text="Save", command=save_config)
save_button.grid(row=5, columnspan=2, pady=10)

root.mainloop()