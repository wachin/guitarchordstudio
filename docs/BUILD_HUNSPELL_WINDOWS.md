# Compilar Hunspell para Windows

Este documento explica cómo compilar `libhunspell-1.7-0.dll` desde el código fuente
ubicado en `third-party/hunspell/`.

## Requisitos

1. **MSYS2** — Entorno de desarrollo tipo Unix para Windows
   - Descargar desde: https://www.msys2.org/
   - Instalar en `C:\msys64` (default)

2. **MinGW-w64 toolchain** — Compilador GCC para Windows
   ```bash
   # Abrir la terminal "MSYS2 MinGW64" (NO la terminal MSYS2 normal)
   pacman -S --needed base-devel mingw-w64-x86_64-toolchain mingw-w64-x86_64-cmake mingw-w64-x86_64-ninja
   ```

## Pasos de compilación

### Opción A: Compilar desde el submódulo (recomendada)

1. **Abrir la terminal "MSYS2 MinGW64"** (icono azul, NO el icono blanco de MSYS2 normal)

2. **Navegar al proyecto:**
   ```bash
   cd /d/guitarchordstudio/third-party/hunspell
   ```

3. **Crear directorio de build:**
   ```bash
   mkdir -p build-win && cd build-win
   ```

4. **Configurar con CMake:**
   ```bash
   cmake -G Ninja \
     -DCMAKE_BUILD_TYPE=Release \
     -DCMAKE_INSTALL_PREFIX=/mingw64 \
     -DBUILD_SHARED_LIBS=ON \
     -DBUILD_STATIC_LIBS=OFF \
     ..
   ```

5. **Compilar:**
   ```bash
   ninja
   ```

6. **La DLL estará en:**
   ```
   build-win/src/hunspell/libhunspell-1.7.dll
   ```

7. **Copiar a resources:**
   ```bash
   cp src/hunspell/libhunspell-1.7.dll /d/guitarchordstudio/resources/hunspell/libhunspell-1.7-0.dll
   ```

### Opción B: Instalar desde paquete MSYS2 (más rápido)

Si solo necesitas la DLL y no quieres compilar:

1. **Abrir la terminal "MSYS2 MinGW64"**

2. **Instalar el paquete precompilado:**
   ```bash
   pacman -S mingw-w64-x86_64-hunspell
   ```

3. **Copiar la DLL:**
   ```bash
   cp /mingw64/bin/libhunspell-1.7-0.dll /d/guitarchordstudio/resources/hunspell/
   ```

## Verificar

Una vez copiada la DLL, verificar que ChordFlow la detecta:

```powershell
# En PowerShell de Windows (no MSYS2)
cd C:\D\guitarchordstudio
.\.venv\Scripts\Activate.ps1
python -c "from chordflow.spellcheck import SpellChecker; sc = SpellChecker('es_ES'); print(f'backend={sc.backend}')"
```

Debería imprimir `backend=hunspell` (en vez de `backend=dic`).

## Notas

- La terminal **MSYS2 MinGW64** es diferente de la terminal **MSYS2** normal.
  - MSYS2 MinGW64: icono azul, compila binarios Windows nativos
  - MSYS2 normal: icono blanco, compila binarios para el entorno MSYS2

- Si el compilador no se encuentra, asegurarse de usar la terminal **MinGW64**
  (no la terminal MSYS2 base ni la UCRT64).

- Para compilar también las herramientas de línea de comandos (`hunspell.exe`):
  ```bash
  cmake -G Ninja -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=ON ..
  ninja
  # El exe estará en build-win/src/tools/hunspell.exe
  ```

## Solución de problemas

| Error | Solución |
|-------|----------|
| `cmake: command not found` | Usar la terminal MinGW64, no MSYS2 normal |
| `ninja: command not found` | Ejecutar `pacman -S mingw-w64-x86_64-ninja` |
| `no CMAKE_C_COMPILER found` | Ejecutar `pacman -S mingw-w64-x86_64-gcc` |
| DLL no detectada por Python | Verificar que está en `resources/hunspell/libhunspell-1.7-0.dll` |
