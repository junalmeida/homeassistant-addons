import json
import logging
import time
import traceback
import paho.mqtt.client as mqtt
import os
import threading

from slugify import slugify
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

        self.cameras: list = list()
    def mqtt_connected(self, client, userdata, flags, rc):
        # spawn camera threads
        from app.camera import Camera
        for cfg in config["cameras"]:
            entity_id = slugify(cfg["name"])
            camera = next((cam for cam in self.cameras if cam._entity_id == entity_id), None)            
            if camera is None:
                camera = Camera(cfg, entity_id, self, config["debug_path"] if "debug_path" in config else None)
                self.cameras.append(camera)
                camera.start()     
            self.mqtt_sensor_discovery(camera.entity_id, camera.name, camera._device_class, camera._unit_of_measurement) 

    def mqtt_disconnected(self, client, userdata, rc):        
        if not self._mqtt_client.is_connected:
            for camera in self.cameras:
                camera.stop()
            self.cameras.clear()
            _LOGGER.debug("%s camera(s) running" % len(self.cameras))    

    def mqtt_start(self):
        while True:
            try:
                username = str(self._mqtt_config["username"])
                password = str(self._mqtt_config["password"])
                host = str(self._mqtt_config["host"])
                port = int(self._mqtt_config["port"])
                _LOGGER.debug("Connecting to mqtt %s..." % host)    
                self._mqtt_client.username_pw_set(username=username,password=password)
                self._mqtt_client.connect(host, port)
                self._mqtt_client.loop_forever()
                return
            except Exception as e:
                _LOGGER.error("Could not connect to mqtt: %s. Retry in 5 secs." % e)
                time.sleep(5)
    def mqtt_sensor_discovery(self, entity_id: str, name: str, device_class: str, unit_of_measurement: str):
        device_id = os.environ["HOSTNAME"] if "HOSTNAME" in os.environ else os.environ["COMPUTERNAME"]
        device = {
                "identifiers": device_id,
                "manufacturer": "Meter Parser",
                "model": "Meter Parser Add-On",
                "name": "Meter Parser",
                "sw_version": "1.0.0" # TODO: Get from git build            
            }
            
        topic_sensor = "%s/sensor/%s/config" % (discovery_prefix, entity_id)
        icon = "mdi:water"
        if device_class == "energy":
            icon = "mdi:flash"
        elif device_class == "gas":
            icon = "mdi:fire"


        payload_sensor = {
            "name": name, 
            "icon": icon,
            "unit_of_measurement": unit_of_measurement,
            "state_class": "total_increasing",
            "state_topic": "%s/sensor/%s/state" % (discovery_prefix, entity_id),
            "availability_topic": "%s/sensor/%s/availability" % (discovery_prefix, entity_id),
            "json_attributes_topic": "%s/sensor/%s/attributes" % (discovery_prefix, entity_id),
            "object_id": entity_id,
            "unique_id": "%s.%s" % (device_id, entity_id),
            "device": device
        }
        if device_class != "water":
            payload_sensor["device_class"] = device_class


        topic_camera = "%s/camera/%s/config" % (discovery_prefix, entity_id)
        payload_camera = {
            "name": name, 
            "topic": "%s/camera/%s/state" % (discovery_prefix, entity_id),
            "availability_topic": "%s/camera/%s/availability" % (discovery_prefix, entity_id),
            "json_attributes_topic": "%s/camera/%s/attributes" % (discovery_prefix, entity_id),
            "object_id": entity_id,
            "unique_id": "%s.%s_cam" % (device_id, entity_id),
            "device": device
        }

        self._mqtt_client.publish(topic_sensor, payload=json.dumps(payload_sensor).encode("utf-8"))
        self._mqtt_client.publish(topic_camera, payload=json.dumps(payload_camera).encode("utf-8"))

    def mqtt_set_state(self, type:str, entity_id: str, state):
        topic = "%s/%s/%s/state" % (discovery_prefix, type, entity_id)
        self._mqtt_client.publish(topic, payload=state)
    def mqtt_set_attributes(self, type:str, entity_id: str, attributes):
        topic = "%s/%s/%s/attributes" % (discovery_prefix, type, entity_id)
        self._mqtt_client.publish(topic, payload=json.dumps(attributes))
    def mqtt_set_availability(self, type:str, entity_id: str, available: bool):
        topic = "%s/%s/%s/availability" % (discovery_prefix, type, entity_id)
        self._mqtt_client.publish(topic, payload=("online" if available else "offline"))
