#!/usr/bin/env bash
set -euo pipefail
sudo apt-get update
sudo apt-get install -y docker.io ffmpeg v4l-utils usbutils wget git
sudo systemctl enable --now docker
getent group plugdev >/dev/null || sudo groupadd --system plugdev
sudo usermod -aG plugdev,video "$USER"
sudo tee /etc/udev/rules.d/97-myriad-usbboot.rules >/dev/null <<'RULES'
SUBSYSTEM=="usb", ATTR{idVendor}=="03e7", ATTR{idProduct}=="2150", GROUP="plugdev", MODE="0660"
SUBSYSTEM=="usb", ATTR{idVendor}=="03e7", ATTR{idProduct}=="2485", GROUP="plugdev", MODE="0660"
SUBSYSTEM=="usb", ATTR{idVendor}=="03e7", ATTR{idProduct}=="f63b", GROUP="plugdev", MODE="0660"
RULES
sudo udevadm control --reload-rules
sudo udevadm trigger --subsystem-match=usb
printf '%s\n' 'Reconnect the stick; log out/in after adding groups. Docker commands use sudo.'
