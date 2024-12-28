# picam

A simple implentation of motion detection using Discord as a frontend for alerts and configuration. Built to run on a Raspberry Pi and written in Python.

## Commands

### 1. "md"
- **Description**: Toggles the motion detection feature on or off.  
- **Usage**: /md enable/disable

### 2. "mdschedule"
- **Description**: Modifies the schedule for motion detection.  
- **Usage**: /mdschedule set/disable

### 3. "capture"
- **Description**: Manually captures an image.
- **Usage**: /capture

### 4. "endpoint"
- **Description**: Connects to an optional socket server which will receive motion alerts.
- **Usage**: /endpoint connect/disconnect

MD, mdschedule, and capture also have their respective buttons within the interface embed.

## Setup

This project was designed specifically for the Raspberry Pi. If you want to use it on another platform, all you'd really need to change is the methods for capturing images and videos. I'd recomend using a library like opencv-python.

### 1. Create a Discord server.
- Add the following text channels:
  - interface
  - commands
  - alerts

### 2. Create a Discord bot.
- Open [Discord Developer Portal](https://discord.com/developers).
- Click new application.
- Go to the "Bot" tab, scroll down to Privileged Gateway Intents, and check all three.
- Go to the "Installation" tab, scroll down to Default Install Settings, and do the following:
  - Under Guild Install type "applications.commands" and "bot" into the Scopes field.
  - Under Guild Install type "Administrator" into the Permissions field.
- Scroll up to Install Link, copy it, and open it in a new tab to invite the bot to your server.

### 1. Create a virtual enviornment and install required packages
- Open command prompt on your Raspberry Pi.
- Run `python -m venv example` in the folder you want the virtual environment created.
- Run `source example/bin/activate` to enter the virtual environment.
- Run `pip install discord.py, opencv-python, picamera2` to install required packages.

### 2. Download the Bot from Github.
