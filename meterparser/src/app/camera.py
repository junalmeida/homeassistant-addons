
import json
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
from app.parsers.parser_digits_ocr_space import parse_digits_ocr_space
from app.parsers.parser_digits_gvision import parse_digits_gvision
import math
from skimage.metrics import structural_similarity as compare_ssim

class Camera (threading.Thread):
    def __init__(self, camera: dict, entity_id: str, mqtt: Mqtt, debug_path: str):
        threading.Thread.__init__(self)
        self.error_limit = 30
        self.reading_limit = 5 # 5 m3? 5 kWh? 5 what? TODO: Check if this is a good fail safe parameter.
        self._wait = threading.Event()
        self._interval = int(camera["interval"])
        self._snapshot_url = str(camera["snapshot_url"])
        self.name = str(camera["name"])
        self._device_class = str(camera["device_class"]) if "device_class" in camera else "energy"
        self._unit_of_measurement = str(camera["unit_of_measurement"]) if "unit_of_measurement" in camera else "kWh"
        self._disposed = False
        self._current_reading = float(data[entity_id]) if entity_id in data else 0.0
        self._dials = camera["dials"] if "dials" in camera else []
        self._dial_size = int(camera["dial_size"]) if "dial_size" in camera else 100
        self._digits = int(camera["digits"]) if "digits" in camera else 0
        self._decimals = int(camera["decimals"]) if "decimals" in camera else 0
        self._ocr_space_key = camera["ocr_space_key"] if "ocr_space_key" in camera else None
        self._ocr_gvision_key = camera["ocr_gvision_key"] if "ocr_gvision_key" in camera else None
        self.entity_id = entity_id
        self._error_count = 0
        self._logger = logging.getLogger("%s.%s" % (__name__, self.entity_id))
        self._mqtt = mqtt
        self._debug_path = debug_path
        self._previous_image = None
        if self._digits == 0 and len(self._dials) == 0:
            raise Exception("Incorrect setup. Set this camera to use either digits or dials.")
        if self._interval < 30: 
            raise Exception("Incorrect interval in seconds. Choose more than 30 seconds.")
        
    def stop(self):
        self._wait.set()
        self._logger.warn("Stopping %s camera..." % self.entity_id)

    def run(self):
        self._logger.info("Starting camera %s" % self.name)
        topic_listen = self._mqtt.mqtt_subscribe("sensor", self.entity_id, self.set_callback)
        while not self._wait.is_set():
            try:
                self._mqtt.mqtt_sensor_discovery(self.entity_id, self.name, self._device_class, self._unit_of_measurement) 
                self._logger.info("Listening to messages at topic %s" % (topic_listen))

                reading = 0.0
                img = None
                image_error = 0
                while img is None and not self._wait.is_set():
                    try:
                        img = self.get_image()
                        self.send_image(img)

                        img = prepare_image(img, self.entity_id, self.send_image, self._debug_path)
                        self.send_image(img)
                        
                    except Exception as e:
                        img = None
                        image_error += 1
                        if image_error > 5:
                            self._mqtt.mqtt_set_availability("camera", self.entity_id, False) 
                            raise e
                        self._wait.wait(10)

                should_process = True
                if self._previous_image is not None:
                    (imgH, imgW, _) = img.shape
                    (pimgH, pimgW, _) = self._previous_image.shape
                    if imgH != pimgH or imgW != pimgW:
                        self._previous_image = cv2.resize(self._previous_image, (imgW, imgH))
                    grayA = cv2.cvtColor(self._previous_image, cv2.COLOR_BGR2GRAY)
                    grayB = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    (score, _) = compare_ssim(grayA, grayB, full=True)
                    # diff = (diff * 255).astype("uint8")
                    if score > 0.93:
                        should_process = False
                        self._logger.debug("Previous and current images have %d percent of simmilarity, so not wasting an OCR call." % score)

                if should_process:
                    self._previous_image = img.copy()
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
                    elif self._digits > 0 and self._ocr_gvision_key is not None:
                        reading = parse_digits_gvision(
                            img,
                            self._digits,
                            self._decimals,
                            self._ocr_gvision_key,
                            self.entity_id,
                            debug_path=self._debug_path,
                        )
                    elif self._digits > 0 and self._ocr_space_key is not None:
                        reading = parse_digits_ocr_space(
                            img,
                            self._digits,
                            self._decimals,
                            self._ocr_space_key,
                            self.entity_id,
                            debug_path=self._debug_path,
                        )
                    else:
                        raise Exception("Invalid configuration. Set either dials or digits to scan. For digits set an API key.")
                    limit = self._current_reading + self.reading_limit 
                    if reading > 0 and reading >= self._current_reading and (self._current_reading == 0 or reading < limit):

                        self._logger.info("Valid reading.\ncurrent=%s, previous=%s" % (reading, self._current_reading))
                        self._current_reading = reading
                        data[self.entity_id] = self._current_reading
                        
                        self._error_count = 0
                    elif reading > 0 and math.floor(reading) == math.floor(self._current_reading):
                        self._error_count = 0
                    else:
                        self._logger.error("Invalid reading. Value could be too high or less than previous.\ncurrent=%s, previous=%s, limit=%s" % (reading, self._current_reading, limit))
                        self._error_count += 1               

            except Exception as e:
                err = {
                        "last_error": "%s" % e,
                        "last_error_at": time.strftime("%Y-%m-%d %H:%M:%S")
                    }
                self._logger.error(err["last_error"])
                self._mqtt.mqtt_set_attributes("sensor", self.entity_id, err)
                self._error_count += 1

            self._mqtt.mqtt_set_availability("sensor", self.entity_id, self._error_count < self.error_limit)      
            if self._error_count < self.error_limit and self._current_reading > 0:
                # send to mqtt
                self._mqtt.mqtt_set_state("sensor", self.entity_id, self._current_reading)
                err = {
                    "last_error": None,
                    "last_error_at": None
                }
                self._mqtt.mqtt_set_attributes("sensor", self.entity_id, err)
            self._logger.debug("Waiting %s secs for next reading." % self._interval)              
            self._wait.wait(self._interval)
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
        
        self._mqtt.mqtt_set_availability("camera", self.entity_id, True) 
        self._mqtt.mqtt_set_state("camera", self.entity_id, bytes(jpg_buffer))

    def set_callback(self, client, userdata, message):
        try:
            message = json.loads(message.payload.decode("utf-8"))
            if message is not None and "value" in message and str(message["value"]).isnumeric():
                self._current_reading = float(message["value"])
                self._logger.info("Resetting %s (%s) to %d" % (self.name, self.entity_id, self._current_reading))
                data[self.entity_id] = self._current_reading
            else:
                self._logger.error("Invalid payload %s" % message)
        except Exception as e:
            self._logger.error("Invalid payload %s" % e)
