import os
import cv2

from src.app.parsers.parser_dial import parse_dials
from src.app.parsers.parser_digits_ocr_space import parse_digits_ocr_space
from src.app.parsers.parser_digits_gvision import parse_digits_gvision
from src.app.parsers.image_utils import crop_image, rotate_image

from .config import config
ocr_space_key = config["cameras"][0]["ocr_space_key"]
ocr_gvision_key = config["cameras"][0]["ocr_gvision_key"]
dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "results")


def test_electricity_dials_1(request):
    samplepath = os.path.join(os.path.dirname(__file__),  "images", 'sample_electricity-1.jpg')
    inputFrame = cv2.imread(samplepath)
    reading = parse_dials(inputFrame, ["CCW", "CW", "CCW", "CW"], 0, request.node.name, minDiameter=150, maxDiameter=340, debug_path=dir_path)
    assert reading == 3124


def test_electricity_dials_2(request):
    samplepath = os.path.join(os.path.dirname(__file__),  "images", 'sample_electricity-2.jpg')
    inputFrame = cv2.imread(samplepath)
    reading = parse_dials(inputFrame, ["CCW", "CW", "CCW", "CW"], 0, request.node.name, minDiameter=200, maxDiameter=300, debug_path=dir_path)
    assert reading == 2211


def test_electricity_dials_3(request):
    samplepath = os.path.join(os.path.dirname(__file__),  "images", 'sample_electricity-3.jpg')
    inputFrame = cv2.imread(samplepath)
    reading = parse_dials(inputFrame, ["CW", "CCW", "CW", "CCW", "CW"], 0, request.node.name, minDiameter=200, maxDiameter=300, debug_path=dir_path)
    assert reading == 68451


def test_gas_dials_1(request):
    samplepath = os.path.join(os.path.dirname(__file__),  "images", 'sample_gas-1.jpg')
    inputFrame = cv2.imread(samplepath)
    reading = parse_dials(inputFrame, ["CCW", "CW", "CCW", "CW"], 0, request.node.name, minDiameter=300, maxDiameter=400, debug_path=dir_path)
    assert reading == 3876


def test_gas_dials_2(request):
    samplepath = os.path.join(os.path.dirname(__file__),  "images", 'sample_gas-2.jpg')
    inputFrame = cv2.imread(samplepath)
    reading = parse_dials(inputFrame, ["CCW", "CW", "CCW", "CW"], 0, request.node.name, minDiameter=290, maxDiameter=330, debug_path=dir_path)
    assert reading == 140


def test_water_dial_1(request):
    samplepath = os.path.join(os.path.dirname(__file__),  "images", 'sample_water-1.jpg')
    inputFrame = cv2.imread(samplepath)
    reading = parse_dials(inputFrame, ["CW"], 0, request.node.name, minDiameter=640, maxDiameter=840, debug_path=dir_path)
    assert reading == 0


def test_water_dial_2(request):
    samplepath = os.path.join(os.path.dirname(__file__), "images",  'sample_water-2.jpg')
    inputFrame = cv2.imread(samplepath)
    reading = parse_dials(inputFrame, ["CW"], 0, request.node.name, minDiameter=1010, maxDiameter=1400, debug_path=dir_path)
    assert reading == 1


def test_water_dial_3(request):
    samplepath = os.path.join(os.path.dirname(__file__), "images",  'sample_water-3.jpg')
    inputFrame = cv2.imread(samplepath)
    reading = parse_dials(inputFrame, ["CW"], 0, request.node.name, minDiameter=1010, maxDiameter=1230, debug_path=dir_path)
    assert reading == 5


def test_water_digits_1(request):
    samplepath = os.path.join(os.path.dirname(__file__), "images",  'sample_water-1.jpg')
    inputFrame = cv2.imread(samplepath)
    inputFrame = crop_image(inputFrame, [179, 155, 194, 50])
    reading = parse_digits_ocr_space(inputFrame, 6, 1, ocr_space_key, request.node.name, debug_path=dir_path)
    assert reading == 2802.0
    reading = parse_digits_gvision(inputFrame, 6, 1, ocr_gvision_key, request.node.name, debug_path=dir_path)
    assert reading == 2802.0


def test_water_digits_2(request):
    samplepath = os.path.join(os.path.dirname(__file__), "images",  'sample_water-2.jpg')
    inputFrame = cv2.imread(samplepath)
    inputFrame = crop_image(inputFrame, [40, 144, 118, 50])
    reading = parse_digits_ocr_space(inputFrame, 6, 2, ocr_space_key, request.node.name, debug_path=dir_path)
    assert reading == 1.10
    reading = parse_digits_gvision(inputFrame, 6, 2, ocr_gvision_key, request.node.name, debug_path=dir_path)
    assert reading == 1.10


def test_water_digits_3(request):
    samplepath = os.path.join(os.path.dirname(__file__), "images",  'sample_water-3.jpg')
    inputFrame = cv2.imread(samplepath)
    inputFrame = crop_image(inputFrame, [451, 414, 372, 133])
    reading = parse_digits_ocr_space(inputFrame, 6, 2, ocr_space_key, request.node.name, debug_path=dir_path)
    assert reading == 2.00
    reading = parse_digits_gvision(inputFrame, 6, 2, ocr_gvision_key, request.node.name, debug_path=dir_path)
    assert reading == 2.00

def test_water_rotate_crop(request):
    samplepath = os.path.join(os.path.dirname(__file__),  "images", 'sample_water-rotate.jpg')
    inputFrame = cv2.imread(samplepath)
    inputFrame = rotate_image(inputFrame, -121)
    cv2.imwrite(os.path.join(dir_path, "%s-rotate.jpg" % request.node.name), inputFrame)
    inputFrame = crop_image(inputFrame, [365, 405, 160, 60])
    reading = parse_digits_gvision(inputFrame, 6, 1, ocr_gvision_key, request.node.name, debug_path=dir_path)
    assert reading >= 2806.0 and reading <= 2806.9
    reading = parse_digits_ocr_space(inputFrame, 6, 1, ocr_space_key, request.node.name, debug_path=dir_path)
    assert reading >= 2806.0 and reading <= 2806.9

