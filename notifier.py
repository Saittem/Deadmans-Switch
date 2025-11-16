import tkinter as tk
from utils import center_window, set_clicked_flag, log_click_time

def send_notification():
    WIDTH, HEIGHT = 325, 125

    root = tk.Tk()
    root.title("Are you awake?")
    center_window(root, WIDTH, HEIGHT)
    root.attributes("-topmost", True)
    root.overrideredirect(True)

    tk.Label(root, text="Click the button or your PC will shut down in 1 minute.").pack(pady=20)

    btn = tk.Button(
        root,
        text="I'm Awake!",
        command=lambda: (
            root.destroy(),
            set_clicked_flag(),
            log_click_time("notification")
        )
    )
    btn.pack(pady=10)

    root.after(60000, root.destroy)
    root.mainloop()
