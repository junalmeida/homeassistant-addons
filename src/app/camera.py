
import logging
import threading
import time
import requests
import numpy as np
import cv2
import traceback
from slugify import slugify
from app.mqtt import Mqtt

from app.parsers.image_utils import prepare_image
from app.parsers.parser_dial import parse_dials
from app.parsers.parser_digits import parse_digits
class Camera (threading.Thread):
    def __init__(self, camera: dict, mqtt: Mqtt, debug_path: str):
        threading.Thread.__init__(self)
        self._interval = int(camera["interval"])
        self._snapshot_url = str(camera["snapshot_url"])
        self._name = str(camera["name"])
        self._device_class = str(camera["device_class"]) if "device_class" in camera else "energy"
        self._unit_of_measurement = str(camera["unit_of_measurement"]) if "unit_of_measurement" in camera else "kWh"
        self._stop = False
        self._disposed = False
        self._current_reading = 0.0
        self._dials = int(camera["dials"]) if "dials" in camera else None
        self._dial_size = int(camera["dial_size"]) if "dial_size" in camera else 100
        self._digits = int(camera["digits"]) if "digits" in camera else None
        self._decimals = int(camera["decimals"]) if "decimals" in camera else None
        self._ocr_key = camera["ocr_key"] if "ocr_key" in camera else None
        self._entity_id = slugify(self._name)
        self._debug_path = None
        self._error_count = 0
        self._logger = logging.getLogger("%s.%s" % (__name__, self._entity_id))
        self._mqtt = mqtt
        self._debug_path = debug_path
        self._flip_horizontal = camera["flip_horizontal"] if "flip_horizontal" in camera else False
        self._flip_vertical = camera["flip_vertical"] if "flip_vertical" in camera else False

        if self._interval < 30: 
            raise Exception("Incorrect interval in seconds. Choose more than 30 seconds.")
        self._mqtt.mqtt_sensor_discovery(self._entity_id, self._name, self._device_class, self._unit_of_measurement)
        
    def stop(self):
        self._stop = True
        self._logger.warn("Stopping camera...")
        while not self._disposed:
            time.sleep(2)

    def run (self):
        self._logger.info("Starting camera %s" % self._name)
        while not self._stop:
            try:
                reading = 0.0
                img = None
                while img is None:
                    try:
                        img = self.get_image()
                    except Exception as e:
                        self._logger.error("Could not get camera snapshot. Retry in 10 sec. %s" % e)
                        time.sleep(10)

                img = prepare_image(img, self._flip_horizontal, self._flip_vertical, self._entity_id, self._debug_path)
                if self._dials is not None:
                    reading = parse_dials(
                        img,
                        readout=self._dials,
                        decimals_count=self._decimals,
                        entity_id=self._entity_id,
                        minDiameter=self._dial_size,
                        maxDiameter=self._dial_size + 250,
                        debug_path=self._debug_path,
                    )
                elif self._digits > 0 and self._ocr_key is not None:
                    reading = parse_digits(
                        img,
                        self._digits,
                        self._decimals,
                        self._ocr_key,
                        self._entity_id,
                        debug_path=self._debug_path,
                    )
                if reading > 0 and reading >= self._current_reading:

                    self._current_reading = reading
                    self._logger.debug("Final reading: %s" % reading)
                    # send to mqtt
                    self._mqtt.mqtt_state(self._entity_id, self._current_reading)
                    self._mqtt.mqtt_availability(self._entity_id, True)
                    self._error_count = 0
                else:
                    self._error_count += 1               
            except Exception as e:
                self._logger.error(e)
                self._error_count += 1
            if self._error_count == 10:
                self._mqtt.mqtt_availability(self._entity_id, False)      
            self._logger.debug("Waiting %s secs for next reading." % self._interval)              
            time.sleep(self._interval)
        self._logger.warn("Camera %s is now disposed." % self._name)
        self._disposed = True

    def get_image(self):
        req = requests.get(self._snapshot_url, stream=True) # TODO: get image from video stream
        if req.status_code == 200:
            stream = req.raw
            arr = np.asarray(bytearray(stream.read()), dtype=np.uint8)
            img = cv2.imdecode(arr, cv2.IMREAD_UNCHANGED) # 'Load it as it is'
            return img
        else:
            raise Exception(req.text)
