""" Digits Parser that uses online OCR tool """

#    Copyright 2021 Marcos Junior

#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at

#        http://www.apache.org/licenses/LICENSE-2.0

#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import logging
import os
import time
import requests
import cv2
import numpy as np
import regex as re
import base64


_LOGGER = logging.getLogger(__name__)


def parse_digits_gvision(
    image,
    digits_count: int,
    decimals_count: int,
    ocr_key: str,
    entity_id: str,
    debug_path: str = None,
):
    """Displaying digits and OCR"""
    global _LOGGER
    _LOGGER = logging.getLogger("%s.%s" % (__name__, entity_id))
    debugfile = time.strftime(entity_id + "-%Y-%m-%d_%H-%M-%S")
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # remove red colors
    sensitivity = 30
    lower_red_0 = np.array([0, 100, 100])
    upper_red_0 = np.array([sensitivity, 255, 255])
    lower_red_1 = np.array([180 - sensitivity, 100, 100])
    upper_red_1 = np.array([180, 255, 255])

    mask_0 = cv2.inRange(hsv, lower_red_0, upper_red_0)
    mask_1 = cv2.inRange(hsv, lower_red_1, upper_red_1)

    mask = cv2.bitwise_or(mask_0, mask_1)
    # Change image to white where we found red
    frame = image.copy()
    frame[np.where(mask)] = (255, 255, 255)

    if debug_path is not None:
        cv2.imwrite(os.path.join(debug_path, "%s-in.jpg" % debugfile), frame)

    reading = float(0) # ocr_tesseract(frame, digits_count, decimals_count, entity_id)
    if reading == 0:
        reading = gvision(frame, digits_count, decimals_count, ocr_key, entity_id)
    return reading

   
URL_API = "https://vision.googleapis.com/v1/images:annotate?key=%s"
def gvision(frame, digits_count, decimals_count, ocr_key, entity_id):
    imencoded = cv2.imencode(".png", frame)[1]
    payload = {
        "requests": [{
            'image': {'content': base64.b64encode(imencoded).decode('utf-8') },
            'features': [{'type': "TEXT_DETECTION"}]
        }]
    }
    
    response = requests.post(
        URL_API % ocr_key,
        json=payload,
        timeout=15,
        headers={
            "Content-Type": "application/json"
        }
    )

    if response.status_code == 200:
        result = response.json()
        if "responses" in result:
            text = ""
            for r in result["responses"]:
                if "fullTextAnnotation" in r and "text" in r["fullTextAnnotation"]:
                    text = text + r["fullTextAnnotation"]["text"] + "\n"
            return parse_result(
                text,
                digits_count,
                decimals_count,
                entity_id,
            )

    raise Exception(response.text)


def parse_result(
    ocr: str, digits_count: int, decimals_count: int, entity_id: str
) -> float:
    """Parse possible results"""
    reading = float(0)
    if ocr is not None and ocr != "":
        array = ocr.strip().split("\n")
        for x_str in array:
            # replace common ocr mistakes
            x_str = (
                x_str.replace(" ", "")
                .replace(".", "")
                .replace(",", "")
                .replace("|", "")
                .replace("/", "")
                .replace("\\", "")
                .replace("o", "0")
                .replace("O", "0")
                .replace("T", "1")
            )
            regex = re.findall("[0-9]{%s}" % (digits_count), x_str, overlapped = True)
            if regex is None or len(regex) == 0:
                # last digit could be in a middle of a spin, so ocr may detect H.
                # I believe it is safe to replace decimals with zeroes, and then
                # repeat last decimal reading later.
                regex = re.findall("[0-9]{%s}" % (digits_count - decimals_count), x_str, overlapped = True)
                if regex is not None and len(regex) > 0:
                    reading = float(regex[-1] + ("0" * decimals_count))
            else:
                reading = float(regex[-1])

    if reading == 0:
        _LOGGER.error("Not a valid OCR result: %s" % ocr.replace("\n", "\\n"))
    else:
        if decimals_count > 0:
            reading = reading / float(10 ** decimals_count)
        _LOGGER.debug(
            "%s: Final reading '%s' from OCR '%s'" % (entity_id, reading, ocr.replace("\n", "\\n"))
        )
    return reading
