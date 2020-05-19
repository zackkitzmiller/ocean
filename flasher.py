import logging
import os
import random
import time

from phue import Bridge

logging.basicConfig()

BRIDGE_IP = "10.0.1.2"
BRIDGE_UN = os.getenv("BRIDGE_UN")
bridge = Bridge(BRIDGE_IP, username=BRIDGE_UN)
LIVING_ROOM_LIGHTS =  ["4", "8", "7", "6", "5", "2", "3"]

while True:
    random.shuffle(LIVING_ROOM_LIGHTS)
    for light in LIVING_ROOM_LIGHTS:
        x = random.random()
        y = random.random()
        bridge.set_light(int(light), 'on', True)
        bridge.set_light(int(light), 'xy', [x, y])
        time.sleep(.6)
