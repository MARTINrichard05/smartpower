#!/bin/bash
echo "installer starting"
sudo mkdir /etc/smartpower
echo "folder created : /etc/smartpower"
echo "installing python libs"
pip install textual
echo "moving new files"
sudo cp bg.py /etc/smartpower
sudo cp storage.json /etc/smartpower
sudo cp ryzen_ctrl.py /etc/smartpower
sudo cp SmartRyzenManager.service /etc/systemd/system
sudo cp -f SmartPowerCtrl.py /usr/bin/
sudo cp -f SmartPowerCtrlTui.py /usr/bin/
sudo cp -f SmartPowerCtrlTuiCss.css /usr/bin/
sudo chmod a+x /usr/bin/SmartPowerCtrl.py
sudo chmod a+x /usr/bin/SmartPowerCtrlTui.py
echo "moved new files, starting daemon"
sudo systemctl enable SmartRyzenManager
sudo systemctl start SmartRyzenManager
echo "done"
