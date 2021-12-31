
import logging
import threading
import time
import requests
import numpy as np
import cv2
import traceback
import base64
from slugify import slugify
from app.mqtt import Mqtt
from app.data import data
from app.parsers.image_utils import prepare_image
from app.parsers.parser_dial import parse_dials
from app.parsers.parser_digits import parse_digits
import math
class Camera (threading.Thread):
    def __init__(self, camera: dict, entity_id: str, mqtt: Mqtt, debug_path: str):
        threading.Thread.__init__(self)
        self._interval = int(camera["interval"])
        self._snapshot_url = str(camera["snapshot_url"])
        self.name = str(camera["name"])
        self._device_class = str(camera["device_class"]) if "device_class" in camera else "energy"
        self._unit_of_measurement = str(camera["unit_of_measurement"]) if "unit_of_measurement" in camera else "kWh"
        self._stop = False
        self._disposed = False
        self._current_reading = float(data[entity_id]) if entity_id in data else 0.0
        self._dials = camera["dials"] if "dials" in camera else []
        self._dial_size = int(camera["dial_size"]) if "dial_size" in camera else 100
        self._digits = int(camera["digits"]) if "digits" in camera else 0
        self._decimals = int(camera["decimals"]) if "decimals" in camera else 0
        self._ocr_key = camera["ocr_key"] if "ocr_key" in camera else None
        self.entity_id = entity_id
        self._error_count = 0
        self._logger = logging.getLogger("%s.%s" % (__name__, self.entity_id))
        self._mqtt = mqtt
        self._debug_path = debug_path
        if self._digits == 0 and len(self._dials) == 0:
            raise Exception("Incorrect setup. Set this camera to use either digits or dials.")
        if self._interval < 30: 
            raise Exception("Incorrect interval in seconds. Choose more than 30 seconds.")
        
    def stop(self):
        self._stop = True
        self._logger.warn("Stopping camera...")
        while not self._disposed:
            time.sleep(2)

    def run(self):
        self._logger.info("Starting camera %s" % self.name)
        while not self._stop:
            try:
                reading = 0.0
                img = None
                while img is None:
                    try:
                        img = self.get_image()
                        self.send_image(img)
                        self._mqtt.mqtt_set_availability("camera", self.entity_id, True)

                        img = prepare_image(img, self.entity_id, self.send_image, self._debug_path)
                        self.send_image(img)
                        
                    except Exception as e:
                        img = None
                        err = {
                                "last_error": "Could not get or process camera snapshot: %s. Retry in 10 sec." % e,
                                "last_error_at": time.strftime("%Y-%m-%d %H:%M:%S")
                            }
                        self._logger.error(err["last_error"])
                        self._mqtt.mqtt_set_attributes("sensor", self.entity_id, err)
                        time.sleep(10)
                
                if self._dials is not None and len(self._dials) > 0:
                    reading = parse_dials(
                        img,
                        readout=self._dials,
                        decimals_count=self._decimals,
                        entity_id=self.entity_id,
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
                        self.entity_id,
                        debug_path=self._debug_path,
                    )
                else:
                    raise Exception("Invalid configuration. Set either dials or digits to scan.")
                if reading > 0 and reading >= self._current_reading and (self._current_reading == 0 or reading < self._current_reading * 2):

                    self._current_reading = reading
                    data[self.entity_id] = self._current_reading
                    self._logger.debug("Final reading: %s" % reading)
                    # send to mqtt
                    self._mqtt.mqtt_set_state("sensor", self.entity_id, self._current_reading)
                    self._mqtt.mqtt_set_availability("sensor", self.entity_id, True)
                    self._error_count = 0
                elif reading > 0 and math.floor(reading) == math.floor(self._current_reading):
                    self._mqtt.mqtt_set_availability("sensor", self.entity_id, True)
                    self._error_count = 0
                else:
                    self._logger.error("Invalid reading: %s, previous reading: %s. Value could be too high or too low?" % (reading, self._current_reading))
                    self._error_count += 1               
            except Exception as e:
                err = {
                        "last_error": "%s" % e,
                        "last_error_at": time.strftime("%Y-%m-%d %H:%M:%S")
                    }
                self._logger.error(err["last_error"])
                self._mqtt.mqtt_set_attributes("sensor", self.entity_id, err)
                self._error_count += 1
            if self._error_count == 10:
                self._mqtt.mqtt_set_availability(self.entity_id, "sensor", False)      
            self._logger.debug("Waiting %s secs for next reading." % self._interval)              
            time.sleep(self._interval)
        self._logger.warn("Camera %s is now disposed." % self.name)
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
    def send_image(self, image):
        ret_code, jpg_buffer = cv2.imencode(".jpg", image, [int(cv2.IMWRITE_JPEG_QUALITY), 95])     
        self._mqtt.mqtt_set_state("camera", self.entity_id, bytes(jpg_buffer))