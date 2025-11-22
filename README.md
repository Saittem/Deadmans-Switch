![Python Version](https://img.shields.io/badge/python-3.13.5+-blue.svg)
# Deadman Switch

A Python-based system tray application that monitors user activity and sends periodic notifications to ensure the user is awake and active. If the user fails to respond, the system will trigger a shutdown.

## Features

- **Dual Monitoring Modes**
  - **Notification Mode**: Sends periodic notifications at configured intervals
  - **Activity Mode**: Monitors keyboard and mouse activity, triggers notification after inactivity threshold

- **System Tray Integration**: Runs quietly in the background with easy access via system tray icon

- **Configurable Settings**
  - Target start time
  - Notification duration
  - Notification interval
  - Inactivity threshold
  - Hot-swappable monitoring modes

- **Audio Alerts**: Plays sound notification when alerting the user

- **Activity Logging**: Tracks all user interactions in a log file

- **Graceful Shutdown Prevention**: Countdown timer with option to cancel shutdown

## Installation

### Setup

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. (Optional) Add a `notification.mp3` audio file to the project directory for custom alert sounds

3. (Optional) Add an `icon.ico` file for a custom system tray icon

## Usage

### Starting the Application

Run the main script:
```bash
python main.py
```

The application will start minimized to the system tray.

### System Tray Menu

Right-click the tray icon to access:
- **I'm Awake**: Manually confirm you're active
- **Settings**: Configure monitoring parameters
- **Exit**: Stop the application

### Configuration

Access settings through the system tray menu. Available options:

| Setting | Description | Default |
|---------|-------------|---------|
| Target Time | Time to start monitoring (HH:MM format) | 02:00 |
| Notification Duration | Seconds before auto-shutdown | 60 |
| Notification Interval | Seconds between notifications | 600 |
| Script Version | `notification` or `activity` mode | notification |
| Inactivity Threshold | Seconds of inactivity before alert (activity mode) | 900 |

### Monitoring Modes

**Notification Mode**
- Waits until the target time
- Sends periodic notifications at the configured interval
- Requires user response to prevent shutdown

**Activity Mode**
- Monitors keyboard and mouse activity continuously
- Triggers notification after the inactivity threshold is exceeded
- Automatically resets when activity is detected

## Customization

### Custom Audio

Replace `notification.mp3` with your preferred alert sound.

### Custom Icon

Replace `icon.ico` with your preferred tray icon (64x64 recommended).

## Logging

All user interactions are logged to `wake_log.txt` with timestamps:
```
[2024-11-22 14:30:45] User clicked 'I'm Awake' via notification.
[2024-11-22 14:45:30] User clicked 'I'm Awake' via tray menu.
```
