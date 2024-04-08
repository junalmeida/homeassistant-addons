# Home Assistant - Meter Parser AddOn
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee] ![Checks][checksbadge]
![Last release][releasebadge] [^1]

This is a Home Assistant AddOn (not HACS) to allow parse of dial and digits utility meters like water, gas, and electricity to provide energy consumption information to home assistant using a regular ip camera.

This repository is under alpha stage, so expect bugs and breaking changes.

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]  

Please consider sponsoring if you feel that this project is somehow useful to you. 


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
[releasebadge]:https://img.shields.io/badge/dynamic/yaml?label=version&query=version&url=https%3A%2F%2Fraw.githubusercontent.com%2Fjunalmeida%2Fhomeassistant-addons%2Fmain%2Fmeterparser%2Fconfig.yaml&style=plastic

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg?style=plastic
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg?style=plastic
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg?style=plastic
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg?style=plastic
[i386-shield]: https://img.shields.io/badge/i386-yes-green.svg?style=plastic