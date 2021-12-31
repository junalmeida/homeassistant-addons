from app.camera import Camera
from app.mqtt import Mqtt
from app.service import Service

mqtt = Mqtt()
service = Service(mqtt.cameras)

service.start()
mqtt.mqtt_start()