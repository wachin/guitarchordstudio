# Chord Autoscroll

Editor de letras con acordes para guitarristas, cantantes y músicos que trabajan con canciones en archivos de texto. Permite abrir canciones, transponer acordes, desplazarse automáticamente durante el ensayo, buscar y reemplazar texto, buscar en varios archivos y consultar sinónimos usando diccionarios Mythes instalados en Linux.

El programa está pensado para Debian 12, MX Linux 23, antiX 23 y distribuciones derivadas.

## Características

- Editor de texto con pestañas.
- Apertura de archivos `.txt`.
- Arrastrar y soltar archivos sobre la ventana.
- Guardado normal, `Guardar como...` y guardado con codificación elegida.
- Detección de codificación y terminadores de línea.
- Lista de archivos recientes.
- Desplazamiento automático para ensayos.
- Control de velocidad del desplazamiento.
- Transposición de acordes por semitonos.
- Opción para usar sostenidos o bemoles.
- Búsqueda y reemplazo dentro del documento.
- Búsqueda y reemplazo en archivos desde `Editar > Buscar/Reemplazar en archivos...`.
- Sinónimos desde `Herramientas > Sinónimos...`, usando diccionarios Mythes como `mythes-es`.
- Selección de fuente.
- Atajos de teclado para las acciones principales.

## Sistemas Probados

- Debian 12 de 32 bits.
- MX Linux 23 de 32 y 64 bits.

## Instalación De Dependencias

En Debian 12, MX Linux 23, antiX 23 y derivados, instala las dependencias con:

```bash
sudo apt-get update
sudo apt-get install python3 python3-pyqt6 python3-chardet \
    qt6-translations-l10n fonts-noto-mono mythes mythes-es
```

Para tener sinónimos en otro idioma, instala el paquete Mythes correspondiente. Por ejemplo:

```bash
sudo apt-get install mythes-de
```

## Ejecutar El Programa

Desde la carpeta del proyecto:

```bash
python3 chord_autoscroll.py
```

También puedes ejecutarlo desde un gestor de archivos si tu distribución tiene una opción para lanzar scripts de Python.

![Lanzando Chord Autoscroll](src/vx_images/01-lanzando-chord_autoscroll.py.webp)

## Uso Básico

### Abrir Canciones

Puedes abrir canciones de dos formas:

- Arrastrando un archivo `.txt` sobre la ventana.
- Usando `Archivo > Abrir`.

El proyecto incluye canciones de ejemplo en la carpeta `Ejemplo/`.

### Transponer Acordes

Usa el botón `Transponer` para subir o bajar semitonos. Esto sirve para adaptar una canción a tu voz o a la afinación del instrumento.

En `Opciones` puedes elegir si la transposición usará sostenidos o bemoles.

### Desplazamiento Automático

El programa puede desplazar la letra automáticamente mientras tocas o cantas.

- `Iniciar`: empieza el desplazamiento.
- `Pausar`: detiene el desplazamiento.
- Control de velocidad: ajusta qué tan rápido avanza el texto.
- `Opciones > Cambiar velocidad máxima`: cambia el rango de velocidad disponible.

### Buscar Y Reemplazar

En el menú `Editar` tienes:

- `Buscar`: muestra el panel de búsqueda.
- `Reemplazar`: muestra el panel de búsqueda y reemplazo.
- `Buscar/Reemplazar en archivos...`: busca o reemplaza texto en varios archivos de una carpeta.

La búsqueda permite coincidencia de mayúsculas/minúsculas y expresiones regulares.

### Sinónimos

Si tienes instalados paquetes como `mythes` y `mythes-es`, puedes seleccionar una palabra y usar:

```text
Herramientas > Sinónimos...
```

o el atajo:

```text
Ctrl+F7
```

Se abrirá una ventana similar a la de LibreOffice, con alternativas y un campo para reemplazar la palabra seleccionada.

### Cambiar Fuente

En `Opciones > Cambiar fuente` puedes elegir la fuente del editor. Se recomienda una fuente monoespaciada para mantener alineados los acordes con la letra. Por defecto se usa `Noto Mono`.

## Guardado De Archivos

El menú `Archivo` incluye tres opciones de guardado:

### Guardar

Guarda el archivo usando la misma codificación y el mismo terminador de línea detectados al abrirlo.

### Guardar Como...

Guarda el archivo en otra ubicación conservando la codificación y el terminador de línea originales.

### Guardar Codificación Como...

Permite elegir codificación y terminador de línea antes de guardar.

Codificaciones disponibles:

- UTF-8
- UTF-16 LE
- UTF-16 BE
- UTF-8 con BOM
- ANSI
- ISO-8859-1

Terminadores de línea disponibles:

- Windows (CRLF)
- Unix (LF)
- Mac (CR)

## Atajos De Teclado

| Función | Atajo |
| --- | --- |
| Nuevo archivo | `Ctrl+N` |
| Abrir archivo | `Ctrl+O` |
| Guardar archivo | `Ctrl+S` |
| Guardar como | `Ctrl+Shift+S` |
| Salir | `Ctrl+Q` |
| Buscar | `Ctrl+F` |
| Buscar/Reemplazar en archivos | `Ctrl+Shift+F` |
| Sinónimos | `Ctrl+F7` |
| Seleccionar todo | `Ctrl+A` |
| Cambiar fuente | `Ctrl+Alt+F` |
| Cambiar velocidad máxima | `Ctrl+Shift+V` |
| Acerca de | `Ctrl+H` |
| Deshacer | `Ctrl+Z` |
| Rehacer | `Ctrl+Shift+Z` |
| Iniciar/Pausar desplazamiento | `Ctrl+Barra espaciadora` |

## Cancionero Recomendado

También puedes usar este programa con el cancionero de letras y acordes disponible en:

[https://github.com/wachin/Cancionero](https://github.com/wachin/Cancionero)

![Descargar cancionero](src/vx_images/03-descarga-mi-cancionero-de-canciones-con-acordes-de-guitarra.webp)

Las canciones están en la carpeta:

```text
Acordes de Guitarra para celular (63x110mm)
```

## Fuentes Tipográficas

Para editar canciones con acordes, conviene usar fuentes monoespaciadas. Algunas recomendaciones:

- Noto Mono
- Consolas
- Iosevka
- Liberation Mono
- DejaVu Sans Mono

Artículos relacionados:

- [Instalar fuentes tipográficas de Windows en Linux](https://facilitarelsoftwarelibre.blogspot.com/2018/11/instalar-fuentes-de-windows-en.html)
- [Cómo instalar fuentes tipográficas descargadas desde Internet en Linux](https://facilitarelsoftwarelibre.blogspot.com/2021/01/como-instalar-fuentes-tipograficas-en-linux.html)
- [Fuentes monoespaciadas en WPS Office no están alineadas](https://facilitarelsoftwarelibre.blogspot.com/2022/05/problema-con-las-fuentes-monoespaciadas.html)

## Notas Sobre Las Dependencias

- `python3`: intérprete necesario para ejecutar el programa.
- `python3-pyqt6`: biblioteca gráfica usada para la interfaz.
- `python3-chardet`: detección automática de codificación de archivos.
- `qt6-translations-l10n`: traducciones de diálogos Qt al español y otros idiomas.
- `fonts-noto-mono`: fuente monoespaciada recomendada.
- `mythes`: soporte base para diccionarios de sinónimos.
- `mythes-es`: diccionario de sinónimos en español.

## Hoja De Ruta

Consulta [ROADMAP.md](ROADMAP.md) para ver lo que ya está implementado y las ideas previstas para futuras versiones.

## Licencia

El programa está pensado para publicarse bajo GPL 3.

Que Dios les bendiga.
