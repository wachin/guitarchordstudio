
# GuitarChordStudio — Multiplatform Spell Checking and Thesaurus Infrastructure Extra Ideas

# 9. Linux dictionaries

The Linux provider should discover installed pairs such as:

```text
es_ES.aff
es_ES.dic

en_US.aff
en_US.dic

de_DE.aff
de_DE.dic

ru_RU.aff
ru_RU.dic
```

A Hunspell dictionary should only be considered valid when the required `.aff` and `.dic` resources are available.

The program must use what is actually installed.

Do not invent supported languages.

---

---

# 11. Linux resource management is read-only

Expose this distinction explicitly.

Conceptually:

```python
provider.can_install_spell_resources = False
provider.can_install_thesaurus_resources = False
```

or use an equivalent capability-based design.

The Qt interface must use those capabilities.

Therefore, on Linux there must NOT be a misleading:

```text
Download dictionary
```

button for system packages.

Instead provide an informational action such as:

```text
How to install language resources
```

or:

```text
System package information
```

---





# 18. Windows may manage/download dictionaries

Unlike Linux, Windows may provide an application-level resource manager.

The Windows provider may support:

```python
provider.can_install_spell_resources = True
provider.can_install_thesaurus_resources = True
```

provided licensing permits redistribution/download.

The application may:

* download a dictionary;
* validate it;
* install it into user application data;
* update it;
* remove it.

This functionality is Windows-specific and MUST NOT accidentally become Linux system-package installation logic.

---

# 19. Secure Windows resource installation

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

# 20. Linguistic resource licenses

Do not assume that every Hunspell dictionary or MyThes thesaurus has the same license.

For downloadable Windows resources preserve, when applicable:

```text
LICENSE
COPYING
README
```

Track:

```text
source
version
license
locale
```

Do not redistribute a dictionary or thesaurus unless its license permits it.


# 26. Preserve working Linux behavior

This requirement is critical.

The existing Linux implementation already works for at least the user's tested Spanish configuration using distribution packages.

Do not regress that functionality while fixing Windows.

Before refactoring, establish tests or diagnostic scripts that demonstrate the existing Linux behavior.

After refactoring, verify equivalent or improved behavior.

---

---


# English-first user interface

This project must be developed **English-first**.

All newly introduced user-facing strings must initially be written in English.

Examples:

```text
Spell checking
Thesaurus
Synonyms
Add to dictionary
Ignore
Spell-checking language
Language resources
Dictionary not installed
Thesaurus not installed
System package information
Download language resources
```

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

# 42. International tokenizer

Do not rely solely on:

```regex
\b\w+\b
```

Build a Unicode-aware tokenizer that can correctly recognize:

```text
Señor
creación
Straße
français
Москва
d’Artagnan
O'Connor
```

If using the third-party `regex` package is justified, Unicode properties such as:

```text
\p{L}
\p{M}
```

may be used.

Avoid unnecessary dependencies if Python can implement the required behavior reliably.

---

# 43. GuitarChordStudio-specific chord detection

This is mandatory.

Do NOT send musical chord symbols to Hunspell.

Examples:

```text
A
Am
A#m
Bb
C#
C#m7
Fmaj7
Gsus4
D/F#
Bb/D
Cadd9
Em7
F#m
```

Before inventing a new regular expression, inspect:

```text
chord_transposer.py
```

and any existing chord parser.

Reuse the project's existing chord grammar/parser if it is robust.

Conceptually provide:

```python
is_chord_token(token)
```

---

# 44. Ignore obvious non-word tokens

Do not spell-check tokens such as:

```text
123
2026
x3
https://example.com
www.example.com
email@example.com
```

while continuing to check real words.

---

# 45. Spell highlighter

Create a reusable component conceptually similar to:

```python
class SpellHighlighter(QSyntaxHighlighter):
    ...
```

It should work with a:

```text
QTextDocument
```

and therefore be reusable with:

```text
QTextEdit
QPlainTextEdit
```

Its responsibility should remain narrow:

```text
tokenize
       ↓
filter chords/non-words
       ↓
ask SpellChecker
       ↓
underline misspellings
```

It must NOT:

* download dictionaries;
* inspect package managers;
* scan the whole filesystem repeatedly;
* rebuild Hunspell.

---

# Spell-check cache

Use a bounded cache for repeated words.

For example, a reasonable LRU cache.

Invalidate it when:

* language changes;
* a personal word is added;
* a personal word is removed;
* relevant dictionary resources change.

---

# 47. Reusable PyQt6 editor

The long-term API should allow:

```python
from ...qt import SpellTextEdit

editor = SpellTextEdit()
editor.set_spell_language("es_ES")
```

and provide:

* misspelling underline;
* suggestions;
* personal dictionary;
* language menu;
* thesaurus;
* synonyms.

---

# 48. Reusable `QPlainTextEdit`

Also provide:

```python
SpellPlainTextEdit
```

without duplicating the entire implementation.

Both widgets should share:

```text
SpellChecker
SpellHighlighter
ThesaurusEngine
context-menu helpers
language-menu helpers
```

---

# 49. Context menu

For a misspelled word such as:

```text
marabillas
```

the English-first context menu could contain:

```text
maravillas
...
────────────────
Add "marabillas" to dictionary
Ignore
────────────────
Synonyms
────────────────
Spell-checking language
```

For a correctly spelled word:

```text
maravillas
```

it may offer:

```text
Synonyms
────────────────
Spell-checking language
```

All these strings must be translatable.

---

# 50. Personal dictionaries

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

---

# 51. Important Linux distinction

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

--
---

# 65. Linux diagnostics

For a working Debian installation, diagnostics might conceptually show:

```text
Platform: Linux
Provider: LinuxSystemProvider

Hunspell:
    library: system
    status: available

Spanish:
    AFF: /usr/share/hunspell/es_ES.aff
    DIC: /usr/share/hunspell/es_ES.dic

Thesaurus:
    source: system
    status: available
```

Do not hardcode these paths into expected test results if the distribution uses different valid paths.


# 69. Nuitka

Review the Windows build scripts, including:

```text
build/build-windows.bat
```

and equivalents.

The Windows distribution must include:

```text
libhunspell.dll
```

and any required application-managed language resources.

Nuitka must NOT rebuild Hunspell.

It should package the already-built DLL.



---

# 76. Spanish acceptance test

This is mandatory.

With Spanish resources available, test:

```text
Canta
Toda
maravillas
creación
Señor
```

as valid according to the actual Spanish dictionary.

Test:

```text
marabillas
creasión
```

as invalid if the actual dictionary reports them invalid.

Do not hardcode spell-check results.

---

# 77. German tests

If German resources are installed/available, test words such as:

```text
Haus
Straße
schön
Deutschland
```

plus a clearly invented misspelling.

Use the actual dictionary result.

---

# 78. Russian tests

If Russian resources are installed/available, test:

```text
Москва
привет
Россия
```

The critical requirement is correct Unicode processing without:

```text
UnicodeEncodeError
UnicodeDecodeError
crash
```

---

# 79. French tests

If French resources are available, test:

```text
français
création
école
```

---

# 80. GuitarChordStudio-specific acceptance test

Use this text:

```text
INTRO X3
A#m   G#   F#

VERSE
C#       G#       A#m      G#    F#
Mi Cristo, mi Rey, nadie es como tú
C#       F#       G#
Toda mi vida, quiero exaltar,
A#m      B        G#
las maravillas de tu amor
```

Expected behavior:

* chord symbols are ignored by spell checking;
* ordinary words are checked;
* `Toda` must not be falsely marked as misspelled when the Spanish dictionary accepts it;
* `maravillas` must not be falsely marked as misspelled when accepted by the dictionary.

---

# 81. Suggestion test

Test:

```text
marabillas
```

If the installed Spanish Hunspell dictionary suggests:

```text
maravillas
```

the application must expose that suggestion correctly.

Do NOT hardcode the suggestion.

---

# 82. Native stress tests

Exercise repeatedly:

```text
create
spell
suggest
free_list
destroy
```

Perform enough iterations to expose obvious lifecycle or memory errors.

Also test repeated language changes.

---

# 83. Language-switching tests

For available resources, test sequences such as:

```text
es_ES
  ↓
de_DE
  ↓
ru_RU
  ↓
fr_FR
  ↓
es_ES
```

Changing language must:

* release the old handle safely;
* create the new handle;
* update dictionary encoding;
* reload the relevant personal dictionary;
* invalidate spell-check cache;
* update thesaurus availability.

---

# 84. Tokenizer tests

Test:

```text
Señor
creación
Straße
français
Москва
d’Artagnan
O'Connor
```

and chord/non-word exclusions.

---

# 85. Chord tests

The following must not be sent to Hunspell:

```text
A#m
C#
F#m7
Bb
D/F#
Cadd9
Gsus4
```

---

# 86. MyThes tests

When a thesaurus is available, test:

* existing word;
* missing word;
* Unicode word;
* multiple meanings;
* duplicate synonyms;
* language with spell checking but no thesaurus.

Tests for optional resources should skip explicitly when the resource is unavailable rather than pretending it exists.

---

# 87. Synonym context menu

For a word with thesaurus data, provide an English-first menu such as:

```text
Synonyms >
    synonym 1
    synonym 2
    ...
```

If meanings are available:

```text
Synonyms >
    Meaning 1 >
        ...
    Meaning 2 >
        ...
```

Avoid enormous menus.

A future:

```text
More synonyms...
```

dialog is acceptable if useful.

---

# 88. Replacing a word with a synonym

When the user chooses a synonym, replace exactly the word under the cursor.

Preserve simple capitalization where safe:

```text
word → synonym
Word → Synonym
WORD → SYNONYM
```

Do not attempt complex morphology that could generate incorrect language.

---

# 89. Spell checking can be disabled

Expose something similar to:

```python
editor.set_spellcheck_enabled(False)
```

The UI may contain:

```text
Spell checking
☑ Enabled
```

using translatable English source strings.

---

# 90. Thesaurus can be disabled or lazy-loaded

Do not load thesaurus data unnecessarily.

Spell checking must remain independent.

---



# 97. Documentation

Create:

```text
docs/linguistics-architecture.md
```

Explain clearly:

* API;
* Hunspell;
* Thesaurus;
* Linux system-resource policy;
* Windows managed-resource policy;
* personal dictionaries;
* Qt integration;
* Nuitka deployment;
* internationalization, and others

rather than duplicating all Windows compilation instructions.

---

# 98. Linux documentation

Explicitly document:

> GuitarChordStudio does not install system Hunspell dictionaries or MyThes packages on Linux. Language resources must be installed through the Linux distribution's package manager.

Include examples for Debian/Ubuntu only when the package names are known and verified.

For example:

```bash
sudo apt install hunspell hunspell-en-us hunspell-es mythes-es
```

Make clear that the command is executed manually by the user, not by GuitarChordStudio.


