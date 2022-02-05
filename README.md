<img src="meterparser/icon.png" align="right" width="128" />  

# Home Assistant - Meter Parser AddOn
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee] ![Checks][checksbadge]
![Last release][releasebadge] [^1]

This is a Home Assistant AddOn (not HACS) to allow parse of dial and digits utility meters like water, gas, and electricity to provide energy consumption information to home assistant using a regular ip camera.

This repository is under alpha stage, so expect bugs and breaking changes.

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]  

[![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg?style=plastic)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fjunalmeida%2Fhomeassistant-addons)


### Highlights of what **Meter Parser** can do

* Parse Meters
* Provide a consumption sensor of `total_increasing` state type.
* Cheap IP or PoE cameras must do.
* Sensor may be used by energy panel in home assistant, or [Utility Meter](https://www.home-assistant.io/integrations/utility_meter/) integration to provide statistics and costs by any time span (monthly, daily, etc.)

### Potential Downsides

* Positioning a camera and getting a good image could be difficult.
* Could be hard to setup calibration parameters.
* To recognize digits, this project relys on OCR services on the internet. I am open to 
suggestions on better local libraries to scan digits. Recognizing dials is simple and local,
no internet connection or APIs are required.

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

## Credits
🎉 [Dial Parser](meterparser/src/app/parsers/parser_dial.py) code is based on the awesome work of [@mirogta](https://github.com/mirogta), please [support his work](https://github.com/mirogta/dial-meter-reader-opencv-py).


[^1]: Icons made by [Smashicons][iconcredit] from [flaticon.com][iconcreditsite]

[iconcredit]: https://www.flaticon.com/authors/smashicons
[iconcreditsite]: https://www.flaticon.com/
[buymecoffee]: https://www.buymeacoffee.com/junalmeida
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-orange?style=plastic&logo=buymeacoffee
[checksbadge]:https://img.shields.io/github/checks-status/junalmeida/homeassistant-addons/main?style=plastic
[releasebadge]:https://img.shields.io/github/v/release/junalmeida/homeassistant-addons?style=plastic&display_name=tag&include_prereleases
<!-- [hacs]:https://github.com/hacs/integration
[hacsbadge]:https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=plastic -->

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg?style=plastic
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg?style=plastic
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg?style=plastic
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg?style=plastic
[i386-shield]: https://img.shields.io/badge/i386-yes-green.svg?style=plastic