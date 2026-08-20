# Windows may manage/download dictionaries

Unlike Linux, Windows may provide an application-level resource manager.

The Windows provider may support:

```python
provider.can_install_spell_resources = True
provider.can_install_thesaurus_resources = True
```

The application may:

* download a dictionary;
* validate it;
* install it into user application data;
* remove it.

This functionality is Windows-specific and MUST NOT accidentally become Linux system-package installation logic.

---

# Secure Windows resource installation

Any downloadable resource must use a safe workflow:

```text
download to temporary location
          ↓
validate
          ↓
safe extraction
          ↓
verify expected files
          ↓
atomic installation
          ↓
cleanup
```

Never use unsafe archive extraction.

Protect against:

```text
../
../../
absolute paths
path traversal
```

If installation fails, preserve the previous working version.

---

# Linguistic resource licenses

Do not assume that every Hunspell dictionary or MyThes thesaurus has the same license.

For downloadable Windows resources preserve all files that include licences, In other words, use everything that has been extracted from the downloaded file.


# English-first user interface

This project must be developed **English-first**.

All newly introduced user-facing strings must initially be written in English.

Do NOT initially write new UI strings in Spanish.

---

# Qt Linguist internationalization

English-first does NOT mean English-only.

All new user-visible strings must use the project's existing Qt translation mechanism.

Use:

```python
self.tr(...)
```

or the appropriate translation mechanism already used by the project.

The architecture must allow later translation into:

```text
Spanish
German
French
Russian
Portuguese
Italian
and other languages
```

Do not hardcode untranslated UI text deep inside backend classes.

Backend errors should preferably use structured error codes/data that the Qt layer can translate.

---

# Important Linux distinction

Therefore Linux has two types of resources:

```text
SYSTEM-MANAGED
    Hunspell library
    .aff
    .dic
    MyThes resources

APPLICATION-MANAGED
    personal user dictionary
    user preferences
```

Only the second category may be written by GuitarChordStudio.

---

# Nuitka

Create a Windows build scripts:

```text
build/build-windows.bat
```

---


# Personal dictionaries

Personal dictionaries are different from system dictionaries.

Even on Linux, GuitarChordStudio MAY maintain a per-user personal dictionary because this does not install or modify system packages.

Use:

```python
QStandardPaths
```

to store application-owned personal words.

Conceptually:

```text
GuitarChordStudio/
└── personal-dictionaries/
    ├── es_ES.txt
    ├── en_US.txt
    ├── de_DE.txt
    └── ru_RU.txt
```

These files may use UTF-8.

At startup:

```text
load personal UTF-8 words
          ↓
Hunspell_add()
```

Do NOT write personal words into:

```text
/usr/share/hunspell/
```

on Linux.


