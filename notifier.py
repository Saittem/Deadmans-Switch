import tkinter as tk
from playsound3 import playsound
import utils as _utils
import config as _config

def send_notification():
    WIDTH, HEIGHT = 325, 175

    root = tk.Tk()
    root.title("Are you awake?")
    _utils.center_window(root, WIDTH, HEIGHT)
    root.attributes("-topmost", True)
    root.overrideredirect(True)

    tk.Label(root, text="Click the button or your PC will shut down.").pack(pady=20)

    label_countdown = tk.Label(root, text="")
    label_countdown.pack(pady=10)

    # Store the after callback ID so we can cancel it
    countdown_id = None

    def update_countdown(count):
        nonlocal countdown_id
        if not root.winfo_exists():  # Check if window still exists
            return
        
        label_countdown.config(text=f"Shutting down in {count} seconds")
        if count > 0:
            countdown_id = root.after(1000, update_countdown, count - 1)
        else:
            root.destroy()

    def on_awake_click():
        nonlocal countdown_id
        # Cancel the countdown timer if it exists
        if countdown_id is not None:
            root.after_cancel(countdown_id)
        
        root.destroy()
        _utils.set_clicked_flag()
        _utils.log_click_time("notification")
        print("Next notification will be in " + str(_config.load_config()["notification_interval"]) + " seconds.")

    btn = tk.Button(
        root,
        text="I'm Awake!",
        command=on_awake_click
    )
    btn.pack(pady=10)

    update_countdown(_config.load_config()["notification_duration"])
    print("Notification sent.")
    playsound("notification.mp3", block=False)
    root.mainloop()