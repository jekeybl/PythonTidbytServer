# Name:     tidbyt_server.py

# This python script emulates the Tidbyt server so that you are able to render multiple WebP's for specific durations
#   * Provides a method to not display certain WebP's based on nighttime when the display should be off or display darker versions
#   * Provides a method to queue the order of Tidbyt apps
#
# usage: tidbyt_server.py [-h] --device DEVICE [--day-start DAY_START] [--day-end DAY_END] [--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
# 
# Tidbyt server script
# 
# options:
#   -h, --help            show this help message and exit
#   --device DEVICE       Name of the Tidbyt device
#   --day-start DAY_START Day start time in HH:MM format
#   --day-end DAY_END     Day end time in HH:MM format
#   --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
#                         Set the logging level
#

import argparse
from datetime import datetime
import logging
import re
import subprocess
import time

class App:
    def __init__(self, name, mode, duration, repetition, star_file, args, webp_file):
        """
            name                Name to identify the entry
            mode                Value used to determine if the app should be displayed at night - False == NOT DISPLAYED, True == DISPLAYED
            duration            Value of how many seconds to sleep while displaying the webp.  This schould be identical to the maximum allowed animation duration (sec) of the .star file (default 15)
            repetition          Value of how many times to repeat the app's FOR loop
            star_file           Filename (with path e.g. "./" if in same directory as this script) of .star file
            args                Arguments for .star file
            webp_file           Filename (with path e.g. "./" if in same directory as this script) of .webp file
        """
        self.name = name
        self.mode = mode      
        self.duration = duration
        self.repetition = repetition
        self.star_file = star_file
        self.args = args
        self.webp_file = webp_file

    def __str__(self):
        return f"App(name={self.name}, mode={self.mode}, duration={self.duration}, repetition={self.repetition}, star_file={self.star_file}, args={self.args}, webp_file={self.webp_file})"

###### Function definitions

def initialize_apps():

    logging.debug("initialize_apps: enter")  

    apps = [
        App('fireflies', True, 10, 1, '../fireflies/fireflies.star', "n_fireflies=15 glow=15 color=#FFFF00 rnd_color=False show_clock=True", '../fireflies/fireflies.webp'),
        # Add other apps as needed
        #App('weatherclock', True, 5, 1, './weatherclock.star', "weatherAPI=xxxx", './weatherclock.webp'),
        #App('biorhythm', False, 15, 1, './biorhythm.star', "BDay='2023-01-01'", './biorhythm.webp'),
        #App('tides', False, 15, 1, './local_tides.star', "", './local_tides.webp'),
    ]

    # Enter the order of the apps to display based on apps index
    queue = [0]

    logging.debug("initialize_apps: exit")

    return apps, queue

def main():

    args = parse_arguments()

    logging.debug("main:--- Tidbyt Server Start ---")

    device = get_device(args.device)
    if device is None:
        logging.error("Device not found: {}".format(args.device))
        return
    else:
        logging.debug(f"main: Device name is {args.device}")

    apps, queue = initialize_apps()

    apps_str = "\n".join(str(app) for app in apps)
    logging.debug("main: List of apps:\n%s", apps_str)
    logging.debug("main: Current queue indices: %s", queue)

    rendertimes = [get_rendertime(app.star_file) for app in apps]
    main_loop(device, apps, queue, rendertimes, args.day_start, args.day_end)

def parse_arguments():

    # Setup argument parser
    parser = argparse.ArgumentParser(description="Tidbyt server script")
    parser.add_argument('--device', type=str, help='Name of the Tidbyt device', required=True)
    parser.add_argument('--day-start', type=str, default="07:00", help='Day start time in HH:MM format')
    parser.add_argument('--day-end', type=str, default="23:00", help='Day end time in HH:MM format')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help='Set the logging level')

    args = parser.parse_args()

    # Setup logging level
    if args.log_level:
        logging.basicConfig(level=getattr(logging, args.log_level), format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    else:
        logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')  # Default to WARNING

    logging.debug("parse_arguments: logging set")
    
    return args

def get_device(deviceName):

    logging.debug("get_device: enter")

    try:
        # Run the command and capture the output
        result = subprocess.run(["pixlet", "devices"], capture_output=True, text=True)
        # Convert the output to a list of devices by splitting it by newlines
        devices = result.stdout.split('\n')
        
        # Iterate over the list to find a device containing deviceName
        for device in devices:
            if deviceName in device:
                # Return the device name, splitting on ' (' to isolate the name part
                logging.debug("get_device: exit")
                return device.split(' (')[0]

        # Return None if no device with deviceName is found
            logging.debug("get_device: exit --- no device found")
        return None

    except subprocess.SubprocessError as e:
        logging.error(f"Failed to get devices: {e}")
        return None

def get_rendertime(file_name):
    logging.debug("get_rendertime: enter")
    logging.debug("get_rendertime: <%s>", file_name)

    try:
        # Run the command and capture the output
        result = subprocess.run(["pixlet", "profile", file_name], capture_output=True, text=True)

        # Compile a regular expression to find the number xxxx in the output of the string "100% of xxxxms total"
        pattern = re.compile(r"100% of (\d+)ms total")
        
        # Search the output for the pattern
        match = pattern.search(result.stdout)
        logging.debug("get_render_time: match %s", match)
        
        logging.debug("get_rendertime: exit")

        # Return the time in seconds if a match is found, otherwise return 0
        return float(match.group(1)) / 1000 if match else 0

    except subprocess.SubprocessError as e:
        logging.error(f"Failed to profile file {file_name}: {e}")
        return 0

def main_loop(device, apps, queue, rendertimes, day_start, day_end):

    logging.debug("main_loop: enter")

    while True:
        is_daytime = is_currently_daytime(day_start, day_end)
        process_app_queue(apps, queue, device, is_daytime, rendertimes)
        
    logging.debug("main_loop: exit")

def is_currently_daytime(day_start, day_end):

    logging.debug("is_currently_daytime: enter")

    start, end = day_time_range(day_start, day_end)

    logging.debug("is_currently_daytime: exit")

    return start <= datetime.now() < end

def day_time_range(day_start, day_end):

    logging.debug("day_time_range: enter")

    """ Returns the start and end time objects for the day. """
    start_hour, start_minute = map(int, day_start.split(':'))
    end_hour, end_minute = map(int, day_end.split(':'))
    now = datetime.now()
    start = now.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
    end = now.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)

    logging.debug("day_time_range: exit")

    return start, end

def process_app_queue(apps, queue, device, is_daytime, rendertimes):

    logging.debug("process_app_queue: enter")

    for idx in queue:
        logging.debug("process_app_queue: idx <%i>", idx)
        app = apps[idx]
        if app.mode or is_daytime:
            for _ in range(app.repetition):
                display_app(app, device)
                next_idx = (idx + 1) % len(queue)
                sleep_duration = app.duration - rendertimes[next_idx]
                logging.debug("process_app_queue: render time %f sec", rendertimes[next_idx])
                logging.debug("process_app_queue: going to sleep for %f sec", sleep_duration)
                time.sleep(max(sleep_duration, 1.0))
                logging.debug("process_app_queue: waking up")

    logging.debug("process_app_queue: exit")

def display_app(app, device):

    logging.debug("display_app: enter")

    render_command = ["pixlet", "render", app.star_file] + app.args.split()
    logging.debug("display_app: render_command <%s>", render_command)
    push_command = ["pixlet", "push", device, app.webp_file]
    logging.debug("display_app: push_command <%s>", push_command)

    try:

        logging.debug("display_app: run render_command")
        subprocess.run(render_command, capture_output=False, text=True)
        logging.debug("display_app: run push_command")
        subprocess.run(push_command, capture_output=False, text=True)
        
        logging.debug("display_app: exit")

    except subprocess.CalledProcessError as e:
        logging.error(f"Error processing {app.name}: {e}")

if __name__ == "__main__":
    main()
