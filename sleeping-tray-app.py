import os
import json
import time
import threading
from datetime import datetime
from datetime import timedelta
import tkinter as tk
from tkinter import messagebox
from pystray import Icon, MenuItem, Menu
from winotify import Notification, Notifier, Registry, audio
from PIL import Image, ImageDraw
from http.server import BaseHTTPRequestHandler, HTTPServer
import sys
import win32com.client


CONFIG_PATH = "config.json"
LOG_FILE_PATH = "wake_log.txt"
CLICKED_FLAG = False
STOP_FLAG = False


app_id = "Dead man's switch"
registry = Registry(app_id=app_id, script_path=__file__)
notifier = Notifier(registry)


# ------------------- Config Functions ------------------- #
def load_config():
    """   
    Loads configuration settings from a JSON file (config.json).
    If the file does not exist, it creates it with default settings.
    Default settings include a start time, notification duration, and interval.
    Returns the loaded (or default) configuration as a dictionary.
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


# ------------------- Logging Function ------------------- #
def log_click_time(source="notification"):
    """
    Logs the current timestamp to the log file (wake_log.txt), indicating
    when the user confirmed being "Awake".
    A string indicating how the click was registered (e.g., "notification" 
    for a click on the toast notification, or with tray menu).
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
    """
    Creates a simple blue circular image with a white ellipse in the center
    to be used as the system tray icon.
    Returns a PIL Image object.
    """
    image = Image.new("RGB", (64, 64), "blue")
    draw = ImageDraw.Draw(image)
    draw.ellipse((16, 16, 48, 48), fill="white")
    return image


# ------------------- Notification and HTTP Server ------------------- #

class ClickHandler(BaseHTTPRequestHandler):
    """
    A custom HTTP request handler for the local web server.
    It processes GET requests. When the '/click' path is accessed,
    it sets the global CLICKED_FLAG to True, sends an HTML response
    that attempts to close the browser tab, and logs the event.
    """
    def do_GET(self):
        global CLICKED_FLAG
        if self.path == "/click":
            CLICKED_FLAG = True
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # HTML, CSS and JavaScript
            response_html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Action Confirmed</title>
                <script type="text/javascript">
                    // Attempt to close the window after a short delay
                    // This may not work in all browsers due to security restrictions.
                    setTimeout(function() {
                        window.close();
                    }, 500); // 500ms delay
                </script>
                <style>
                    body { font-family: sans-serif; text-align: center; margin-top: 50px; }
                    h1 { color: #4CAF50; }
                    p { color: #555; }
                </style>
            </head>
            <body>
                <h1>Action Confirmed!</h1>
                <p>Thank you for responding.</p>
                <p>This tab may close automatically. If not, you can close it manually.</p>
            </body>
            </html>
            """
            self.wfile.write(response_html.encode('utf-8'))
            print("HTTP server: CLICKED_FLAG set to True. Sent HTML with close attempt.")
            log_click_time(source="notification") # Logs that the notification was clicked
        else:
            # For any other path, send a "No Content" response
            self.send_response(204)
            self.end_headers()
            print(f"HTTP server: Unhandled path '{self.path}'")


def start_and_monitor_http_server(timeout_seconds):
    """
    Starts a temporary local HTTP server to listen for a click from the notification.
    The server runs for a specified `timeout_seconds` duration or until a click is received,
    then it shuts itself down.

    Args:
        timeout_seconds (int): The maximum duration (in seconds) to wait for a click.

    Returns:
        bool: True if the user clicked the notification, False if it timed out or was stopped.
    """
    global CLICKED_FLAG 
    # Resets CLICKED_FLAG at the beginning of this monitoring phase
    CLICKED_FLAG = False 

    server_address = ("localhost", 8888)
    httpd = None # Initializes httpd to None

    try:
        httpd = HTTPServer(server_address, ClickHandler)
        # Sets a timeout for handle_request() to make the loop non-blocking.
        # It allows the loop to periodically check STOP_FLAG and the overall timeout.
        httpd.timeout = 1  
        print(f"HTTP server temporarily started on http://{server_address[0]}:{server_address[1]} for {timeout_seconds}s.")

        start_time = time.time()
        while not CLICKED_FLAG and not STOP_FLAG and (time.time() - start_time < timeout_seconds):
            # handle_request() processes one request or times out (based on httpd.timeout).
            # If it times out, the loop continues to check flags and remaining time.
            httpd.handle_request()
            
        return CLICKED_FLAG # Returns the final state of CLICKED_FLAG
            
    except OSError as e:
        print(f"HTTP server error: {e}. Port 8888 might be in use. Cannot listen for click.")
        return False # Indicates a failure to start/listen
    except Exception as e:
        print(f"An unexpected error occurred in HTTP server: {e}")
        return False # Indicates an unexpected error during server operation
    finally:
        # Ensures the server is closed and the port is released when the function exits
        if httpd:
            httpd.server_close()
            print("HTTP server stopped for this cycle.")


def send_notification():
    """
    Creates and displays a Windows toast notification with an "I'm Awake!" button.
    The button's action is set to launch a local HTTP URL which will be handled
    by the temporarily running HTTP server.
    """
    toast = Notification(app_id=app_id,
                         title="Are you awake?",
                         msg="Click the button or your PC will shut down in 1 minute.",
                         duration="long")
    toast.set_audio(audio.Default, loop=False)
    toast.add_actions(label="I'm Awake!", launch="http://localhost:8888/click")
    toast.show()
    print("Notification shown. Waiting for user response via HTTP click.")


# ------------------- Wait Until Time ------------------- #
def wait_until_time(target_str):
    """
    Pauses the execution of the program until a specific target time (HH:MM) is reached.
    If the target time has already passed for the current day, it waits until that time
    on the next day. It continuously checks the STOP_FLAG to allow for early termination.

    Args:
        target_str (str): The target time in "HH:MM" 24-hour format (e.g., "02:00").
    """
    target_hour, target_minute = map(int, target_str.split(":"))
    print(f"Waiting until {target_str} to start monitoring...")
    while True:
        now = datetime.now()
        # Creates a datetime object for the target time on the current day
        target_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
        
        # If the target time has already passed today, set it for tomorrow
        if now > target_time:
            target_time += timedelta(days=1)
            
        # Check if the exact target minute has been reached
        if now.hour == target_hour and now.minute == target_minute:
            break 
            
        # Check the global STOP_FLAG to allow the wait to be interrupted
        if STOP_FLAG:
            print("Wait until time interrupted by STOP_FLAG.")
            return

        # Calculates time remaining and sleep in chunks to remain responsive to STOP_FLAG
        time_to_sleep = (target_time - now).total_seconds()
        if time_to_sleep > 0:
            # Sleep for a maximum of 20 seconds, or the remaining time if less
            sleep_chunk = min(time_to_sleep, 20) 
            time.sleep(sleep_chunk)
        else:
            # If time is exactly now or slightly past due to execution delays, sleep briefly
            time.sleep(1)


# ------------------- Monitoring Thread ------------------- #
def monitor_loop():
    """
    The main monitoring loop of the application.
    It waits until the configured start time, then repeatedly:
    1. Sends a notification.
    2. Starts a temporary HTTP server to listen for a user click for a defined duration.
    3. If no click is received within the duration, it initiates a system shutdown.
    4. If a click is received, it waits for a defined interval before repeating the cycle.
    The loop terminates if the global STOP_FLAG is set.
    """
    global CLICKED_FLAG # Declares intent to read this global flag
    config = load_config()
    
    # The line below is for testing purposes
    # wait_until_time((datetime.now() + timedelta(minutes=1)).strftime("%H:%M"))
    wait_until_time(config["start_time"])


    while not STOP_FLAG:
        send_notification()
        
        # Starts the HTTP server to listen for a click for the notification's duration.
        # The function returns True if the user clicked, False otherwise.
        user_responded = start_and_monitor_http_server(config["notification_duration"]) 

        # After start_and_monitor_http_server returns, the temporary HTTP server is shut down.
        # Now, check if the user responded or if the application needs to stop.
        if not user_responded and not STOP_FLAG:
            print("No response within duration. Shutting down.")
            # This line will initiate system shutdown with a 15-second delay.
            os.system("shutdown /s /t 15") 
            break # Exits the monitoring loop as shutdown is initiated
        
        # If STOP_FLAG was set during the monitoring/waiting phase, exit the loop
        if STOP_FLAG:
            print("Monitoring loop exiting due to STOP_FLAG.")
            break

        print(f"User confirmed. Sleeping for {config['notification_interval']} seconds before next check.")
        time.sleep(config["notification_interval"])
    
    print("Monitoring loop finished.")


# ------------------- Tray Menu Handlers ------------------- #
def on_awake_clicked(icon, item):
    """
    Handles the event when the "I'm Awake" item is clicked in the system tray menu.
    It manually sets the global CLICKED_FLAG to True, mimicking a notification click,
    and logs the event.
    
    Args:
        icon: The pystray Icon object.
        item: The MenuItem object that was clicked.
    """
    global CLICKED_FLAG
    print("User clicked 'I'm Awake' from tray menu.")
    CLICKED_FLAG = True # Manually sets the flag
    log_click_time(source="tray menu") # Logs the manual click


def on_exit(icon, item):
    """
    Handles the event when the "Exit" item is clicked in the system tray menu.
    It sets the global STOP_FLAG to True to signal all running threads (like monitor_loop
    and the HTTP server if active) to terminate gracefully.
    It then stops the system tray icon.
    
    Args:
        icon: The pystray Icon object.
        item: The MenuItem object that was clicked.
    """
    global STOP_FLAG
    
    STOP_FLAG = True # Signals all threads to stop
    print("Exit command received. Signaling threads to stop...")

    # The start_and_monitor_http_server function manages its own lifecycle.
    # If it's currently running, it will detect STOP_FLAG and exit gracefully.
    
    icon.stop() # Stops the pystray icon's main loop
    print("Tray icon stopped.")


# ------------------- Startup Shortcut Function ------------------- #
def create_startup_shortcut():
    """
    Creates a shortcut (.lnk file) to the application's executable in the
    current user's Windows Startup folder.
    """

    try:
        exe_path = sys.executable 
        
        # Gets the path to the current user's Startup folder
        startup_folder = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        
        # Defines the path for the shortcut file
        # Uses a consistent name for the shortcut for easy management
        shortcut_name = "Dead Man's Switch.lnk"
        shortcut_path = os.path.join(startup_folder, shortcut_name)

        # Creates the shell object to create shortcuts
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.TargetPath = exe_path
        
        # Sets description and icon location for the shortcut
        shortcut.Description = "Runs Dead Man's Switch on Windows startup."
        # shortcut.IconLocation = os.path.join(os.path.dirname(exe_path), "your_app_icon.ico")
        
        shortcut.Save() # Saves the shortcut file

        messagebox.showinfo("Startup Shortcut", 
                            f"Shortcut to '{os.path.basename(exe_path)}' created successfully in your Startup folder:\n{startup_folder}\n\n"
                            "The app will now run automatically when you log in.")
        print(f"Startup shortcut created at: {shortcut_path}")

    except Exception as e:
        messagebox.showerror("Startup Shortcut Error", 
                             f"Failed to create startup shortcut.\n\nError: {e}\n\n"
                             "This feature requires the 'pywin32' library and administrator privileges if trying to install for all users (which this version doesn't do). "
                             "Please ensure the app is run as an executable for this feature to point correctly.")
        print(f"Error creating startup shortcut: {e}")


def open_settings(icon=None, item=None):
    """
    Opens a Tkinter window allowing the user to configure application settings
    (start time, notification duration, and interval) and manage startup settings.
    
    Args:
        icon: The pystray Icon object (optional, not directly used in this function).
        item: The MenuItem object that was clicked (optional, not directly used in this function).
    """
    config = load_config() # Loads current settings

    def save():
        """
        Internal function called when the "Save" button in the settings window is clicked.
        It validates input, saves the settings, and closes the settings window.
        """
        try:
            # Validates input formats
            time.strptime(start_time_entry.get(), "%H:%M") # Checks HH:MM format
            int(duration_entry.get()) # Checks if it's an integer
            int(interval_entry.get()) # Checks if it's an integer

            save_config(start_time_entry.get(), duration_entry.get(), interval_entry.get())
            messagebox.showinfo("Saved", "Settings saved.")
            settings_window.destroy() # Closes the settings window
        except ValueError:
            messagebox.showerror("Error", "Invalid input. Please check time format (HH:MM) and ensure duration/interval are numbers.")

    # Creates the settings Tkinter window
    settings_window = tk.Tk()
    settings_window.title("Wake Check Settings")

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
    
    # Button for creating startup shortcut
    tk.Button(settings_window, text="Add to Windows Startup", command=create_startup_shortcut).grid(row=4, columnspan=2, pady=5)


    # Configures columns to expand horizontally with the window
    settings_window.grid_columnconfigure(1, weight=1)

    settings_window.mainloop() # Starts the Tkinter event loop for the settings window


# ------------------- Run Tray App ------------------- #
def run_tray():
    """
    Initializes and runs the main application.
    It starts the `monitor_loop` in a separate thread and then
    creates and runs the system tray icon, which provides menu options
    like "I'm Awake", "Settings", and "Exit".
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

if __name__ == "__main__":
    # Ensures global flags are in a clean state when the script starts
    CLICKED_FLAG = False
    STOP_FLAG = False
    
    # Starts the main application by running the system tray icon setup
    run_tray()
    print("Application finished.")