FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive PIP_DISABLE_PIP_VERSION_CHECK=1
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip python3-venv libusb-1.0-0 libstdc++6 ca-certificates usbutils && rm -rf /var/lib/apt/lists/*
RUN python3 -m venv /opt/ncs2
ENV PATH="/opt/ncs2/bin:${PATH}"
RUN python -m pip install --no-cache-dir 'pip==24.3.1' && python -m pip install --no-cache-dir 'numpy==1.24.4'
COPY l_openvino_toolkit_ubuntu20_2022.3.2.9279.e2c7e4d7b4d_x86_64.tgz /tmp/openvino.tgz
RUN mkdir -p /opt/intel/openvino && tar -xzf /tmp/openvino.tgz -C /opt/intel/openvino --strip-components=1 && rm /tmp/openvino.tgz
ENV PYTHONPATH="/opt/intel/openvino/python/python3.8"
ENV LD_LIBRARY_PATH="/opt/intel/openvino/runtime/lib/intel64:/opt/intel/openvino/runtime/3rdparty/tbb/lib"
RUN apt-get update && apt-get install -y --no-install-recommends libpugixml1v5 libtbb2 && rm -rf /var/lib/apt/lists/*
RUN python -m pip install --no-cache-dir opencv-python-headless==4.8.1.78
WORKDIR /work
CMD ["bash"]
