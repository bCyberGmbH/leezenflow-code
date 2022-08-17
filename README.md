# Leezenflow Source Code

This repo contains the (python) code to run [Leezenflow](https://github.com/bCyberGmbH/leezenflow-doku). It includes a script to parse the traffic light data (message_interpreter.py) and the animation (leezenflow.py).

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

## Installation
- For initializing your Raspberry Pi with an operating system, install the official Raspberry PI imager (we used version v.1.7.2) on a computer with a microSD card reader. Plug in an empty microSD card and select Raspberry Pi OS (other) -> Raspberry Raspberry Pi OS Lite (32-Bit). We used version 2022-04-04. Make sure that you activate SSH.
- Find out the ip address of your Raspberry Pi and connect to it using `ssh pi@IPADDRESS`.
- Install git, e.g. using `sudo apt update` and `sudo apt install git`.
- Install pip, e.g. using `sudo apt-get install python3-pip`
- Clone [rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix) to e.g. `/home/pi/`
- You can adjust the Makefile if you made any hardware modifications. See: https://github.com/hzeller/rpi-rgb-led-matrix/tree/master/bindings/python 
- Build the library. First, change directories into `rpi-rgb-led-matrix/bindings/python/`. Then:
```
sudo apt-get update && sudo apt-get install python3-dev python3-pillow -y
make build-python PYTHON=$(command -v python3)
sudo make install-python PYTHON=$(command -v python3)
```
- Deactivate the sound module as described in the readme of https://github.com/hzeller/rpi-rgb-led-matrix.
- Check an example by running `sudo python runtext.py` in directory `rpi-rgb-led-matrix/bindings/python/samples/`
- Another example: `sudo python pulsing-brightness.py --led-gpio-mapping=adafruit-hat-pwm --led-cols=96 --led-rows=32`
- Let's add the Leezenflow code: Clone this repo this to e.g. `/home/pi/`
- Install Python library to receive MQTT messages: `sudo pip install -r requirements.txt`
- Start an endless simulation with `sudo python leezenflow.py --test 0`

The implemention assumes you have made the "adafruit-hat-pwm" modification to your hardware.

## Production usage

- Use `sudo python leezenflow.py --help` to get an overview over command line options.
- `--receiver` How messages should be received. 0=None, 1=MQTT, 2=UDP
- `--test` Use a test dataset (instead of using live data via a receiver).
- `--modifier` Select a modifier to smooth inaccurate predictions.
- `--animation` Select animation: 0,1,2,3,...

For receiving live data: copy `config.ini.example` to a new file named `config.ini` and adjust the settings as needed

Setup the leezenflow.py script as service such that Leezenflow runs on start:
- `cd /etc/systemd/system`
- Create file: `sudo touch leezenflow.service`
- Edit file: `sudo nano leezenflow.service`
- Enter (for example) the following:
```
[Unit]
Description=Start leezenflow listening on UDP messages on boot with Hoerstertor modifier
After=multi-user.target
[Service]
WorkingDirectory=/home/pi/leezenflow-code
ExecStart=/usr/bin/python -u /home/pi/leezenflow-code/leezenflow.py --animation 0 --receiver 2 --modifier 1
User=root
[Install]
WantedBy=multi-user.target
```
- This starts animation `0` with the UDP listener and modifier `1` on start. In order to run the animation with test data you can use:
`ExecStart=/usr/bin/python -u /home/pi/leezenflow-code/leezenflow.py --animation 0 --test 4`
- Reload: `sudo systemctl daemon-reload`
- After testing the service with `sudo systemctl start leezenflow.service`, run: `sudo systemctl enable leezenflow.service` to enable automatic startup after a reboot.
- The service can be stopped with: `sudo systemctl stop leezenflow.service `
- Reminder: Do not forget to use the `python -u` (as used above) flag in your service definition to prevent logging problems