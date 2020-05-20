import os
import time

from phue import Bridge
import progressbar
import requests


TEMP_MAP = {
    '20': {
        'hue': 46483,
        'bri': 124,
        'sat': 190
    },
    '30': {
        'hue': 40611,
        'bri': 124,
        'sat': 190
    },
    '40': {
        'hue': 20142,
        'bri': 124,
        'sat': 254
    },
    '50':{
        'hue': 28932,
        'bri': 124,
        'sat': 254
    },
    '60': {
        'hue': 11011,
        'bri': 124,
        'sat': 190
    },
    '70': {
        'hue': 4463,
        'bri': 162,
        'sat': 190
    },
    '80': {
        'hue': 64978,
        'bri': 124,
        'sat': 190
    }

}

BRIDGE_IP = os.getenv("BRIDGE_IP")
BRIDGE_UN = os.getenv("BRIDGE_UN")

LAT = 41.92
LNG = -87.72
UNITS = "imperial"

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
OPENWEATHER_BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
WEATHER_LIGHT_ID =  2


class HueWeather(object):

    def __init__(self):
        self.bridge = None
        self.init_bridge()
        self.last_know_temp = None

        self.ensure_lit()

    def ensure_lit(self):
        on = self.bridge.get_light(WEATHER_LIGHT_ID, parameter="on")
        if  on:
            print("[LIGHT SERVICE] Light is on... ")
            return
        print("[LIGHT SERVICE] Turning on weather light...")
        self.bridge.set_light(WEATHER_LIGHT_ID, 'on', True)

    def init_bridge(self):
        print("[BRIDGE SERVICE] Initializing...")
        self.bridge = Bridge(BRIDGE_IP, username=BRIDGE_UN)

    def convert_f_to_cct(self, current_temp):
        print(2500+(7500*((100-current_temp)/100)))
        return 2500+(7500*((100-current_temp)/100))

    def get_params_for_temp(self, temp):
        if temp <= 30:
            params = TEMP_MAP['30']
        if 30 <= temp <= 50:
            params = TEMP_MAP['40']
        if 50 <= temp <= 70:
            params = TEMP_MAP['50']
        if 70 <= temp <= 80:
            params = TEMP_MAP['70']
        if temp > 80:
            params = TEMP_MAP['80']
        return params

    def set_light(self, temp):
        self.ensure_lit()
        params = self.get_params_for_temp(temp)

        print(self.bridge.set_light(WEATHER_LIGHT_ID, params))
        print("[LIGHT SERVICE] Temp: {0} xy: {1}".format(
            temp, params
        ))

    def get_temp(self):
        weather_params = {
            "lat": LAT,
            "lon": LNG,
            'appid': OPENWEATHER_API_KEY,
            'units': UNITS
        }
        r = requests.get(OPENWEATHER_BASE_URL, params=weather_params)
        weather = r.json()

        current_temp = weather['main']['feels_like']
        temp_changed = False
        if current_temp != self.last_know_temp:
            print("[TEMPERATURE SERVICE] Temperature Change Detected")
            print("[TEMPERATURE SERVICE] Old: {0} New: {1}".format(
                self.last_know_temp, current_temp
            ))
            self.last_know_temp = current_temp
            temp_changed = True
        return current_temp, temp_changed

    def run(self):
        while True:
            try:
                temp, changed = self.get_temp()
                print("[RUNNER] Temp: {0}, Changed: {1}".format(
                    temp, changed))
                if changed:
                    self.set_light(temp)
            except Exception as e:
                print("[RUNNER] Error: {0}".format(e))

            widgets = [progressbar.ETA(
                format="%(eta)8s ",
                format_finished="",
                format_not_started=""
                ),
                progressbar.AnimatedMarker()
            ]
            bar = progressbar.ProgressBar(
                prefix="Time to Update: ", widgets=widgets
            )
            for _ in bar(range(30)):
                time.sleep(1)


# while True:
#     for i, xy in TEMP_MAP.items():
#         set_light(int(i))
#         time.sleep(3)


if __name__ == '__main__':
    processor = HueWeather()
    processor.run()
