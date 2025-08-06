# Deadman's Switch

![Python](https://img.shields.io/badge/python-3.13.5-blue)
![PyStray](https://img.shields.io/badge/pystray-0.19.5-brightgreen)
![Pillow](https://img.shields.io/badge/pillow-11.3.0-brightgreen)

A lightweight Python tray utility that periodically checks if you're awake. If no response is received, it assumes you're asleep and shuts down your PC automatically.

---

## 📌 Features

- ✅ Custom notification via `tkinter` asking “Are you asleep?”
- 🕐 Customizable delays:
  - Time for the first notification
  - Time to respond
  - Time between notifications
- 💾 **Wake log**: Tracks every "I'm awake" click in `wake_log.txt`
- 🧰 Tray icon with right-click menu:
  - "I'm awake"
  - Settings
  - Exit

---

## 📦 Installation

```bash
pip install -r requirements.txt
```

---

## ⚙️ Usage

Run the script:

```bash
python deadmans-switch.py
```

### Tray Icon Menu Options:
- **"I'm awake"** – Confirms you're active
- **Settings** – Customize time intervals
- **Exit** – Close the script

When the notification pops up:
- Click **“I’m awake”** to dismiss
- If ignored, your computer will shut down

---

## 🧾 Wake Log

Every time you confirm you're awake, an entry is added to `wake_log.txt` in the root directory.
