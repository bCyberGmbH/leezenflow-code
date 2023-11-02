# Leezenflow Source Code

This repo contains the (python) code to run [Leezenflow](https://github.com/bCyberGmbH/leezenflow-doku). It includes a script to parse the traffic light data (message_interpreter.py) and the animation (leezenflow.py).

## License

Copyright (C) 2021-2023 bCyber GmbH

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

## Requirements

The hardware setup is described in detail in this [guide](https://github.com/bCyberGmbH/leezenflow-doku/blob/main/case.md).
The basics are:
- Raspberry PI 3 Model B+
- [Adafruit RGB Matrix HAT + RTC for Raspberry Pi](https://www.adafruit.com/product/2345)
- [32x32 RGB LED Matrix Panel - 5mm Pitch](https://www.adafruit.com/product/2026)
- [64x32 RGB LED Matrix - 5mm pitch](https://www.adafruit.com/product/2277)

To test the setup we recommend to check out: https://github.com/hzeller/rpi-rgb-led-matrix. \
As stated in the docs, you should disable sound: https://github.com/hzeller/rpi-rgb-led-matrix#bad-interaction-with-sound
and bridge GPIO Pins 4 and 18 as documented here: https://github.com/hzeller/rpi-rgb-led-matrix#improving-flicker

![image](https://user-images.githubusercontent.com/66736282/131323333-051d12f2-3675-4559-b143-b1451a63ec5d.png)
Source: https://github.com/hzeller/rpi-rgb-led-matrix/blob/master/img/adafruit-mod.jpg

## Setup on Raspberry PI

1. For initializing your Raspberry Pi with an operating system, install the official Raspberry PI imager (we used version v.1.7.2) on a computer with a microSD card reader. Plug in an empty microSD card and select Raspberry Pi OS (other) -> Raspberry Raspberry Pi OS Lite (32-Bit). We used version 2022-04-04. Make sure that you activate SSH.
2. Find out the ip address of your Raspberry Pi and connect to it using `ssh pi@IPADDRESS`.
3. Install git, e.g. using `sudo apt update` and `sudo apt install git`.
4. Install pip, e.g. using `sudo apt-get install python3-pip`
5. Clone [rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix) to e.g. `/home/pi/`
6. You can adjust the Makefile if you made any hardware modifications. See: https://github.com/hzeller/rpi-rgb-led-matrix/tree/master/bindings/python 
7. Build the library. First, change directories into `rpi-rgb-led-matrix/bindings/python/`. Then:
```
sudo apt-get update && sudo apt-get install python3-dev python3-pillow -y
make build-python PYTHON=$(command -v python3)
sudo make install-python PYTHON=$(command -v python3)
```
8. Deactivate the sound module as described in the readme of https://github.com/hzeller/rpi-rgb-led-matrix.
9. Check an example by running `sudo python runtext.py` in directory `rpi-rgb-led-matrix/bindings/python/samples/`
10. Another example: `sudo python pulsing-brightness.py --led-gpio-mapping=adafruit-hat-pwm --led-cols=96 --led-rows=32`
11. Let's add the Leezenflow code: Clone this repo this to e.g. `/home/pi/`
12. Install Python library to receive MQTT messages: `sudo pip install -r requirements.txt`

The implemention assumes you have made the "adafruit-hat-pwm" modification to your hardware.

## Development setup

1. Create virtual environment: `python -m venv venv`
2. Install dependencies (within virtual environment):

    ```bash
    pip install -r requirements.txt
    ```

3. Install `leezenflow` package in editable mode (within virtual environment): 

    ```bash
    pip install -e .
    ```
4. (optional) Run unit tests, which are located in folder `tests`:

    ```bash
    pytest tests
    ```

## Production usage (on Raspberry PI)

Run the following commands in the `leezenflow-code` directory:

```bash
sudo pip install -r requirements.txt
sudo pip install -e .
```

- Use `sudo python leezenflow.py --help` to get an overview over command line options.

Setup the leezenflow.py script as service such that Leezenflow runs on start:
- `cd /etc/systemd/system`
- Create file: `sudo touch leezenflow.service`
- Edit file: `sudo nano leezenflow.service`
- Enter (for example) the following:
```
[Unit]
Description=Start leezenflow
After=multi-user.target
[Service]
WorkingDirectory=/home/pi/leezenflow-code
ExecStart=/usr/bin/python -u /home/pi/leezenflow-code/leezenflow.py --your-settings
User=root
[Install]
WantedBy=multi-user.target
```

- Reload: `sudo systemctl daemon-reload`
- After testing the service with `sudo systemctl start leezenflow.service`, run: `sudo systemctl enable leezenflow.service` to enable automatic startup after a reboot.
- The service can be stopped with: `sudo systemctl stop leezenflow.service`
- Reminder: Do not forget to use the `python -u` (as used above) flag in your service definition to prevent logging problems
