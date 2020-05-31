import json
import os

import greenstalk
from phue import Bridge
from twilio.rest import Client


BEANSTALK_IP = os.getenv("BEANSTALK_IP")
BEANSTALK_PORT = os.getenv("BEANSTALK_PORT")

BRIDGE_IP = os.getenv("BRIDGE_IP")
BRIDGE_UN = os.getenv("BRIDGE_UN")
WEATHER_LIGHT_ID = 2

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOK = os.getenv("TWILIO_TOK")
TWILIO_MSG_SID = os.getenv("TWILIO_MSG_SID")
TEST_SMS = os.getenv("TEST_SMS")

class OceanWorker(object):

    def __init__(self):
        self.twilio_client = None
        if TWILIO_SID:
            self.init_twilio()
        self.beanstalk_client = None
        self.init_beanstalk()
        self.bridge = None
        self.init_bridge()

    def init_bridge(self):
        print("[BRIDGE SERVICE] Initializing...")
        self.bridge = Bridge(BRIDGE_IP, username=BRIDGE_UN)

    def init_beanstalk(self):
        print("[BEANSTALK SERVICE] Initializing Beanstalk Client")
        self.beanstalk_client = greenstalk.Client(
            host=BEANSTALK_IP,
            port=BEANSTALK_PORT,
            watch="ocean"
        )

    def init_twilio(self):
        print("[TWILIO SERVICE] Initializing...")
        self.twilio_client = Client(TWILIO_SID, TWILIO_TOK)

    def send_sms(self):
        message = self.twilio_client.messages \
            .create(
                body="Motion Detected. Lights should now change",
                messaging_service_sid=TWILIO_MSG_SID,
                to=TEST_SMS
            )

        print("[TWILIO SERVICE] Message sent with ID: {0}".format(
            message.sid))

    def process_messages(self):
        print("[OCEAN WORKER] Waiting for Job...")
        job = self.beanstalk_client.reserve()
        print("[OCEAN WORKER] recieved job: {0}".format(
            job.id
        ))
        try:
            params = json.loads(job.body)
        except:
            print("[OCEAN WORKER] Invalid JSON")
            self.beanstalk_client.delete(job)
            return

        print("[OCEAN WORKER] Setting light saturation to {0}".format(params['sat']))
        print("[OCEAN WORKER] Setting light XY to {0}".format(params['xy']))
        status = self.bridge.set_light(WEATHER_LIGHT_ID, params)
        if len(status) and len(status[0]):
            if 'error' in status[0][0]:
                print("[OCEAN WORKER] {0}".format(
                    status[0][0]['error']['description']))
                self.bridge.set_light(WEATHER_LIGHT_ID, "on", True)
                self.bridge.set_light(WEATHER_LIGHT_ID, params)
        # send_sms()
        self.beanstalk_client.delete(job)

if __name__ == "__main__":
    worker = OceanWorker()
    while True:
        worker.process_messages()
