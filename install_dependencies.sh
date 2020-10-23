#!/usr/bin/bash
# kivy install from master
echo "Installing kivy from master branch"
sudo apt install python3-pip build-essential git python3 python3-dev ffmpeg libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev
sudo apt install libgstreamer1.0 gstreamer1.0-plugins-base gstreamer1.0-plugins-good
sudo pip3 install ffpyplayer
sudo pip3 install cython
sudo pip3 install git+https://github.com/kivy/kivy.git@master

# install picamera
echo "installing picamera module"
sudo pip3 install picamera



