#!/bin/bash
echo "updater starting, disabling daemon"
sudo systemctl disable smartpower
sudo systemctl stop smartpower
echo "disabled daemon, moving files"
sudo cp bg.py /etc/smartpower
sudo cp ryzen_ctrl.py /etc/smartpower
sudo cp smartpower.service /etc/systemd/system
sudo cp tui.py /usr/bin/
sudo chmod a+x /usr/bin/tui.py
echo "moved new files, starting daemon"
sudo systemctl enable smartpower
sudo systemctl start smartpower
echo "daemon started"
echo "done"