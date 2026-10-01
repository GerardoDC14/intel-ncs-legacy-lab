"""Regenerate figures from committed numeric measurements; no camera data."""
import csv
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'figures';OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none','svg.hashsalt':'intel-ncs-legacy-lab'})
COLORS=['#2676b8','#279b66']
def save(fig,name):
 for ext in ['svg','png']:
  path=OUT/(name+'.'+ext)
  fig.savefig(path,dpi=180,facecolor='white',**({'metadata':{'Date':None}} if ext=='svg' else {}))
  if ext=='svg':path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')
 plt.close(fig)
def bars(ax,values,xlabel):
 ax.barh(['CPU','NCS1 / MYRIAD'],values,color=COLORS,height=.48)
 ax.invert_yaxis();ax.set_xlim(0,max(values)*1.24);ax.set_xlabel(xlabel)
 ax.xaxis.grid(True,alpha=.18);ax.set_axisbelow(True)
 for i,v in enumerate(values):ax.text(v+max(values)*.025,i,f'{v:.2f}',va='center',fontweight='bold')
live=json.loads((ROOT/'results/mobilenet-live.json').read_text())['devices']
fig,axes=plt.subplots(1,2,figsize=(11,3.8));fig.subplots_adjust(left=.13,right=.97,bottom=.30,top=.70,wspace=.55)
fig.suptitle('MobileNet-SSD: CPU frente a NCS1',fontsize=17,fontweight='bold',y=.96)
for ax,key,label in zip(axes,['mean_ms_5s','inferences_per_second_5s'],['Latencia media de inferencia (ms) ↓','Inferencias recibidas por segundo ↑']):
 bars(ax,[live[d][key] for d in ['CPU','MYRIAD']],label)
fig.text(.13,.08,'Últimos 5 s de una sesión conjunta · CPU: 2 hilos · Cámara: 640 × 480, 15 fps\nOpenVINO 2020.3.2 · NUC i3-7100U · 30/09/2026 · Sin evaluación de exactitud',fontsize=10,color='#555555')
save(fig,'mobilenet-live')
static=[json.loads((ROOT/f'results/retail-static-{d}.json').read_text()) for d in ['CPU','MYRIAD']]
fig,ax=plt.subplots(figsize=(9,3.8));fig.subplots_adjust(left=.20,right=.96,bottom=.31,top=.75)
fig.suptitle('Retail-0013: inferencia sobre una imagen fija',fontsize=16,fontweight='bold',y=.96)
bars(ax,[r['median_ms'] for r in static],'Latencia de inferencia (ms) ↓')
ax.scatter([r['p95_ms'] for r in static],[0,1],marker='D',c='#333333',s=30,label='p95 reportado',zorder=3);ax.legend(loc='lower left',bbox_to_anchor=(0,1.02),frameon=False,borderaxespad=0)
fig.text(.20,.08,'Barras: mediana · Dispositivos ensayados por separado · 5 calentamientos + 20 medidas\nBatch 1, síncrono · OpenVINO 2020.3.2 · Excluye captura y preprocesamiento',fontsize=10,color='#555555')
save(fig,'retail-static')
with (ROOT/'results/openvino2022-cpu.csv').open() as f:rows=list(csv.DictReader(f))
fig,ax=plt.subplots(figsize=(10,4.5));fig.subplots_adjust(left=.38,right=.96,bottom=.25,top=.80)
fig.suptitle('Modelos de detección: benchmark CPU',fontsize=16,fontweight='bold',y=.96)
values=[float(r['inference_median_ms']) for r in rows]
ax.barh([r['model'] for r in rows],values,color='#2676b8',height=.52);ax.invert_yaxis();ax.set_xlim(0,max(values)*1.22);ax.set_xlabel('Latencia de inferencia (ms) ↓');ax.xaxis.grid(True,alpha=.18);ax.set_axisbelow(True)
ax.scatter([float(r['inference_p95_ms']) for r in rows],range(len(rows)),marker='D',s=28,c='#333333',label='p95 reportado',zorder=3);ax.legend(loc='lower left',bbox_to_anchor=(0,1.02),frameon=False,borderaxespad=0)
for i,v in enumerate(values):ax.text(max(v,float(rows[i]['inference_p95_ms']))+.5,i,f'{v:.2f}',va='center',fontweight='bold')
fig.text(.08,.06,'Barras: mediana · OpenVINO 2022.3.2 · CPU: 4 hilos · 16 imágenes, 64 medidas, 10 calentamientos\nBatch 1, síncrono · Excluye captura y preprocesamiento · No representa inferencia NCS2',fontsize=10,color='#555555')
save(fig,'openvino2022-cpu')
print('Generated 3 figures as SVG and PNG from results/')
