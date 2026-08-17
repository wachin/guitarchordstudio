# GuitarChordStudio

Este repositorio puede organizarse como una suite con varias aplicaciones, de
forma parecida a WPS Office. Ahora mismo incluye:

- `chordflow`: editor de letras con acordes y autoscroll.
- `chordpages`: editor WYSIWYG orientado a páginas, con diseño de página real,
  márgenes configurables y soporte multi-página.

## Ejecutar Las Aplicaciones

Desde la raíz del repositorio:

```bash
python3 -m chordflow
python3 -m chordpages
```

Si instalas el proyecto como paquete Python, quedarán dos lanzadores:

```bash
chordflow
chordpages
```

---

# Aplicación ChordFlow

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
python3 -m chordflow
```

También puedes ejecutarlo desde un gestor de archivos si tu distribución tiene una opción para lanzar scripts de Python.


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

| Función  | Atajo |
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
- `python3-pyqt6`: biblioteca gráfica que provee la interfaz de usuario
  (ventanas, botones, menús, editor de texto, diálogos de archivo, etc.).
- `python3-chardet`: detecta automáticamente la codificación de un archivo de
  texto al abrirlo (UTF-8, ISO-8859-1, Windows-1252, etc.). Sin esta librería,
  el usuario tendría que especificar la codificación manualmente cada vez que
  abre un archivo, y los archivos creados en Windows (ANSI, UTF-8 con BOM) o
  macOS (Mac Roman) no se abrirían correctamente. También se usa en la función
  "Buscar/Reemplazar en archivos" para leer archivos con cualquier codificación
  dentro de una carpeta.
- `qt6-translations-l10n`: traducciones de los diálogos nativos de Qt al
  español y otros idiomas. Por ejemplo, los botones "Abrir", "Guardar",
  "Cancelar" en los cuadros de diálogo de archivos aparecen en español cuando
  el sistema está configurado en ese idioma.
- `fonts-noto-mono`: fuente monoespaciada recomendada por defecto para el
  editor. Las fuentes monoespaciadas mantienen los acordes alineados
  verticalmente con la letra, lo cual es esencial para que las canciones se
  vean correctamente.
- `mythes`: soporte base para diccionarios de sinónimos (thesaurus). El programa
  usa los diccionarios Mythes instalados en el sistema (los mismos que usa
  LibreOffice) para ofrecer sinónimos de palabras. Sin este paquete, la opción
  "Sinónimos..." del menú Herramientas no tendría diccionarios que cargar.
- `mythes-es`: diccionario de sinónimos en español para el thesaurus Mythes.
  Permite buscar sinónimos en español desde el menú `Herramientas > Sinónimos...`.
  Para otros idiomas se pueden instalar paquetes como `mythes-de` (alemán),
  `mythes-en` (inglés), etc.

---

# Aplicación ChordPages

ChordPages es un editor WYSIWYG orientado a páginas para canciones con letras y
acordes de guitarra. A diferencia de `chordflow`, que muestra el texto en una
sola vista desplazable, ChordPages organiza el contenido en páginas reales
(como A4 o Carta) que se ven en pantalla tal como se imprimirían.

El programa está diseñado para compositores, arreglistas y músicos que prefieren
trabajar con un diseño de página real, márgenes configurables y una vista
multi-página.

## Características

- Edición WYSIWYG en páginas reales con fondo, borde y sombra.
- Vista 3-up: tres páginas por fila dentro de un scroll vertical general.
- Modos de vista: una página, dos páginas, y tres páginas por fila.
- Márgenes configurables en milímetros con presets (normal, estrecho, moderado, ancho, espejo).
- Soporte de tamaño de página: A4, Carta, Legal, apaisado/vertical y tamaño personalizado.
- Zoom: acercar, alejar, 100%, ajustar al ancho y ajustar a la página.
- Edición básica: escribir, Enter, Tab, Backspace, Delete, selección con mouse y teclado.
- Copiar, cortar, pegar y seleccionar todo.
- Abrir y guardar archivos en formato `.mchord` y texto plano.
- Exportación a PDF a través del sistema de impresión de Qt.
- Paginador propio que divide el texto en páginas según caracteres por línea y líneas por página.
- Reflujo automático al cambiar zoom, papel, fuente y márgenes.
- Cursor medido con `QTextLayout` para alineación precisa como en un editor nativo.
- Tema de aplicación: sistema, claro y oscuro.
- Diálogo de preferencias con selección de idioma en vivo.
- Autoguardado en segundo plano para recuperación ante fallos.
- Copias de seguridad automáticas antes de sobrescribir documentos.
- Diálogo de recuperación al inicio si hay borradores sin guardar.
- Snapshots de versión para historial restaurable de `.mchord`.
- Traducciones al español e inglés mediante Qt Linguist.
- Soporte para arrastrar y soltar archivos.

## Sistemas Probados

- Debian 12 / MX Linux 23 de 64 bits.
- Windows (con Python 3.11+ y PyQt6).
- macOS (con Python 3.11+ y PyQt6).

## Instalación De Dependencias

### Debian / MX Linux

```bash
sudo apt-get update
sudo apt-get install python3 python3-pyqt6 \
    qt6-translations-l10n
```

### Windows

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install PyQt6 pytest
```

### macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install PyQt6 pytest
```

## Ejecutar El Programa

```bash
python3 -m chordpages
```

## Ejecutar Las Pruebas

```bash
pytest -q chordpages/tests/
```

## Flujo De Trabajo De Traducciones

ChordPages mantiene archivos de traducción Qt Linguist en `chordpages/translations/`.
Al iniciar, carga `chordpages_<locale>.qm` con `QTranslator`.

Actualizar los archivos de traducción después de cambiar cadenas visibles:

```bash
pylupdate6 chordpages/ --ts chordpages/translations/chordpages_es.ts
pylupdate6 chordpages/ --ts chordpages/translations/chordpages_en.ts
```

Editar con Qt Linguist y compilar:

```bash
linguist-qt6 chordpages/translations/chordpages_es.ts
lrelease chordpages/translations/chordpages_es.ts -qm chordpages/translations/chordpages_es.qm
lrelease chordpages/translations/chordpages_en.ts -qm chordpages/translations/chordpages_en.qm
```

---

## Dependencias de desarrollo

Estos paquetes solo son necesarios si vas a ejecutar las pruebas o trabajar
con traducciones. No se requieren para ejecutar las aplicaciones.

### Debian / MX Linux

```bash
sudo apt-get install python3-pytest python3-pytest-qt \
    pyqt6-dev-tools qt6-l10n-tools
```

- `python3-pytest`: ejecutor de pruebas. Necesario para correr la suite de
  tests con `pytest`.
- `python3-pytest-qt`: proporciona el fixture `qtbot` para crear y manipular
  widgets de Qt durante las pruebas (abrir ventanas, hacer clic, escribir
  texto, etc.). Sin este paquete no se pueden ejecutar los tests que
  interactúan con la interfaz gráfica.
- `pyqt6-dev-tools`: provee `pylupdate6`, la herramienta que extrae cadenas
  traducibles del código fuente para generar los archivos `.ts` de Qt Linguist.
- `qt6-l10n-tools`: provee `linguist-qt6` (editor visual de traducciones) y
  `lrelease` (compilador de `.ts` a `.qm`). Se usan en el flujo de trabajo de
  traducciones.

### Windows / macOS

```bash
pip install pytest pytest-qt
```

---

## Hoja De Ruta

Consulta [ROADMAP.md](ROADMAP.md) para ver lo que ya está implementado y las
ideas previstas para futuras versiones de ambas aplicaciones.

## Licencia

Los programas están pensados para publicarse bajo GPL 3.

Que Dios les bendiga.