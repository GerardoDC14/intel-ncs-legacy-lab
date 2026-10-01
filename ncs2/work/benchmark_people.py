import argparse, json, time
from pathlib import Path
import cv2
import numpy as np
from openvino.runtime import Core, get_version

p = argparse.ArgumentParser()
p.add_argument('--model', required=True)
p.add_argument('--device', choices=['CPU', 'MYRIAD'], required=True)
p.add_argument('--iterations', type=int, default=64)
p.add_argument('--capture-dir', default='/work/captures')
a = p.parse_args()
root = Path('/work')
outdir = root/'results'/f'{a.model}-{a.device}'
outdir.mkdir(parents=True, exist_ok=True)
paths = sorted(Path(a.capture_dir).glob('*.jpg'))
frames = [cv2.imread(str(x)) for x in paths]
assert frames and all(x is not None for x in frames), 'No usable camera frames'
core = Core()
t = time.perf_counter()
model = core.read_model(str(root/'models'/a.model/f'{a.model}.xml'))
config = {'INFERENCE_NUM_THREADS': 4, 'NUM_STREAMS': '1'} if a.device == 'CPU' else {}
compiled = core.compile_model(model, a.device, config)
compile_s = time.perf_counter()-t
request = compiled.create_infer_request()
_, _, height, width = compiled.input(0).shape
def prep(frame):
    # OMZ Intel models expect BGR and embed their model-specific normalization.
    return np.ascontiguousarray(cv2.resize(frame, (width, height)).transpose(2,0,1)[None], dtype=np.float32)
person_label = 1 if 'retail' in a.model else 0
def boxes(result):
    return [d.tolist() for d in next(iter(result.values())).reshape(-1,7)
            if d[0] >= 0 and int(d[1]) == person_label and d[2] >= 0.5]
for i in range(10):
    request.infer({0:prep(frames[i % len(frames)])})
infer_ms, pipeline_ms, detections = [], [], []
for i in range(a.iterations):
    frame = frames[i % len(frames)]
    t0 = time.perf_counter()
    tensor = prep(frame)
    t1 = time.perf_counter()
    result = request.infer({0:tensor})
    t2 = time.perf_counter()
    found = boxes(result)
    t3 = time.perf_counter()
    infer_ms.append((t2-t1)*1000)
    pipeline_ms.append((t3-t0)*1000)
    if i < len(frames):
        detections.append({'frame':paths[i].name,'boxes':found})
summary = dict(model=a.model,device=a.device,openvino=get_version(),input_shape=list(compiled.input(0).shape),
    iterations=a.iterations,warmup=10,frames=len(frames),threshold=.5,compile_s=compile_s,
    inference_median_ms=float(np.median(infer_ms)),inference_p95_ms=float(np.percentile(infer_ms,95)),
    pipeline_median_ms=float(np.median(pipeline_ms)),pipeline_p95_ms=float(np.percentile(pipeline_ms,95)),
    serial_pipeline_fps=1000/float(np.mean(pipeline_ms)),
    frames_with_people=sum(bool(d['boxes']) for d in detections),
    total_detections=sum(len(d['boxes']) for d in detections),
    explicit_compile_device=[a.device],
    notes='Synchronous batch=1, 1 request. Pipeline excludes camera capture, decoding, drawing, disk IO. No ground-truth accuracy evaluation.')
(outdir/'result.json').write_text(json.dumps(dict(summary=summary,inference_ms=infer_ms,pipeline_ms=pipeline_ms,detections=detections),indent=2))
print(json.dumps(summary),flush=True)
