#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
case "${1:-ncs1}" in
 ncs1) target=ncs1; archive=l_openvino_toolkit_runtime_ubuntu18_p_2020.3.355.tgz; url="https://storage.openvinotoolkit.org/repositories/openvino/packages/2020.3.2/$archive"; image=ncs1-openvino:2020.3.2;;
 ncs2) target=ncs2; archive=l_openvino_toolkit_ubuntu20_2022.3.2.9279.e2c7e4d7b4d_x86_64.tgz; url="https://storage.openvinotoolkit.org/repositories/openvino/packages/2022.3.2/linux/$archive"; image=ncs2-openvino:2022.3.2;;
 *) echo 'Usage: build-runtime.sh [ncs1|ncs2]'; exit 2;;
esac
cd "$root/$target"
if [[ ! -s "$archive" ]]; then wget -O "$archive.part" "$url"; mv "$archive.part" "$archive"; fi
# Validate archive readability and retain the downloaded hash for reproducibility.
tar tzf "$archive" >/dev/null
sha256sum "$archive" > runtime-sha256.local.txt
sudo docker build -t "$image" .
mkdir -p work/models
