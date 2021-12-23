import time
import sys
import paho.mqtt.client as mqtt
import threading

from .ha_api import supervisor
from .config import config
from .camera import Camera

mqtt_config = supervisor("mqtt")
mqtt_client = mqtt.Client("meter-parser-addon")


def mqtt_connected(client, userdata, flags, rc):
    # spawn camera threads
    for cfg in config:
        Camera(cfg).start()

def mqtt_start():
    while True:
        try:
            print("connecting to mqtt...")    
            mqtt_client.username_pw_set(username=mqtt_config["username"],password=mqtt_config["password"])
            mqtt_client.connect(mqtt_config["host"], mqtt_config["port"])
            mqtt_client.loop_forever()
            return
        except Exception as e:
            print("Could not connect to mqtt. Retry in 5 secs. %s" % e, file=sys.stderr)
            time.sleep(5)

mqtt_client.on_connect = mqtt_connected
