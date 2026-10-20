# Recuperación del NCS1

Pruebas realizadas el 19 de octubre de 2026 en la segunda NUC7i3BNK, Ubuntu 24.04.4, kernel 7.0.0-38-generic, NCS1 y cámara Logitech C910. Runtime: OpenVINO 2020.3.2; modelo MobileNet-SSD FP16.

## Qué encontramos

El fallo es intermitente: algunas secuencias de apertura y cierre funcionaban y otras terminaban en `Can not init Myriad device: NC_ERROR`. La ejecución del modelo ya había funcionado, por lo que el fallo observado estaba en la reinicialización del dispositivo.

Probamos `VPU_MYRIAD_FORCE_RESET=YES` mediante `IECore.set_config()`. Esta opción está descrita en el [código de OpenVINO 2020.3](https://github.com/openvinotoolkit/openvino/blob/2020.3.0/inference-engine/include/vpu/myriad_plugin_config.hpp), pero no recuperó el dispositivo de forma consistente en estas pruebas. No la dejamos activada en el visor.

Después de un fallo, un reset dirigido al nodo USB del stick mediante `USBDEVFS_RESET` permitió cargar el modelo y ejecutar 10 inferencias, con 3 iteraciones de calentamiento. Mediana NCS1: 84.26 ms, salida finita de forma `[1, 1, 100, 7]`. La entrada fue un tensor sintético; esta prueba comprueba ejecución, no calidad de detección.

## Cambios en el visor

- Liberación explícita de la red ejecutable antes de destruir el plugin.
- Espera de hasta 20 segundos para cerrar los procesos de inferencia.
- Cierre ordenado del proceso principal al recibir SIGINT o SIGTERM.
- Bloqueo para impedir visores simultáneos del mismo usuario.
- Código de salida 75 cuando MYRIAD falla antes de producir su primer resultado. El lanzador interpreta ese código y solicita un único reset USB y reintento.
- Una sesión sin resultados de alguno de los dispositivos deja de contarse como prueba exitosa.

Con estos cambios completamos tres sesiones consecutivas de 10 segundos con CPU y MYRIAD activos, liberación de recursos y salida 0. Como el fallo también puede desaparecer temporalmente sin cambios, estas pruebas no demuestran que su causa esté eliminada. Falta comprobar estabilidad durante sesiones de clase y después de cierres abruptos.

## Reset dirigido

El lanzador ejecuta el script solo después de cerrar su contenedor. Para usarlo manualmente, cierra antes cualquier proceso que esté usando el stick:

```bash
sudo python3 scripts/reset-ncs1-usb.py
```

El script busca una sola VPU Movidius con ID `2150` o `f63b` y rechaza el reset si otro proceso tiene abierto su nodo USB. El ID `f63b` también puede corresponder a otras generaciones Movidius: usar este procedimiento únicamente con el NCS1 identificado y sin otras VPUs conectadas. No reinicia el hub ni solicita resets a la cámara, teclado o ratón.

Un reset del bus puede recuperar la comunicación sin cortar VBUS. Si el firmware necesita un corte real de alimentación, todavía puede ser necesaria la reconexión física o un puerto con control de alimentación. Esa segunda alternativa depende del hardware, como explica [uhubctl](https://github.com/mvp/uhubctl); no se probó con esta NUC.
