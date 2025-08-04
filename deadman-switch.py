import os
import json
import time
import threading
from datetime import datetime
from datetime import timedelta
import tkinter as tk
from tkinter import messagebox
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw


CONFIG_PATH = "config.json"
LOG_FILE_PATH = "wake_log.txt"
CLICKED_FLAG = False
STOP_FLAG = False

# Defines the path to your icon file
# Ensures 'icon.ico' is in the same directory as your script/executable
ICON_PATH = "icon.ico"

# ------------------- Config Functions ------------------- #
def load_config():
    """   
    Loads configuration settings from a JSON file (config.json).
    If the file does not exist, it creates it with default settings.
    Default settings include a start time, notification duration, and interval.
    """

    default_config = {"start_time": "02:00", "notification_duration": 60, "notification_interval": 600}
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "w") as f:
            json.dump(default_config, f)
        return default_config
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def save_config(start_time, duration, interval):
    """
    Saves the provided configuration settings (start time, notification duration, and interval)
    to the config.json file in JSON format.
    """

    config = {
        "start_time": start_time,
        "notification_duration": int(duration),
        "notification_interval": int(interval)
    }
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f)

def set_clicked_flag():
    """Sets the global CLICKED_FLAG to True, mimicking a notification click."""

    global CLICKED_FLAG
    CLICKED_FLAG = True

def center_window(window, window_width, window_height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    window.geometry(f"+{x}+{y}")

# ------------------- Logging Function ------------------- #
def log_click_time(source="notification"):
    """
    Logs the current timestamp to the log file (wake_log.txt), indicating
    when the user confirmed being "Awake".
    Types of sources include "notification" and "tray menu".
    """

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] User clicked 'I'm Awake' via {source}.\n"
    try:
        with open(LOG_FILE_PATH, "a") as f:
            f.write(log_message)
        print(f"Logged: {log_message.strip()}")
    except Exception as e:
        print(f"Error writing to log file: {e}")


# ------------------- Tray Image ------------------- #
def create_icon_image():
    try:
        # Loads the icon from the specified path
        icon_image = Image.open(ICON_PATH)
        # Ensures it's in RGBA format for pystray compatibility
        icon_image = icon_image.convert("RGBA")
        return icon_image
    except FileNotFoundError:
        print(f"Warning: icon.ico not found at {ICON_PATH}. Using default generated icon.")
        # Fallback to the previous generated icon if icon.ico is not found
        image = Image.new("RGB", (64, 64), "blue")
        draw = ImageDraw.Draw(image)
        draw.ellipse((16, 16, 48, 48), fill="white")
        return image
    except Exception as e:
        print(f"Error loading icon.ico: {e}. Using default generated icon.")
        image = Image.new("RGB", (64, 64), "blue")
        draw = ImageDraw.Draw(image)
        draw.ellipse((16, 16, 48, 48), fill="white")
        return image



# ------------------- Notification ------------------- #

def send_notification():
    """
    Creates and displays a simple GUI window with a button to confirm being "Awake".
    The window is set to close automatically after 1 minute if the button is not clicked.
    """
    root = tk.Tk()
    root.title("Are you awake?")
    center_window(root, 300, 100)
    root.geometry("300x100")
    label = tk.Label(root, text="Click the button or your PC will shut down in 1 minute.")
    label.pack()
    button = tk.Button(root, text="I'm Awake!", command=lambda: (root.destroy(), set_clicked_flag(), log_click_time(source="notification")))
    button.pack()
    root.after(60000, root.destroy)  # Destroy the window after 1 minute
    root.mainloop()
    print("Notification shown. Waiting for user response via window click.")


# ------------------- Wait Until Time ------------------- #
def wait_until_time(target_time_str):
    """
    Pauses the execution until the specified target time (HH:MM).
    Handles cases where the target time crosses midnight.
    """
    target_hour, target_minute = map(int, target_time_str.split(":"))
    now = datetime.now()
    
    # Create a datetime for today at the target time
    target_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
    
    # If the target time has already passed, move it to the next day
    if target_time <= now:
        target_time += timedelta(days=1)

    print(f"Waiting until {target_time.strftime('%Y-%m-%d %H:%M:%S')} to start monitoring...")

    while True:
        now = datetime.now()
        
        if now >= target_time:
            break

        if STOP_FLAG:
            print("Wait until time interrupted by STOP_FLAG.")
            return

        time_to_sleep = (target_time - now).total_seconds()
        sleep_chunk = min(time_to_sleep, 20)
        time.sleep(sleep_chunk)


# ------------------- Monitoring Thread ------------------- #
def monitor_loop():
    """
    The main monitoring loop of the application.
    It waits until the configured start time, then repeatedly:
    1. Sends a notification.
    2. If no click is received within the defined duration, it initiates a system shutdown.
    3. If a click is received, it waits for a defined interval before repeating the cycle.
    The loop terminates if the global STOP_FLAG is set.
    """
    global CLICKED_FLAG # Declares intent to read this global flag
    config = load_config()
    
    # The line below is for testing purposes
    wait_until_time((datetime.now() + timedelta(minutes=1)).strftime("%H:%M"))
    #wait_until_time(config["start_time"])


    while not STOP_FLAG:
        send_notification()

        # Now, check if the user responded or if the application needs to stop.
        if not CLICKED_FLAG and not STOP_FLAG:
            print("No response within duration. Shutting down.")
            # This line will initiate system shutdown with a 15-second delay.
            #os.system("shutdown /s /t 15")
            print("Shutdown")
            break # Exits the monitoring loop as shutdown is initiated
        
        # If STOP_FLAG was set exit the loop
        if STOP_FLAG:
            print("Monitoring loop exiting due to STOP_FLAG.")
            break

        print(f"User confirmed. Sleeping for {config['notification_interval']} seconds before next check.")
        time.sleep(config["notification_interval"])
    
    print("Monitoring loop finished.")


# ------------------- Tray Menu Handlers ------------------- #
def on_awake_clicked():
    """
    Handles the event when the "I'm Awake" item is clicked in the system tray menu.
    It manually sets the global CLICKED_FLAG to True, mimicking a notification click,
    and logs the event.
    """
    global CLICKED_FLAG
    print("User clicked 'I'm Awake' from tray menu.")
    CLICKED_FLAG = True # Manually sets the flag
    log_click_time(source="tray menu") # Logs the manual click


def on_exit(icon):
    """
    Handles the event when the "Exit" item is clicked in the system tray menu.
    It sets the global STOP_FLAG to True to signal all running threads to terminate gracefully.
    It then stops the system tray icon.
    """
    global STOP_FLAG
    
    STOP_FLAG = True # Signals all threads to stop
    print("Exit command received. Signaling threads to stop...")
    
    icon.stop() # Stops the pystray icon's main loop
    print("Tray icon stopped.")

def restart_monitor_loop_after_delay():
    global STOP_FLAG
    time.sleep(1)  # Give the old thread time to stop
    STOP_FLAG = False
    threading.Thread(target=monitor_loop, daemon=True).start()


def open_settings():
    """
    Opens a Tkinter window allowing the user to configure application settings
    (start time, notification duration, and interval).
    """
    config = load_config() # Loads current settings

    def save():
        global STOP_FLAG
        try:
            # Validates inputs
            time.strptime(start_time_entry.get(), "%H:%M")
            new_duration = int(duration_entry.get())
            new_interval = int(interval_entry.get())
            new_start_time = start_time_entry.get()

            # Loads old config
            old_config = load_config()

            # Checks if any setting changed
            if (old_config["start_time"] != new_start_time or
                old_config["notification_duration"] != new_duration or
                old_config["notification_interval"] != new_interval):

                print("Settings changed. Saving and restarting monitoring loop...")

                # Saves new settings
                save_config(new_start_time, new_duration, new_interval)

                # Restarts monitor loop
                STOP_FLAG = True  # Tell the old monitor loop to stop
                settings_window.destroy()

                # Starts a new thread after a small delay to give the old one time to shut down
                threading.Thread(target=restart_monitor_loop_after_delay, daemon=True).start()

            else:
                print("No changes detected. Closing settings.")
                settings_window.destroy()

        except ValueError:
            messagebox.showerror("Error", "Invalid input. Please check time format (HH:MM) and ensure duration/interval are numbers.")


    # Creates the settings Tkinter window
    settings_window = tk.Tk()
    settings_window.title("Wake Check Settings")
    center_window(settings_window, 300, 200)

    # Sets the icon for the Tkinter settings window
    try:
        if os.path.exists(ICON_PATH):
            settings_window.iconbitmap(ICON_PATH)
        else:
            print(f"Warning: {ICON_PATH} not found for settings window icon.")
    except Exception as e:
        print(f"Error setting Tkinter icon: {e}")

    # Creates and places labels and entry fields for settings
    tk.Label(settings_window, text="Start Time (HH:MM 24hr):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    start_time_entry = tk.Entry(settings_window)
    start_time_entry.insert(0, config["start_time"]) # Populate with current setting
    start_time_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    tk.Label(settings_window, text="Notification Duration (seconds):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    duration_entry = tk.Entry(settings_window)
    duration_entry.insert(0, str(config["notification_duration"]))
    duration_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    tk.Label(settings_window, text="Interval After Click (seconds):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
    interval_entry = tk.Entry(settings_window)
    interval_entry.insert(0, str(config["notification_interval"]))
    interval_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

    # Save button
    tk.Button(settings_window, text="Save", command=save).grid(row=3, columnspan=2, pady=10)
    
    # Configures columns to expand horizontally with the window
    settings_window.grid_columnconfigure(1, weight=1)

    settings_window.mainloop() # Starts the Tkinter event loop for the settings window


# ------------------- Run Tray App ------------------- #
def run_tray():
    """
    Initializes and runs the main application.
    It starts the `monitor_loop` in a separate thread and then
    creates and runs the system tray icon, which provides menu options "I'm Awake", "Settings", and "Exit".
    """
    # Starts the monitoring loop in a separate daemon thread.
    # A daemon thread will automatically terminate when the main program exits.
    monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
    monitor_thread.start()

    # Initializes and runs the system tray icon
    icon = Icon("WakeChecker")
    icon.icon = create_icon_image() # Set the custom icon image
    icon.menu = Menu(
        MenuItem("I'm Awake", on_awake_clicked),  # Menu item to manually confirm awake status
        MenuItem("Settings", open_settings),      # Menu item to open settings window
        MenuItem("Exit", on_exit)                 # Menu item to exit the application gracefully
    )
    print("Tray icon running.")
    # Runs the pystray icon
    icon.run() 

# ------------------- Main ------------------- #
if __name__ == "__main__":
    # Ensures global flags are in a clean state when the script starts
    CLICKED_FLAG = False
    STOP_FLAG = False
    
    # Starts the main application by running the system tray icon setup
    run_tray()
    print("Application finished.")