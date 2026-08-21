# Manual de GitHub Actions y releases manuales

Esta guía explica cómo utilizar GitHub Actions en `pyqt6-linguistic-tools` sin
activar ejecuciones automáticas ni acumular innecesariamente artefactos,
cachés, minutos de ejecución o notificaciones por correo.

## Política de este proyecto

- Ningún workflow debe ejecutarse con un `push`, pull request, tag o calendario.
- Todos los workflows utilizan únicamente `workflow_dispatch` y necesitan que
  una persona pulse **Run workflow**.
- Subir informes como artefactos es opcional y está desactivado por defecto.
- Los artefactos solicitados expresamente se conservan durante tres días.
- No existe actualmente un workflow que publique releases.
- Cualquier release futuro también deberá iniciarse y publicarse manualmente.

Estas reglas están documentadas además en los archivos `AGENTS.md` para impedir
que un agente de desarrollo vuelva a añadir disparadores automáticos.

## Repositorio que contiene los workflows

Los workflows no pertenecen directamente al repositorio principal
`guitarchordstudio`. Están dentro de su submódulo independiente:

```text
guitarchordstudio/
└── libs/
    └── pyqt6-linguistic-tools/
        └── .github/
            └── workflows/
                ├── ci.yml
                └── corpus.yml
```

Por eso, para ejecutar las pruebas en GitHub hay que entrar al repositorio
`wachin/pyqt6-linguistic-tools`, no a la página de Actions del repositorio
principal.

## Requisitos para ejecutar manualmente un workflow

- El archivo del workflow debe estar presente en la rama predeterminada.
- La cuenta debe tener permiso de escritura en el repositorio.
- GitHub Actions debe permanecer habilitado en la configuración del
  repositorio.

El evento `workflow_dispatch` permite iniciar el workflow desde la interfaz
web, GitHub CLI o la API. Para el uso normal se recomienda la interfaz web.

## Ejecutar manualmente las pruebas rápidas

El workflow **Fast CI** comprueba Linux, Windows, macOS, Python 3.10/3.14,
tipado estático y diccionarios instalados en Ubuntu. Ejecuta varios trabajos y
por ello debe utilizarse únicamente cuando sea necesario.

1. Abre el repositorio `wachin/pyqt6-linguistic-tools` en GitHub.
2. Pulsa la pestaña **Actions**.
3. En la barra lateral, selecciona **Fast CI**.
4. Pulsa **Run workflow**.
5. Selecciona la rama `main`.
6. Pulsa nuevamente el botón verde **Run workflow**.
7. Espera a que aparezca la ejecución y entra en ella para revisar cada trabajo.

Crear commits o hacer `git push` no ejecutará este workflow.

## Ejecutar manualmente las pruebas de diccionarios

El workflow **LibreOffice corpus** ofrece dos modalidades:

- `curated`: prueba una selección representativa en Linux, Windows y macOS.
- `full`: prueba el corpus completo en Ubuntu y puede consumir bastante tiempo
  y memoria.

Para ejecutarlo:

1. Abre `wachin/pyqt6-linguistic-tools` en GitHub.
2. Entra en **Actions**.
3. Selecciona **LibreOffice corpus**.
4. Pulsa **Run workflow**.
5. Elige la rama `main`.
6. En **Corpus suite to run**, elige `curated` o `full`.
7. Deja **Upload JUnit reports as temporary artifacts** desactivado si solo
   quieres conocer el resultado de las pruebas.
8. Activa esa casilla únicamente cuando necesites descargar el XML del informe.
9. Pulsa **Run workflow**.

No ejecutes `full` repetidamente durante cambios pequeños. Las pruebas locales
y `curated` son normalmente suficientes durante el desarrollo.

## Artefactos: cuándo activarlos

Un artefacto es un archivo que GitHub conserva después de terminar una
ejecución. En este proyecto los informes JUnit solamente se suben cuando se
marca explícitamente `upload_reports`.

Si la casilla permanece desactivada:

- las pruebas se ejecutan normalmente;
- el resultado se puede leer desde los logs;
- el XML temporal desaparece con la máquina virtual del trabajo;
- no se consume almacenamiento persistente de artefactos.

Si la casilla se activa, los informes se eliminan automáticamente después de
tres días. Descárgalos antes si necesitas conservarlos localmente.

## Eliminar artefactos antiguos para recuperar espacio

Cambiar los workflows no elimina archivos creados por ejecuciones anteriores.
Para borrar un artefacto antiguo:

1. Abre el repositorio correspondiente en GitHub.
2. Entra en **Actions**.
3. Selecciona el workflow en la barra lateral.
4. Abre una ejecución anterior.
5. Busca la sección **Artifacts**.
6. Usa el icono de papelera situado junto al artefacto.

Eliminar un artefacto es irreversible. Si eliminas una ejecución completa,
GitHub elimina también los artefactos asociados a esa ejecución.

## Eliminar cachés de dependencias

Los workflows usan la caché de `pip` para acelerar instalaciones. Las cachés
son diferentes de los artefactos y también pueden ocupar almacenamiento.

1. Abre el repositorio en GitHub.
2. Entra en **Actions**.
3. En la barra lateral, busca **Management**.
4. Pulsa **Caches**.
5. Revisa el tamaño y la última fecha de uso.
6. Elimina con el icono de papelera las cachés que ya no necesites.

No es necesario conservar cachés para que las pruebas funcionen. Si se borran,
una futura ejecución manual simplemente volverá a descargar sus dependencias.

## Reducir la retención general del repositorio

Además de los tres días definidos en `corpus.yml`, GitHub permite establecer
una retención general para artefactos y logs nuevos:

1. En el repositorio, entra en **Settings**.
2. En la barra lateral, abre **Actions** y después **General**.
3. Busca **Artifact and log retention**.
4. Introduce el número de días deseado. Para minimizar espacio, puede usarse
   un día si el tipo de cuenta y repositorio lo permiten.
5. Pulsa **Save**.

Este ajuste no es retroactivo: no reduce automáticamente la duración de los
artefactos que ya existían. Esos deben eliminarse manualmente.

## Cancelar o eliminar una ejecución

Si se inició por error un corpus completo:

1. Abre **Actions** y entra en la ejecución activa.
2. Utiliza **Cancel workflow** para detener los trabajos que sigan ejecutándose.

Para eliminar una ejecución terminada, abre su menú y selecciona
**Delete workflow run**. Al eliminarla también desaparecen sus artefactos. Los
logs y resultados ya no podrán consultarse después.

## Crear un release solamente de forma manual

En este momento ningún workflow crea releases. Cuando sea necesario publicar
una versión manualmente:

1. Abre la página principal del repositorio que se publicará.
2. Pulsa **Releases**.
3. Pulsa **Draft a new release**.
4. Elige un tag existente o crea uno nuevo, por ejemplo `v1.0.0`.
5. Comprueba cuidadosamente la rama o commit de destino.
6. Escribe el título y las notas de la versión.
7. Adjunta archivos binarios solamente si realmente deben distribuirse.
8. Usa **Save draft** si todavía necesitas revisar el contenido.
9. Pulsa **Publish release** únicamente cuando decidas publicarlo.

Crear un tag o hacer `git push` no debe publicar un release automáticamente en
este proyecto. Si en el futuro se añade un workflow de empaquetado o release,
su único disparador permitido será:

```yaml
on:
  workflow_dispatch:
```

## Comprobación antes de subir cambios de workflows

Después de editar `.github/workflows/*.yml`, comprueba que no aparezcan estos
disparadores:

```yaml
push:
pull_request:
schedule:
```

También debe evitarse cualquier workflow que publique a partir de un tag. Los
dos workflows actuales deben conservar esta forma básica:

```yaml
on:
  workflow_dispatch:
```

Antes del commit, valida el YAML y revisa las diferencias. Después sube primero
`pyqt6-linguistic-tools` y finalmente el repositorio principal, siguiendo
`docs/GIT-SUBMODULE-COMMIT-AND-PUSH-GUIDE.md`.

## Documentación oficial de GitHub

- [Ejecutar manualmente un workflow](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow)
- [Eliminar artefactos de un workflow](https://docs.github.com/es/actions/how-tos/manage-workflow-runs/remove-workflow-artifacts)
- [Administrar cachés de GitHub Actions](https://docs.github.com/es/actions/how-tos/manage-workflow-runs/manage-caches)
- [Configurar Actions, artefactos y retención](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository)
- [Crear y administrar releases](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository)

