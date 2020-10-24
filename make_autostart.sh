#!/usr/bin/env bash
# make autostart for lxde
echo "Install autostart"
echo " remove ~/.config/lxsession/LXDE-pi/autostart to restore previous config"
echo "@bash /home/pi/pylapse/launch_pylapse.sh" | tee -a ~/.config/lxsession/LXDE-pi/autostart
