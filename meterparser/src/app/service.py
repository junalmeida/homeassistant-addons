import sys
import threading

from app.data import data
from app.camera import Camera

class Service(threading.Thread):
    def __init__(self, camera_list):
        threading.Thread.__init__(self)
        self.cameras: list[Camera] = camera_list

    def read_stdin(self):
        readline = sys.stdin.readline()
        while readline:
            yield readline
            readline = sys.stdin.readline()
    def run(self):
        for line in self.read_stdin():
            line = line.split()
            if "reset" in line and len(line) > 1:
                line.pop(0)
                if line[-1].isnumeric():
                    value = float(line.pop(len(line) - 1))
                self.reset(" ".join(line), value)
            elif "list" in line:
                self.list()
            else:
                print("Invalid input: %s" % line)
    def list(self):
        if len(self.cameras) == 0:
            print("No camera initialized.")
        else:
            for cam in self.cameras:    
                print("%s (%s)" % (cam.name, cam.entity_id))

    def reset(self, meter: str, value: float):
        for cam in self.cameras:
            if cam.name == meter or cam.entity_id == meter:
                print("Resetting %s (%s) to %d" % (cam.name, cam.entity_id, value))
                data[cam.entity_id] = float(value)
                return
        print("Could not find %s" % meter, file=sys.stderr)