import json
import logging
import time
import traceback
import paho.mqtt.client as mqtt
import os
from app.ha_api import supervisor
from app.config import config

_LOGGER = logging.getLogger(__name__)
discovery_prefix = "homeassistant"

class Mqtt:
    def __init__(self):

        if "mqtt" in config and "host" in config["mqtt"]:
            self._mqtt_config = config["mqtt"]
        else:    
            self._mqtt_config = supervisor("mqtt")
        self._mqtt_client = mqtt.Client("meter-parser-addon")
        self._mqtt_client.on_connect = self.mqtt_connected
        self._mqtt_client.on_disconnect = self.mqtt_disconnected
        self._cameras: list = list()
    def mqtt_connected(self, client, userdata, flags, rc):
        # spawn camera threads
        from app.camera import Camera
        _LOGGER.debug("Connected to mqtt, restarting cameras")
        self.mqtt_disconnected(client, userdata, rc)
        for cfg in config["cameras"]:
            camera = Camera(cfg, self, config["debug_path"] if "debug_path" in config else None)
            self._cameras.append(camera)
            camera.start()
        _LOGGER.debug("%s cameras running" % len(self._cameras))    
        

    def mqtt_disconnected(self, client, userdata, rc):        
        for camera in self._cameras:
            camera.stop()
        self._cameras.clear()

    def mqtt_start(self):
        while True:
            try:
                _LOGGER.debug("Connecting to mqtt...")    
                username = str(self._mqtt_config["username"])
                password = str(self._mqtt_config["password"])
                host = str(self._mqtt_config["host"])
                port = int(self._mqtt_config["port"])
                self._mqtt_client.username_pw_set(username=username,password=password)
                self._mqtt_client.connect(host, port)
                self._mqtt_client.loop_forever()
                return
            except Exception as e:
                _LOGGER.error("Could not connect to mqtt. Retry in 5 secs. %s" % e)
                time.sleep(5)
    def mqtt_sensor_discovery(self, entity_id: str, name: str, device_class: str, unit_of_measurement: str):
        topic = "%s/sensor/%s/config" % (discovery_prefix, entity_id)
        device_id = os.environ["HOSTNAME"] if "HOSTNAME" in os.environ else os.environ["COMPUTERNAME"]
        icon = "mdi:water"
        if device_class == "energy":
            icon = "mdi:flash"
        elif device_class == "gas":
            icon = "mdi:fire"
        payload = {
            "name": name, 
            "icon": icon,
            "unit_of_measurement": unit_of_measurement,
            "state_class": "total_increasing",
            "state_topic": "%s/sensor/%s/state" % (discovery_prefix, entity_id),
            "availability_topic": "%s/sensor/%s/availability" % (discovery_prefix, entity_id),
            "object_id": entity_id,
            "unique_id": "%s.%s" % (device_id, entity_id),
            "device": {
                "identifiers": device_id,
                "manufacturer": "Marcos Junior",
                "model": "Meter Parser Add-On",
                "name": "Meter Parser",
                "sw_version": "1.0.0" # TODO: Get from git build            
            }
        }
        if device_class != "water":
            payload["device_class"] = device_class
        self._mqtt_client.publish(topic, payload=json.dumps(payload).encode("utf-8"))

    def mqtt_state(self, entity_id: str, state):
        topic = "%s/sensor/%s/state" % (discovery_prefix, entity_id)
        self._mqtt_client.publish(topic, payload=state)
    def mqtt_availability(self, entity_id: str, available: bool):
        topic = "%s/sensor/%s/availability" % (discovery_prefix, entity_id)
        self._mqtt_client.publish(topic, payload=("online" if available else "offline"))
