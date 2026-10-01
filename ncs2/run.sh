#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
exec sudo docker run --rm -it --network=none --user "$(id -u):$(id -g)" --group-add "$(getent group plugdev | cut -d: -f3)" --cap-drop=ALL --security-opt=no-new-privileges --device-cgroup-rule='c 189:* rwm' --mount type=bind,src=/dev/bus/usb,dst=/dev/bus/usb --mount "type=bind,src=$PWD/work,dst=/work" ncs2-openvino:2022.3.2 "$@"
