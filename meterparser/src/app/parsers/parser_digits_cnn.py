# import cv2
# import logging
# import time
# import keras
# import numpy as np
# import operator
# import os
# from keras.preprocessing.image import img_to_array
# from .model import load_model
# import tensorflow as tf

# model = None

# possible_numbers = []
# for i in range(ord('0'), ord('9') + 1):
#     possible_numbers.append(chr(i))

# def parse_digits_cnn(
#     image,
#     digits_count: int,
#     decimals_count: int,
#     entity_id: str,
#     debug_path: str = None,
# ):
#     global _LOGGER
#     global model
#     _LOGGER = logging.getLogger("%s.%s" % (__name__, entity_id))
#     if model is None:
#         model = load_model()
#     debugfile = time.strftime(entity_id + "-%Y-%m-%d_%H-%M-%S")

#     digits = get_numbers_images(image, debug_path)
#     if len(digits) < digits_count - decimals_count:
#         _LOGGER.error("Not a valid AI result of digits count: expected %d, found %d" % (digits_count, len(digits)))
#         return 0.0
#     else:
#         reading = "0"
#         for ix, digit in enumerate(digits):
#             digit_str = get_prediction(digit, debug_path, "%s-%d.png" % (debugfile, ix))
#             reading = "%s%s" % (reading, digit_str)
#         if len(digits) == digits_count - decimals_count:
#             reading = reading + ("0" * decimals_count)

#         if reading.isnumeric():
#             reading = float(reading)
#         else:
#             _LOGGER.error("Not a valid AI result: %s" % reading)
#             reading = 0.0
    
#         if reading > 0:
#             if decimals_count > 0:
#                 reading = reading / float(10 ** decimals_count)
#             _LOGGER.debug(
#                 "%s: Final reading from AI '%s'" % (entity_id, reading)
#             )
            
#         return reading


# def get_numbers_images(image, debug_path):
#     coords = []

#     image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     canny = cv2.Canny(image, 179, 200)
#     if debug_path is not None:
#         cv2.imwrite(os.path.join(debug_path, "step-0.jpg"), canny)

#     cnts, _ = cv2.findContours(canny.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
#     cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:150]
#     for c in cnts:
#         area = cv2.contourArea(c)
#         peri = cv2.arcLength(c, True)
#         approx = cv2.approxPolyDP(c, 0.01 * peri, True)
#         x,y,w,h = cv2.boundingRect(approx)
#         aspect_ratio = w / float(h)

#         if (aspect_ratio >= 0.4 and aspect_ratio <= 1.3):
#             if area > 150:
#                 # ROI = original[y:y+h, x:x+w]
#                 # cv2.rectangle(image,(x,y),(x+w,y+h),(0,255,0),2)
#                 coords.append(c)

#     numbers_images = []
#     for ix, ele in enumerate(coords):
#         if debug_path is not None:
#             cv2.imwrite(os.path.join(debug_path, "segmented-%d.jpg" % ix), ele[0])
#         numbers_images.append(ele[0])
#         # count += 1

#     # rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 1)

#     # cv2.imwrite(filePath + "contour-canny%d.jpg" % 100, image)

#     # cv2.imwrite(filePath + "canny%d.jpg" % 100, edges)
#     return numbers_images


# def get_prediction(image, debug_path, debug_file):
#     image = cv2.resize(image, (28, 28))
#     if debug_path is not None:
#         cv2.imwrite(os.path.join(debug_path, debug_file), image)

#     image = image.astype("float") / 255.0
#     image = img_to_array(image)
#     image = np.expand_dims(image, axis=0)
#     # load the trained convolutional neural network
#     # print("[INFO] loading network...")
#     results = model.predict(image)[0]
#     # print(results)
#     proba = max(results)
#     max_index = np.argmax(results)
#     label = possible_numbers[max_index]
#     return label

