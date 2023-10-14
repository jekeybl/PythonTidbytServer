# Name:     tidbyt_server.py

# This python script mimics the Tidbyt server so that you are able to render multiple WebP's for specific durations
#   * Provides a method to not display certain WebP's based on nighttime when the display should be off or display darker versions
#   * Provides a method to queue the order of Tidbyt apps

import subprocess
import datetime
import time
import re

###### Function definitions

def get_device():

    # Run the command and capture the output
    output = subprocess.check_output("pixlet devices", shell=True)

    # Convert the output to a string and split it by newlines (\n)
    output_lines = str(output, 'utf-8').split('\n')
    devices_line = output_lines[0]

    return devices_line.split(' (')[0]

def get_rendertime(file_name):

    process = subprocess.run(["pixlet", "profile", file_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    output = process.stdout

    # Compile a regular expression to find the number xxxx in the output of the string "100% of xxxxms total"
    pattern = re.compile(r"100% of (\d+)ms total")

    # Search the output for the pattern
    match = pattern.search(output)

    # Show return the time in seconds
    if match:
        tm = int(match.group(1)) / 1000.
        return tm
    else:
        return 0

######

###### Define variables

debug = False

# MODE          Value used to determine if the app should be displayed at night - False == NOT DISPLAYED, True == DISPLAYED
#                   The MODE and DAY variables control the logic whether the app will be called - ( MODE || DAY )
# DURATION      Value of how many seconds to sleep while displaying the webp
# REPETITION    Value of how many times to repeat the app's for loop
# Tidybt = [{'NAME': '', 'MODE': True, 'DURATION': 1, 'REPETITION': 1, 'STAR_FILE': '', 'ARGS': '', 'WEBP_FILE': ''},]

Tidbyt = [
    {'NAME': 'my_clock', 'MODE': True, 'DURATION': 5, 'REPETITION': 1, 'STAR_FILE': '/Users/Shared/Tidbyt/weatherclock.star', 'ARGS': 'weatherAPI=xxxx', 'WEBP_FILE': '/Users/Shared/Tidbyt/weatherclock.webp'},
    {'NAME': 'biorhythm', 'MODE': False, 'DURATION': 5, 'REPETITION': 1, 'STAR_FILE': '/Users/Shared/Tidbyt/biorhythm.star', 'ARGS': 'BDay=\'2023-01-01\'', 'WEBP_FILE': '/Users/Shared/Tidbyt/biorhythm.webp'},
    {'NAME': 'tides', 'MODE': False, 'DURATION': 5, 'REPETITION': 1, 'STAR_FILE': '/Users/Shared/Tidbyt/local_tides.star', 'ARGS': '', 'WEBP_FILE': '/Users/Shared/Tidbyt/local_tides.webp'},
    {'NAME': 'fireflies', 'MODE': True, 'DURATION': 10, 'REPETITION': 1, 'STAR_FILE': '/Users/Shared/Tidbyt/fireflies.star', 'ARGS': 'n_fireflies=\'15\' glow=15 color=\'#FFFF00\' rnd_color=False show_clock=True', 'WEBP_FILE': '/Users/Shared/Tidbyt/fireflies.webp'},
    {'NAME': 'New_App', 'MODE': False, 'DURATION': 1, 'REPETITION': 1, 'STAR_FILE': '', 'ARGS': '', 'WEBP_FILE': ''},         
    ]
nTidbyt = len(Tidbyt)

T_MYCLOCK=0
T_BIORHYTHM=1
T_TIDES=2
T_FIREFLIES = 3
T_NEWAPP=4

# Enter the order of the apps to display
Queue = [T_FIREFLIES]           
nQueue = len(Queue)
device = get_device()

# Hours of daytime operation
H_DAY = 7         # 0 - 23
M_DAY = 0         # 0 - 59
H_NIGHT = 23      # 0 - 23
M_NIGHT = 0       # 0 - 59

######

# Determine how long it takes to render each of the apps in the queue
rendertime = []

for i in range(nQueue):
    rendertime.append(get_rendertime(Tidbyt[Queue[i]]['STAR_FILE']))

####################################
# TIDBYT SERVER
####################################

while True:

    now = datetime.datetime.now()
    am = datetime.datetime(now.year, now.month, now.day, H_DAY, M_DAY)
    pm = datetime.datetime(now.year, now.month, now.day, H_NIGHT, M_NIGHT)       
    if (now >= am and now < pm):
        DAY = True
    else:
        DAY = False

    for i in range(nQueue):

        x = Queue[i]
        if ( ( Tidbyt[x]['MODE'] or DAY ) ):

            for t in range(Tidbyt[x]['REPETITION']):

                if debug:
                    print(datetime.datetime.now(), Tidbyt[x]['NAME'], Tidbyt[x]['SWITCH'], Tidbyt[x]['MODE'], DAY)

                input = "pixlet render " + Tidbyt[x]['STAR_FILE'] + " " + Tidbyt[x]['ARGS']
                try:
                    output = subprocess.check_output(input, shell=True)
                except:
                    print(datetime.datetime.now(), "error render: ", Tidbyt[x]['NAME'], input)

                input = "pixlet push " + str(device) + " " + Tidbyt[x]['WEBP_FILE'] 
                try:
                    output = subprocess.check_output(input, shell=True)
                except:
                    print(datetime.datetime.now(), "error push: ", Tidbyt[x]['NAME'], input)

                sleep = Tidbyt[x]['DURATION'] - rendertime[(i + 1) % nQueue]
                if sleep <= 0:
                    sleep = Tidbyt[x]['DURATION']
                time.sleep(sleep)