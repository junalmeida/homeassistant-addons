import os
import cv2

from src.app.parsers.image_utils import crop_image, rotate_image, prepare_image
from src.app.parsers.parser_dial import parse_dials
from src.app.parsers.parser_digits import parse_digits


ocr_key = "890a9b9b8388957"
entity_id = "test.test"
dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "results")


def test_parse_aruco_digits(request):
    samplepath = os.path.join(os.path.dirname(__file__), "images", "sample_water-aruco.jpg")
    inputFrame = cv2.imread(samplepath)
    inputFrame = prepare_image(inputFrame, request.node.name, None, dir_path)
    reading = parse_digits(inputFrame, 6, 1, ocr_key, request.node.name, debug_path=dir_path)
    assert reading == 2813.0
