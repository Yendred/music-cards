import string
import csv
import os.path
import sys

from evdev import categorize, ecodes, InputDevice, list_devices
from select import select

rfidScanner = ""
keys = "X^1234567890XXXXqwertzuiopXXXXasdfghjklXXXXXyxcvbnmXXXXXXXXXXXXXXXXXXXXXXX"

path = os.path.dirname(os.path.realpath(__file__))
deviceNameFilePath = os.path.join(path, "deviceName.txt")
rfidScanner = None
if not os.path.isfile(deviceNameFilePath):
    sys.exit(
        "Could not find a device, Please run config.py to configure your RFID reader"
    )
else:
    with open(deviceNameFilePath, "r") as f:
        deviceName = f.read()

    for device in [InputDevice(fn) for fn in list_devices()]:
        if device.name == deviceName:
            print("Found device:" + device.name)
            rfidScanner = device
            break
    if rfidScanner == None or rfidScanner == "":
        sys.exit(
            "Could not find the device %s.\nMake sure is connected, or reconfigure the scanner by running config.py"
            % deviceName
        )

stri = ""
key = ""
while key != "KEY_ENTER":
    r, w, x = select([rfidScanner], [], [])
    for event in rfidScanner.read():
        if event.type == 1 and event.value == 1:
            stri += keys[event.code]
            key = ecodes.KEY[event.code]
print(stri[:-1])
