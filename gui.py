import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pystray
from PIL import Image, ImageDraw
import config


def save(t, d, i, s):
    config.save_config(t, d, i, s)
    messagebox.showinfo("Saved", "Settings saved successfully!")


def create_image(width, height, color1, color2):
    # Generate an image and draw a pattern
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        (width // 2, 0, width, height // 2),
        fill=color2)
    dc.rectangle(
        (0, height // 2, width // 2, height),
        fill=color2)

    return image

def run_tray():
    print("Running tray...")

    icon = pystray.Icon(
        'test name',
        icon=create_image(64, 64, 'black', 'white')
    )

    menu = pystray.Menu(
        pystray.MenuItem('Open settings', lambda: open_settings()),
        pystray.MenuItem('Exit', lambda: icon.stop())
    )

    icon.menu = menu
    icon.run()


def open_settings():
    config.load_config()
    #settings_window.show()

    root = tk.Tk()
    root.title("Settings")
    root.geometry("350x200")

    # ---- Target Time ----
    label_target_time = tk.Label(root, text="Target time:")
    label_target_time.grid(row=0, column=0, sticky="w", padx=10, pady=5)
    entry_target_time = tk.Entry(root)
    entry_target_time.grid(row=0, column=1, padx=10, pady=5)
    entry_target_time.insert(0, "02:00")

    # ---- Notification Duration ----
    label_notification_duration = tk.Label(root, text="Notification duration:")
    label_notification_duration.grid(row=1, column=0, sticky="w", padx=10, pady=5)
    entry_notification_duration = tk.Entry(root)
    entry_notification_duration.grid(row=1, column=1, padx=10, pady=5)
    entry_notification_duration.insert(0, "60")

    # ---- Notification Interval ----
    label_notification_interval = tk.Label(root, text="Notification interval:")
    label_notification_interval.grid(row=2, column=0, sticky="w", padx=10, pady=5)
    entry_notification_interval = tk.Entry(root)
    entry_notification_interval.grid(row=2, column=1, padx=10, pady=5)
    entry_notification_interval.insert(0, "600")

    # ---- Script Version ----
    label_script_version = tk.Label(root, text="Script version:")
    label_script_version.grid(row=3, column=0, sticky="w", padx=10, pady=5)
    combo_script_version = ttk.Combobox(root, values=["notification", "activity"], state="readonly")
    combo_script_version.grid(row=3, column=1, padx=10, pady=5)
    combo_script_version.current(0)

    # ---- Save Button ----
    save_button = tk.Button(root, text="Save", command=lambda: save(entry_target_time, entry_notification_duration, entry_notification_interval, combo_script_version))
    save_button.grid(row=4, column=0, columnspan=2, pady=15)

    root.mainloop()

if __name__ == "__main__":
    run_tray()
