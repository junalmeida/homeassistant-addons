### [1.0.2.11]
- Moving token from env vars to parameter

### [1.0.2.10]
- Upgrade base image
- Change checks for missing variables

### [1.0.2.9]
- Fix missing hostname

### [1.0.2.8]
- Add armv7 support
### [1.0.2.5]

- Reduce ffmpeg logs, reduce amount of time to seek for a snapshot
- Improve ocr.space retry logic, add engine 5 as a fallback

### [1.0.2.3]

- Fix incorrect ffmpeg path.
- Add force_ffmpeg setting

### [1.0.2.1]

- Add a user setting for reading limits for error margins
- Add trigger to run on and after getting images from the camera. Useful to turn a flash light on

### [1.0.1.5]

- Accept decimal values on meter reset command.
- Fix deprecated calls in build action.

### [1.0.1.4]

- Add `device_class` to water meter sensor.

### [1.0.1.3]

- Expand image when rotating to re-read ArUco markers.

### [1.0.1.2]

- Fix incorrect error message

### [1.0.1.1]

- Fix incorrect mqtt_url default

### [1.0.1.0]

- Set an specific aruco marker number so you can add multiple counters using the same camera
- Move custom mqtt setting to a single url (breaking change)
- If url schema is not http(s), try get an image using ffmpeg

### [1.0.0.28]

- Adjust time limit for camera scan interval
- Update base docker images

### [1.0.0.25]

- Deal with possible HA restart and username/password change.

### [1.0.0.*]

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
