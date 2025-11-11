import time
import threading
from datetime import datetime
from datetime import timedelta
import gui
import config


CLICKED_FLAG = False
STOP_FLAG = False


def set_clicked_flag():
    """Sets the global CLICKED_FLAG to True, mimicking a notification click."""

    global CLICKED_FLAG
    CLICKED_FLAG = True

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
    global CLICKED_FLAG
    
    # The line below is for testing purposes
    wait_until_time((datetime.now() + timedelta(minutes=1)).strftime("%H:%M"))
    #wait_until_time(CONFIG["start_time"])


    while not STOP_FLAG:
        gui.send_notification()

        # Now, check if the user responded or if the application needs to stop.
        if not CLICKED_FLAG and not STOP_FLAG:
            print("No response within duration. Shutting down.")
            # This line will initiate system shutdown with a 15-second delay.
            #os.system("shutdown /s /t 15")
            print("Shutting down...")
            break # Exits the monitoring loop as shutdown is initiated
        
        # If STOP_FLAG was set exit the loop
        if STOP_FLAG:
            print("Monitoring loop exiting due to STOP_FLAG.")
            break

        print(f"User confirmed. Sleeping for {config.CONFIG['notification_interval']} seconds before next check.")
        CLICKED_FLAG = False
        time.sleep(config.CONFIG["notification_interval"])
    
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
    config.log_click_time(source="tray menu") # Logs the manual click


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



# ------------------- Main ------------------- #
if __name__ == "__main__":
    # Ensures global flags are in a clean state when the script starts
    CLICKED_FLAG = False
    STOP_FLAG = False
    
    # Starts the main application by running the system tray icon setup
    config.load_config()
    gui.run_tray()
    print("Application finished.")