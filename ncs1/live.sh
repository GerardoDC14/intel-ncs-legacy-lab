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
  if v4l2-ctl -d "$dev" --list-formats-ext 2>/dev/null | grep "'YUYV'" >/dev/null; then camera="$dev"; break; fi
 done
fi
: "${camera:?No RGB YUYV camera found}"
echo "Camera: $camera | Mode: $mode | Q/Esc closes the viewer"
# Keep a second viewer from competing for the camera or the stick.
exec 9>"${XDG_RUNTIME_DIR:-/tmp}/intel-ncs1-live-$(id -u).lock"
flock -n 9 || { echo 'Another NCS1 viewer is already running. Close it first.'; exit 1; }
sudo -v
set +e
for attempt in 1 2; do
ffmpeg -nostdin -hide_banner -loglevel warning -f v4l2 -input_format yuyv422 -video_size 640x480 -framerate 15 -i "$camera" -an -pix_fmt bgr24 -f rawvideo - | sudo docker run -i --rm --network=host --user "$(id -u):$(id -g)" --group-add "$(getent group plugdev | cut -d: -f3)" --group-add "$(getent group video | cut -d: -f3)" --cap-drop=ALL --security-opt=no-new-privileges --device-cgroup-rule='c 189:* rwm' --device "$camera:/dev/camera" --mount type=bind,src=/dev/bus/usb,dst=/dev/bus/usb --mount type=bind,src=/run/udev,dst=/run/udev,readonly --mount type=bind,src=/tmp/.X11-unix,dst=/tmp/.X11-unix,readonly --mount "type=bind,src=$XAUTHORITY,dst=/tmp/ncs-xauthority,readonly" --mount "type=bind,src=$PWD/work,dst=/work" -e "DISPLAY=$DISPLAY" -e XAUTHORITY=/tmp/ncs-xauthority -e LD_LIBRARY_PATH=/opt/intel/openvino/deployment_tools/ngraph/lib:/opt/intel/openvino/deployment_tools/inference_engine/lib/intel64:/opt/intel/openvino/deployment_tools/inference_engine/external/tbb/lib ncs1-openvino:2020.3.2 python3 /work/live_people.py --mode "$mode" "$@"
 status=("${PIPESTATUS[@]}")
 code="${status[1]}"
 if [[ "$code" != 75 || "$attempt" == 2 ]]; then exit "$code"; fi
 echo 'MYRIAD initialization failed. Resetting the idle USB stick and retrying once...'
 if ! sudo python3 ../scripts/reset-ncs1-usb.py; then exit 1; fi
done
