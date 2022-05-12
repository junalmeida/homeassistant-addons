<img src="meterparser/icon.png" align="right" width="128" />  

# Home Assistant - Meter Parser AddOn


## Installation through Supervisor

1. Add [https://github.com/junalmeida/homeassistant-addons](https://github.com/junalmeida/homeassistant-addons) as a custom
   repository on supervisor repositories.
2. Click install under "Meter Parser" in the Add-on Store.
3. If you have native MQTT enabled, supervisor may provide configuration. Otherwise, setup mqtt host, port, user, and password.
3. Setup the meter camera snapshot url, dials or digits. See the example below.
4. Start the add-on 
5. Print two 4x4 ArUco markers (https://chev.me/arucogen/) and stick on the top-left and bottom-right (order is important) of the region of interest. 
6. Check the logs add on and MQTT devices to see the last processed image and potential failures.


## Usage

* Entities will show up as `sensor.<friendly name>`, for example (`sensor.water_meter`).
```yaml
# Add-on configuration example
cameras:
- snapshot_url: http://192.168.100.153/snapshot.jpg
  name: Water Meter
  interval: 60 # in seconds. smaller interval will result on more calls to the ocr api for digit parse

  # to parse a meter with rolling digits, you may choose ocr.space or google vision OCR services. At least one service is required. 
  ocr_space_key: "123456789" # grab a key at https://ocr.space/ (watch for rate limits)
  ocr_gvision_key: "XXXXXXX" # head to google vision api to grab a key (watch for costs)

  digits: 6 # required for digits, number of expected total digits (including decimals)
  decimals: 1 # optional number of decimals
  device_class: water # energy, gas or water
  unit_of_measurement: m³ # m³, ft³, kWh, MWh, Wh, gal, L

- snapshot_url: http://192.168.100.154/snapshot.jpg
  name: Gas Meter
  interval: 60 # seconds
  dials: # Add CW for Clockwise and CCW for Counter-clockwise dials. 1 line per dial
    - CCW
    - CW
    - CCW
    - CW
  dial_size: 200 # approximately size in pixels of each dial. Used to ignore smaller or larger circles on the image.

  decimals: 1 # optional number of decimals (if last dial(s) is/are fraction, set this)
  device_class: gas # energy, gas or water
  unit_of_measurement: m³ # m³, ft³, kWh, MWh, Wh, gal, L

mqtt: # or mqtt: {} when automatically handled by home assistant
  host: hostname
  username: johndoe
  password: verysecurepwd
  port: 1883

log_level: INFO # DEBUG, INFO, WARN, ERROR
``` 

If you change your meter or for some other reason need to reset the previous control value, use the home assistant mqtt publish service or your mqtt broker to set the value.

```yaml
service: mqtt.publish
data:
  topic: homeassistant/sensor/XXXXXXX-meter-parser/water-meter/set
  payload: '{ "value": 1000.2 }'
```

## Reporting an Issue

File an issue in this Github Repository, add logs and if possible an image of your meter. Please redact sensitive information.

I also appreciate if you share the camera device specs and light conditions.