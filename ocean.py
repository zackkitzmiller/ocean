import random
import time

from phue import Bridge


BRIDGE_IP = "10.0.1.2"
BRIDGE_UN = "w6jTpTU6f7YaCpmbUImJCFJBy0mDf79clgJF1zCf"

SENSOR_ID =  46
WEATHER_LIGHT_ID = 2

class HueMotion(object):

    def __init__(self):
        self.bridge = None
        self.init_bridge()
        self.ensure_active()
        self.previous_sensor_state = False

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
                self.bridge.set_light(WEATHER_LIGHT_ID, params)
                self.previous_sensor_state = True
            elif not sensor_state and self.previous_sensor_state:
                self.previous_sensor_state = sensor_state
                print("[SENSOR SERVICE] No Motion Detected... ")


if __name__ == '__main__':
    processor = HueMotion()
    processor.run()
