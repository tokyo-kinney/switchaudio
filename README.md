# Switch Audio
Switch speakers and microphones with **pactl** only, in a less hackish way.

- This python 3.9+ script allows you to find and set up default speakers and microphones sets and switch between sets.
- Speakers and Microphones are found by name and connection type.
- All applications actively using audio will be switched as well.
- Creates a INI config file in same directory of script (switch-audio.ini)

## Install
1. Download the Zip or Clone with git from the green Code button above.
2. Confirm you have the pactl command.
~~~
$ which pactl
~~~
3. Move the switch-audio.py script to your preferred location and make it executable
~~~
$ mkdir -p ~/bin/audio/
$ mv ~/Downloads/switchaudio-main/switch-audio.py ~/bin/audio/
$ chmod 754 ~/bin/audio/switch-audio.py
~~~
4. Use the **Settings > Sounds** UI to set the Speaker and Microphone the way you like for the first set.
5. Back in terminal, **name** these defaults as a set.
~~~
$ ~/bin/audio/switch-audio.py --save headset
~~~
6. Repeat steps 4 and 5 for each set of Speaker and Microphone you need.
7. Close the Settings UI window completely (See [Known Issues](##Known Issues)). 
8. Setup alias or key shortcuts to run the script with a given **set** ([in KDE](https://docs.kde.org/stable5/en/khelpcenter/fundamentals/shortcuts.html)) or ([GNOME](https://docs.fedoraproject.org/en-US/quick-docs/proc_setting-key-shortcut/))
~~~
~/bin/audio/switch-audio.py --use headset
~/bin/audio/switch-audio.py --use laptop
~~~

## Usage
### Show available devices
~~~
$ switch-audio.py --available
~~~

### Save the current defaults as a named set.
~~~
$ switch-audio.py --save laptop
~~~

### Use the Speaker and Microphone of a set as defaults
~~~
$ switch-audio.py --use headset
~~~

### Check the sets created/available.
~~~
$ switch-audio.py --sets
~~~

### Find a name of a device
~~~
$ switch-audio.py --find Blackwire
~~~

## Purpose
- Switching quickly between Speakers and Microphones is too slow and error prone through the UI.
- There was no method of saving sets of Speaker+Microphone.
- Switching the audio used by multiple application is difficult.
- The IDs of the devices always changes especially if these are switched in and out.
- This script matches the names and connection type of speakers and microphones.
- Adding a keyboard shortcut makes switching faster.
- The INI file is human readable and can be backed up and hand edited.

## Known Issues
- When switching sets (--use headset) the **Settings UI** is seen as an application, so either the microphone or speaker will not be changed. Workaround: Close Settings UI while switching sets.
- Currently, tested only on Fedora 36 KDE and Gnome clean installs.

### ToDo:
- Add a preset volume in the settings to change the speakers to.
