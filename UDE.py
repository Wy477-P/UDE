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

# DIRECTORIES #
workdir = os.getcwd()

def folfind(fo):
    return os.path.join(workdir, fo)

def filfind(fo, fi):
    return os.path.join(fo, fi)

logdir = folfind("logs")

configini = filfind(workdir,"config.ini")
gcontextjson = filfind(logdir,"gcontext.json")
goutput = filfind(logdir,"goutput.txt")
# DIRECTORIES #



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
running = True
def UDP(delay_per_key, word_delay_min, word_delay_max):
    global running
    running = True
    text = pyperclip.paste()
    text = text.lstrip()  
    
    time.sleep(0.1)
    
    for char in text:
        if not running:
            break
        if char == '’':
            pyautogui.typewrite("'")
        else:
            if char.isupper() or char in [':', '"', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+', '{', '}', '|', '<', '>', '?', '~']:
                pyautogui.keyDown('shift')
                pyautogui.typewrite(char)
                pyautogui.keyUp('shift')
            else:
                pyautogui.typewrite(char)

        time.sleep(delay_per_key)
        
        if char == ' ':
            word_delay = random.uniform(word_delay_min, word_delay_max)
            time.sleep(word_delay)
# UDP FUNCTION #



# UDP KILLSWITCH #
def kill_switch():
    global running
    running = False
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
