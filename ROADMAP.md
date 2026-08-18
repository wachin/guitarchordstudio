# ROADMAP

Suite de aplicaciones para letras y acordes de guitarra.

---

## chordflow — Editor con autoscroll

Editor de letras con acordes pensado para abrir canciones, transponer acordes y
acompañar ensayos con desplazamiento automático.

### Hecho

- [x] Editor de texto con pestañas.
- [x] Apertura de archivos `.txt`.
- [x] Arrastrar y soltar archivos sobre la ventana.
- [x] Guardado normal.
- [x] Guardar como.
- [x] Guardar seleccionando codificacion y terminador de linea.
- [x] Deteccion de codificacion al abrir archivos.
- [x] Deteccion de terminadores de linea: Windows, Unix y Mac.
- [x] Indicador de codificacion y terminador de linea en la interfaz.
- [x] Lista de archivos recientes con fecha y ruta.
- [x] Titulo de ventana con nombre del archivo activo.
- [x] Marcado de documentos modificados con `*`.
- [x] Advertencia antes de cerrar pestañas o salir si hay cambios sin guardar.
- [x] Nuevo archivo.
- [x] Copiar, pegar, cortar y seleccionar todo.
- [x] Deshacer y rehacer.
- [x] Busqueda dentro del documento.
- [x] Busqueda anterior y siguiente.
- [x] Resaltado de coincidencias de busqueda.
- [x] Opcion de busqueda con mayusculas/minusculas.
- [x] Opcion de busqueda con expresiones regulares.
- [x] Reemplazo dentro del documento.
- [x] Reemplazar todo dentro del documento.
- [x] Panel de busqueda/reemplazo que cambia correctamente entre modo Buscar y modo Reemplazar.
- [x] Busqueda y reemplazo en archivos desde `Editar > Buscar/Reemplazar en archivos...`.
- [x] Busqueda recursiva en carpetas.
- [x] Filtros por patrones de archivo, por ejemplo `*.txt;*.md;*.chord;*.pro`.
- [x] Resultados de busqueda en archivos con archivo, linea, columna y vista previa.
- [x] Doble clic en un resultado para abrir el archivo en la linea encontrada.
- [x] Desplazamiento automatico del texto.
- [x] Pausar desplazamiento.
- [x] Atajo para iniciar/pausar desplazamiento con `Ctrl+Space`.
- [x] Control de velocidad de desplazamiento.
- [x] Guardado de la ultima velocidad seleccionada.
- [x] Configuracion de velocidad maxima.
- [x] Transposicion de acordes por semitonos.
- [x] Conservacion aproximada de espacios al transponer acordes.
- [x] Opcion para usar sostenidos o bemoles al transponer.
- [x] Seleccion y persistencia de fuente.
- [x] Menu `Herramientas > Sinonimos...`.
- [x] Atajo de sinonimos con `Ctrl+F7`.
- [x] Lectura de diccionarios Mythes instalados en el sistema, como `mythes-es`.
- [x] Ventana de sinonimos estilo LibreOffice con palabra actual, idioma, alternativas y reemplazo.
- [x] Reemplazo de la palabra seleccionada usando un sinonimo.
- [x] Dialogo `Acerca de...`.
- [x] Traduccion de dialogos Qt al español cuando esta disponible.

### Pendiente

- [ ] Migrar a modulo empaquetable (`chordflow`).

---

## chordpages — Editor WYSIWYG orientado a paginas

Editor de canciones en texto plano para letras y acordes de guitarra. Su
objetivo es aprovechar pantallas de ordenador mostrando tres paginas por fila,
con comportamiento de escritura estable, paginas reales, margenes configurables
y soporte para archivos `.txt`

**Nota:** En el futuro una vez que el programa fucnione bien tal vez también soporte para: `.pro`, `.cho` y `.chordpro` (como el agregar soporte semantico opcional para ChordPro: directivas, titulos,  comentarios, transpose y bloques).

### Reglas tecnicas no negociables

- [x] El texto fuente debe vivir en una sola cadena interna.
- [x] Las paginas y lineas visuales son una representacion recalculada del texto
      fuente; nunca deben modificar, recortar ni reordenar el texto real.
- [x] Cada `PageLine` debe guardar offsets reales `start_idx` y `end_idx` dentro
      del texto fuente.
- [x] El wrap visual de lineas largas no debe usar `strip`, `rstrip`, `lstrip`
      ni ninguna transformacion que cambie el mapeo entre caracteres visibles y
      posiciones del texto.
- [x] El cursor, la seleccion, los clics y la navegacion por teclado deben usar
      los offsets reales, no indices aproximados por pagina.
- [x] Al pegar o abrir archivos, los saltos de linea deben normalizarse a `\n`.
- [x] Al cambiar margenes, fuente, papel o zoom, el programa debe recalcular la
      vista completa sin perder el texto ni mover el cursor a una posicion
      incorrecta.
- [x] El area util de la pagina debe recortar visualmente el texto para que no
      se dibuje fuera de los margenes.
- [x] No se debe usar un `QTextEdit` con scroll interno para resolver el
      desbordamiento de una pagina. Si el texto no cabe, se crean mas paginas
      visuales.

### Logrado

- [x] Vista 3-up: tres paginas por fila dentro de un scroll vertical general.
- [x] Modelo de texto unico separado del layout visual.
- [x] Paginador propio para dividir texto plano en paginas segun caracteres por
      linea y lineas por pagina.
- [x] Reflujo automatico al cambiar zoom, papel, fuente y margenes.
- [x] Edicion basica: escribir, Enter, Tab, Backspace, Delete.
- [x] Seleccion con mouse y con teclado.
- [x] Copiar, cortar, pegar y seleccionar todo.
- [x] Abrir y guardar archivos de texto.
- [x] Dialogo de fuente.
- [x] Dialogo de margenes en milimetros.
- [x] Cursor corregido para que la escritura no salte hacia la izquierda ni se
      asocie con una linea visual equivocada despues del wrap.
- [x] Paginador corregido para preservar offsets exactos cuando una linea larga
      se parte en varias lineas visuales.
- [x] Seleccion y cursor medidos con el ancho real del texto dibujado, no solo
      con una columna aproximada.
- [x] Los margenes vuelven a funcionar con reflow completo y calculo de
      capacidad desde el area util real.
- [x] Cursor, seleccion y clics recalculados con `QTextLayout`, usando el motor
      de texto de Qt para alinear el cursor como en un editor nativo.
- [x] Navegacion vertical ajustada por posicion X real del cursor, no solo por
      numero de caracter.
- [x] Texto dibujado con `QTextLayout.draw` para que la posicion de letras,
      espacios, tabs y cursor se calcule con el mismo motor.
- [x] Zoom manual agregado: acercar, alejar, zoom 100% y ajuste de tres paginas
      al ancho.
- [x] El zoom escala la fuente junto con la pagina, igual que en LibreOffice.
- [x] Atajos de zoom agregados: `Ctrl++`, `Ctrl+=`, `Ctrl+-` y `Ctrl+0`.
- [x] Barra de herramientas agregada para controles de zoom.
- [x] Ventana principal con acciones de archivo.
- [x] Superficie de edicion de pagina A4 visible.
- [x] Edicion basica de texto a traves de Qt.
- [x] Margenes de pagina en la superficie del editor.
- [x] Presets de margenes: normal, estrecho, moderado, ancho y espejo.
- [x] Margen de medianil y geometria de espaciado de encabezado/pie.
- [x] Modelo de pagina/documento para el motor de maquetacion futuro.
- [x] Soporte de geometria de pagina A4, Carta, Legal, apaisado/vertical y
      personalizado.
- [x] Redimensionamiento dinamico de pagina y marco escribible al cambiar
      maquetacion o zoom.
- [x] Controles de zoom en menu Ver y barra de herramientas.
- [x] Renderizado de fondo, borde y sombra de pagina fisica.
- [x] Vista multi-pagina vertical con scroll continuo y orientaciones mixtas.
- [x] Modos de vista de una y dos paginas.
- [x] El texto fuente cargado se divide en paginas fisicas.
- [x] Geometria de area segura de impresion con visualizacion de margenes no
      imprimibles.
- [x] Capacidad de filas derivada de la geometria de pagina para paginacion
      consciente de la orientacion.
- [x] DOM semantico interno con bloques de cancion y parrafo.
- [x] Guardado/carga del formato inicial `.mchord`.
- [x] Exportacion PDF a traves de la impresion de Qt.
- [x] Seleccion de tema sistema/claro/oscuro.
- [x] Dialogo de preferencias con seleccion de idioma en vivo.
- [x] Borradores de autoguardado para documentos modificados.
- [x] Snapshots de version para historial restaurable de `.mchord`.
- [x] Ayudas de restauracion de snapshots para archivos `.mchord` y `.mchordbook`.
- [x] Copias de seguridad automaticas antes de sobrescribir documentos.
- [x] Descubrimiento de recuperacion de documentos para borradores autoguardados.
- [x] Descubrimiento de recuperacion de cancioneros para borradores de
      `.mchordbook`.
- [x] Dialogo de recuperacion de inicio para borradores de documentos
      autoguardados.
- [x] Snapshots de version de cancionero para historial restaurable de
      `.mchordbook`.
- [x] Analizador ChordPro en Python puro para metadatos, directivas, acordes
      inline y texto tradicional de acordes sobre letras.
- [x] Renderizador monoespaciado de acordes sobre letras con evitacion basica
      de colisiones de acordes.
- [x] Ajuste de renderizador consciente de acordes para columnas estrechas y
      paginacion futura.
- [x] Filas de renderizado ChordPro estructuradas para maquetacion futura de
      pagina, columna y pintura.
- [x] Secciones de cancion semanticas con marcadores explicitos de verso, coro
      y puente.
- [x] Rangos de silabas liricas con adjuncion de acordes para maquetacion
      consciente de musica.
- [x] Paginacion basada en filas que fluye las filas de renderizado a traves de
      una o mas columnas manteniendo juntos los segmentos de acorde/letra.
- [x] Directivas de salto de pagina y columna manual en el motor de maquetacion
      estructurado.
- [x] Carga de traducciones de Qt Linguist con catalogo inicial en ingles y
      espanol.

### Pendiente

- [ ] Agregar pruebas automaticas para `SimplePager`: lineas largas, lineas
      vacias, saltos de pagina, texto con `\r\n`, tabs y seleccion entre
      paginas.
- [ ] Agregar pruebas automaticas de edicion para confirmar que escribir
      caracter por caracter mantiene `caret_idx` y `text` correctos despues de
      cada reflow.
- [ ] Medir el wrap por ancho real en pixeles usando `QTextLayout`/`QFontMetrics`,
      no solo por cantidad aproximada de caracteres.
- [ ] Agregar undo/redo.
- [ ] Agregar busqueda y reemplazo.
- [ ] Agregar impresion/exportacion a PDF respetando las paginas visuales.
- [ ] Guardar preferencias del usuario: papel, margenes, fuente, zoom y ultimo
      directorio usado.

### Instrucciones para futuras versiones

- [ ] Si se cambia el layout, primero comprobar que
      `PageLine.text == source_text[PageLine.start_idx:PageLine.end_idx]` para
      todas las lineas visuales.
- [ ] Si se cambia el wrap, conservar todos los espacios del texto fuente. Los
      espacios son importantes para alinear acordes.
- [ ] Si se cambia el comportamiento del cursor, probar escritura continua,
      Enter, Backspace, Delete, flechas, Home, End, PageUp y PageDown.
- [ ] Si se agrega soporte ChordPro, mantener dos capas separadas: texto fuente
      editable y representacion interpretada. No reemplazar el texto escrito
      por el usuario con una version renderizada.