import argparse, multiprocessing as mp, queue, time, json, sys
from collections import deque
from pathlib import Path
import cv2
import numpy as np
from openvino.inference_engine import IECore
p=argparse.ArgumentParser();p.add_argument('--mode',choices=['both','cpu','myriad'],default='both');p.add_argument('--seconds',type=float,default=0);p.add_argument('--model',default='mobilenet-ssd');p.add_argument('--threshold',type=float,default=.4);a=p.parse_args()
devices=['CPU','MYRIAD'] if a.mode=='both' else [a.mode.upper()]
stop=mp.Event();results={};errors={};channels={d:(mp.Queue(1),mp.Queue(2)) for d in devices}
def worker(device, inputs, outputs):
 try:
  ie=IECore();net=ie.read_network('/work/models/'+a.model+'.xml','/work/models/'+a.model+'.bin');key=next(iter(net.inputs));shape=net.inputs[key].shape
  cfg={'CPU_THREADS_NUM':'2','CPU_THROUGHPUT_STREAMS':'1'} if device=='CPU' else {}
  exe=ie.load_network(net,device,config=cfg)
  print(device,'model loaded',flush=True)
  while not stop.is_set():
   try:frame,fid=inputs.get(timeout=.2)
   except queue.Empty:continue
   start=time.perf_counter();x=cv2.resize(frame,(shape[3],shape[2])).transpose(2,0,1)[None].astype(np.float32);t=time.perf_counter();r=exe.infer({key:x});ms=(time.perf_counter()-t)*1000
   boxes=[d for d in next(iter(r.values())).reshape(-1,7) if d[0]>=0 and d[1]==(15 if a.model=='mobilenet-ssd' else 1) and d[2]>=a.threshold]
   image=frame.copy()
   for d in boxes:
    x1,y1,x2,y2=(np.clip(d[3:7],0,1)*np.array([frame.shape[1],frame.shape[0]]*2)).astype(int);cv2.rectangle(image,(x1,y1),(x2,y2),(0,255,0),2);cv2.putText(image,'person %.2f'%d[2],(x1,max(18,y1-5)),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,255,0),1)
   message=('result',(image,ms,1/(time.perf_counter()-start),len(boxes),time.monotonic(),fid))
   try:outputs.put_nowait(message)
   except queue.Full:pass
 except Exception as e:
  outputs.put(('error',str(e)))
  print(device,'ERROR:',e,flush=True)
 finally:
  outputs.cancel_join_thread();inputs.cancel_join_thread()
processes=[mp.Process(target=worker,args=(d,*channels[d]),daemon=True) for d in devices]
for proc in processes:proc.start()
cv2.namedWindow('People detection - CPU / NCS1',cv2.WINDOW_NORMAL);cv2.resizeWindow('People detection - CPU / NCS1',1280 if len(devices)==2 else 640,695)
started=time.monotonic();fid=0
history={d:deque() for d in devices}
colors={'CPU':(255,180,60),'MYRIAD':(70,220,110)}
def stats(device, now):
 samples=[r for r in history[device] if now-r[0]<=5]
 if not samples:return None,0
 # Rate includes capture, preprocessing, inference and scheduling; not reciprocal latency.
 elapsed=min(5,max(.001,now-started))
 return float(np.mean([r[1] for r in samples])),len(samples)/elapsed
def chart(now, width):
 canvas=np.full((160,width,3),22,np.uint8)
 left,right,top,bottom=65,width-20,48,133
 all_ms=[ms for h in history.values() for _,ms in h]
 ymax=max(50,100*np.ceil(max(all_ms or [100])/100))
 cv2.putText(canvas,'Inference latency | last 30 s | '+a.model,(12,21),cv2.FONT_HERSHEY_SIMPLEX,.5,(220,220,220),1)
 for frac in (0,.5,1):
  y=int(bottom-frac*(bottom-top));cv2.line(canvas,(left,y),(right,y),(65,65,65),1)
  cv2.putText(canvas,'%d ms'%(ymax*frac),(3,y+4),cv2.FONT_HERSHEY_SIMPLEX,.35,(160,160,160),1)
 for d in devices:
  points=[(int(right-(now-t)/30*(right-left)),int(bottom-min(ms/ymax,1)*(bottom-top))) for t,ms in history[d]]
  if len(points)>1:cv2.polylines(canvas,[np.array(points,np.int32)],False,colors[d],2)
  avg,rate=stats(d,now)
  text=d+' (loading)' if avg is None else '%s: %.1f ms avg | %.1f infer/s'%(d,avg,rate)
  x=left if d=='CPU' or len(devices)==1 else width//2
  cv2.putText(canvas,text,(x,40),cv2.FONT_HERSHEY_SIMPLEX,.42,colors[d],1)
 cpu,_=stats('CPU',now) if 'CPU' in history else (None,0)
 stick,_=stats('MYRIAD',now) if 'MYRIAD' in history else (None,0)
 tail='-30 s                                              now'
 if cpu is not None and stick is not None:tail+=' | NCS1 - CPU: %+.1f ms (5 s avg)'%(stick-cpu)
 cv2.putText(canvas,tail,(left,153),cv2.FONT_HERSHEY_SIMPLEX,.4,(190,190,190),1)
 return canvas
try:
 while not stop.is_set():
  raw=sys.stdin.buffer.read(640*480*3)
  if len(raw)!=640*480*3:raise RuntimeError('Camera stream ended; check USB connection')
  frame=np.frombuffer(raw,dtype=np.uint8).reshape(480,640,3).copy()
  for device,(inputs,outputs) in channels.items():
   try:inputs.get_nowait()
   except queue.Empty:pass
   try:inputs.put_nowait((frame.copy(),fid))
   except queue.Full:pass
   while True:
    try:kind,value=outputs.get_nowait()
    except queue.Empty:break
    if kind=='result':
     results[device]=value;history[device].append((value[4],value[1]))
    else:errors[device]=value
  now=time.monotonic()
  for h in history.values():
   while h and now-h[0][0]>30:h.popleft()
  snapshot=results.copy();err=errors.copy()
  fid+=1;panels=[]
  for device in devices:
   data=snapshot.get(device);image=data[0].copy() if data else frame.copy();header=np.zeros((55,640,3),np.uint8)
   label=device+(' | NCS1' if device=='MYRIAD' else '')
   if data:label+=' | %.1f ms | %.1f infer/s | %d people'%(data[1],stats(device,now)[1],data[3]);cv2.putText(header,'result age %.0f ms | frame %d'%((time.monotonic()-data[4])*1000,data[5]),(8,45),cv2.FONT_HERSHEY_SIMPLEX,.45,(180,180,180),1)
   else:label+=' | loading model...'
   cv2.putText(header,label,(8,22),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,255,255),1)
   if device in err:cv2.putText(image,'NCS1 error - reconnect stick and restart',(15,45),cv2.FONT_HERSHEY_SIMPLEX,.65,(0,0,255),2)
   panels.append(np.vstack([header,image]))
  combined=np.vstack([np.hstack(panels),chart(now,640*len(devices))]);cv2.imshow('People detection - CPU / NCS1',combined)
  if cv2.waitKey(1)&255 in (27,ord('q')):break
  if a.seconds and time.monotonic()-started>=a.seconds:break
finally:
 stop.set()
 for proc in processes:
  proc.join(timeout=3)
  if proc.is_alive():proc.terminate();proc.join()
 for inputs,outputs in channels.values():
  inputs.cancel_join_thread();inputs.close();outputs.cancel_join_thread();outputs.close()
 cv2.destroyAllWindows()
 summary={d:dict(inference_ms=r[1],mean_ms_5s=stats(d,now)[0],inferences_per_second_5s=stats(d,now)[1],people=r[3],frame=r[5]) for d,r in results.items()}
 Path('/work/live-status.json').write_text(json.dumps({'frames_captured':fid,'devices':summary,'errors':errors},indent=2));print('LIVE_STATUS',json.dumps(summary),errors,flush=True)
 if errors:raise SystemExit(1)
