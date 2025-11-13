from datetime import datetime
import threading
import os
import config
import gui

def get_time():
    return datetime.now().strftime("%H:%M:%S")

def monitor_time():
    while True:
        current_time = get_time()
        if current_time == config.CONFIG["target_time"]:
            os.system("shutdown /s /t 0")

def input_listener():
    while True:
        user_input = input()
        if user_input.lower() == "exit":
            print("Goodbye!")
            os._exit(0)
        elif user_input.lower() == "settings":
            gui.open_settings()

if __name__ == "__main__":
    config.load_config()
    target_time = config.CONFIG["target_time"]

    # Start threads correctly
    threading.Thread(target=monitor_time, daemon=True).start()
    threading.Thread(target=input_listener, daemon=True).start()

    print("Time to sleep:", target_time)

    # Keep main thread alive
    while True:
        pass
