from datetime import datetime
import threading
import time
import os
import config
import gui


def get_time():
    return datetime.now().strftime("%H:%M:%S")


def monitor_time():
    while True:
        current_time = get_time()
        if current_time == config.CONFIG["target_time"]:
            print("Time to sleep!")
            #os.system("shutdown /s /t 15")
        time.sleep(1)


def input_listener():
    while True:
        try:
            user_input = input("> ")
        except EOFError:
            break

        if user_input.lower() == "exit":
            print("Goodbye!")
            os._exit(0)
        elif user_input.lower() == "settings":
            gui.open_settings()


if __name__ == "__main__":
    config.load_config()
    target_time = config.CONFIG["target_time"]

    print("Time to sleep:", target_time)

    # Start threads
    threading.Thread(target=monitor_time, daemon=True).start()
    threading.Thread(target=input_listener, daemon=True).start()

    # Run tray in main thread (must be main thread)
    gui.run_tray()

    while True:
        time.sleep(1)
    