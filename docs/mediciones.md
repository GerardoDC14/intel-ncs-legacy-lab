# Método y resultados

## Sesión MobileNet-SSD CPU / NCS1

Fuente: [mobilenet-live.json](../results/mobilenet-live.json), guardada el 30 de septiembre de 2026. Ambos dispositivos estaban activos en la misma sesión; captura 640 × 480 a 15 fps, un proceso por dispositivo, CPU con 2 hilos y un stream. Se capturaron 125 fotogramas. Los valores comparados corresponden a los últimos 5 segundos del visor, no a la media de toda la sesión.

| Dispositivo | Media de inferencia en 5 s (ms) | Resultados recibidos/s en 5 s |
|---|---:|---:|
| CPU | 36.4182 | 14.8 |
| NCS1 / MYRIAD | 83.0147 | 11.2 |

La latencia mide solo `infer()`. La tasa real también está condicionada por captura, resize, dibujo, planificación, colas y recepción de resultados. Por eso no equivale a `1000 / ms`. La CPU está cerca del límite de 15 fps de la cámara; no es una medida de su máximo rendimiento sin captura.

De esta sesión conservamos los promedios finales, por lo que la gráfica del repositorio muestra esos valores. La curva temporal se genera en el visor mientras está funcionando. Ambos dispositivos ejecutaron sin errores; la escena estaba vacía, así que esta prueba solo sirve para comparar rendimiento.

## Benchmark estático retail-0013, OpenVINO 2020.3.2

Fuentes: [CPU](../results/retail-static-CPU.json), [MYRIAD](../results/retail-static-MYRIAD.json). Imagen fija, batch 1, inferencia síncrona, 5 calentamientos, 20 iteraciones; dispositivos ensayados por separado y configuración CPU por defecto. La imagen se preprocesó antes del bucle. Captura, preprocesamiento, carga del modelo y dibujo no están incluidos en la latencia.

| Dispositivo | Mediana (ms) | p95 (ms) |
|---|---:|---:|
| CPU | 28.9878 | 29.1355 |
| NCS1 / MYRIAD | 156.5033 | 157.5699 |

Los JSON de esta prueba conservan mediana y p95. En la gráfica, el rombo marca el p95. El detector no encontró personas por encima del umbral 0.5 en la escena con una persona sentada y parcialmente fuera de cuadro.

## Cuatro modelos CPU, OpenVINO 2022.3.2

Fuente: [CSV](../results/openvino2022-cpu.csv) y JSON `*-CPU.json` con las 64 duraciones por modelo. Batch 1, una solicitud síncrona, 4 hilos CPU, un stream, 10 calentamientos, 64 medidas usando 16 imágenes repetidas cuatro veces. Umbral 0.5. Preprocesamiento BGR y etiqueta persona por modelo.

![Modelos CPU con OpenVINO 2022.3.2](../figures/openvino2022-cpu.svg)

| Modelo | Mediana inferencia (ms) | p95 (ms) | Imágenes con detección / 16 |
|---|---:|---:|---:|
| person-detection-0200 | 8.62 | 8.98 | 2 |
| person-detection-0201 | 18.26 | 18.79 | 2 |
| person-detection-0202 | 33.09 | 33.77 | 8 |
| person-detection-retail-0013 | 28.44 | 29.60 | 0 |

La última columna cuenta las imágenes en las que el modelo produjo una detección. Como no etiquetamos la escena ni revisamos sistemáticamente los falsos positivos y negativos, ese conteo no permite calcular precisión o recall. La persona estaba sentada y parcialmente fuera de cuadro.

`pipeline_*` en los archivos incluye resize, inferencia y filtrado de cajas, pero excluye captura, decodificación, visualización y escritura. `serial_pipeline_fps` es una tasa calculada para ese bucle, no FPS de la cámara. Estos ensayos no incluyen ejecución NCS2.

## Interpretación

La CPU fue más rápida que el NCS1 en ambos ensayos. La comparación es válida entre dispositivos dentro de cada prueba; entre pruebas cambian el modelo, la configuración de hilos y el método. Para evaluar consumo energético, calidad de detección o rendimiento en otros equipos necesitamos mediciones adicionales.

## Cómo repetir las mediciones

1. Usar el mismo modelo, precisión y datos para CPU y MYRIAD; comprobar selección explícita de dispositivo.
2. Registrar equipo, kernel, versiones, cámara, resolución, configuración de hilos, calentamiento e iteraciones.
3. Separar carga del modelo, inferencia, pipeline y captura. Guardar muestras individuales antes de calcular mediana y p95.
4. Para evaluar detección, obtener escenas etiquetadas con personas sentadas, de pie y ocluidas. Medir calidad aparte de velocidad.
5. Si se estudia consumo, incorporar una medición eléctrica y energía por inferencia; no inferirla a partir de latencia.

Con `ncs1/work/benchmark.py` puedes usar una imagen propia y guardar el tiempo de cada inferencia. Los resultados de este repositorio corresponden a las pruebas realizadas en la NUC. Revisamos la sintaxis de los scripts de instalación, pero todavía falta repetir todo el proceso en una segunda instalación limpia.
