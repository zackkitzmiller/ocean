#1/bin/bash

sudo cp etc/systemd/system/ocean.system /etc/systemd/system/ocean.service
sudo systemctl enable ocean
