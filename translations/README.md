# Application translations

This directory is shared by every GuitarChordStudio application. Keeping the
Qt Linguist sources and compiled catalogs at the repository root avoids tying
them to one application package and lets ChordFlow, ChordPages, and future
programs add their own catalogs side by side.

## File naming

```text
<application>_<locale>.ts   Qt Linguist source
<application>_<locale>.qm   compiled catalog loaded at runtime
```

Current catalogs:

```text
chordpages_en.ts
chordpages_en.qm
chordpages_es.ts
chordpages_es.qm
```

The base strings in the source code are English and use `self.tr(...)`.
Translators edit the `.ts` files with Qt Linguist; developers compile them with
`lrelease`.

## Updating ChordPages

From the repository root:

```bash
pylupdate6 chordpages --ts translations/chordpages_es.ts
pylupdate6 chordpages --ts translations/chordpages_en.ts
linguist-qt6 translations/chordpages_es.ts
lrelease translations/chordpages_es.ts -qm translations/chordpages_es.qm
lrelease translations/chordpages_en.ts -qm translations/chordpages_en.qm
```

The source-run loader reads this directory directly. Installed packages read
`share/chordpages/translations` or `share/chordflow/translations`.
