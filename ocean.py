import json
import os
import random
import time

import greenstalk
from phue import Bridge

BRIDGE_IP = os.getenv("BRIDGE_IP")
BRIDGE_UN = os.getenv("BRIDGE_UN")
BEANSTALK_IP = os.getenv("BEANSTALK_IP")
BEANSTALK_PORT = os.getenv("BEANSTALK_PORT")

SENSOR_ID =  46
WEATHER_LIGHT_ID = 2

class HueMotion(object):

    def __init__(self):
        self.bridge = None
        self.init_bridge()
        self.ensure_active()
        self.previous_sensor_state = False
        self.queue = None
        self.init_queue()

    def init_queue(self):
        print("[QUEUE SERVICE] Initializing...")
        self.queue = greenstalk.Client(host=BEANSTALK_IP, port=BEANSTALK_PORT)

    def ensure_active(self):
        sensor = self.bridge.get_sensor(sensor_id=SENSOR_ID)
        print("[SENSOR SERVICE] Initializing...")
        if not sensor['config']['on']:
            self.bridge.set_sensor_config(SENSOR_ID, {'on': True})

    def init_bridge(self):
        print("[BRIDGE SERVICE] Initializing...")
        self.bridge = Bridge(BRIDGE_IP, username=BRIDGE_UN)

    def run(self):
        while True:
            sensor = self.bridge.get_sensor(sensor_id=SENSOR_ID)
            sensor_state = sensor['state']['presence']
            if sensor_state and not self.previous_sensor_state:
                print("[SENSOR SERVICE] Motion Detected... ")
                params = {
                    'xy': [random.random(), random.random()]
                }
                self.queue.put(json.dumps(params))
                # self.bridge.set_light(WEATHER_LIGHT_ID, params)
                self.previous_sensor_state = True
            elif not sensor_state and self.previous_sensor_state:
                self.previous_sensor_state = sensor_state
                print("[SENSOR SERVICE] No Motion Detected... ")


if __name__ == '__main__':
    processor = HueMotion()
    processor.run()
