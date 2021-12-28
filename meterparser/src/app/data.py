import json
import os
import logging
import threading

from app.dirtydict import DirtyDict

data_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "data", "data.json")
data = DirtyDict()
if os.path.isfile(data_path):
    with open(data_path, mode="r", encoding="utf-8") as file:
        data = DirtyDict(json.load(file))

def save_data():
    threading.Timer(10.0, save_data).start()
    if data.dirty:
        with open(data_path, mode="w", encoding="utf-8") as file:
            json.dump(data, file)
        data.dirty = False

save_data()