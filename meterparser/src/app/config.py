import json
import os
import logging

config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "data", "options.json")
config = dict()
with open(config_path, mode="r", encoding="utf-8") as file:
    config = json.load(file)

log_level = config["log_level"] if "log_level" in config else "INFO"

orig_factory = logging.getLogRecordFactory()

def record_factory(*args, **kwargs):
    record = orig_factory(*args, **kwargs)
    record.sname = record.name[-25:] if len(
        record.name) > 25 else record.name
    return record

logging.basicConfig(level=logging.getLevelName(log_level), format='%(sname)-25s %(asctime)s - %(levelname)-10s %(message)s', datefmt='%Y-%m-%d %I:%M:%S %p')
logging.setLogRecordFactory(record_factory)