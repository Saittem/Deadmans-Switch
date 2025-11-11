from PIL import Image, ImageDraw
import os
import time
import threading
import tkinter as tk
from tkinter import messagebox
from pystray import Icon, MenuItem, Menu
from main import ICON_PATH
import main
import config

# Defines the path to your icon file
ICON_PATH = "icon.ico"

def center_window(window, window_width, window_height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    window.geometry(f"+{x}+{y}")

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

    WINDOW_WIDTH = 325
    WINDOW_HEIGHT = 125

    root = tk.Tk()
    root.title("Are you awake?")
    center_window(root, WINDOW_WIDTH, WINDOW_HEIGHT)
    root.geometry(str(WINDOW_WIDTH) + "x" + str(WINDOW_HEIGHT))
    # Makes the window always on top
    root.attributes("-topmost", True)
    root.overrideredirect(True)
    label = tk.Label(root, text="Click the button or your PC will shut down in 1 minute.")
    label.pack(pady=20)
    button = tk.Button(root, text="I'm Awake!", command=lambda: (root.destroy(), main.set_clicked_flag(), config.log_click_time(source="notification")))
    button.pack(pady=10)
    button.pack()
    root.after(config.CONFIG["notification_duration"], root.destroy)  # Destroy the window after 1 minute
    print("Notification shown. Waiting for user response via window click.")
    root.mainloop()

def open_settings():
    """
    Opens a Tkinter window allowing the user to configure application settings
    (start time, notification duration, and interval).
    """
    global CONFIG

    def save():
        global STOP_FLAG
        try:
            # Validates inputs
            time.strptime(start_time_entry.get(), "%H:%M")
            new_duration = int(duration_entry.get())
            new_interval = int(interval_entry.get())
            new_start_time = start_time_entry.get()

            # Checks if any setting changed
            if (CONFIG["start_time"] != new_start_time or
                CONFIG["notification_duration"] != new_duration or
                CONFIG["notification_interval"] != new_interval):

                print("Settings changed. Saving and restarting monitoring loop...")

                # Saves new settings
                config.save_config(new_start_time, new_duration, new_interval)

                # Restarts monitor loop
                STOP_FLAG = True  # Tell the old monitor loop to stop
                settings_window.destroy()

                # Starts a new thread after a small delay to give the old one time to shut down
                threading.Thread(target=main.restart_monitor_loop_after_delay, daemon=True).start()

            else:
                print("No changes detected. Closing settings.")
                settings_window.destroy()

        except ValueError:
            messagebox.showerror("Error", "Invalid input. Please check time format (HH:MM) and ensure duration/interval are numbers.")

    WINDOW_WIDTH = 300
    WINDOW_HEIGHT = 200

    # Creates the settings Tkinter window
    settings_window = tk.Tk()
    settings_window.title("Wake Check Settings")
    settings_window.attributes('-toolwindow', True)
    center_window(settings_window, WINDOW_WIDTH, WINDOW_HEIGHT)

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
    start_time_entry.insert(0, CONFIG["start_time"]) # Populate with current setting
    start_time_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    tk.Label(settings_window, text="Notification Duration (seconds):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    duration_entry = tk.Entry(settings_window)
    duration_entry.insert(0, str(CONFIG["notification_duration"]))
    duration_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    tk.Label(settings_window, text="Interval After Click (seconds):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
    interval_entry = tk.Entry(settings_window)
    interval_entry.insert(0, str(CONFIG["notification_interval"]))
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
    monitor_thread = threading.Thread(target=main.monitor_loop, daemon=True)
    monitor_thread.start()

    # Initializes and runs the system tray icon
    icon = Icon("WakeChecker")
    icon.icon = create_icon_image() # Set the custom icon image
    icon.menu = Menu(
        MenuItem("I'm Awake", main.on_awake_clicked),  # Menu item to manually confirm awake status
        MenuItem("Settings", open_settings),      # Menu item to open settings window
        MenuItem("Exit", main.on_exit)                 # Menu item to exit the application gracefully
    )
    print("Tray icon running.")
    # Runs the pystray icon
    icon.run() 