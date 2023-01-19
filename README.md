# Switch Audio
Switch speakers and microphones with pactl only, in a less hackish way.

This python 3 script allows you to find and set up default speackers and microphones sets and switch between sets.
Instead of searching for the ID and creating a fragile shell script.

## Usage
Run the script with --display , and all speakers and microphones will be listed.
~~~
$ switch-audio.py --display
~~~


The KDE desktop of Fedora 36 didn't come with PulseAudio daemon set to run.
Only the pactl command was available.
