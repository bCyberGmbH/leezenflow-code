#!/usr/bin/env bash

# clone git repository
mkdir build
git clone https://github.com/hzeller/rpi-rgb-led-matrix.git build/rpi-rgb-led-matrix

# build C library
make -C build/rpi-rgb-led-matrix build-python PYTHON=$(which python3)

# build python wheel
pip wheel build/rpi-rgb-led-matrix/bindings/python -w lib
