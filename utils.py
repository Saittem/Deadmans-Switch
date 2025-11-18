from datetime import datetime
from PIL import Image, ImageDraw

LOG_FILE_PATH = "wake_log.txt"
ICON_PATH = "icon.ico"

CLICKED_FLAG = False
STOP_FLAG = False

def set_clicked_flag():
    global CLICKED_FLAG
    CLICKED_FLAG = True

def log_click_time(source="notification"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = f"[{timestamp}] User clicked 'I'm Awake' via {source}.\n"
    with open(LOG_FILE_PATH, "a") as f:
        f.write(msg)

def center_window(window, w, h):
    sw = window.winfo_screenwidth()
    sh = window.winfo_screenheight()
    x = (sw - w) // 2
    y = (sh - h) // 2
    window.geometry(f"{w}x{h}+{x}+{y}")

def create_icon_image():
    try:
        return Image.open(ICON_PATH).convert("RGBA")
    except:
        img = Image.new("RGB", (64, 64), "blue")
        draw = ImageDraw.Draw(img)
        draw.ellipse((16,16,48,48), fill="white")
        return img
