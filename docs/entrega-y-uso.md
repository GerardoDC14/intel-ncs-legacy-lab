# Entrega y uso del equipo

Para las prácticas de sistemas ciberfísicos se entregarán **tres NUC en total**, identificadas como **ciberfisicos1**, **ciberfisicos2** y **ciberfisicos3**. Cada estudiante que reciba un equipo tendrá una NUC asignada y su número de serie registrado en la entrega.

## Registro de entrega

Completar el registro al asignar cada equipo:

| Equipo | Número de serie de la NUC | Estudiante responsable |
|---|---|---|
| ciberfisicos1 | Por registrar | Por asignar |
| ciberfisicos2 | Por registrar | Por asignar |
| ciberfisicos3 | Por registrar | Por asignar |

Estas son las identificaciones de inventario. Para conectarse por SSH, consulta el nombre configurado en Ubuntu con `hostname` y el usuario con `whoami`; pueden diferir de la etiqueta del equipo.

## Material incluido por estudiante

- Una computadora Intel NUC con su carcasa o case.
- Fuente de alimentación y cable de corriente de la NUC.
- Un módulo de **8 GB de RAM** instalado, confirmado en las tres NUC.
- Una unidad SSD instalada; registrar su capacidad junto con el equipo.
- Un **Intel Movidius Neural Compute Stick de primera generación (NCS1)** para las prácticas de inferencia.

Revisa el estado de la carcasa, los conectores y los accesorios al recibirlos. Transporta y manipula la NUC y el stick con cuidado; evita golpes, tirones de los cables y esfuerzos sobre los puertos USB.

## Acceso al sistema

La contraseña inicial establecida para las tres NUC es:

```text
1234567
```

Cada estudiante puede conservarla o cambiarla. Para cambiar la contraseña de su usuario, ejecutar en una terminal:

```bash
passwd
```

La contraseña publicada es la inicial de entrega; si se cambia, debe utilizarse la nueva también al conectar por SSH o ejecutar comandos con `sudo`.

## Accesorios recomendados

Se recomienda que cada estudiante consiga:

- Un **hub USB con conexión USB-C** para los periféricos.
- Un **cable HDMI** para conectar la NUC a un monitor o pantalla.

El teclado, el ratón y la cámara que se utilicen en la práctica se conectan al hub. Estos accesorios no forman parte del material incluido en la entrega anterior.

## Distribución de conexiones

| Dispositivo | Conexión recomendada |
|---|---|
| NCS1 | Directamente a un puerto USB 3.0 de la NUC |
| Hub de periféricos | Al puerto USB-C de la NUC |
| Teclado, ratón y cámara | A los puertos del hub |
| Monitor o pantalla | A la salida HDMI de la NUC |
| Fuente de alimentación | Al conector de alimentación de la NUC |

Por el tamaño del NCS1, el puerto USB contiguo puede quedar obstruido. Usa el hub USB-C para los demás dispositivos y deja el stick conectado directamente a la NUC. Evita forzar otro conector junto al stick.

## Temperatura y tiempo de uso

Es normal que el NCS1 se caliente durante la inferencia. Ten cuidado al manipularlo después de utilizarlo y deja que se enfríe antes de guardarlo.

Para estas prácticas, **no utilizar el stick durante más de 20 minutos continuos**. Al terminar cada sesión, cierra el visor y haz una pausa para que se enfríe. Este límite es una indicación de uso del equipo de la clase, no una especificación térmica del fabricante.

Si se dispone de enfriamiento adicional, se recomienda dirigir ventilación externa hacia el stick. Mantén también libres las rejillas de ventilación de la NUC.

## Si el modelo no carga

El visor intenta recuperar una inicialización fallida del NCS1 con un reset USB y un único reintento automático. Durante ese proceso, la ventana puede cerrarse y volver a abrirse.

Si el segundo intento falla, cierra el visor, desconecta y reconecta el stick, y vuelve a abrirlo. No abras varios visores al mismo tiempo. El procedimiento y sus límites están en [Recuperación del NCS1](ncs1-recuperacion.md).
