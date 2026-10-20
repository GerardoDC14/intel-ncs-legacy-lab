# Recuperar el NCS1 si falla la carga

## Recuperación automática

Si MYRIAD falla antes de producir el primer resultado, el lanzador:

1. Cierra el visor y sus procesos de inferencia.
2. Espera a que termine el contenedor.
3. Solicita un reset USB dirigido al stick.
4. Vuelve a abrir el visor una sola vez.

Durante el proceso, la ventana puede cerrarse y volver a abrirse. Si el segundo intento falla, el lanzador termina con error. La recuperación automática no actúa sobre fallos posteriores al inicio de la inferencia.

## Si el reintento no funciona

1. Cierra cualquier visor que siga abierto con **Q o Esc**.
2. Desconecta el NCS1 y vuelve a conectarlo directamente a USB 3.0.
3. Abre una terminal del escritorio de la NUC y ejecuta:

```bash
cd ~/intel-ncs-legacy-lab
./ncs1/live.sh both
```

## Solicitar un reset manual por software

Cierra antes cualquier proceso que utilice el stick. Desde la carpeta del repositorio:

```bash
sudo python3 scripts/reset-ncs1-usb.py
./ncs1/live.sh both
```

El script rechaza el reset si otro proceso tiene abierto el nodo USB o si hay varias VPUs Movidius conectadas. Está destinado a un único NCS1 identificado: el ID inicial es `03e7:2150`, mientras que el ID arrancado `03e7:f63b` también puede pertenecer a otras generaciones.

Si informa que el dispositivo está ocupado, cierra el proceso indicado antes de volver a intentarlo. No fuerces un reset durante la inferencia.

## Cierre del visor

Cierra con Q o Esc y espera a que termine el comando antes de abrir otra sesión. El visor libera la red ejecutable antes del plugin y espera hasta 20 segundos para cerrar sus procesos. También atiende SIGINT y SIGTERM y bloquea la apertura de otro visor del mismo usuario.

## Alcance técnico

El script utiliza `USBDEVFS_RESET`, que reinicia la comunicación del dispositivo sin garantizar un corte de alimentación VBUS. Algunos bloqueos pueden seguir requiriendo reconexión física. No reinicia el hub ni solicita resets a la cámara, teclado o ratón.

El código de salida 75 indica un fallo de inicialización de MYRIAD y activa el único reintento del lanzador. Una sesión sin resultados del dispositivo no se considera una ejecución correcta. El proceso MYRIAD no sustituye la VPU por CPU.

La opción [`VPU_MYRIAD_FORCE_RESET`](https://github.com/openvinotoolkit/openvino/blob/2020.3.0/inference-engine/include/vpu/myriad_plugin_config.hpp) no está activada porque no ofrece una recuperación consistente en esta configuración. Un corte de alimentación por software requeriría un puerto compatible con control de potencia, como los descritos por [uhubctl](https://github.com/mvp/uhubctl); ese método no forma parte del procedimiento.
