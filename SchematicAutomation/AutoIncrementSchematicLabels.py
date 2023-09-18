#!/usr/bin/env python3
"""
This script allows quick incrementing of schematic labels.
First, run the script in a background shell.

When in the kicad schematic editor, select ONE (!) label and press
Shift+Alt+Q to increment the label by [increment]

By default, the increment is 1. To change the increment, press
Shift+Alt+1 and enter the new increment in the dialog box.
"""
import subprocess
import pyautogui
import time
import re
import pyperclip
import sexpdata

current_increment = 1

def increment_label(label, step=1):
    """
    Increment the numeric part of a label string by the given step.

    Args:
        label (str): The label string to increment.
        step (int): The amount to increment the numeric part of the label by.

    Returns:
        str: The incremented label string.
    """
    # Search for a bunch of digits at the end
    match = re.search(r'\d+$', label)
    # If found
    if match:
        # Get the number
        number = match.group(0)
        # Increment by 1
        number = int(number) + step
        # Replace the number in the clipboard
        return re.sub(r'\d+$', str(number), label)
    # Return unchanged
    return label


def run():
    print("Running...")
    # Press "e" key to edit
    time.sleep(0.2)
    # Press Ctrl+C to copy
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(0.1)
    # Copy from clipboard
    selection = pyperclip.paste()
    print("Selection: ", selection)
    if not selection:
        print("No selection")
        return
    # Selection is an s-expression such as:
    # (label "D_{Out}14" (at 31.75 142.24 0) (fields_autoplaced)
    #     (effects (font (size 1.27 1.27)) (justify left bottom))
    #     (uuid afb8599a-3fd7-42b6-a72a-152f78b11cf5)
    # )
    # Parse it!
    try:
        selection = sexpdata.loads(selection)
    except:
        print("Failed to parse selection: ", selection)
        return
    if str(selection[0]) == 'label':
        label_value = selection[1]
        selection[1] = sexpdata.Symbol()
        print(sexpdata.dumps(selection))
        
        # compute new label
        new_label = increment_label(label_value, step=current_increment)
        
        # Edit this label
        pyautogui.hotkey('e')
        time.sleep(0.1)
        # Remove the old label
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace')
        # Paste!
        pyperclip.copy(new_label)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.1)
        # Press Enter key to save
        pyautogui.press('enter')
    return

# Do something with the user input

def change_increment():
    """
    Show a dialog box to get user input and update the global variable current_increment
    """
    global current_increment
    # Start new thread that brings the dialog to the front
    subprocess.Popen('sleep 0.5 ; wmctrl -F -a "Increment" -b add,above', shell=True)
    #
    try:
        user_input = subprocess.check_output(f'zenity --title "Increment" --entry --text "Increment:" --entry-text "{current_increment}" --modal', shell=True).decode().strip()
        try:
            current_increment = int(user_input)
        except ValueError:
            print("Failed to parse user input: ", user_input)
            return
    except subprocess.CalledProcessError:
        print("Increment edit cancelled")
        return

# Register hotkeys
from system_hotkey import SystemHotkey
hk = SystemHotkey()
hk.register(('shift', 'alt', 'q'), callback=lambda x: run())
hk.register(('shift', 'alt', '1'), callback=lambda x: change_increment())

# Wait for exit
while True:
    time.sleep(10)