"""Static synchronous benchmark using a user-provided image. No camera image saved."""
import argparse, json, time
from pathlib import Path
import cv2
import numpy as np
from openvino.inference_engine import IECore, get_version
p=argparse.ArgumentParser()
p.add_argument('--device', choices=['CPU','MYRIAD'], required=True)
p.add_argument('--model', default='mobilenet-ssd')
p.add_argument('--image', required=True)
p.add_argument('--iterations', type=int, default=20)
p.add_argument('--warmup', type=int, default=5)
a=p.parse_args()
if a.iterations < 1 or a.warmup < 0:p.error('Invalid iteration count')
ie=IECore();path=Path('/work/models')/(a.model+'.xml')
net=ie.read_network(str(path),str(path.with_suffix('.bin')))
key=next(iter(net.inputs));shape=net.inputs[key].shape
frame=cv2.imread(a.image)
if frame is None:raise ValueError('Cannot read input image')
x=cv2.resize(frame,(shape[3],shape[2])).transpose(2,0,1)[None].astype(np.float32)
exe=ie.load_network(net,a.device)  # explicit device: no automatic CPU fallback
for _ in range(a.warmup):exe.infer({key:x})
times=[]
for _ in range(a.iterations):
 start=time.perf_counter();exe.infer({key:x});times.append((time.perf_counter()-start)*1000)
result=dict(model=a.model,device=a.device,openvino=get_version(),iterations=a.iterations,warmup=a.warmup,median_ms=float(np.median(times)),p95_ms=float(np.percentile(times,95)),inference_ms=times,note='Inference only; one image; no accuracy or energy measurement')
Path('/work/benchmark-'+a.device+'.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
