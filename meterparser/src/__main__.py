from app.mqtt import Mqtt
from app.service import Service
import sys
import signal

mqtt = Mqtt()
service = Service(mqtt.cameras)
def signal_handler(sig, frame):
    print('Exiting...')
    mqtt.mqtt_stop()
    sys.exit(0)

def run():
    service.start()
    mqtt.mqtt_start() # locks the execution

signal.signal(signal.SIGINT, signal_handler)
run()