import os.path
from evdev import InputDevice, list_devices

i = 0
devices = [InputDevice(fn) for fn in list_devices()]
print("Choose the reader from list?")
for dev in devices:
    print(i + " : " + dev.name)
    i += 1

dev_id = int(input("Device Number: "))

path = os.path.dirname(os.path.realpath(__file__))
with open(path + "/deviceName.txt", "w") as f:
    f.write(devices[dev_id].name)
    f.close()
