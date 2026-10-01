FROM ubuntu:18.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-numpy python3-opencv libusb-1.0-0 libtbb2 libpugixml1v5 libgomp1 ca-certificates && rm -rf /var/lib/apt/lists/*
COPY l_openvino_toolkit_runtime_ubuntu18_p_2020.3.355.tgz /tmp/openvino.tgz
RUN mkdir -p /opt/intel/openvino && tar -xzf /tmp/openvino.tgz -C /opt/intel/openvino --strip-components=1 && rm /tmp/openvino.tgz
ENV PYTHONPATH="/opt/intel/openvino/python/python3.6"
ENV LD_LIBRARY_PATH="/opt/intel/openvino/deployment_tools/ngraph/lib:/opt/intel/openvino/deployment_tools/inference_engine/lib/intel64:/opt/intel/openvino/deployment_tools/inference_engine/external/tbb/lib"
RUN apt-get update && apt-get install -y --no-install-recommends libpython3.6 && rm -rf /var/lib/apt/lists/*
WORKDIR /work
CMD ["bash"]
