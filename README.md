# Monitor de Facturas PDF

Script en Python para monitorear automáticamente una carpeta, extraer
datos desde facturas electrónicas en PDF y enviarlas a una impresora
térmica por puerto serial.

------------------------------------------------------------------------

## Descripción

El programa observa la carpeta:

Desktop/Facturas

Cuando detecta nuevos archivos PDF:

1.  Solicita confirmación para procesarlos.
2.  Extrae los datos principales de la factura (emisor, receptor,
    productos y totales).
3.  Formatea la información.
4.  La envía a impresión por conexión serial.

Pensado para facturas electrónicas chilenas con estructura estándar.

------------------------------------------------------------------------

## Requisitos

-   Python 3.x
-   pymupdf
-   watchdog
-   pyserial

Instalación de dependencias:

pip install pymupdf watchdog pyserial

------------------------------------------------------------------------

## Uso

Ejecutar el script:

python nombre_del_script.py

El monitor quedará activo hasta detenerlo con:

Ctrl + C

------------------------------------------------------------------------

## Notas

-   La impresora se detecta por HWID configurado en el código.
-   La carpeta Facturas se crea automáticamente si no existe.
-   El formato de extracción depende de la estructura del PDF.
