## Tidbyt Server

---

To test my apps and see what they look like directly on the Tidbyt, I wanted to create a way to emulate the community Tidbyt server so that I could continuously cycle through one or more of my apps and create updated renderings and push the WebP's to my Tidbyt.

The use cases for the emulation are to:
+ Handle the management of any Tidbyt digital display device
+ Push .webp files generated from .star files to the Tidbyt
+ Have the ability to display WebP's for specific durations
+ Have the ability to not display selected WebP's because it is night
+ Have the ability to queue the order that the Tidbyt apps are displayed on the screen
+ Have the ability to continuously cycle through the selected apps
+ Already have the next WebP ready to be pushed to Tidbyt as the current WebP finishes displaying

**SOLUTION**

The Python file named `tidbyt_server.py` simulates the behavior of a Tidbyt server using Pixlet to render *Star* files and then display the *WebP* files for defined durations.  The script controls when specific apps are shown on the Tidbyt device based on the time of day, with specific attention given to whether or not the app should be displayed during nighttime hours.

***NOTE:*** The Tidbyt server file uses my developed apps (which are available on community/apps) in the `Tidbyt` list as examples of how to use the script.

Here is the general overview of the script:

1. **Imports:** The script imports several standard libraries: `subprocess`, `datetime`, `time`, and `re`.

2. **Function Definitions:**
   * `get_device()`: This function uses the `subprocess` module to run the command "pixlet devices" in the shell and capture its output, and returns the first line. 
   * `get_rendertime(file_name)`: This function takes a `.star` file as input, uses the `subprocess` module to run a pixlet profiling command with the file_name, and then uses regular expressions to extract the time it took to render the file.

3. **Variables Definitions:** There are several variables defined in the script:
   * `Tidbyt` list: Is a dictionary of elements for different Tidbyt apps having attributes like 'NAME', 'MODE', 'DURATION', 'REPETITION', 'STAR_FILE', 'ARGS', 'WEBP_FILE'.
   		* `NAME`: Name of the app (currently only informational)
		* `MODE`: Boolean indicating whether the app should be displayed at night (True means it will display, False means it will be skipped)
		* `DURATION`: How long (in seconds) the WebP will display.  The value should equal the duration that the app's animation is displayed or how long you want to display a non-changing image.  The maximum value should be around 15 seconds.  Some trial and error may need to be performed.
		* `REPETITION`: How many times the app's for loop should be repeated (Useful for clock apps)
		* `STAR_FILE`: Path to the `.star` file for rendering the display
		* `WEBP_FILE`: Path to the `.webp` file for uploading to the device
		* `ARGS`: Any additional arguments that are passed via the schema
   * `Queue` list: Here, we define the sequence to display the applications. The contents are the indices of apps in the `Tidbyt` list.
   * Several other variables to control the app's behavior (like `debug` for debugging, and `H_DAY`, `M_DAY`, `H_NIGHT`, `M_NIGHT` to control hours of operation).
   
4. **Main Logic**: The script enters an infinite loop where it constantly checks the current time and determines whether it's in day or night mode based on predefined variables. Then, it iteratively goes through each app in the queue and:
   * Checks if each app should be displayed or not based on its mode and whether it's day or night.
   * For each app to be displayed, the script attempts to run `pixlet render` and `pixlet push` commands via `subprocess.check_output(input, shell=True)`.
   * If an exception occurs while running these commands, the script will print an error message.  
   * The process goes to sleep for 'DURATION' (seconds) minus the time (seconds) that the next app in the queue needs to render the next WebP file so it is available once the current WebP file finishes displaying.

The .star files do not have to be located in the same folder as the Python script (tidbyt_server.py) by using the full path for the file names.  To run the script use the terminal to run the command:

*python3 tidbyt_server.py*


