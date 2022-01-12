import os
import json
config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "data", "options.json")
config = dict()
with open(config_path, mode="r", encoding="utf-8") as file:
    config = json.load(file)