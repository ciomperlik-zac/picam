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

### 1. Create a Discord server
- Add the following text channels:
  - interface
  - commands
  - alerts

### 2. Create a Discord bot
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

### 2. Download and set up the Bot from Github
- Download the "picam.py" file.
- Go back to [Discord Developer Portal](https://discord.com/developers).
- Go to the "bot" tab, and under "TOKEN" click "Reset token" and copy the key.
- At the very top of the program where the variable "token" is defined, replace "Your key" with the API key from discord.
- Scroll down to the very bottom of the program where it says "Setup code".
- Where the variable "interface_id" is defined, replace "None" with the id of your interface channel. To get the ID right click the channel and click Copy Channel ID.
- Run the bot once, it should crash and thats fine.
- Now scroll to the top and find the "discord_ids" list and enter all the respective IDs.
