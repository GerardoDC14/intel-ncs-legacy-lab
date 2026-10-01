FROM ncs1-openvino:2020.3.2
USER root
RUN apt-get update && apt-get install -y --no-install-recommends python3-pip && python3 -m pip install networkx==2.5 numpy==1.19.5 protobuf==3.6.1 defusedxml==0.6.0 && rm -rf /var/lib/apt/lists/*
