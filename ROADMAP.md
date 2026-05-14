# ROADMAP

Hoja de ruta para Chord Autoscroll, un editor de letras con acordes pensado para abrir canciones, transponer acordes y acompañar ensayos con desplazamiento automatico.

## Hecho

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

## Proximo

- [ ] Crear `README.md` completo con capturas, instalacion, uso y dependencias.
- [ ] Crear una seccion de instalacion especifica para Debian 12, MX Linux 23, Ubuntu y derivadas.
- [ ] Documentar dependencias: PyQt6, chardet, mythes y paquetes de diccionarios.
- [ ] Añadir archivo `LICENSE` si se va a publicar como GPL 3.
- [ ] Añadir `.gitignore` para evitar subir `__pycache__`, archivos temporales y configuraciones locales.
- [ ] Renombrar `config12.json` a un nombre mas claro, por ejemplo `config.json`.
- [ ] Guardar la configuracion en una ruta de usuario, por ejemplo `~/.config/chord-autoscroll/`.
- [ ] Permitir abrir extensiones utiles ademas de `.txt`, como `.md`, `.pro`, `.chord` y `.cho`.
- [ ] Mostrar errores de busqueda/reemplazo en archivos cuando un archivo no se pudo leer o escribir.
- [ ] Pedir confirmacion antes de hacer reemplazos masivos en archivos.
- [ ] Añadir una vista previa antes de reemplazar en varios archivos.
- [ ] Añadir opcion para cerrar/ocultar el panel de busqueda.
- [ ] Permitir limpiar el resaltado de busqueda.

## Importante Para Un Editor De Letras Y Acordes

- [ ] Deteccion mas robusta de acordes, incluyendo acordes complejos como `Cmaj7`, `F#m7b5`, `G/B`, `Asus4`, `Dadd9`.
- [ ] No transponer texto normal que parezca acorde accidentalmente.
- [ ] Soporte para notacion latina: `Do`, `Re`, `Mi`, `Fa`, `Sol`, `La`, `Si`.
- [ ] Alternar entre notacion inglesa y latina.
- [ ] Transponer canciones completas a una tonalidad destino, no solo por semitonos.
- [ ] Detectar tonalidad probable de la cancion.
- [ ] Insertar acordes de forma alineada sobre la letra.
- [ ] Mantener mejor la alineacion visual despues de transponer acordes de distinto largo.
- [ ] Modo presentacion/ensayo con texto grande y controles minimos.
- [ ] Pantalla completa para escenario.
- [ ] Cuenta regresiva antes de iniciar el autoscroll.
- [ ] Guardar perfiles de velocidad por cancion.
- [ ] Marcadores dentro de la cancion: intro, verso, coro, puente, final.
- [ ] Navegacion rapida entre secciones.
- [ ] Exportar a PDF.
- [ ] Imprimir cancion con acordes.
- [ ] Tema oscuro y tema claro.
- [ ] Atajos configurables por el usuario.
- [ ] Restaurar automaticamente las pestañas abiertas en la sesion anterior.
- [ ] Guardado automatico opcional.
- [ ] Historial de copias de seguridad por archivo.
- [ ] Comparar version actual con version guardada.

## Calidad Y Mantenimiento

- [ ] Separar el codigo en modulos: interfaz, archivos, busqueda, transposicion, sinonimos y configuracion.
- [ ] Añadir pruebas unitarias para la transposicion de acordes.
- [ ] Añadir pruebas unitarias para deteccion de acordes.
- [ ] Añadir pruebas unitarias para lectura de diccionarios Mythes.
- [ ] Añadir pruebas basicas para abrir/guardar con distintas codificaciones.
- [ ] Añadir comprobacion automatica de sintaxis.
- [ ] Revisar conflictos de atajos de teclado.
- [ ] Normalizar nombres de funciones y comentarios.
- [ ] Evitar duplicacion entre `open_file`, `open_dropped_file` y `load_file`.
- [ ] Mejorar el manejo de errores y mostrar mensajes mas claros al usuario.
- [ ] Preparar estructura para empaquetado con `pyproject.toml`.
- [ ] Crear instalador o paquete `.deb`.

## Publicacion En GitHub

- [ ] Elegir el nuevo nombre del proyecto.
- [ ] Revisar que no se suban archivos personales o temporales.
- [ ] Añadir capturas de pantalla.
- [ ] Añadir una descripcion corta del proyecto.
- [ ] Añadir instrucciones de instalacion.
- [ ] Añadir instrucciones de uso.
- [ ] Añadir seccion de atajos de teclado.
- [ ] Añadir seccion de dependencias opcionales, como Mythes para sinonimos.
- [ ] Crear primera version etiquetada, por ejemplo `v0.1.0`.

## Posibles Nombres

- `chord-autoscroll-editor`
- `chordscroll`
- `acordes-autoscroll`
- `letras-y-acordes`
- `song-chord-scroller`
- `chord-reader-editor`
- `cancionero-autoscroll`
- `pychord-scroll`
- `chordflow`
- `acordes-en-vivo`

