# Modelos y conversión

## MobileNet-SSD actual

Fuente original: https://github.com/chuanqi305/MobileNet-SSD
Revisión fijada en el descargador: `bb17b6c3eef36d80be441ae8e5339be66e8e3b7a`.

| Archivo original | SHA256 |
|---|---|
| `mobilenet_iter_73000.caffemodel` | `52eed8be80522c152a17fb56740de705b79881bde1a167e0e747310523685fc7` |
| `deploy.prototxt` | `2d180f723b3109e21f8287f6b3c691390d07b60eed998327cd3259ffa0e50608` |

Estos pesos contienen capas BatchNorm y Scale y requieren el prototxt de la misma revisión. El archivo antiguo de [OMZ 2020.3](https://github.com/openvinotoolkit/open_model_zoo/blob/2020.3/models/public/mobilenet-ssd/model.yml) usa otra estructura; mezclar su prototxt con estos pesos produce errores de conversión.

Conversión: Model Optimizer del archivo de desarrollo Intel `l_openvino_toolkit_dev_ubuntu18_p_2020.3.355.tgz`, Python 3.6, networkx 2.5, NumPy 1.19.5, protobuf 3.6.1 y defusedxml 0.6.0 en una imagen de conversión separada. La conversión se realiza en un contenedor separado del visor. Se produce IR versión 10, FP16, entrada `[1,3,300,300]`; media y escala 127.5 integradas. Inferencia CPU y NCS1 comprobadas.

## Retail-0013 anterior

[Manifiesto oficial OMZ 2020.3](https://raw.githubusercontent.com/openvinotoolkit/open_model_zoo/2020.3/models/intel/person-detection-retail-0013/model.yml). Se descargaron XML/BIN FP16 de esa generación y se verificaron sus hashes. Clase persona 1. El benchmark estático de `results/retail-static-*.json` corresponde a ese IR, no al de OMZ 2022.3.

Para repetir la prueba, descarga la pareja XML/BIN indicada por el manifiesto, verifica sus hashes y colócala en `ncs1/work/models/` con nombre `person-detection-retail-0013`. Después:

```bash
./ncs1/live.sh both --model person-detection-retail-0013 --threshold 0.5
./ncs1/run.sh python3 /work/benchmark.py --device CPU --model person-detection-retail-0013 --image /work/input.jpg
./ncs1/run.sh python3 /work/benchmark.py --device MYRIAD --model person-detection-retail-0013 --image /work/input.jpg
```

Coloca la imagen que quieras probar en `ncs1/work/input.jpg`. Los tiempos dependerán de tu equipo y de las condiciones de ejecución.

## Ensayos CPU con OpenVINO 2022.3.2

Se descargaron los Intel `person-detection-0200`, `0201`, `0202` y `person-detection-retail-0013` FP16 desde OMZ 2022.3. Los hashes XML/BIN se verificaron contra los manifiestos oficiales de esa revisión. Los resultados numéricos están en `results/`.

Manifiestos: `https://raw.githubusercontent.com/openvinotoolkit/open_model_zoo/2022.3.0/models/intel/<nombre>/model.yml`. Descarga esos archivos en `ncs2/work/models/<nombre>/` y coloca las imágenes de prueba en `ncs2/work/captures/`. Después ejecuta:

```bash
./ncs2/run.sh python /work/benchmark_people.py --model person-detection-0202 --device CPU --capture-dir /work/captures --iterations 64
```

Usa un IR compatible con la versión del runtime. Además de ejecutar en CPU, un modelo debe tener operaciones y requisitos de memoria compatibles con la VPU. Todavía no hemos probado otros detectores, como YOLO, en el stick.
