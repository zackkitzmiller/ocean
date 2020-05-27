import json
import os
import random
import time

import greenstalk
from phue import Bridge
import redis

BRIDGE_IP = os.getenv("BRIDGE_IP")
BRIDGE_UN = os.getenv("BRIDGE_UN")
BEANSTALK_IP = os.getenv("BEANSTALK_IP")
BEANSTALK_PORT = os.getenv("BEANSTALK_PORT")
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")

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
        self.redis = None
        self.init_redis()

    def init_redis(self):
        print("[REDIS SERVICE] Initializing...")
        self.redis = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

    def init_queue(self):
        print("[QUEUE SERVICE] Initializing...")
        self.queue = greenstalk.Client(host=BEANSTALK_IP, port=BEANSTALK_PORT)
        self.queue.use("ocean")

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
            if self.redis.get('ocean:disabled'):
                print("[OCEAN SERVICE] Ocean Disabled")
                time.sleep(30)
                continue

            try:
                sensor = self.bridge.get_sensor(sensor_id=SENSOR_ID)
            except Exception as e:
                print("[SENSOR SERVICE] Error getting Sensor: {0}".format(e))
                continue
            sensor_state = sensor['state']['presence']
            if sensor_state and not self.previous_sensor_state:
                print("[SENSOR SERVICE] Motion Detected... ")
                params = {
                    'sat': random.randint(0, 254),
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
