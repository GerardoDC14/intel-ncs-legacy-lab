# Instalación en la segunda NUC

El 19 de octubre de 2026 preparamos una segunda Intel NUC7i3BNK para ejecutar las prácticas con NCS1. Partimos de Ubuntu 24.04.4, kernel `7.0.0-38-generic`, 8 GB de RAM y una instalación sin Git ni Docker.

## Preparación

Habilitamos SSH desde la terminal de la NUC y continuamos la instalación desde otra computadora de la misma red. Los comandos de acceso están en el [README](../README.md#acceso-remoto-por-ssh-opcional).

Instalamos Git, clonamos el repositorio y ejecutamos:

```bash
sudo apt update
sudo apt install git -y
git clone https://github.com/GerardoDC14/intel-ncs-legacy-lab.git
cd intel-ncs-legacy-lab
./scripts/setup-host.sh
./scripts/build-runtime.sh ncs1
./scripts/prepare-mobilenet.sh
```

El primer script instaló Docker, FFmpeg y las herramientas USB/V4L2 y configuró las reglas udev. Los siguientes construyeron el runtime OpenVINO 2020.3.2 y el contenedor de conversión, verificaron los archivos de MobileNet y generaron el IR FP16. Después de cambiar los grupos, cierra sesión y vuelve a entrar; reconecta el stick para aplicar sus permisos USB.

## Comprobación del stick

El dispositivo apareció con ID USB `03e7:2150`, correspondiente al NCS1. Se cargó MobileNet-SSD en CPU y MYRIAD y se ejecutaron 10 inferencias por dispositivo, con 3 calentamientos y entrada sintética. Ambos devolvieron valores finitos y salida `[1, 1, 100, 7]`.

Medianas iniciales: CPU 21.13 ms y NCS1 84.49 ms. La entrada sintética permite comprobar el runtime y el stick antes de conectar una cámara. [Método y resultados](mediciones.md#segunda-nuc-19-de-octubre-de-2026).

## Cámara y escritorio

Conectamos una Logitech HD Webcam C910 (`046d:0821`), cuyo canal de vídeo apareció en `/dev/video0`. La cámara ofrece YUYV a 640 × 480 y 15 fps, compatible con el flujo de FFmpeg del visor.

Encontramos un fallo en la selección automática: con `pipefail`, `grep -q` podía cerrar la tubería antes de que V4L2 terminara de listar los formatos. El lanzador interpretaba esa salida como ausencia de cámara. Se corrigió la comprobación para consumir la salida completa.

La vista doble se abrió desde la sesión gráfica local de la NUC. También instalamos manualmente tres accesos directos en el escritorio: **Deteccion CPU**, **Deteccion NCS1** y **Deteccion CPU y NCS1**. Esos accesos ejecutan `ncs1/live.sh` con `cpu`, `myriad` o `both`; no los crea el script de instalación del anfitrión.

Para abrir desde una terminal del escritorio:

```bash
cd ~/intel-ncs-legacy-lab
./ncs1/live.sh both
```

## Reinicialización y recuperación

Al volver a abrir el visor apareció `NC_ERROR`. La reconexión física recuperó el stick. Después probamos un reset USB dirigido que también permitió ejecutar inferencia, y añadimos liberación explícita del modelo, cierre ordenado y un único reintento automático ante un fallo de carga inicial.

Completamos tres sesiones consecutivas de 10 segundos con ambos dispositivos y sin errores. [Procedimiento y límites de la recuperación](ncs1-recuperacion.md).

En esta segunda NUC se preparó y probó únicamente el NCS1. El estado del NCS2 sigue siendo el de las [pruebas anteriores](ncs2.md).
