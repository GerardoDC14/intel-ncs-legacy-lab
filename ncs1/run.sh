#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
exec sudo docker run --rm -it --network=host -e LD_LIBRARY_PATH=/opt/intel/openvino/deployment_tools/ngraph/lib:/opt/intel/openvino/deployment_tools/inference_engine/lib/intel64:/opt/intel/openvino/deployment_tools/inference_engine/external/tbb/lib --user "$(id -u):$(id -g)" --group-add "$(getent group plugdev | cut -d: -f3)" --cap-drop=ALL --security-opt=no-new-privileges --device-cgroup-rule='c 189:* rwm' --mount type=bind,src=/dev/bus/usb,dst=/dev/bus/usb --mount type=bind,src=/run/udev,dst=/run/udev,readonly --mount "type=bind,src=$PWD/work,dst=/work" ncs1-openvino:2020.3.2 "$@"
