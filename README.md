# Leezenflow Source Code

This repo contains the (python) code to run [Leezenflow](https://github.com/bCyberGmbH/leezenflow-doku).

## Requirements

The hardware setup is described in detail in this [guide](https://github.com/bCyberGmbH/leezenflow-doku/blob/main/case.md).
The basics are:
- Raspberry PI 3 Model B+
- [Adafruit RGB Matrix HAT + RTC for Raspberry Pi](https://www.adafruit.com/product/2345)
- [32x32 RGB LED Matrix Panel - 5mm Pitch](https://www.adafruit.com/product/2026)
- [64x32 RGB LED Matrix - 5mm pitch](https://www.adafruit.com/product/2277)

To test the setup we recommend to check out: https://github.com/hzeller/rpi-rgb-led-matrix
As stated in the docs, you should disable sound: https://github.com/hzeller/rpi-rgb-led-matrix#bad-interaction-with-sound
and bridge GPIO Pins 4 and 18 as documented here: https://github.com/hzeller/rpi-rgb-led-matrix#improving-flicker

![image](https://user-images.githubusercontent.com/66736282/131323333-051d12f2-3675-4559-b143-b1451a63ec5d.png)
Source: https://github.com/hzeller/rpi-rgb-led-matrix/blob/master/img/adafruit-mod.jpg

**Reminder: use the `--led-gpio-mapping=adafruit-hat-pwm` flag after you've modified the Matrix hat!**

## Installation
- check out this repo this to e.g. `/home/pi/`
- `pip3 install -r requirements.txt`
- start an endless simulation with `sudo python3 leezenflow.py --test 3`

## Production usage

- copy `config.ini.example` to `config.ini` and adjust the settings as needed
- Setup this code to run as a system service, as described in this guide: https://www.raspberrypi.org/documentation/computers/using_linux.html#creating-a-service
- After testing the service, run: `sudo systemctl enable leezenflow.service` to enable automatic startup after a reboot

**Reminder: do not forget to use the `python3 -u` flag in your service definition to prevent logging problems**
