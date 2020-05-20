import json
import os

import greenstalk
from phue import Bridge
from twilio.rest import Client


BEANSTALK_IP = os.getenv("BEANSTALK_IP")
BEANSTALK_PORT = os.getenv("BEANSTALK_PORT")
QUEUE = greenstalk.Client(host=BEANSTALK_IP, port=BEANSTALK_PORT)

BRIDGE_IP = os.getenv("BRIDGE_IP")
BRIDGE_UN = os.getenv("BRIDGE_UN")
BRIDGE = Bridge(BRIDGE_IP, username=BRIDGE_UN)
WEATHER_LIGHT_ID = 2

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOK = os.getenv("TWILIO_TOK")
TWILIO_MSG_SID = os.getenv("TWILIO_MSG_SID")
TEST_SMS = os.getenv("TEST_SMS")


def send_sms():
    client = Client(TWILIO_SID, TWILIO_TOK)

    message = client.messages \
        .create(
            body="Motion Detected. Lights should now change",
            messaging_service_sid=TWILIO_MSG_SID,
            to=TEST_SMS
        )

    print(message.sid)

def process_messages():
    print("[OCEAN WORKER] Waiting for Job...")
    job = QUEUE.reserve()
    print("[OCEAN WORKER] recieved job: {0}".format(
        job.id
    ))
    try:
        params = json.loads(job.body)
    except:
        print("[OCEAN WORKER] Invalid JSON")
        QUEUE.delete(job)
        return

    BRIDGE.set_light(WEATHER_LIGHT_ID, params)
    send_sms()
    QUEUE.delete(job)

if __name__ == "__main__":
    while True:
        process_messages()
