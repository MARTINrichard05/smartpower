#!/bin/bash
echo "installer starting"
sudo mkdir /etc/smartpower
echo "folder created : /etc/smartpower"
echo "moving new files"
sudo cp bg.py /etc/smartpower
sudo cp storage.json /etc/smartpower
sudo cp ryzen_ctrl.py /etc/smartpower
sudo cp smartpower.service /etc/systemd/system
sudo cp -f SmartPowerCtrl.py /usr/bin/
sudo chmod a+x /usr/bin/SmartPowerCtrl.py
echo "moved new files, starting daemon"
sudo systemctl enable smartpower
sudo systemctl start smartpower
echo "done"