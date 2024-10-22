import os
import configparser
import json
import pyperclip
import keyboard
from functools import partial
import requests
import pyautogui
import time
import random
import sys
import ctypes
import threading
import subprocess

current_version = "v1.1"
repo_url = "https://api.github.com/repos/Wy477-P/UDE" 

# DIRECTORIES #
workdir = os.getcwd()

def folfind(fo):
    return os.path.join(workdir, fo)

def filfind(fo, fi):
    return os.path.join(fo, fi)

logdir = folfind("logs")
dlldir = folfind("dlls")
configini = filfind(workdir,"config.ini")
gcontextjson = filfind(logdir,"gcontext.json")
goutput = filfind(logdir,"goutput.txt")
udpdll = filfind(dlldir, "UDP.dll")
autoupdate = filfind(workdir, "autoupdate.py")
# DIRECTORIES #



# AUTOUPDATE #
def check_for_updates():
    
    response = requests.get(f"{repo_url}/releases/latest")
    response.raise_for_status()
    latest_release = response.json()
    latest_version = latest_release['tag_name']

    
    if current_version != latest_version:
        subprocess.Popen(["python", autoupdate])
        os._exit(0)

check_for_updates()
# AUTOUPDATE #



# UDPDLL SETUP #
udp_dll = ctypes.CDLL(udpdll)
udp_dll.start_udp.argtypes = []
udp_dll.stop_udp.argtypes = []
udp_dll.udp.argtypes = [ctypes.c_char_p, ctypes.c_float, ctypes.c_float, ctypes.c_float]
udp_thread = None
def run_udp(text, delay_per_key, word_delay_min, word_delay_max):
    udp_dll.start_udp()
    udp_dll.udp(text.encode('utf-8'), delay_per_key, word_delay_min, word_delay_max)
# UDPDLL SETUP #



# EXIT FUNCTION #
def closeude():
    keyboard.unhook_all_hotkeys()
    os._exit(0)
# EXIT FUNCTION #



# UPDATE CONTEXT FUNCTION #
def ac(t, r):
    with open(gcontextjson, 'r') as f:
        con = json.load(f)
    e = {'role': r, 'parts': [{'text': t}]}
    con.append(e)
    with open(gcontextjson, 'w') as f:
        json.dump(con, f)
# UPDATE CONTEXT FUNCTION #



# UDG FUNCTION #
def UDG(key, inst, temper, toppp, topkk):
    if not os.path.isfile(gcontextjson):
        with open(gcontextjson, 'w') as f:
            json.dump([], f)
    userin = pyperclip.paste()
    user = "user"
    ac(userin, user)
    with open(gcontextjson, 'r') as f:
        con = json.load(f)
    SN = {
        "system_instruction": {
            "parts": [{
                "text": inst
            }]
        },
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ],
        "generationConfig": {
            "temperature": temper,
            "topP": toppp,
            "topK": topkk
        },
        "contents": con
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-8b:generateContent?key={key}"
    response = requests.post(url, json=SN, headers={'Content-Type': 'application/json'})
    RP = response.json()
    OP = RP.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
    pyperclip.copy(OP)
    ac(OP, "model")
    with open(goutput, 'w') as file:
        json.dump(RP, file)
# UDG FUNCTION #



# UDP FUNCTION #
def UDP(delay_per_key, word_delay_min, word_delay_max):
    global udp_thread
    text = pyperclip.paste()
    text = text.lstrip()
    text = text.replace('’', '\'')
    time.sleep(1.2)
    udp_thread = threading.Thread(target=run_udp, args=(text, delay_per_key, word_delay_min, word_delay_max))
    udp_thread.start()
# UDP FUNCTION #



# UDP KILLSWITCH #
def kill_switch():
    global udp_thread
    if udp_thread is not None and udp_thread.is_alive():
        udp_dll.stop_udp()
        udp_thread.join()
        udp_thread = None
# UDP KILLSWITCH #



# CLEAR CONTEXT #
def clearcon():
    if os.path.isfile(gcontextjson):
        os.remove(gcontextjson)
    with open(gcontextjson, 'w') as f:
        json.dump([], f)
# CLEAR CONTEXT #



# CHECK & IMPORT CONFIGS & UPDATE HOTKEYS #
apikey = None
sysin = None
temp = None
topp = None
topk = None
dpk = None
wdmin = None
wdmax = None
EXIT = None
CALLUDG = None
CALLUDP = None
CLEARCONTEXT = None
UPDATECONFIG = None
KILLSWITCH = None
def updatecfg(relod):
    global apikey, sysin, temp, topp, topk, dpk, wdmin, wdmax, EXIT, CALLUDG, CALLUDP, CLEARCONTEXT, UPDATECONFIG
    config = configparser.ConfigParser()
    config.read(configini)
    
    apikey = config['UDG']['api_key']
    sysin = config['UDG']['system_instructions']
    temp = float(config['UDG']['temperature'])
    topp = float(config['UDG']['top_p'])
    topk = float(config['UDG']['top_k'])
    dpk = float(config['UDP']['delay_per_key'])
    wdmin = float(config['UDP']['word_delay_min'])
    wdmax = float(config['UDP']['word_delay_max'])
    EXIT = config['HOTKEYS']['exit_hotkey']
    CALLUDG = config['HOTKEYS']['udg_hotkey']
    CALLUDP = config['HOTKEYS']['udp_hotkey']
    CLEARCONTEXT = config['HOTKEYS']['clear_context']
    UPDATECONFIG = config['HOTKEYS']['update_config']
    KILLSWITCH = config['HOTKEYS']['udp_killswitch']
    
    if relod:
        keyboard.remove_hotkey(EXIT)
        keyboard.remove_hotkey(CALLUDG)
        keyboard.remove_hotkey(CALLUDP)
        keyboard.remove_hotkey(CLEARCONTEXT)
        keyboard.remove_hotkey(UPDATECONFIG)
        keyboard.remove_hotkey(KILLSWITCH)
    
    keyboard.add_hotkey(EXIT, closeude)
    keyboard.add_hotkey(CALLUDG, partial(UDG, apikey, sysin, temp, topp, topk))
    keyboard.add_hotkey(CALLUDP, partial(UDP, dpk, wdmin, wdmax))
    keyboard.add_hotkey(CLEARCONTEXT, clearcon)
    keyboard.add_hotkey(UPDATECONFIG, partial(updatecfg, True))
    keyboard.add_hotkey(KILLSWITCH, kill_switch)
updatecfg(False)
# CHECK & IMPORT CONFIGS & UPDATE HOTKEYS #



keyboard.wait()
