# Description: Build the rpi-rgb-led-matrix library and python wheel.
#!/usr/bin/env bash

REPO_PATH="build/rpi-rgb-led-matrix"

# clone git repository
mkdir build
git clone https://github.com/hzeller/rpi-rgb-led-matrix.git $REPO_PATH

# build C library
make -C $REPO_PATH build-python PYTHON=$(which python3)

# build python wheel
pip wheel $REPO_PATH/bindings/python -w lib
