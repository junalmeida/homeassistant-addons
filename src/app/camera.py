import threading
class Camera (threading.Thread):
    def __init__(self, camera):
        self._camera = camera
        threading.Thread.__init__(self)

    def run (self):
        print( str(self._camera))