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
# import pytesseract

_LOGGER = logging.getLogger(__name__)


def parse_digits_ocr_space(
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
        reading = ocr_space(frame, digits_count, decimals_count, ocr_key, entity_id)
    return reading

# # tesseract code for when we have good trained data
# def ocr_tesseract(frame, digits_count, decimals_count, entity_id):
#     reading = 0
#     try:
#         _LOGGER.debug("Sending frame to tesseract %s" % (pytesseract.get_tesseract_version()))
        
#         text = pytesseract.image_to_string(frame, lang="digits_comma", config="--psm 7 -c tessedit_char_whitelist=0123456789", timeout=15)
#         reading = parse_result(
#                 text,
#                 digits_count,
#                 decimals_count,
#                 entity_id,
#             )
#     except Exception as e:
#         _LOGGER.debug("Error while OCR with tesseract: %s" % e)
#     return reading
    

URL_API = "https://api.ocr.space/parse/image"
def ocr_space(frame, digits_count, decimals_count, ocr_key, entity_id):
    payload = {"apikey": ocr_key, "language": "eng", "scale": "true", "OCREngine": "2", "filetype": "PNG"}

    _LOGGER.debug("OCR image: %s, payload=%s" % (URL_API, payload))
    imencoded = cv2.imencode(".png", frame)[1]
    response = requests.post(
        URL_API,
        data=payload,
        files={"file.png": imencoded.tobytes()},
        timeout=15,
    )

    if response.status_code == 200:
        result = response.json()
        if "ParsedResults" in result:
            text = ""
            for reg in result["ParsedResults"]:
                if "ParsedText" in reg:
                    text = text + reg["ParsedText"]
                text = text + "\n"
            return parse_result(
                text,
                digits_count,
                decimals_count,
                entity_id,
            )
        if "ErrorMessage" in result:
            raise Exception(result["ErrorMessage"])

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
