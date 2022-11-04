
import os
from pydoc import allmethods
import time

import cv2
import numpy as np
import math
from dataclasses import dataclass
arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
arucoParams = cv2.aruco.DetectorParameters_create()

@dataclass
class Marker:
    id: int
    topLeft: tuple[int, int]
    topRight: tuple[int, int]
    bottomLeft: tuple[int, int]
    bottomRight: tuple[int, int]
    center: tuple[int, int]
    angle: int

def prepare_image(image, entity_id:str, send_image, debug_path: str, first_aruco: int, second_aruco: int):
    debugfile = time.strftime(entity_id + "-%Y-%m-%d_%H-%M-%S")

    image = automatic_brightness_and_contrast(image)[0]
    image = cv2.bilateralFilter(image,9,75,75)
    image_to_aruco = image.copy()

    if send_image is not None:
        send_image(image_to_aruco)

    markers = get_markers(image_to_aruco, first_aruco, second_aruco)

    if len(markers) == 2:
        if debug_path is not None:
            cv2.imwrite(os.path.join(debug_path, "%s-aruco-in.jpg" % debugfile), image_to_aruco)

        avg_angle = sum(int(item.angle) for item in markers) / len(markers)
        if avg_angle != 0:
            image = rotate_image(image, -avg_angle)

        image_to_aruco = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        markers = get_markers(image_to_aruco, first_aruco, second_aruco)
        if len(markers) < 2:
            if send_image is not None:
                send_image(image_to_aruco)
            raise Exception("Could not find the same markers after rotating the image. This is usually a very bad quality image.")

        for marker in markers:
            # draw the bounding box of the ArUCo detection
            cv2.line(image, marker.topLeft, marker.topRight, (0, 255, 0), 2)
            cv2.line(image, marker.topRight, marker.bottomRight, (0, 255, 0), 2)
            cv2.line(image, marker.bottomRight, marker.bottomLeft, (0, 255, 0), 2)
            cv2.line(image, marker.bottomLeft, marker.topLeft, (0, 255, 0), 2)
            cX = int((marker.topLeft[0] + marker.bottomRight[0]) / 2.0)
            cY = int((marker.topLeft[1] + marker.bottomRight[1]) / 2.0)
            cv2.putText(image, str(marker.id),
                        (cX - 15, cY + 15),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8, (0, 255, 0), 2)
            cv2.circle(image, (cX, cY), 4, (0, 0, 255), -1)
        topLeft = markers[0].bottomRight
        bottomRight = markers[1].topLeft
        if send_image is not None:
            send_image(image)
        if debug_path is not None:
            cv2.imwrite(os.path.join(debug_path, "%s-aruco-in.jpg" % debugfile), image)

        image = crop_image(image, (topLeft[0], topLeft[1], bottomRight[0] - topLeft[0], bottomRight[1] - topLeft[1]))

    else:
        if send_image is not None:
            send_image(image_to_aruco)
        if debug_path is not None:
            cv2.imwrite(os.path.join(debug_path, "%s-aruco-err.jpg" % debugfile), image_to_aruco)
        raise Exception("Could not find ArUco markers. Please print two markers at https://chev.me/arucogen/ and stick to the top-left and bottom-right corners of the region of interest. If markers are already there check your camera's light conditions and quality.")

    return image

def get_markers(image, first_aruco: int, second_aruco: int):
    (corners, ids, _) = cv2.aruco.detectMarkers(
        image, arucoDict, parameters=arucoParams
    )
    markers = list[Marker]()
    if corners is None or ids is None or len(ids) == 0:
        return markers # exit with empty list

    for (markerCorner, markerID) in zip(corners, ids): 
        marker = extract_one_marker(markerCorner, markerID[0])
        markers.append(marker)
    if (first_aruco is not None and second_aruco is not None and first_aruco != second_aruco):
        markers = [item for item in markers if item.id == first_aruco or item.id == second_aruco]
    markers.sort(key=lambda x: x.id)

    if len(markers) == 2 and markers[0].id == markers[1].id: 
        raise Exception("The ArUco markers found have the same id. Please use different ids and stick to the top-left and bottom-right corners of the region of interest, respecting the id order.")

    return markers
    
def extract_one_marker(markerCorner, markerID: int):
    # extract the marker corners (which are always returned in
    # top-left, top-right, bottom-right, and bottom-left order)
    corners = markerCorner.reshape((4, 2))
    (topLeft, topRight, bottomRight, bottomLeft) = corners
    # convert each of the (x, y)-coordinate pairs to integers
    topRight = (int(topRight[0]), int(topRight[1]))
    bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
    bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
    topLeft = (int(topLeft[0]), int(topLeft[1]))
    # compute the center (x, y)-coordinates of the ArUco
    # marker
    center = (int((topLeft[0] + bottomRight[0]) / 2.0), int((topLeft[1] + bottomRight[1]) / 2.0))

    # Find angle
    angle1 = angle_between(topLeft, topRight)
    angle2 = angle_between(bottomLeft, bottomRight)
    estimated_angle = round((angle1 + angle2) / 2.0)

    return Marker(markerID, topLeft, topRight, bottomLeft, bottomRight, center, estimated_angle)

def angle_between(p1: tuple[int, int], p2: tuple[int, int]) -> float:  # tuple[x,y]
    (p1x, p1y) = p1
    (p2x, p2y) = p2
    return math.degrees(math.atan2(p2y-p1y, p2x-p1x))

def rotate_image(image, angle):
    """
    Rotates an image (angle in degrees) and expands image to avoid cropping
    """

    height, width = image.shape[:2] # image shape has 3 dimensions
    image_center = (width/2, height/2) # getRotationMatrix2D needs coordinates in reverse order (width, height) compared to shape

    rotation_mat = cv2.getRotationMatrix2D(image_center, -angle, 1.)

    # rotation calculates the cos and sin, taking absolutes of those.
    abs_cos = abs(rotation_mat[0,0]) 
    abs_sin = abs(rotation_mat[0,1])

    # find the new width and height bounds
    bound_w = int(height * abs_sin + width * abs_cos)
    bound_h = int(height * abs_cos + width * abs_sin)

    # subtract old image center (bringing image back to origo) and adding the new image center coordinates
    rotation_mat[0, 2] += bound_w/2 - image_center[0]
    rotation_mat[1, 2] += bound_h/2 - image_center[1]

    # rotate image with the new bounds and translated rotation matrix
    rotated_mat = cv2.warpAffine(image, rotation_mat, (bound_w, bound_h), flags=cv2.INTER_NEAREST)
    return rotated_mat


def crop_image(image, rect):
    x = rect[0]
    y = rect[1]
    w = rect[2]
    h = rect[3]
    if w < 0 or h < 0:
        raise Exception("Invalid width and height")
    return image[y: y + h, x: x + w]

def automatic_brightness_and_contrast(image, clip_hist_percent=1):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Calculate grayscale histogram
    hist = cv2.calcHist([gray],[0],None,[256],[0,256])
    hist_size = len(hist)
    
    # Calculate cumulative distribution from the histogram
    accumulator = []
    accumulator.append(float(hist[0]))
    for index in range(1, hist_size):
        accumulator.append(accumulator[index -1] + float(hist[index]))
    
    # Locate points to clip
    maximum = accumulator[-1]
    clip_hist_percent *= (maximum/100.0)
    clip_hist_percent /= 2.0
    
    # Locate left cut
    minimum_gray = 0
    while accumulator[minimum_gray] < clip_hist_percent:
        minimum_gray += 1
    
    # Locate right cut
    maximum_gray = hist_size -1
    while accumulator[maximum_gray] >= (maximum - clip_hist_percent):
        maximum_gray -= 1
    
    # Calculate alpha and beta values
    alpha = 255 / (maximum_gray - minimum_gray)
    beta = -minimum_gray * alpha
    
    '''
    # Calculate new histogram with desired range and show histogram 
    new_hist = cv2.calcHist([gray],[0],None,[256],[minimum_gray,maximum_gray])
    plt.plot(hist)
    plt.plot(new_hist)
    plt.xlim([0,256])
    plt.show()
    '''

    auto_result = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    return (auto_result, alpha, beta)
