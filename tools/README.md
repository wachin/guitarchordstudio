# Tools

Utility scripts for packaging and distributing Hunspell & Mythes dictionaries.

## package-dicts.sh

Compress each dictionary folder from the `third-party/` submodule into
individual `.tar.gz` archives and place them in the `build/` directory.

### Usage

From the repository root:

```bash
bash tools/package-dicts.sh
```

### Output

All archives are written to `build/`:

```
build/dict-en.tar.gz
build/dict-es.tar.gz
build/dict-de.tar.gz
...
```

Each archive contains a single `dict-XX/` folder with the Hunspell (`.aff`,
`.dic`) and Mythes (`.dat`, `.idx`) files for that language.

---

## fetch-dict-list.py

The catalog generator now lives in the toolkit:
`libs/pyqt6-linguistic-tools/tools/fetch-dict-list.py`. It writes the bundled
catalog at
`libs/pyqt6-linguistic-tools/src/pyqt6_linguistic_tools/data/dictionaries.json`,
so the toolkit owns the download list and other applications get it with
`load_bundled_dictionary_catalog()`.

### Usage

From the GuitarChordStudio repository root:

```bash
python3 libs/pyqt6-linguistic-tools/tools/fetch-dict-list.py \
  --tag v1.0-dictionaries-thesaurus
```

See `libs/pyqt6-linguistic-tools/tools/README.md` for the output schema and
options.

---

## Release workflow

To publish a new dictionary release:

1. Make sure the `third-party/` submodule is up to date:
   ```bash
   git submodule update --init --recursive
   ```

2. Package the dictionaries:
   ```bash
   bash tools/package-dicts.sh
   ```

3. Upload all `build/dict-*.tar.gz` files to a new GitHub Release on the
   [libreoffice-dictionaries-collection](https://github.com/wachin/libreoffice-dictionaries-collection)
   repository.

4. After publishing the release, regenerate the bundled catalog from the
   toolkit:
   ```bash
   python3 libs/pyqt6-linguistic-tools/tools/fetch-dict-list.py --tag <TAG_NAME>
   ```

5. Commit the updated catalog in the
   [pyqt6-linguistic-tools](https://github.com/wachin/pyqt6-linguistic-tools)
   repository, then update the GuitarChordStudio submodule pointer.