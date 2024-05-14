## Tidbyt Server

---

### Introduction
The ***tidbyt_server.py*** script serves as a Python-based server emulation for managing and displaying WebP images on Tidbyt devices based on certain conditions. It allows users to specify device names (helpful if you own multiple devices) and control the logging level through command-line arguments. The script is structured to continuously manage and display different apps based on time conditions and app settings.

##### Use Cases for the Emulation

+ Handle the  management for a Tidbyt digital display device
+ Use .webp files generated from .star files to render animations
+ Ability to display WebP's for specific durations
+ Ability to turn off rendering certain WebP's based on nighttime when the display should be off or show darker versions
+ Ability to queue the order of the Tidbyt apps
+ Ability to continuously cycle through the selected apps
+ Already have the next WebP ready to be sent to Tidbyt when the current WebP finishes displaying

### Purpose and Functionality
+ **Main Goal**: The script allows users to control the display of WebP images on a Tidbyt device based on time settings (daytime vs nighttime) and pre-set schedules. It also offers a facility to customize display content and duration for each app.
+ **Configuration**: It utilizes command-line arguments to configure the device name, day start/end times, and logging level, making it flexible for different environments and use cases.

#### Code Structure and Modules
+ **Modules Used**: The script imports standard Python modules such as argparse, datetime, logging, re, subprocess, and time which collectively support command-line parsing, date and time manipulation, regular expressions, external process management, and time-related functions.
+ **Class Definition**: A class App is defined to encapsulate the properties of each application or display item, including its name, display mode (day/night), duration, repetition frequency, related file names, and additional arguments.
#### Functions and Their Operations
+ **Initialization**: initialize_apps() sets up initial display items (apps) and their order of display.
+ **Device Handling**: get_device() identifies the connected Tidbyt device by name using the pixlet command-line tool.
+ **Time Management**: day_time_range() computes the start and end times of the day based on input arguments, essential for determining whether it's daytime or nighttime.
+ **Argument Parsing**: parse_arguments() sets up and parses command-line options, also configuring the logging level.
+ **Rendering and Display**: display_app() manages the rendering and pushing of WebP files to the device.
+ **Queue Processing** : process_app_queue() manages the sequence of app displays, taking into account whether it's appropriate to display them (daytime or app-specific settings).
#### Execution Flow
+ **Main Loop**: The main_loop() continuously checks the time of day and processes the queue of apps accordingly.
+ **Main Function**: Establishes the script's entry point, initializing necessary settings and starting the main loop.
#### Robustness and Error Handling
+ The script includes basic error handling for subprocesses to manage possible failures in external commands. It logs errors appropriately, helping in troubleshooting.

The .star files do not have to be located in the same folder as the Python script (tidbyt_server.py).

#### Usage
> ***python3** **tidbyt_server.py** [-h] --device DEVICE [--day-start DAY_START] [--day-end DAY_END] [--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}]*
>
>Tidbyt server script
>
>options:
>  -h, --help            show help message and exit
>  --device DEVICE &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Name of the Tidbyt device
>  --day-start DAY_START &nbsp;Day start time in HH:MM format - default 07:00
>  --day-end DAY_END &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Day end time in HH:MM format - default 23:00
>  --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Set the logging level - default WARNING


