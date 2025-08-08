#!/bin/bash

set -e

echo "[1/4] Updating system..."
sudo apt update && sudo apt upgrade -y

echo "[2/4] Installing GNU Radio dependencies..."
sudo apt install -y git cmake g++ python3 python3-pip \
 build-essential pkg-config libboost-all-dev \
 swig libgmp-dev libmpfr-dev gnuradio \
 libfftw3-dev libcomedi-dev libsdl1.2-dev \
 libgsl-dev libusb-1.0-0-dev libqt5svg5-dev \
 python3-numpy python3-mako python3-sphinx \
 doxygen libqt5opengl5-dev qttools5-dev \
 qttools5-dev-tools python3-click python3-zmq \
 python3-scipy libuhd-dev uhd-host

echo "[3/4] Cloning and building gr-reveng..."
git clone https://github.com/paulgclark/gr-reveng.git
cd gr-reveng
mkdir build && cd build
cmake ..
make -j$(nproc)
sudo make install
sudo ldconfig

echo "[4/4] Setup complete! Test GRC with 'gnuradio-companion'"
