import tkinter as tk
from playsound3 import playsound
import utils as _utils

def send_notification():
    WIDTH, HEIGHT = 325, 125

    root = tk.Tk()
    root.title("Are you awake?")
    _utils.center_window(root, WIDTH, HEIGHT)
    root.attributes("-topmost", True)
    root.overrideredirect(True)

    tk.Label(root, text="Click the button or your PC will shut down in 1 minute.").pack(pady=20)

    btn = tk.Button(
        root,
        text="I'm Awake!",
        command=lambda: (
            root.destroy(),
            _utils.set_clicked_flag(),
            _utils.log_click_time("notification")
        )
    )
    btn.pack(pady=10)

    root.after(60000, root.destroy)
    print("Notification sent.")
    playsound("notification.mp3", block=False)
    root.mainloop()
