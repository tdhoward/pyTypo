# pyTypo v0.1
# written by Tim Howard, 2019


# Supports all these types of mistakes:
# 1. Reversed letters  (e.g. "Please join me for lnuch")        50%
# 2. Wrong letters (nearby) (e.g. "Please join me for lumch")   20%
# 3. Missing letters  (e.g. "Please join me for luch")          15%
# 4. Extra letters (nearby)  (e.g. "Please join me for lunmch") 15%

#DEBUG = True

if not DEBUG:
    # hide the console window right away
    import win32console,win32gui
    window = win32console.GetConsoleWindow()
    win32gui.ShowWindow(window,0)


#Disallow Multiple Instance
import win32event, win32api, winerror
mutex = win32event.CreateMutex(None, 1, 'mutex_var_typo')
if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
    mutex = None
    if DEBUG:
        print("Multiple instances not allowed")
    exit(0)


import pythoncom, pyHook
import ctypes
from ctypes import wintypes
import time
import threading
import random


def time_milli():
    return int(round(time.time() * 1000))


user32 = ctypes.WinDLL('user32', use_last_error=True)

INPUT_MOUSE    = 0
INPUT_KEYBOARD = 1
INPUT_HARDWARE = 2

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP       = 0x0002
KEYEVENTF_UNICODE     = 0x0004
KEYEVENTF_SCANCODE    = 0x0008

MAPVK_VK_TO_VSC = 0

# Find keycodes at msdn.microsoft.com/en-us/library/dd375731

keycode = {
    '0': 0x30,
    '1': 0x31,
    '2': 0x32,
    '3': 0x33,
    '4': 0x34,
    '5': 0x35,
    '6': 0x36,
    '7': 0x37,
    '8': 0x38,
    '9': 0x39,
    'A': 0x41,
    'B': 0x42,
    'C': 0x43,
    'D': 0x44,
    'E': 0x45,
    'F': 0x46,
    'G': 0x47,
    'H': 0x48,
    'I': 0x49,
    'J': 0x4A,
    'K': 0x4B,
    'L': 0x4C,
    'M': 0x4D,
    'N': 0x4E,
    'O': 0x4F,
    'P': 0x50,
    'Q': 0x51,
    'R': 0x52,
    'S': 0x53,
    'T': 0x54,
    'U': 0x55,
    'V': 0x56,
    'W': 0x57,
    'X': 0x58,
    'Y': 0x59,
    'Z': 0x5A,
    ';': 0xBA,
    ',': 0xBC,
    '-': 0xBD,
    '.': 0xBE,
    '[': 0xDB
}

# translate to reverse the keycode
codekey = {v: k for k, v in keycode.items()}

keys_nearby = {
    'A': ['Q','W','S','Z'],
    'B': ['V','G'],
    'C': ['X','D','F','V'],
    'D': ['S','E','R','F','C','X'],
    'E': ['R','D','S','W'], # 3, 4
    'F': ['R','T','G','V','C','D'],
    'G': ['T','B','V','F'],
    'H': ['Y','U','J','N'],
    'I': ['O','K','J','U'], # 8, 9
    'J': ['U','I','K','M','N','H'],
    'K': ['I','O','L',',','M','J'],
    'L': ['O','P',';','.',',','K'],
    'M': ['K',',','N','J'],
    'N': ['H','J','M'],
    'O': ['P','L','K','I'], # 0, 9
    'P': ['[',';','L','O'], #0, -
    'Q': ['W','A'],  # 2, 1
    'R': ['T','F','D','E'], # 4,5
    'S': ['E','D','X','Z','A','W'],
    'T': ['G','F','R'],  # 5, 6
    'U': ['I','J','H','Y'],  # 7, 8
    'V': ['G','B','C','F'],
    'W': ['E','S','A','Q'],  #3, 2
    'X': ['D','C','Z','S'],
    'Y': ['U','H'], # 7
    'Z': ['S','X','A'],
}


def get_nearby_keyid(keyid):
    global keycode, codekey
    key = codekey[keyid]
    key_options = keys_nearby[key]
    if not key_options:  # no options found
        return keyid  # get out with the same keyid
    return keycode[key_options[random.randint(1,len(key_options))-1]]


# C struct definitions

wintypes.ULONG_PTR = wintypes.WPARAM

class MOUSEINPUT(ctypes.Structure):
    _fields_ = (("dx",          wintypes.LONG),
                ("dy",          wintypes.LONG),
                ("mouseData",   wintypes.DWORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))

class KEYBDINPUT(ctypes.Structure):
    _fields_ = (("wVk",         wintypes.WORD),
                ("wScan",       wintypes.WORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))

    def __init__(self, *args, **kwds):
        super(KEYBDINPUT, self).__init__(*args, **kwds)
        # some programs use the scan code even if KEYEVENTF_SCANCODE
        # isn't set in dwFflags, so attempt to map the correct code.
        if not self.dwFlags & KEYEVENTF_UNICODE:
            self.wScan = user32.MapVirtualKeyExW(self.wVk,
                                                 MAPVK_VK_TO_VSC, 0)

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = (("uMsg",    wintypes.DWORD),
                ("wParamL", wintypes.WORD),
                ("wParamH", wintypes.WORD))

class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = (("ki", KEYBDINPUT),
                    ("mi", MOUSEINPUT),
                    ("hi", HARDWAREINPUT))
    _anonymous_ = ("_input",)
    _fields_ = (("type",   wintypes.DWORD),
                ("_input", _INPUT))

LPINPUT = ctypes.POINTER(INPUT)

def _check_count(result, func, args):
    if result == 0:
        raise ctypes.WinError(ctypes.get_last_error())
    return args

user32.SendInput.errcheck = _check_count
user32.SendInput.argtypes = (wintypes.UINT, # nInputs
                             LPINPUT,       # pInputs
                             ctypes.c_int)  # cbSize


def PressKey(hexKeyCode):
    x = INPUT(type=INPUT_KEYBOARD,
              ki=KEYBDINPUT(wVk=hexKeyCode))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

def ReleaseKey(hexKeyCode):
    x = INPUT(type=INPUT_KEYBOARD,
              ki=KEYBDINPUT(wVk=hexKeyCode,
                            dwFlags=KEYEVENTF_KEYUP))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

    
def pushkey(hexKeyCode):
    PressKey(hexKeyCode)
    ReleaseKey(hexKeyCode)
    

prev_time = 0
cur_time = 0
time_threshold = 125  # low time delta triggers operation

random_percentage = 30  # to make things less predictable...

resume_operation = 0  # time until we resume operation
resume_timeout = 17000  # in milliseconds

moved_keypress_delay = 250  # milliseconds to hold before sending the keypress

stored_key_id = 0  # which keypress are we delaying for later?
stored_timing = 0  # when will we release that keypress?

in_word = False
last_key_id = 0  # what was the previous key that was pressed?
current_key_id = 0  # current key being pressed
    
def OnKeyboardEvent(event):
    global prev_time, cur_time, time_threshold, resume_operation, stored_key_id, stored_timing
    global moved_keypress_delay, resume_timeout, in_word, random_percentage, last_key_id, current_key_id
    prev_time = cur_time
    cur_time = event.Time
    time_delta = cur_time - prev_time

    if DEBUG:
        print(event.KeyID,' ',time_delta,' (',event.Key,')')
    old_in_word = in_word
    last_key_id = current_key_id
    current_key_id = event.KeyID
    
    # Get out if we're not in the middle of a word.
    if current_key_id in range(65, 91):  # alphabet
        in_word = True
    else:
        in_word = False
        
    if not in_word or not old_in_word:
        return True
        
    if time_delta < time_threshold:  # we hit the timing trigger
        now_time = time_milli()
        if now_time > resume_operation:  # check if we're allowed to operate again
            if DEBUG:
                print(event.KeyID,' ',time_delta,' (',event.Key,')')
            if random.random() > (random_percentage / 100.0):  # don't do this EVERY time...
                if DEBUG:
                    print('Nope')
                return True
            if DEBUG:
                print('Yep')
            
            # decide which type of error to produce
            # 1. Reversed letters  (e.g. "Please join me for lnuch")        60%
            # 2. Wrong letters (nearby) (e.g. "Please join me for lumch")   10%
            # 3. Missing letters  (e.g. "Please join me for luch")          20%
            # 4. Extra letters (nearby)  (e.g. "Please join me for lunmch") 10%

            r = random.random()
            if r < 0.10:  # 10%
                type = 4
                if current_key_id == last_key_id:  # don't use this on repeated letters
                    return True
            elif r < 0.30:  # 20%
                type = 3
            elif r < 0.40:  # 10%
                type = 2
                if current_key_id == last_key_id:  # don't use this on repeated letters
                    return True
            else:           # 60%
                type = 1
                if current_key_id == last_key_id:  # don't use this on repeated letters
                    return True
                
            resume_operation = now_time + resume_timeout  # store the next resume_operation time

            if type == 1:  # Reversed letters
                stored_key_id = current_key_id  # store the key ID
                stored_timing = now_time + moved_keypress_delay  # store the time to send the key (add a delay)
                return False
            elif type == 2:  # Wrong letters (nearby)
                stored_key_id = get_nearby_keyid(current_key_id)  # store the key ID based on what is nearby
                stored_timing = now_time  # send the key now
                return False
            elif type == 3:  # Missing letters
                return False  # just skip this letter
            else:            # Extra letters (nearby)
                stored_key_id = get_nearby_keyid(current_key_id)  # store the key ID based on what is nearby
                stored_timing = now_time  # send the key now, as well as the original key
                return True
    return True


#thread for sending characters
class TimerClass(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.event = threading.Event()
    def run(self):
        global stored_key_id, stored_timing
        while not self.event.is_set():
            if stored_key_id:
                if time_milli() >= stored_timing:
                    pushed_key = stored_key_id
                    stored_key_id = 0
                    pushkey(pushed_key)
            self.event.wait(0.005)  # wait 5 milliseconds


sendkeys_thread=TimerClass()
sendkeys_thread.start()
            
# create a hook manager
hm = pyHook.HookManager()
# watch for all mouse events
hm.KeyDown = OnKeyboardEvent
# set the hook
hm.HookKeyboard()
# wait forever
pythoncom.PumpMessages()
