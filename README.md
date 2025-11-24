# Vehicle-Service-Reminder
Vehicle Service Reminder System provides automated alerts based on time and mileage, ensuring timely maintenance.

This project is a simple **Vehicle Service Reminder** application written in Python using Tkinter.
It implements the rule:

Next service = last service + 10,000 km OR 1 year (whichever comes first).

## Included
- main.py : Main Tkinter GUI application (run this)
- vehicle_service.json : Data file (created automatically; sample included)
- README.md : This file


## How to run
1. Ensure you have Python 3.8+ installed.
2. In a terminal, run: python main.py

## Files
- The app stores data in "vehicle_service.json" (same directory as "main.py").
- Use the "Tools" tab to backup and restore JSON.
