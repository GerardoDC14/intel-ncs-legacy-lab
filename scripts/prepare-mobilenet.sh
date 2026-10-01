#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root/ncs1/converter"
revision=bb17b6c3eef36d80be441ae8e5339be66e8e3b7a
wget -O mobilenet-ssd.caffemodel "https://raw.githubusercontent.com/chuanqi305/MobileNet-SSD/$revision/mobilenet_iter_73000.caffemodel"
wget -O mobilenet-ssd.prototxt "https://raw.githubusercontent.com/chuanqi305/MobileNet-SSD/$revision/deploy.prototxt"
cat <<'HASHES' | sha256sum --check
52eed8be80522c152a17fb56740de705b79881bde1a167e0e747310523685fc7  mobilenet-ssd.caffemodel
2d180f723b3109e21f8287f6b3c691390d07b60eed998327cd3259ffa0e50608  mobilenet-ssd.prototxt
HASHES
archive=l_openvino_toolkit_dev_ubuntu18_p_2020.3.355.tgz
wget -O "$archive" "https://storage.openvinotoolkit.org/repositories/openvino/packages/2020.3.2/$archive"
tar xzf "$archive" --strip-components=2 "l_openvino_toolkit_dev_ubuntu18_p_2020.3.355/deployment_tools/model_optimizer"
sudo docker build -t ncs1-converter:2020.3.2 .
mkdir -p ../work/models
sudo docker run --rm --user "$(id -u):$(id -g)" -v "$PWD:/convert:ro" -v "$root/ncs1/work:/work" ncs1-converter:2020.3.2 python3 /convert/model_optimizer/mo.py --framework caffe --input_model /convert/mobilenet-ssd.caffemodel --input_proto /convert/mobilenet-ssd.prototxt --input_shape '[1,3,300,300]' --mean_values '[127.5,127.5,127.5]' --scale_values '[127.5,127.5,127.5]' --data_type FP16 --model_name mobilenet-ssd --output_dir /work/models
