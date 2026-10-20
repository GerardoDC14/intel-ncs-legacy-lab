# Configuración y diagnóstico de NCS2

**Utiliza NCS1 para completar la práctica.** El entorno descrito aquí permite preparar el runtime y revisar la conexión del NCS2, pero tiene una limitación de carga de firmware pendiente de resolver.

## Preparar el entorno

Completa primero la instalación del anfitrión indicada en el [README](../README.md). Desde la carpeta del repositorio:

```bash
./scripts/build-runtime.sh ncs2
./ncs2/run.sh python /work/check_ncs2.py
```

El contenedor utiliza Ubuntu 20.04, Python 3.8, NumPy 1.24.4 y el archivo completo de Intel OpenVINO 2022.3.2. El anfitrión permanece en Ubuntu 24.04.

## Comprobar USB y plugin

```bash
lsusb
```

El NCS2 sin firmware aparece como `03e7:2485`. El comando `check_ncs2.py` informa los plugins disponibles en OpenVINO. Que aparezca `MYRIAD` no confirma que el stick pueda cargar el firmware ni ejecutar inferencia.

## Identificar el fallo de firmware

Al compilar un modelo para MYRIAD puede aparecer:

```text
Failed to find booted device after boot
RuntimeError: Failed to allocate graph: MYRIAD device is not opened.
```

Este fallo ocurre antes de la inferencia. No deben interpretarse los resultados CPU como resultados del NCS2. Cambiar los permisos USB o ejecutar el contenedor como root no constituye una solución confirmada para esta configuración.

Para aislar un fallo de este tipo, comprueba el stick en un sistema conocido como funcional o utiliza otro NCS2 en la misma NUC. La causa puede involucrar dispositivo, conexión USB, firmware, bibliotecas o kernel; el contenedor no sustituye el kernel del anfitrión. Una enumeración a 480 Mb/s antes del arranque no basta para diagnosticar un puerto USB 3 defectuoso.

## Mantener la versión del runtime

Utiliza la revisión indicada en el Dockerfile. OpenVINO [2022.3.0](https://github.com/openvinotoolkit/openvino/releases/tag/2022.3.0) excluye soporte VPU en esa revisión y [2022.3.1](https://github.com/openvinotoolkit/openvino/releases/tag/2022.3.1) lo incorpora; no son intercambiables para este fin. Antes de actualizar el runtime, comprueba que incluya el plugin MYRIAD.

El lanzador normal utiliza un usuario sin privilegios dentro del contenedor, capacidades eliminadas y red deshabilitada. Conserva esta configuración para el uso habitual.
