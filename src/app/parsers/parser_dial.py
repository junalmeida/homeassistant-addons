""" Dial Parser based on https://github.com/mirogta/dial-meter-reader-opencv-py with changes to accomodate parametrized methods and minor adjustments """

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

import os
import time
import numpy as np
import logging
import cv2

_LOGGER = None

IDEAL_WIDTH = 1500
HORIZONTAL_MAX_DIFF = 400
KEY_ESCAPE = 27
COLOR_ORANGE = (0, 128, 255)
COLOR_MAGENTA = (255, 0, 255)
COLOR_GREEN = (0, 255, 0)
COLOR_RED = (0, 0, 255)
COLOR_BLUE = (255, 0, 0)
COLOR_BLACK = (0, 0, 0)


def filter_circles(circles, maxDiff, entity_id: str):
    # convert the (x, y) coordinates and radius of the circles to integers
    circles = np.round(circles[0, :]).astype("int")
    # sort by X-axis
    circles = sorted(circles, key=lambda x: x[0])

    # remove circles with Y-axis deviating too much from the rest
    valid_circles = []
    min_y = None
    for c in circles:
        y = c[1]
        if min_y is None:
            min_y = y
        if y < min_y:
            min_y = y

    for c in circles:
        x = c[0]
        y = c[1]
        r = c[2]
        if abs(y - min_y) < maxDiff:
            valid_circles.append((x, y, r))

    _LOGGER.debug("%s: Found #%i circles:" % (entity_id, len(valid_circles)))
    return valid_circles


def find_needle(image, cx, cy, radius):

    # https://en.wikipedia.org/wiki/Bresenham%27s_line_algorithm

    size = radius * 0.8
    slices = 40
    factor = 360 / slices
    center = tuple([cx, cy])

    needle_pt = None
    # find the longest dark line from the centre
    longest_dark = 0
    value = None

    for i in range(slices):
        # original angle:
        #     360
        # 180      0
        #     90
        angle = i * factor - 90
        # converted angle:
        #     0
        # 360      90
        #     180
        dark_length = 0
        x2 = cx + int(size * np.cos(angle * np.pi / 180.0))
        y2 = cy + int(size * np.sin(angle * np.pi / 180.0))

        # cv2.line(image, center, (x2, y2), 255, thickness=2)
        points_on_line = np.linspace(
            center, (x2, y2), radius
        )  # 100 samples on the line
        for pt in points_on_line:
            point = np.int32(pt)
            px = point[0]
            py = point[1]
            b = image[:, :, 0][py, px]
            g = image[:, :, 1][py, px]
            r = image[:, :, 2][py, px]
            # Compute grayscale with naive equation
            gray = (b.astype(int) + g.astype(int) + r.astype(int)) / 3
            # debug: show points on the line
            # cv2.circle(image, tuple(point), 1, (255,i*10,0), -1)
            # if sufficiently dark
            if gray < 100:
                # cv2.circle(image, tuple(point), 1, (255, gray, 0), -1)
                dark_length += 1
            else:
                continue

        if dark_length > longest_dark:
            longest_dark = dark_length
            needle_pt = tuple(point)
            value = 10 * i / slices  # scale to 0-10

    return value, needle_pt


def process_values(values: list, decimals_count: int):
    reading = ""
    for i, (v) in enumerate(values):
        whole = int(np.floor(v))
        if i == len(values) - 1:
            reading = reading + str(whole)
            break
        decimals = v - whole
        if decimals < 0.5 and values[i + 1] > 5:
            # decimal value low but the next value is high, so need to adjust the reading by -1
            whole = whole - 1
        reading = reading + str(whole)
    reading = float(reading)
    if decimals_count > 0:
        reading = reading / float(10 ** decimals_count)
    return reading


def parse_dials(
    frame, readout: list[str], decimals_count: int, entity_id: str, minDiameter=200, maxDiameter=340, debug_path: str = None
):
    global _LOGGER
    _LOGGER = logging.getLogger("%s.%s" % (__name__, entity_id))

    width = frame.shape[1]
    if width < IDEAL_WIDTH:
        frame = image_resize(frame, IDEAL_WIDTH)  # larger images are better

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 2)
    gray = cv2.medianBlur(gray, 5)

    width = gray.shape[1]
    ratio = width / IDEAL_WIDTH
    minRadius = round((minDiameter / 2) * ratio)
    maxRadius = round((maxDiameter / 2) * ratio)
    maxDiff = round(HORIZONTAL_MAX_DIFF * ratio)

    debugfile = time.strftime(entity_id + "-%Y-%m-%d_%H-%M-%S")
    if debug_path is not None:
        cv2.imwrite(os.path.join(debug_path, "%s-in.jpg" % debugfile), gray)

    output = frame.copy()

    # TODO: move values to config, or try to figure them out (increase values incrementally?)
    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        1.5,
        minDist=minRadius - 10,
        minRadius=minRadius,
        maxRadius=maxRadius,
    )

    if circles is None:
        raise Exception(
            "Could not find any dial. Check dial diameter setting and try again."
        )

    # find circles which are roughly on the same level
    circles = filter_circles(circles, maxDiff, entity_id)

    values = []

    # loop over the (x, y) coordinates and radius of the circles
    minx = 0
    miny = 0
    radius = 0
    for i, ((x, y, r), convention) in enumerate(zip(circles, readout)):
        value, tip = find_needle(output, x, y, r)
        actual_value = read_value(value, convention)
        values.append(actual_value)

        _LOGGER.debug(
            "%s: #%i: (%i, %i) radius: %i - value: %f" % (entity_id, i, x, y, r, actual_value)
        )

        # draw needle and value
        cv2.line(output, (x, y), tip, COLOR_MAGENTA, thickness=3)
        cv2.putText(
            output,
            str(actual_value),
            (x - 19, y + r + 24),
            cv2.FONT_HERSHEY_TRIPLEX,
            1,
            COLOR_RED,
        )
        cv2.putText(
            output,
            str(actual_value),
            (x - 21, y + r + 26),
            cv2.FONT_HERSHEY_TRIPLEX,
            1,
            COLOR_BLACK,
        )  # try to make a bold font

        # draw the circle in the output image, then draw a rectangle
        # corresponding to the center of the circle
        cv2.circle(output, (x, y), r, COLOR_GREEN, 4)
        cv2.rectangle(output, (x - 2, y - 2), (x + 2, y + 2), COLOR_ORANGE, -1)

        if i == 0:
            minx = x
            miny = y
            radius = r

    reading = process_values(values, decimals_count)
    _LOGGER.debug("%s: Final reading: %s" % (entity_id, reading))
    cv2.putText(
        output,
        str(reading),
        (minx, miny - maxRadius + round(radius / 2)),
        cv2.FONT_HERSHEY_TRIPLEX,
        1.3,
        COLOR_RED,
    )
    cv2.putText(
        output,
        str(reading),
        (minx - 2, miny - maxRadius - 2 + round(radius / 2)),
        cv2.FONT_HERSHEY_TRIPLEX,
        1.3,
        COLOR_BLACK,
    )  # try to make a bold font

    if debug_path is not None:
        cv2.imwrite(os.path.join(debug_path, "%s-out.jpg" % debugfile), output)
    # ignore results if an exact number of dials wasn't found
    # we could do that earlier, but we would lose important debug messages
    dials_count = len(readout)
    if len(circles) != dials_count:
        _LOGGER.error(
            "Could not find the correct amount of dials. Found: %d" % len(circles)
        )
        return 0

    return reading


def read_value(value, convention):
    if convention == "CCW":
        result = 10.0 - value
    else:
        result = value
    if result == 10:
        result = 0
    return result


def image_resize(image, width=None, height=None, inter=cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]

    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image

    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation=inter)

    # return the resized image
    return resized
