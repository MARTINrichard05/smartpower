#!/bin/bash
echo "installer starting"
sudo mkdir /etc/smartpower
echo "folder created : /etc/smartpower"
echo "moving new files"
sudo cp bg.py /etc/smartpower
sudo cp data.json /etc/smartpower
sudo cp processes.json /etc/smartpower
sudo cp ryzen_ctrl.py /etc/smartpower
sudo cp smartpower.service /etc/systemd/system
echo "moved new files, starting daemon"
sudo systemctl enable smartpower
sudo systemctl start smartpower
echo "done"