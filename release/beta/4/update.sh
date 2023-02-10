#!/bin/bash
echo "updater starting, disabling daemon"
sudo systemctl disable smartpower
sudo systemctl stop smartpower
echo "disabled daemon, moving files"
sudo cp -f bg.py /etc/smartpower
sudo cp -f ryzen_ctrl.py /etc/smartpower
sudo cp -f smartpower.service /etc/systemd/system
sudo cp -f SmartPowerCtrl.py /usr/bin/
sudo chmod a+x /usr/bin/SmartPowerCtrl.py
echo "moved new files, starting daemon"
sudo systemctl enable smartpower
sudo systemctl start smartpower
echo "daemon started"
echo "done"