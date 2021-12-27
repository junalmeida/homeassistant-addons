import json
import os
import logging

config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "data", "options.json")
config = dict()
with open(config_path, mode="r", encoding="utf-8") as file:
    config = json.load(file)

log_level = config["log_level"] if "log_level" in config else "INFO"
logging.basicConfig(level=logging.getLevelName(log_level), format='%(asctime)s - %(levelname)-10s %(message)s\t\t%(name)s', datefmt='%Y-%m-%d %I:%M:%S %p')
