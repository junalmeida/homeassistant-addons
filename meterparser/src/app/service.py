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
                self.reset(" ".join(line))
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

    def reset(self, meter: str):
        for cam in self.cameras:
            if cam.name == meter or cam.entity_id == meter:
                print("Resetting %s (%s) to 0" % (cam.name, cam.entity_id))
                data[cam.entity_id] = 0
                return
        print("Could not find %s" % meter, file=sys.stderr)