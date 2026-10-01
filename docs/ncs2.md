# NCS2: proceso y punto de detención

## Camino seguido

1. Ubuntu 24.04 recién instalado; se habilitó acceso SSH (`sudo apt install openssh-server`). Para otros equipos usar su usuario y nombre de host; no se incluye la autenticación del laboratorio.
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

El lanzador público conserva el modo normal sin privilegios completos, con capacidades eliminadas y red deshabilitada. Las variantes anteriores son evidencia histórica; no se automatiza la ejecución privilegiada como configuración habitual.

## Qué sabemos y qué falta

El punto de detención es **carga de firmware / apertura del dispositivo**, antes de obtener tiempos de inferencia. [Extracto del error](../results/ncs2-failure.txt). No se atribuyen mediciones CPU al NCS2.

No se ha determinado si la causa corresponde al stick, la conexión USB, firmware, bibliotecas o interacción con el kernel del anfitrión. Ver 480 Mb/s en el dispositivo sin arrancar no demuestra por sí solo que el puerto USB 3 esté averiado. El contenedor no reemplaza el kernel.

El siguiente ensayo que permitiría aislar el problema sería probar este NCS2 en una máquina y sistema conocidos como funcionales, o probar otro NCS2 en esta NUC. Ambos están pendientes, al igual que la inferencia NCS2 y cualquier comparación energética.

## Versión del runtime

Las revisiones importan: [2022.3.0](https://github.com/openvinotoolkit/openvino/releases/tag/2022.3.0) anunció que los productos VPU no estaban soportados en esa revisión; [2022.3.1](https://github.com/openvinotoolkit/openvino/releases/tag/2022.3.1) anunció su soporte. El laboratorio utilizó 2022.3.2 y también ensayó 2022.3.1. No sustituirlas por 2022.3.0 suponiendo equivalencia.

No actualizar el runtime de este laboratorio sin verificar específicamente la disponibilidad de MYRIAD. Esta guía documenta versiones históricas, no promete soporte actual del fabricante para Ubuntu 24.04.
