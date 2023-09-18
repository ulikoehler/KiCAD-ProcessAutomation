#!/usr/bin/env python3
import pyautogui
import time
import re
import pyperclip
import sexpdata

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
        new_label = increment_label(label_value)
        
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
    
    # If not found
    # Press Enter key to save
    pyautogui.press('enter')
    # Press "o" key to exit
    pyautogui.press('o')

# Register hotkeys
from system_hotkey import SystemHotkey
hk = SystemHotkey()
hk.register(('shift', 'alt', 'q'), callback=lambda x: run())

# Wait for exit
while True:
    time.sleep(10)