#!/usr/bin/python

import subprocess
import argparse
import re
from pprint import pp
from configparser import ConfigParser
import os.path

# Configuration sets are saved in this file
config_file = 'switch-audio.ini'
config = ConfigParser()

# Variables
all_speakers = {}
all_microphones = {}
all_apps_output = {}
all_apps_input = {}
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

def gather_apps_output():
    global all_apps_output
    # Gather sinks(speaker)
    allappssinks = subprocess.run(['pactl', 'list', 'sink-inputs'], capture_output=True, text=True)
    sinks_list = gather_list(allappssinks.stdout, 'Sink Input #')
    if sinks_list:
        all_apps_output = sinks_list
    return

def gather_apps_input():
    global all_apps_input
    # Gather sources(microphones)
    allappssources = subprocess.run(['pactl', 'list', 'source-outputs'], capture_output=True, text=True)
    sources_list = gather_list(allappssources.stdout, 'Source Output #')
    if sources_list:
        all_apps_input = sources_list
    return

def gather_defaults():
    global all_speakers
    global all_microphones
    global default_speaker
    global default_microphone
    
    speaker = subprocess.run(['pactl', 'get-default-sink'], capture_output=True, text=True)
    speaker_raw = speaker.stdout
    speaker_text = speaker_raw.rstrip('\n')
    default_speaker = search_speakers(speaker_text)
    
    microphone = subprocess.run(['pactl', 'get-default-source'], capture_output=True, text=True)
    microphone_raw = microphone.stdout
    microphone_text = microphone_raw.rstrip('\n')
    default_microphone = search_microphones(microphone_text)

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
                if line.startswith(list_type):
                #if line[0:6] == list_type or line[0:8] == list_type or line[0:12] == list_type or line[0:16] == list_type:
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
    print("========== Microphones ==========")
    for s in all_microphones:
        format_output('microphone', s)

def list_applications():
    list_apps_speakers()
    list_apps_microphones()

def list_apps_speakers():
    global all_apps_output
    print("========== Applications (speakers) ==========")
    for s in all_apps_output:
        format_output('app_speakers', s)

def list_apps_microphones():
    global all_apps_input
    print("========== Applications (microphones) ==========")
    for s in all_apps_input:
        format_output('app_microphones', s)

def format_output(type_of, key):
    global all_speakers
    global all_microphones
    global all_apps_output
    global all_apps_input
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
    elif type_of == 'app_speakers':
        linkedid = int(all_apps_output[key]['Sink'])
        print("ID: " + str(key)
          + "\tApp: " + all_apps_output[key]['application.name']
          + "\tLinked to: " + str(linkedid)
          + " (" + all_speakers[ linkedid ]['Description'] + ") ")
    elif type_of == 'app_microphones':
        linkedid = int(all_apps_input[key]['Source'])
        print("ID: " + str(key)
          + "\tApp: " + all_apps_input[key]['application.name']
          + "\tLinked to: " + str(linkedid)
          + " (" + all_microphones[ linkedid ]['Description'] + ") ")
    else:
        print("Data type missing")

def list_sets():
    global config
    for section in config.sections():
        print("Set: ", section)
        for key, value in config.items(section):
            print('   {} = {}'.format(key, value))
        print()

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
                continue
    return found

def search_microphones(searchString):
    global all_microphones
    found = {}
    for sid in all_microphones:
        for k in all_microphones[sid]:
            if searchString in all_microphones[sid][k]:
                found[sid] = all_microphones[sid]
                continue
    return found

def format_to_config(speaker, microphone):
    # Take pactl output and assign to config format.
    # The config only needs the Name and Type
    # Device IDs change so those are useless
    result = {}
    result['speaker_name'] = speaker['Description']
    result['speaker_type'] = speaker['alsa.id']
    result['mic_name'] = microphone['Description']
    result['mic_type'] = microphone['alsa.id']
    return result

def read_config():
    global config
    global config_file
    global default_speaker
    global default_microphone

    if os.path.exists(config_file):
        config.read(config_file)
    else:
        # No config file so create one from the defaults
        s_key = list(default_speaker.keys())[0]
        m_key = list(default_microphone.keys())[0]
        current = format_to_config(default_speaker[s_key], default_microphone[m_key])
        if not config.has_section("CURRENT"):
            #config.add_section("CURRENT")
            config["CURRENT"] = current
            with open(config_file, 'w') as configout:
                config.write(configout)
        print("No sets found. Create set from current defaults")
        list_sets()

def match_name_type(desc, alsa_id, search_type):
    found = []
    if search_type == 'speaker':
        speaker_match = search_speakers(desc)
        if speaker_match:
            for sid in speaker_match:
                # From each match check if the alsa.id matches the request
                if alsa_id in speaker_match[sid]['alsa.id']:
                    found.append(sid)
    elif search_type == 'microphone':
        mic_match = search_microphones(desc)
        if mic_match:
            for mid in mic_match:
                # From each match check if the alsa.id matches the request
                if alsa_id in mic_match[mid]['alsa.id']:
                    found.append(mid)

    return found

def set_new_default_speaker(sink_id):
    speaker = subprocess.run(['pactl', 'set-default-sink', sink_id], capture_output=True, text=True)
    pp(speaker.stdout)

def set_new_default_microphone(source_id):
    speaker = subprocess.run(['pactl', 'set-default-source', source_id], capture_output=True, text=True)
    pp(speaker.stdout)

def set_apps_sinks(sink_id):
    global all_apps_output
    for sid in all_apps_output:
        # sid is the application ID
        # sink_id is the speaker SINK
        application = subprocess.run(['pactl', 'move-sink-input', sid, sink_id], capture_output=True, text=True)
        pp(application.stdout)

def set_apps_source(source_id):
    global all_apps_input
    for sid in all_apps_input:
        # sid is the application ID
        # source_id is the microphone SOURCE
        application = subprocess.run(['pactl', 'move-source-output', sid, source_id], capture_output=True, text=True)
        pp(application.stdout)

def use_set(section):
    global config
    # Section search
    if config.has_section(section):
        # Match Set settings and set as defaults for system
        speaker_id = match_name_type(config.get(section, 'speaker_name'), config.get(section, 'speaker_type'), 'speaker')
        microphone_id = match_name_type(config.get(section, 'mic_name'), config.get(section, 'mic_type'), 'microphone')
        set_new_default_speaker(speaker_id)
        set_new_default_microphone(microphone_id)
        # Change any running applications to use the same speaker and microphone
        if all_apps_output:
            set_apps_sinks(speaker_id)
        if all_apps_input:
            set_apps_source(microphone_id)
    else:
        print("Set does not exist")
        list_sets()

def add_section(section):
    global config
    global config_file
    global default_speaker
    global default_microphone

    # If a unique name for Set then save
    if not config.has_section(section):
        # add defaults with this section name
        s_key = list(default_speaker.keys())[0]
        m_key = list(default_microphone.keys())[0]
        current = format_to_config(default_speaker[s_key], default_microphone[m_key])
        config.add_section(section)
        config[section] = current
        with open(config_file, 'w') as configout:
            config.write(configout)
    else:
        print("Set not saved because name not unique")
        list_sets()

    
    
# Main script

# Arguments
parser = argparse.ArgumentParser()

parser.add_argument('--use', action='store', required=False,
                    help='Use given Set as defaults')

parser.add_argument('--sets', action='store_true', required=False,
                    help='Show configured Sets')

# Available devices
parser.add_argument('--available', action='store_true', required=False,
                    help='Display all available Inputs and Outputs')

# Save current defaults as a Set
parser.add_argument('--save', required=False)

# Check Regex of given name
parser.add_argument('--find', action='store', required=False,
                    help='Check if name of device matches.')



args = parser.parse_args()

# Gather all data first
gather_speakers()
gather_microphones()
gather_apps_output()
gather_apps_input()
gather_defaults()
read_config()

if args.use:
    use_set(args.use)
    exit

exit

if args.sets:
    list_sets()
    exit

if args.available:
    list_microphones()
    list_speakers()
    list_applications()
    exit

if args.save:
    add_section(args.save)

if args.find:
    found = find_text(args.find)
    list_found_text(found)
