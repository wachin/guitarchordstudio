# Compilar Hunspell para Windows

Este documento explica cómo compilar `libhunspell-1.7-0.dll` desde el código fuente
ubicado en `third-party/hunspell/`, incluyendo **libiconv** (necesario para diccionarios
con codificaciones distintas de UTF-8).

## Por qué libiconv es importante

Sin `libiconv`, la compilación termina exitosamente pero los diccionarios que usan
codificaciones como ISO-8859-1/2/15 (comunes en diccionarios europeos) **fallan en runtime**.
Los diccionarios de este proyecto (`es_ES`, `en_US`) están en UTF-8, pero es mejor
tener iconv para compatibilidad con diccionarios adicionales que el usuario pueda instalar.

> El propio README de Hunspell lo dice:
> *"Without mingw-w64-x86_64-libiconv the build still succeeds but the hunspell tool
> cannot convert between dictionary encodings, so any test or dictionary that declares
> a non-UTF-8 SET (e.g. ISO8859-1/2/15) will fail at runtime."*

## Requisitos

### 1. MSYS2

Descargar e instalar desde: https://www.msys2.org/

Se instala por defecto en `C:\msys64`.

### 2. Paquetes necesarios

Abrir la terminal **"MSYS2 MinGW64"** (icono azul en el menú inicio — NO la terminal blanca MSYS2 normal):

```bash
# Actualizar el sistema primero
pacman -Syu

# Cerrar la terminal y reabrirla cuando lo pida

# Instalar herramientas de compilación + libiconv + gettext + autotools
pacman -S base-devel mingw-w64-x86_64-toolchain mingw-w64-x86_64-libtool \
          mingw-w64-x86_64-libiconv mingw-w64-x86_64-gettext autoconf automake autopoint
```

**Paquetes instalados:**

| Paquete | Para qué sirve |
|---------|---------------|
| `base-devel` | make, patch, etc. |
| `mingw-w64-x86_64-toolchain` | GCC, G++, linker para Windows 64-bit |
| `mingw-w64-x86_64-libtool` | Generación de librerías compartidas (.dll) |
| `mingw-w64-x86_64-libiconv` | **Conversión de codificaciones** (UTF-8 ↔ ISO-8859, etc.) |
| `mingw-w64-x86_64-gettext` | Internacionalización (NLS) |
| `autoconf`, `automake`, `autopoint` | Generación de scripts configure (autotools) |

## Pasos de compilación

### Con autotools (método recomendado — igual que en Linux/macOS)

Según el README de Hunspell, el método estándar es autotools. Los comandos son:

1. **Abrir la terminal "MSYS2 MinGW64"** (icono azul)

2. **Navegar al submódulo:**
   ```bash
   cd /c/D/guitarchordstudio/third-party/hunspell
   ```

3. **Generar los scripts de configure:**
   ```bash
   autoreconf -vfi
   ```

4. **Configurar el build:**
   ```bash
   ./configure --prefix=/mingw64 --enable-shared --disable-static
   ```

   - `--enable-shared` → genera la DLL
   - `--disable-static` → no genera .lib estático
   - `--prefix=/mingw64` → instala en el prefix de MinGW64

   **Verifica en la salida** que dice `iconv: yes`. Si dice `iconv: no`, el paquete
   `mingw-w64-x86_64-libiconv` no está instalado correctamente.

5. **Compilar:**
   ```bash
   make -j$(nproc)
   ```

6. **Verificar que iconv se linkó correctamente:**
   ```bash
   ldd src/hunspell/.libs/libhunspell-1.7-0.dll | grep iconv
   ```
   Debería mostrar algo como `libiconv-2.dll => /mingw64/bin/libiconv-2.dll`

7. **Copiar las DLLs al proyecto:**
   ```bash
   cp src/hunspell/.libs/libhunspell-1.7-0.dll /c/D/guitarchordstudio/resources/hunspell/
   cp /mingw64/bin/libiconv-2.dll /c/D/guitarchordstudio/resources/hunspell/
   cp /mingw64/bin/libgcc_s_seh-1.dll /c/D/guitarchordstudio/resources/hunspell/
   cp /mingw64/bin/libstdc++-6.dll /c/D/guitarchordstudio/resources/hunspell/
   ```

   **Nota:** Las DLLs de GCC y libstdc++ son necesarias porque MinGW las linkea dinámicamente.
   También necesitarás copiarlas junto al `.exe` cuando distribuyas con Nuitka.

## Verificar en Windows

Una vez copiada la DLL (y sus dependencias), verificar que ChordFlow la detecta:

```powershell
# En PowerShell de Windows (no MSYS2)
cd C:\D\guitarchordstudio
.\.venv\Scripts\Activate.ps1
python -c "from chordflow.spellcheck import SpellChecker; sc = SpellChecker('es_ES'); print(f'backend={sc.backend}')"
```

Debería imprimir `backend=hunspell` (en vez de `backend=dic`).

Para verificar que iconv funciona y las affix rules se procesan correctamente:

```powershell
python -c "
from chordflow.spellcheck import SpellChecker
sc = SpellChecker('es_ES')
print(f'backend={sc.backend}')
print(f'canta={sc.check(\"canta\")}')
print(f'vida={sc.check(\"vida\")}')
print(f'quiero={sc.check(\"quiero\")}')
"
```

Con el backend hunspell, "vida" y "quiero" deberían dar `True` (el motor C++ de Hunspell
procesa las affix rules completas).

## DLLs necesarias para distribución

Cuando compiles con Nuitka para distribuir el `.exe`, necesitarás incluir estas DLLs
en el mismo directorio que el ejecutable:

| DLL | Origen | Necesaria |
|-----|--------|-----------|
| `libhunspell-1.7-0.dll` | Compilada por ti | ✅ Sí |
| `libiconv-2.dll` | `C:\msys64\mingw64\bin\` | ✅ Sí (para encodings no-UTF8) |
| `libgcc_s_seh-1.dll` | `C:\msys64\mingw64\bin\` | ✅ Sí (runtime de GCC) |
| `libstdc++-6.dll` | `C:\msys64\mingw64\bin\` | ✅ Sí (runtime de C++) |

El script `build/build-windows.bat` copia estas DLLs automáticamente cuando están presentes
en `resources/hunspell/`.

## Notas importantes

- La terminal **MSYS2 MinGW64** (icono azul) es diferente de la terminal **MSYS2** normal (icono blanco).
  - **MinGW64**: compila binarios Windows nativos (sin dependencia de MSYS2 runtime)
  - **MSYS2 normal**: compila binarios que dependen de `msys-2.0.dll`

- Si `autoreconf` falla con "command not found", ejecutar:
  ```bash
  pacman -S autoconf automake autopoint
  ```

- Para verificar qué DLLs necesita el hunspell compilado:
  ```bash
  ldd src/hunspell/.libs/libhunspell-1.7-0.dll
  ```

## Solución de problemas

| Error | Solución |
|-------|----------|
| `autoreconf: command not found` | `pacman -S autoconf automake autopoint` |
| `libtool: command not found` | `pacman -S mingw-w64-x86_64-libtool` |
| `iconv.h: No such file` | `pacman -S mingw-w64-x86_64-libiconv` |
| DLL no detectada por Python | Verificar que está en `resources/hunspell/libhunspell-1.7-0.dll` |
| `libiconv-2.dll not found` al ejecutar | Copiar `C:\msys64\mingw64\bin\libiconv-2.dll` al dir del exe |
| El configure dice "iconv: no" en el resumen | Asegurarse de usar MinGW64 terminal, no MSYS2 normal |

## Resumen rápido

```bash
# 1. Abrir MSYS2 MinGW64 (icono azul)
# 2. Instalar dependencias
pacman -S base-devel mingw-w64-x86_64-toolchain mingw-w64-x86_64-libtool \
          mingw-w64-x86_64-libiconv mingw-w64-x86_64-gettext autoconf automake autopoint

# 3. Compilar
cd /c/D/guitarchordstudio/third-party/hunspell
autoreconf -vfi
./configure --prefix=/mingw64 --enable-shared --disable-static
make -j$(nproc)

# 4. Copiar DLLs al proyecto
cp src/hunspell/.libs/libhunspell-1.7-0.dll /c/D/guitarchordstudio/resources/hunspell/
cp /mingw64/bin/libiconv-2.dll /c/D/guitarchordstudio/resources/hunspell/
cp /mingw64/bin/libgcc_s_seh-1.dll /c/D/guitarchordstudio/resources/hunspell/
cp /mingw64/bin/libstdc++-6.dll /c/D/guitarchordstudio/resources/hunspell/
```
