#!/usr/bin/python

import subprocess
import argparse
import re
from pprint import pp

# Variables
# Define the device hints for headset and built-in
# ToDo: also define volumes
devices = {
    'builtin': {
        'speaker': {
            'name': 'Comet Lake PCH cAVS Speaker + Headphones',
            'type': 'HDA Analog (*)'
            },
        'microphone': {
            'name': 'Comet Lake PCH cAVS Digital Microphone',
            'type': 'DMIC (*)'
            }
    },
    'headset': {
        'speaker': {
            'name': 'Plantronics Blackwire 5220 Series Analog Stereo',
            'type': 'USB Audio'
            },
        'microphone': {
            'name': 'Plantronics Blackwire 5220 Series Mono',
            'type': 'USB Audio'
            }
        }
    }

all_speakers = {}
all_microphones = {}
all_applications = {}
default_speaker = 'unknown'
default_microphone = 'unknown'

# Methods
def count_leading_tabs(long, short):
    diff = long.strip(short)
    return diff.count('\t')

def gather_speakers():
    global all_speakers
    allsinks = subprocess.run(['pactl', 'list', 'sinks'], capture_output=True, text=True)
    all_list = gather_list(allsinks.stdout, 'Sink #')
    if all_list:
        all_speakers = all_list
    return

def gather_microphones():
    global all_microphones
    allsinks = subprocess.run(['pactl', 'list', 'sources'], capture_output=True, text=True)
    all_list = gather_list(allsinks.stdout, 'Source #')
    if all_list:
        all_microphones = all_list
    return

def gather_applications():
    global all_applications
    allapps = subprocess.run(['pactl', 'list', 'sink-inputs'], capture_output=True, text=True)
    all_list = gather_list(allapps.stdout, 'Sink Input #')
    if all_list:
        all_applications = all_list
    return

def gather_defaults():
    global all_speakers
    global all_microphones
    global default_speaker
    global default_microphone
    
    speaker = subprocess.run(['pactl', 'get-default-sink'], capture_output=True, text=True)
    default_speaker = speaker.stdout
    default_speaker = default_speaker.rstrip('\n')
    
    microphone = subprocess.run(['pactl', 'get-default-source'], capture_output=True, text=True)
    default_microphone = microphone.stdout
    default_microphone = default_microphone.rstrip('\n')

    return

def gather_list(resp, list_type):
    #print("type of listing: " + list_type)
    list_data = {}
    # loop all sinks. divider: \n\n
    for sink in resp.split("\n\n"):
        # loop all details of this sink divider: \n
        sink_id = 0 # key for each Sink
        mode = 'unknown'
        for s in sink.split("\n"):
            tab_count = 0 # Tracks tab level of each line
            c = []
            line = s.lstrip()
            tab_count = count_leading_tabs(s, line)
            #print("Tabs: " + str(tab_count))
            # Check for 'List Type'
            if tab_count == 0:
                # Detect the type of list
                if line[0:6] == list_type or line[0:8] == list_type or line[0:12] == list_type:
                    mode = 'sinkid'
                    sinkid = line.split(" #")
                    sink_id = int(sinkid[1])
                    if sinkid[1] not in list_data:
                        list_data[sink_id] = {}
                continue
            elif tab_count == 1:
                if line[0:11] == 'Properties:':
                    mode = 'properties'
                    continue # Skipping because properties are below this
                elif (line[0:7] == 'Volume:' or mode == 'volume'):
                    mode = 'volume'
                    #c = line.split(' ')
                    continue # Ignoring volume for now
                elif line[0:6] == 'Ports:':
                    mode = 'ports'
                    continue # Ignoring available ports for now
                elif line[0:8] == 'Formats:':
                    mode = 'formats'
                    continue # Ignoring available formats for now
                else:
                    mode = 'keyvalue'
                    c = line.split(": ")
            elif tab_count == 2:
                if mode == 'properties':
                    c = re.split(r'\s+=\s+', line)
                    v = c[1].lstrip('"')
                    v = v.rstrip('"')
                    c[1] = v
                elif mode == 'volume':
                    continue
                elif mode == 'ports':
                    continue
                elif mode == 'formats':
                    continue
            else:
                continue
            
            # Add the key value to the current sink ID
            list_data[sink_id].update({c[0]: c[1]})
    return list_data

def list_speakers():
    global all_speakers
    #global default_speaker
    print("========== Speakers ==========")
    for s in all_speakers:
        format_output('speaker', s)
        
def list_microphones():
    global all_microphones
    #global default_microphone
    print("========== Microphones ==========")
    for s in all_microphones:
        format_output('microphone', s)

def list_applications():
    global all_applications
    #global all_speakers
    print("========== Applications ==========")
    for s in all_applications:
        format_output('application', s)

def format_output(type_of, key):
    global all_speakers
    global all_microphones
    global all_applications
    global default_speaker    
    global default_microphone
    
    if type_of == 'speaker':
        default = ''
        if all_speakers[key]['Name'] == default_speaker:
            default = '(Default)'
        print(default + "ID: " + str(key)
          + "\tName: " + all_speakers[key]['Description']
          + " (" + all_speakers[key]['alsa.long_card_name']
          + ")\tType: " + all_speakers[key]['alsa.id']
          + "\tState: " + all_speakers[key]['State'])
    elif type_of == 'microphone':
        default = ''
        if all_microphones[key]['Name'] == default_microphone:
            default = '(Default)'
        print(default + "ID: " + str(key)
          + "\tName: " + all_microphones[key]['Description']
          + " (" + all_microphones[key]['alsa.long_card_name']
          + ")\tType: " + all_microphones[key]['alsa.id']
          + "\tState: " + all_microphones[key]['State'])
    elif type_of == 'application':
        linkedid = int(all_applications[key]['Sink'])
        print("ID: " + str(key)
          + "\tApp: " + all_applications[key]['application.name']
          + "\tLinked to: " + str(linkedid)
          + " (" + all_speakers[ linkedid ]['Description'] + ") ")
    else:
        print("Data type missing")

def find_text(text):
    result = {'result': False,
              'speaker': {},
              'microphone': {}
              }
    #text_in = alphanumeric(text)
    text_in = text
    if text_in:
        speakers = search_speakers(text_in)
        microphones = search_microphones(text_in)
        if speakers:
            result['result'] = True
            result['speaker'] = speakers
        if microphones:
            result['result'] = True
            result['microphone'] = microphones
    return result

def list_found_text(found):
    if found['result']:
        if found['speaker']:
            print("========== Speakers ==========")
            for s in found['speaker']:
                format_output('speaker', s)
        if found['microphone']:
            print("========== Microphones ==========")
            for s in found['microphone']:
                format_output('microphone', s)
    else:
        print("No Results")

def alphanumeric(data):
    if not re.match(r'(^[\w._]+$)', data, re.UNICODE):
        return False
    return data

def search_speakers(searchString):
    global all_speakers
    found = {}
    for sid in all_speakers:
        for k in all_speakers[sid]:
            if searchString in all_speakers[sid][k]:
                found[sid] = all_speakers[sid]
    return found

def search_microphones(searchString):
    global all_microphones
    found = {}
    for sid in all_microphones:
        for k in all_microphones[sid]:
            if searchString in all_microphones[sid][k]:
                found[sid] = all_microphones[sid]
    return found

def search_applications(searchString):
    global all_applications
    found = {}
    for sid in all_applications:
        for k in all_applications[sid]:
            if searchString in all_applications[sid][k]:
                found[sid] = all_applications[sid]
    return found

def set_new_default_speaker(sink_id):
    speaker = subprocess.run(['pactl', 'set-default-sink', sink_id], capture_output=True, text=True)
    pp(speaker.stdout)
    
# Main script

# Arguments
parser = argparse.ArgumentParser()

# Toggle to pre-defined speaker and mic device set
parser.add_argument('--headset', action='store_true', required=False,
                    help='Switch to predefined Headset for both speaker and microphone')
parser.add_argument('--builtin', action='store_true', required=False,
                    help='Switch to predefined Built-in for both speaker and microphone')

# Display
parser.add_argument('--display', action='store', required=False,
                    help='Display all available Inputs and Outputs')

# Check Regex of given name
parser.add_argument('--find', action='store', required=False,
                    help='Check if name of device matches.')



args = parser.parse_args()

# Gather all data first
gather_speakers()
gather_microphones()
gather_applications()
gather_defaults()

if args.display:
    list_microphones()
    list_speakers()
    list_applications()
    exit

if args.headset:
    pp(devices['headset'])
    exit

if args.builtin:
    pp(devices['builtin'])
    exit

if args.find:
    found = find_text(args.find)
    list_found_text(found)
    


"""
list_microphones()
list_speakers()
list_applications()
"""

"""
print("+~+~+~+~+~++~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+")
found = find_text('HDA Analog')
list_found_text(found)
"""
