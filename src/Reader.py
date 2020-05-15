import csv
import os.path
import string
import sys
from select import select

from evdev import InputDevice, ecodes, list_devices


class Reader:
    def __init__(self):
        path = os.path.dirname(os.path.realpath(__file__))
        self.keys = (
            "X^1234567890XXXXqwertzuiopXXXXasdfghjklXXXXXyxcvbnmXXXXXXXXXXXXXXXXXXXXXXX"
        )
        if not os.path.isfile(os.path.join(path, "deviceName.txt")):
            sys.exit("Please run config.py first")

        with open(os.path.join(path, "deviceName.txt"), "r") as f:
            deviceName = f.read()

        devices = [InputDevice(fn) for fn in list_devices()]
        for device in devices:
            if device.name == deviceName:
                self.rfidDevice = device
                break
        try:
            self.rfidDevice
        except:
            sys.exit(
                f"Could not find the device '{deviceName}'.\nMake sure it is connected and you are in the 'input' group"
            )

    def readCard(self):
        stri = ""
        key = ""
        while key != "KEY_ENTER":
            # print(f"Key: {key}")
            r, w, x = select([self.rfidDevice], [], [])
            for event in self.rfidDevice.read():
                if event.type == 1 and event.value == 1:
                    stri += self.keys[event.code]
                    key = ecodes.KEY[event.code]
        return stri[:-1]
