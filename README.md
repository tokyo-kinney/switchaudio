# Switch Audio
Switch speakers and microphones with pactl only, in a less hackish way.

This python 3 script allows you to find and set up default speakers and microphones sets and switch between sets.
Instead of searching for the ID and creating a fragile shell script.

## Usage
### First set the Speaker and Microphone via the GUI. These become a set with the name you give.
1. Run the script with the --save **name for set**
~~~
$ switch-audio.py --save headset
~~~
2. Repeat steps 1 and 2 for each set you want.

### Now you can switch using the set name you gave.
1. Run the script with the --use **set name**
~~~
$ switch-audio.py --use laptop
~~~
The speaker and microphone will change to the ones specified in that set.
If an application is actively using a speaker and/or microphone, it will be switched as well.

### Check the sets created/available.
1. Run the script with just the --sets parameter.
~~~
$ switch-audio.py --sets
~~~

### List all the devices pactl can see.
1.Run the script with just the --display parameter and all speakers and microphones will be listed.
~~~
$ switch-audio.py --display
~~~

The KDE desktop of Fedora 36 didn't come with PulseAudio daemon set to run.
Only the pactl command was available.
This script matches the names and connection type of speakers and microphones.
This was done because the device IDs change each time.
Currently, tested and built on Fedora 36 KDE 5.
