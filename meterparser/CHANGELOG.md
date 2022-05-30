# Changelog

## [1.0.0.28]
- Adjust time limit for camera scan interval 
- Update base docker images
## [1.0.0.25]
- Deal with possible HA restart and username/password change. 
## [1.0.0.*]
- Make a lower limit so device won't be unavailable
- Easier to read log messages
- Tune limits and fail safe OCR readings
- General fixes (see commit history)
- Fix percent message
- Compare image simmilarities
- Introduce Google Cloud Vision API
- Improve fail safe readings, allow to reset reading via mqtt
- Add SIGINT logic and refactorings
- Set qos
- Rewrite topic to allow concurrent instances.
- Send current value to sensor on intervals
- Fix service type on devices
- Fix incorrect variable name.
- Save image to PNG for OCR.
- Add `stdin` input to list and reset the control value. 
- Fix code errors and error messages.
- Initial version.