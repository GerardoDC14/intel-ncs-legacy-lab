# Pruebas con NCS2

## Preparación y pruebas

1. Partimos de una instalación limpia de Ubuntu 24.04 y habilitamos SSH con `sudo apt install openssh-server`.
2. Se planteó un entorno Python aislado. Como MYRIAD necesita componentes nativos y firmware antiguos, se preparó un contenedor Ubuntu 20.04, Python 3.8 y NumPy 1.24.4.
3. Se usó el archivo completo Intel OpenVINO 2022.3.2. El paquete PyPI ensayado no aportó el plugin MYRIAD necesario en ese entorno.
4. Se configuraron permisos udev y paso de dispositivos USB; Docker mantiene visible `/dev/bus/usb`, incluidos dispositivos que cambian durante el boot.
5. OpenVINO enumeró CPU, GNA y MYRIAD. El USB NCS2 `03e7:2485` era visible. Se ejecutaron modelos en CPU, pero la compilación explícita para MYRIAD falló durante el arranque.
6. Se probaron las variantes de la tabla, sin conseguir una inferencia NCS2. Se conservó este entorno y se pasó al NCS1.

| Variante ensayada | Resultado observado |
|---|---|
| OpenVINO 2022.3.2, usuario del contenedor y permisos USB | Falla al abrir / arrancar MYRIAD |
| Red del anfitrión y montaje udev | Persiste el fallo |
| Contenedor privilegiado/root, solo diagnóstico | Persiste el fallo |
| libusb 1.0.27 compilada sin udev | Persiste el fallo |
| OpenVINO 2022.3.1 separado | Persiste el fallo |
| Reconexión física directa a USB 3 | Sin inferencia exitosa en los ensayos guardados |

El lanzador público conserva el modo normal sin privilegios completos, con capacidades eliminadas y red deshabilitada. El acceso privilegiado se usó únicamente para comprobar si el fallo dependía de los permisos USB.

## Qué sabemos y qué falta

El fallo aparece durante la **carga del firmware y la apertura del dispositivo**, antes de ejecutar inferencia. El mensaje está en [ncs2-failure.txt](../results/ncs2-failure.txt).

No se ha determinado si la causa corresponde al stick, la conexión USB, firmware, bibliotecas o interacción con el kernel del anfitrión. Ver 480 Mb/s en el dispositivo sin arrancar no demuestra por sí solo que el puerto USB 3 esté averiado. El contenedor no reemplaza el kernel.

Para aislar el problema falta probar este NCS2 en una máquina y sistema conocidos como funcionales, o probar otro NCS2 en esta NUC. Estas pruebas siguen pendientes.

## Versión del runtime

La versión concreta de OpenVINO importa: [2022.3.0](https://github.com/openvinotoolkit/openvino/releases/tag/2022.3.0) anunció que los productos VPU no estaban soportados en esa revisión; [2022.3.1](https://github.com/openvinotoolkit/openvino/releases/tag/2022.3.1) anunció su soporte. El laboratorio utilizó 2022.3.2 y también ensayó 2022.3.1. Por esa diferencia usamos las revisiones posteriores.

Antes de cambiar la versión del runtime, revisa que incluya el plugin MYRIAD. El entorno descrito usa versiones antiguas dentro de un contenedor; Ubuntu 24.04 es el sistema anfitrión.
