#!/bin/bash
echo "installer starting"
sudo mkdir /etc/SmartRyzenManager
echo "folder created : /etc/smartpower"
echo "moving new files"
sudo cp bg.py /etc/SmartRyzenManager
sudo cp data.json /etc/SmartRyzenManager
sudo cp processes.json /etc/SmartRyzenManager
sudo cp presets.json /etc/SmartRyzenManager
sudo cp ryzen_ctrl.py /etc/SmartRyzenManager
sudo cp SmartRyzenManager.service /etc/systemd/system
sudo cp -f SmartPowerCtrl.py /usr/bin/
sudo chmod a+x /usr/bin/SmartPowerCtrl.py
echo "moved new files, starting daemon"
sudo systemctl enable SmartRyzenManager
sudo systemctl start SmartRyzenManager
echo "done"