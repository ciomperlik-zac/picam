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

### 1. Create a virtual enviornment and install required packages
- Run "python -m venv example" in the folder you want it created.
- Run pip install 

### 2.
