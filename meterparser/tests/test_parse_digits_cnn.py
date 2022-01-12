# import os
# import cv2

# from src.app.parsers.image_utils import prepare_image
# from src.app.parsers.model import generate_model
# from src.app.parsers.parser_digits_cnn import parse_digits_cnn
# import pytest

# entity_id = "test.test"
# dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "results")

# @pytest.fixture(scope="session", autouse=True)
# def execute_before_any_test():
#     generate_model()


# def test_parse_digits_cnn(request):
#     samplepath = os.path.join(os.path.dirname(__file__), "images", "sample_water-aruco.jpg")
#     inputFrame = cv2.imread(samplepath)
#     inputFrame = prepare_image(inputFrame, request.node.name, None, dir_path)
#     reading = parse_digits_cnn(inputFrame, 6, 1, request.node.name, debug_path=dir_path)
#     assert reading == 2813.0


