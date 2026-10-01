#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mode="${1:-both}"
if [[ $# -gt 0 ]]; then shift; fi
case "$mode" in both|cpu|myriad) ;; *) echo 'Usage: live.sh [both|cpu|myriad]'; exit 2;; esac
# Get the current graphical session, including GNOME Wayland's Xwayland credentials.
while IFS='=' read -r name value; do
 case "$name" in DISPLAY|XAUTHORITY) if [[ -z "${!name:-}" ]]; then export "$name=$value"; fi;; esac
done < <(systemctl --user show-environment)
: "${DISPLAY:?Run this launcher from the NUC graphical desktop}"
: "${XAUTHORITY:?No graphical-session authorization found}"
camera="${NCS_CAMERA:-}"
if [[ -z "$camera" ]]; then
 for dev in /dev/video*; do
  if v4l2-ctl -d "$dev" --list-formats-ext 2>/dev/null | grep -q "'YUYV'"; then camera="$dev"; break; fi
 done
fi
: "${camera:?No RGB YUYV camera found}"
echo "Camera: $camera | Mode: $mode | Q/Esc closes the viewer"
sudo -v
set +e
ffmpeg -nostdin -hide_banner -loglevel warning -f v4l2 -input_format yuyv422 -video_size 640x480 -framerate 15 -i "$camera" -an -pix_fmt bgr24 -f rawvideo - | sudo docker run -i --rm --network=host --user "$(id -u):$(id -g)" --group-add "$(getent group plugdev | cut -d: -f3)" --group-add "$(getent group video | cut -d: -f3)" --cap-drop=ALL --security-opt=no-new-privileges --device-cgroup-rule='c 189:* rwm' --device "$camera:/dev/camera" --mount type=bind,src=/dev/bus/usb,dst=/dev/bus/usb --mount type=bind,src=/run/udev,dst=/run/udev,readonly --mount type=bind,src=/tmp/.X11-unix,dst=/tmp/.X11-unix,readonly --mount "type=bind,src=$XAUTHORITY,dst=/tmp/ncs-xauthority,readonly" --mount "type=bind,src=$PWD/work,dst=/work" -e "DISPLAY=$DISPLAY" -e XAUTHORITY=/tmp/ncs-xauthority -e LD_LIBRARY_PATH=/opt/intel/openvino/deployment_tools/ngraph/lib:/opt/intel/openvino/deployment_tools/inference_engine/lib/intel64:/opt/intel/openvino/deployment_tools/inference_engine/external/tbb/lib ncs1-openvino:2020.3.2 python3 /work/live_people.py --mode "$mode" "$@"

status=("${PIPESTATUS[@]}")
exit "${status[1]}"
