
# GuitarChordStudio — Multiplatform Spell Checking and Thesaurus Infrastructure Extra Ideas
--

# International tokenizer

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

# GuitarChordStudio-specific chord detection

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

# Ignore obvious non-word tokens

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

# Spell highlighter

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


# Context menu

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

---

# Spanish acceptance test

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

# German tests

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

# Russian tests

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

# French tests

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

# Replacing a word with a synonym

When the user chooses a synonym, replace exactly the word under the cursor.

Preserve simple capitalization where safe:

```text
word → synonym
Word → Synonym
WORD → SYNONYM
```

Do not attempt complex morphology that could generate incorrect language.

---

# Spell checking can be disabled

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

# Thesaurus can be disabled or lazy-loaded

Do not load thesaurus data unnecessarily.

Spell checking must remain independent.

---



# 97. Documentation

Create:

```text
docs/linguistics-architecture.md
```

---


