
# GuitarChordStudio — Multiplatform Spell Checking and Thesaurus Infrastructure

## 1. Main objective

I want you to redesign and improve the linguistic infrastructure of the `GuitarChordStudio` project.

The repository contains two main PyQt6 applications:

* `ChordFlow`
* `ChordPages`

Both applications need professional multilingual:

* spell checking;
* spelling suggestions;
* personal dictionaries;
* language selection;
* thesaurus/synonym support;
* Unicode support;
* reusable PyQt6 text-editing integration.

The architecture must also be designed so that the linguistic subsystem can later be extracted from GuitarChordStudio and reused in other PyQt6 applications.

The applications are intended to run on:

```text
GNU/Linux
Windows 10
Windows 11
macOS
```

However, the way linguistic resources are obtained and managed MUST NOT be identical on every operating system.

That distinction is a fundamental requirement of this task.

---

# 2. Fundamental architectural principle

Do NOT create independent spell-checking implementations for ChordFlow, ChordPages, Linux and Windows.

I want:

```text
ChordFlow ─────┐
               │
ChordPages ────┼────► Common PyQt6 Linguistics API
               │
Future apps ───┘
                       │
              ┌────────┴────────┐
              │                 │
         SpellChecker      ThesaurusEngine
              │                 │
              └────────┬────────┘
                       │
               Resource Providers
                       │
           ┌───────────┼───────────┐
           │           │           │
         Linux       Windows      macOS
```

ChordFlow and ChordPages must NOT contain operating-system-specific spell-checking logic.

They should call APIs such as:

```python
checker = SpellChecker("en_US")

checker.check("beautiful")
checker.suggest("beautifull")
```

and:

```python
thesaurus = ThesaurusEngine("en_US")
results = thesaurus.lookup("beautiful")
```

The linguistic infrastructure must determine internally how those resources are provided on each operating system.

---

# 3. Very important: Linux and Windows use different resource-management strategies

The user has already verified that on Debian-based GNU/Linux systems the existing distribution packages work correctly.

For example:

```bash
sudo apt install hunspell hunspell-es mythes-es
```

provides working Spanish spell checking and thesaurus support.

Therefore:

## GNU/Linux

GuitarChordStudio MUST use linguistic resources installed and managed by the Linux distribution.

## Windows

GuitarChordStudio MUST use application-managed linguistic resources and the bundled native Hunspell DLL.

These differences must be hidden behind the common linguistic API.

---

# 4. CRITICAL Linux rule: GuitarChordStudio must NOT install system dictionaries

This is a strict requirement.

On GNU/Linux, GuitarChordStudio MUST NOT:

* download Hunspell dictionaries into system directories;
* install Hunspell dictionaries;
* install MyThes packages;
* run `apt`;
* run `apt-get`;
* run `dpkg`;
* run Synaptic;
* invoke `sudo`;
* invoke `pkexec`;
* request privilege elevation;
* modify `/usr/share/hunspell`;
* modify `/usr/share/mythes`;
* modify package-manager databases;
* attempt to become a Linux package manager.

Linux linguistic resources belong to the operating system/package manager.

GuitarChordStudio must be a **consumer**, not an installer, of those resources.

---

# 5. Linux package installation belongs to the user

If a dictionary is missing, GuitarChordStudio may explain what is missing.

For example, an English source string could say:

```text
The Spanish spell-checking dictionary is not installed.

On Debian or Ubuntu, you can install the appropriate Hunspell
dictionary using your system package manager.
```

If we have a reliable mapping between a locale and a Debian/Ubuntu package, the UI may additionally display something such as:

```text
Suggested package:

hunspell-es
```

or:

```text
Suggested package:

mythes-es
```

It may display an informational command:

```text
sudo apt install hunspell-es
```

but GuitarChordStudio MUST NOT execute that command.

The user must install packages externally using:

* Synaptic;
* apt in a terminal;
* Discover or another distribution package manager;
* another system administration tool.

---

# 6. Do not assume Debian package names for every language

Do not generate package names blindly.

For example, do NOT assume that:

```text
locale = xx_YY
```

necessarily means:

```text
hunspell-xx
mythes-xx
```

Package names differ between languages and distributions.

If we maintain package suggestions, create an explicit data-driven mapping for known packages.

For unknown languages, simply say that the appropriate Hunspell/MyThes package should be installed through the distribution package manager.

---

# 7. Linux must primarily discover installed system resources

Create a Linux resource provider conceptually similar to:

```python
class LinuxSystemLinguisticProvider:
    ...
```

Its responsibility is detection and resolution.

It should detect installed Hunspell dictionaries in appropriate system locations such as:

```text
/usr/share/hunspell/
```

and other standard locations actually used by supported Linux distributions.

Do not hardcode only one directory if the current project or target distributions require additional standard locations.

Use deterministic priority rules.

---

# 8. Linux Hunspell library

On Linux, do NOT bundle the Windows DLL.

Use the Hunspell shared library supplied by the operating system.

The architecture should allow something conceptually equivalent to:

```text
Python
   ↓
ctypes
   ↓
system libhunspell.so
   ↓
system .aff + .dic
```

Prefer robust native-library discovery mechanisms such as:

```python
ctypes.util.find_library(...)
```

where appropriate.

Do not hardcode a single ABI filename such as:

```text
libhunspell-1.7.so.0
```

unless required as a documented fallback.

Different Linux releases may ship different compatible Hunspell versions.

---

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

# 10. Linux MyThes

The user has verified that:

```text
mythes-es
```

provides working Spanish synonym/thesaurus data on Linux.

Create a MyThes-compatible thesaurus resolver capable of discovering system-installed thesaurus resources.

Search appropriate system directories based on actual Debian/Ubuntu packaging and the current project environment.

Do not assume that every installed Hunspell language also has a MyThes thesaurus.

These are independent capabilities:

```text
Spanish
    Spell checking: available
    Thesaurus: available

Another language
    Spell checking: available
    Thesaurus: unavailable
```

That is a perfectly valid state.

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

# 12. Debian/Ubuntu packaging compatibility

This architecture should be friendly to eventual Debian packaging.

GuitarChordStudio should not unnecessarily vendor libraries or dictionaries that Debian/Ubuntu already manage well.

The intended Linux model is:

```text
GuitarChordStudio
        │
        ├── system Hunspell library
        │
        ├── system Hunspell dictionaries
        │
        └── system MyThes resources
```

This also allows the distribution to:

* update dictionaries;
* patch security issues;
* update Hunspell;
* manage licenses;
* manage dependencies.

Do not undermine that package-management model.

---

# 13. Windows strategy is intentionally different

Windows does not have Debian's package-management infrastructure.

Therefore, on Windows GuitarChordStudio WILL manage its own linguistic resources.

The intended architecture is:

```text
GuitarChordStudio
        │
        ├── bundled libhunspell.dll
        │
        ├── managed Hunspell dictionaries
        │
        └── managed MyThes thesauri
```

This is expected and correct.

Do NOT try to force Linux and Windows to use identical deployment strategies.

They need the same public API, not the same resource distribution mechanism.

---

# 14. Windows Hunspell DLL already exists

Hunspell 1.7.3 has already been compiled manually from the official source code using:

```text
Microsoft Visual Studio
MSVC
Release_dll
x64
```

The resulting library is:

```text
libhunspell.dll
```

This DLL was tested with VirusTotal and that specific build produced:

```text
0 / 71 detections
```

Therefore:

**DO NOT rebuild Hunspell.**

**DO NOT download another Hunspell DLL.**

**DO NOT use the `hunspell` Python package from PyPI as the primary backend.**

**DO NOT use `cyhunspell` as the primary backend.**

Use the existing MSVC-built:

```text
libhunspell.dll
```

---

# 15. Important wording about the Windows DLL

Do not describe this DLL as:

```text
Microsoft Hunspell DLL
```

or:

```text
Microsoft's Hunspell library
```

That would be incorrect.

The correct description is:

```text
Hunspell 1.7.3 built from the official Hunspell source code
using Microsoft Visual Studio/MSVC.
```

Microsoft provided the compiler/toolchain, not Hunspell itself.

---

# 16. Windows DLL location

Prefer:

```text
resources/
└── hunspell/
    └── libhunspell.dll
```

If the repository already uses another coherent location, inspect it before changing anything.

The Windows loader must work when running:

* directly from source;
* from a virtual environment;
* from a Nuitka standalone build;
* from a future Nuitka onefile build if used.

Do not rely on:

```text
PATH
C:\Windows
C:\Windows\System32
```

---

# 17. Windows linguistic resources

Application-managed dictionaries should live in an appropriate per-user location obtained through:

```python
QStandardPaths
```

Do not manually construct AppData paths in multiple modules.

Conceptually:

```text
GuitarChordStudio/
└── linguistic-resources/
    ├── dictionaries/
    │   ├── es_ES.aff
    │   ├── es_ES.dic
    │   ├── de_DE.aff
    │   ├── de_DE.dic
    │   ├── ru_RU.aff
    │   └── ru_RU.dic
    │
    ├── thesauri/
    │   └── ...
    │
    └── personal/
        └── ...
```

Do not assume those exact files already exist.

Discover what the repository currently contains first.

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

---

# 21. macOS

The application also targets macOS.

Design the provider architecture now so that macOS has a clean extension point:

```python
class MacOSLinguisticProvider:
    ...
```

However:

**Do not invent an unverified macOS packaging strategy.**

First inspect the existing repository and current macOS behavior.

Implement only what can be supported confidently.

If macOS resource management cannot be completed during this task, document it clearly as pending rather than copying the Windows strategy blindly.

---

# 22. One common Hunspell backend where possible

Linux and Windows should not require completely separate spelling engines.

The native backend should ideally be common:

```text
                    HunspellNativeBackend
                           │
              ┌────────────┴────────────┐
              │                         │
           Linux                     Windows
              │                         │
       libhunspell.so             libhunspell.dll
       from system                bundled with app
```

Once the native library is loaded, the wrapper should expose the same API.

The platform-specific difference should mainly concern:

```text
Where is the native library?
Where are the dictionaries?
Who manages those resources?
```

---

# 23. Proposed reusable architecture

Inspect the existing repository before choosing exact names, but conceptually create something similar to:

```text
linguistics/
├── __init__.py
│
├── core/
│   ├── language.py
│   ├── paths.py
│   ├── normalization.py
│   ├── capabilities.py
│   └── diagnostics.py
│
├── native/
│   ├── hunspell.py
│   └── library_resolver.py
│
├── providers/
│   ├── base.py
│   ├── linux.py
│   ├── windows.py
│   └── macos.py
│
├── spellcheck/
│   ├── engine.py
│   ├── dictionary_resolver.py
│   ├── tokenizer.py
│   ├── personal_dictionary.py
│   └── highlighter.py
│
├── thesaurus/
│   ├── engine.py
│   ├── mythes.py
│   ├── resolver.py
│   └── models.py
│
└── qt/
    ├── spell_text_edit.py
    ├── spell_plain_text_edit.py
    ├── context_menu.py
    ├── language_menu.py
    └── resource_dialog.py
```

Names may change if the existing project architecture suggests something better.

The important separation is:

```text
native API
platform providers
spell checking
thesaurus
Qt integration
applications
```

---

# 24. Do not call the Python package `hunspell`

Avoid creating:

```text
hunspell/
```

as a top-level Python package.

It could conflict with third-party Python modules.

Use a distinctive namespace such as:

```text
gcs_linguistics
qt_linguistics
pyqt_linguistics
```

or another appropriate project-specific name.

---

# 25. Existing code must be audited first

Before modifying anything, inspect all current spell-checking and dictionary-related code, including at minimum:

```text
chordflow/spellcheck.py
chordflow/dict_manager.py
chordpages/spellcheck.py
chordflow/main_window.py
chordpages/ui/page_editor.py
dictionaries.json
resources/
build/
```

and any other relevant files you discover.

Determine:

* how ChordFlow currently performs spell checking;
* how ChordPages reuses ChordFlow;
* how dictionaries are currently located;
* what works on Linux;
* what currently fails on Windows;
* whether MyThes support already exists;
* where language settings are stored;
* how Nuitka currently packages resources.

Do not replace working Linux behavior blindly.

---

# 26. Preserve working Linux behavior

This requirement is critical.

The existing Linux implementation already works for at least the user's tested Spanish configuration using distribution packages.

Do not regress that functionality while fixing Windows.

Before refactoring, establish tests or diagnostic scripts that demonstrate the existing Linux behavior.

After refactoring, verify equivalent or improved behavior.

---

# 27. Native Hunspell wrapper

Use Python's standard:

```python
ctypes
```

for the native API.

Create a low-level class conceptually similar to:

```python
class HunspellNative:
    ...
```

It should be responsible only for:

* loading the native library;
* defining the C function signatures;
* creating Hunspell handles;
* destroying handles;
* encoding strings;
* decoding results;
* releasing native memory.

Qt widgets must never call `ctypes` directly.

---

# 28. Use the actual Hunspell headers

Inspect the Hunspell 1.7.3 headers already present in the repository.

Do not guess function signatures.

At minimum inspect the actual declarations for:

```text
Hunspell_create
Hunspell_create_key
Hunspell_destroy
Hunspell_spell
Hunspell_suggest
Hunspell_free_list
Hunspell_add
Hunspell_add_with_affix
Hunspell_remove
Hunspell_get_dic_encoding
Hunspell_analyze
Hunspell_stem
Hunspell_generate
```

Set:

```python
argtypes
restype
```

once after loading the library.

---

# 29. `Hunspell_suggest()` memory handling is critical

Verify the exact Hunspell 1.7.3 C API.

Represent the `char ***` output correctly with `ctypes`.

The intended flow is:

```text
Hunspell_suggest()
        ↓
read N strings
        ↓
convert to Python strings
        ↓
Hunspell_free_list()
```

Avoid:

* memory leaks;
* double-free;
* invalid pointer arithmetic;
* out-of-bounds access.

This must be covered by tests.

---

# 30. Handle lifecycle

Provide an idempotent:

```python
close()
```

For example:

```python
checker = SpellChecker("es_ES")

...

checker.close()
checker.close()
```

must not crash.

Use `weakref.finalize` or another safe strategy if appropriate.

---

# 31. Common public spell-checking API

The applications should use something similar to:

```python
checker = SpellChecker("es_ES")

checker.available
checker.language
checker.resolved_language
checker.dictionary_encoding

checker.check("maravillas")
checker.suggest("marabillas")

checker.add_word("ChordFlow")
checker.remove_personal_word("ChordFlow")

checker.set_language("de_DE")

checker.close()
```

ChordFlow must not know whether the backend is using:

```text
/usr/lib/.../libhunspell.so
```

or:

```text
resources/hunspell/libhunspell.dll
```

---

# 32. Dictionary encoding

Do NOT assume every Hunspell dictionary is UTF-8.

Hunspell `.aff` files may declare:

```text
SET UTF-8
SET ISO8859-1
SET ISO8859-15
SET CP1251
...
```

Prefer:

```text
Hunspell_get_dic_encoding()
```

when supported by the actual API.

Use parsing of:

```text
SET ...
```

as a fallback.

The selected encoding must be used consistently for:

```text
spell
suggest
add
remove
analyze
stem
generate
```

and for decoding suggestions.

This is especially important for multilingual support such as Russian and Central/Eastern European languages.

---

# 33. Unicode normalization

Normalize input appropriately, preferably using:

```python
unicodedata.normalize("NFC", word)
```

or an equivalent justified approach.

The system must handle words such as:

```text
Señor
creación
corazón

Straße
schön
über

français
école

Москва
Россия
привет

ação
coração
```

without encoding exceptions or corruption.

---

# 34. Do not lowercase everything

Do NOT blindly do:

```python
word = word.lower()
```

before calling Hunspell.

Capitalization can be linguistically meaningful.

Test:

```text
canta
Canta
CANTA

toda
Toda
TODA
```

and respect Hunspell's response.

---

# 35. Locale handling

Support locale identifiers such as:

```text
es_ES
es_EC
es_MX

en_US
en_GB

de_DE
de_AT
de_CH

pt_BR
pt_PT

ru_RU
fr_FR
```

but only advertise resources that are actually available.

---

# 36. Regional fallback

If:

```text
es_EC
```

is requested but unavailable, a documented fallback may be used.

Conceptually:

```text
es_EC
  ↓
compatible es_* resource
  ↓
configured default such as es_ES
```

but only if that fallback actually exists.

Do not fabricate dictionary paths.

The application must distinguish:

```text
Requested language: es_EC
Resolved dictionary: es_ES
```

in diagnostics.

---

# 37. Available language discovery

Expose something like:

```python
available_languages()
```

The result must be derived from actual installed/managed resources.

On Linux this means system resources.

On Windows this means application-managed resources.

Do not maintain a fake list of languages that may not exist.

---

# 38. Human-readable language names

Use:

```python
QLocale
```

where practical instead of maintaining a huge hand-written locale table.

The UI may display names such as:

```text
English (United States)
English (United Kingdom)
Spanish (Spain)
Spanish (Ecuador)
German (Germany)
Russian (Russia)
French (France)
```

Internally retain locale codes such as:

```text
en_US
es_ES
de_DE
ru_RU
```

---

# 39. English-first user interface

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

# 40. Qt Linguist internationalization

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

# 41. Language persistence

Store the selected spell-checking language using the existing Qt settings infrastructure.

For example:

```text
spellcheck/language = es_ES
```

or an equivalent key consistent with the current application.

The selection must survive application restarts.

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

# 46. Spell-check cache

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

# 52. Thesaurus is not Hunspell spell checking

Do not misuse Hunspell as the thesaurus implementation.

Create a separate API:

```python
class ThesaurusEngine:
    def lookup(self, word: str):
        ...
```

Spell checking uses:

```text
Hunspell
.aff
.dic
```

Synonyms use:

```text
MyThes-compatible thesaurus data
```

or another explicitly supported thesaurus backend.

---

# 53. MyThes parser/backend

Implement a reusable MyThes-compatible backend based on the actual resources available in the repository/system.

Do not assume every language package has exactly the same filenames.

Inspect actual data.

Support appropriate `.dat`, `.idx`, or other required files according to the real MyThes format being consumed.

Do not invent missing indexes.

---

# 54. Preserve thesaurus meanings

If a thesaurus distinguishes multiple meanings, do not flatten everything into one giant synonym list.

Use models such as:

```python
@dataclass
class ThesaurusMeaning:
    definition: str | None
    synonyms: list[str]
```

and:

```python
@dataclass
class ThesaurusResult:
    word: str
    meanings: list[ThesaurusMeaning]
```

Adapt these models if the actual MyThes data suggests a better representation.

---

# 55. Thesaurus Unicode

Thesaurus lookup must correctly support Unicode, including:

```text
Spanish
German
French
Russian
Portuguese
```

without `UnicodeEncodeError` or `UnicodeDecodeError`.

---

# 56. Spell-check and thesaurus availability are independent

The resource registry should be able to represent:

```python
LanguageResources(
    locale="es_ES",
    spellcheck_available=True,
    thesaurus_available=True,
)
```

or:

```python
LanguageResources(
    locale="some_locale",
    spellcheck_available=True,
    thesaurus_available=False,
)
```

A missing thesaurus must never disable spell checking.

---

# 57. Resource-provider abstraction

Create a clean provider abstraction.

Conceptually:

```python
class LinguisticResourceProvider:
    def available_spell_languages(self): ...
    def available_thesaurus_languages(self): ...
    def resolve_spell_dictionary(self, locale): ...
    def resolve_thesaurus(self, locale): ...
    def capabilities(self): ...
```

Then:

```text
LinuxSystemProvider
WindowsManagedProvider
MacOSProvider
```

The rest of the application should not care which provider is active.

---

# 58. Platform detection in one place

Platform branching should be centralized.

For example:

```python
provider = create_platform_provider()
```

Do NOT spread code like this throughout ChordFlow and ChordPages:

```python
if sys.platform.startswith("linux"):
    ...
elif sys.platform == "win32":
    ...
```

A small amount of platform detection inside the provider factory is expected.

Repeated platform checks throughout the UI are not.

---

# 59. Platform capabilities

The provider should expose capabilities instead of forcing the UI to know platform details.

Conceptually:

```python
capabilities.system_managed_resources
capabilities.can_download_dictionaries
capabilities.can_remove_dictionaries
capabilities.can_download_thesauri
capabilities.can_show_package_hint
```

For Linux:

```text
system_managed_resources = True
can_download_dictionaries = False
can_remove_dictionaries = False
can_download_thesauri = False
can_show_package_hint = True
```

For Windows:

```text
system_managed_resources = False
can_download_dictionaries = True
can_remove_dictionaries = True
can_download_thesauri = True
```

assuming licenses permit those operations.

---

# 60. UI behavior based on capabilities

Do not write:

```python
if platform.system() == "Linux":
    hide_download_button()
```

Instead use:

```python
if not provider.capabilities.can_download_dictionaries:
    ...
```

This keeps platform policy out of the Qt widgets.

---

# 61. Linux resource dialog

On Linux, a Language Resources dialog should primarily show:

```text
Language Resources

Spanish (Spain)
Spell checking: Installed
Thesaurus: Installed

German (Germany)
Spell checking: Installed
Thesaurus: Not installed
```

If something is missing, offer:

```text
System package information
```

rather than:

```text
Download
```

---

# 62. Windows resource dialog

On Windows the same dialog may show:

```text
Language Resources

Spanish (Spain)
Spell checking: Installed
Thesaurus: Installed

German (Germany)
Spell checking: Not installed
Thesaurus: Not installed

[Download]
```

The visual design can remain largely common while provider capabilities determine available actions.

---

# 63. No privilege elevation from the application

This applies especially to Linux.

Do NOT introduce code that invokes:

```text
sudo
pkexec
su
apt
apt-get
dpkg
synaptic
```

for installing linguistic resources.

Do not add Polkit rules for this purpose.

The application must remain an ordinary desktop application.

---

# 64. Diagnostics

Create:

```text
tools/linguistics_diagnostics.py
```

It should report useful information such as:

```text
Operating system:
Python architecture:
Provider:
Resource management mode:

Hunspell library:
Hunspell library loaded:

Requested locale:
Resolved locale:

AFF:
DIC:
Dictionary encoding:

Thesaurus:
Personal dictionary:
```

On Linux additionally report something like:

```text
Resource source: system
```

On Windows:

```text
Resource source: application
```

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

---

# 66. Windows diagnostics

Conceptually:

```text
Platform: Windows
Provider: WindowsManagedProvider

Hunspell:
    DLL: .../resources/hunspell/libhunspell.dll
    architecture: x64
    status: loaded

Spanish:
    AFF: ...
    DIC: ...

Thesaurus:
    ...
```

---

# 67. Windows architecture check

The current DLL is x64.

Verify compatibility among:

```text
Python architecture
Nuitka application architecture
libhunspell.dll architecture
```

A mismatch should produce a clear diagnostic rather than an unexplained crash.

---

# 68. Windows MSVC runtime

Determine what runtime the compiled:

```text
libhunspell.dll
```

actually requires.

Do not copy arbitrary Microsoft runtime DLLs.

Document whether the final application requires the Microsoft Visual C++ Redistributable or whether Nuitka/installer deployment already handles the required runtime.

---

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

# 70. Linux packaging

Do not bundle the Windows DLL into Linux packages.

Linux builds should resolve Hunspell through the system.

When preparing Debian metadata, use appropriate dependency/recommendation relationships based on the actual packaging strategy.

Do not make every possible language dictionary a mandatory dependency.

A user may only need one or two languages.

---

# 71. Consider package recommendations carefully

For Debian packaging, distinguish:

```text
core runtime requirement
optional language resources
```

Hunspell runtime/library requirements may belong in normal dependencies.

Individual language dictionaries and MyThes packages may be optional/recommended/suggested depending on final packaging policy.

Do not make:

```text
hunspell-es
hunspell-de-*
hunspell-ru
mythes-es
...
```

all mandatory dependencies.

Document recommendations instead.

---

# 72. Logging

Use:

```python
logging
```

rather than scattered `print()` calls.

DEBUG information may include:

```text
platform provider selected
native library found
native library loaded
requested locale
resolved locale
AFF path
DIC path
dictionary encoding
thesaurus path
resource source
fallback used
```

Use WARNING/ERROR appropriately.

---

# 73. Backend failure behavior

If Hunspell cannot be loaded:

**Do NOT mark every word as misspelled.**

Instead:

```python
checker.available == False
```

The editor must remain usable without spell checking.

Likewise, a missing thesaurus must not break the context menu or editor.

---

# 74. Performance

Do not load every installed language simultaneously.

Primarily load the currently selected spell-checking language.

Load thesaurus resources lazily when synonyms are first requested if practical.

Do not repeatedly scan `/usr/share` on every keystroke.

Cache resource discovery appropriately.

---

# 75. Threading

Do not add threads unnecessarily for native spell checks if they are fast.

Dictionary/resource downloads on Windows may use background work if the existing architecture supports it.

Document thread-safety assumptions for the native Hunspell wrapper.

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

# 91. ChordFlow integration

Migrate ChordFlow to the common infrastructure.

Preserve existing functionality including:

* spell checking;
* chord handling;
* context menus;
* language selection;
* personal words;
* application settings.

Add thesaurus integration where resources exist.

---

# 92. ChordPages integration

ChordPages must use exactly the same linguistic infrastructure.

Do NOT copy:

```text
hunspell wrapper
tokenizer
resource resolver
MyThes parser
```

into ChordPages.

ChordPages should consume the common API.

---

# 93. Zero duplicated engines

The target is:

```text
1 Hunspell native wrapper
1 spell-check engine
1 tokenizer
1 resource-provider abstraction
1 MyThes/thesaurus subsystem
```

shared by:

```text
ChordFlow
ChordPages
future PyQt6 applications
```

---

# 94. Do not break unrelated features

Do not regress:

* chord transposition;
* auto-scroll;
* tabs;
* file loading/saving;
* pagination;
* printing;
* exporting;
* themes;
* translations;
* settings.

---

# 95. Prepare for future extraction

The linguistic package must not import ChordFlow UI internals.

Do NOT create dependencies such as:

```python
from chordflow.main_window import ...
```

inside the linguistic core.

The dependency direction must be:

```text
ChordFlow
    ↓
linguistics
```

not:

```text
linguistics
    ↓
ChordFlow
```

---

# 96. Future standalone PyQt6 Linguistics Toolkit

Although the code initially lives inside GuitarChordStudio, design it so that it could later become an independent project such as:

```text
PyQt6 Linguistics Toolkit
```

without rewriting the core.

A future application should be able to do something conceptually like:

```python
from pyqt_linguistics import SpellChecker
from pyqt_linguistics.qt import SpellTextEdit
```

Do NOT publish anything to PyPI during this task.

---

# 97. Documentation

Create:

```text
docs/linguistics-architecture.md
```

Explain clearly:

* common API;
* Hunspell native backend;
* MyThes;
* platform providers;
* Linux system-resource policy;
* Windows managed-resource policy;
* personal dictionaries;
* Qt integration;
* Nuitka deployment;
* internationalization.

Reference the existing:

```text
BUILD_HUNSPELL_WINDOWS.md
```

rather than duplicating all Windows compilation instructions.

---

# 98. Linux documentation

Explicitly document:

> GuitarChordStudio does not install system Hunspell dictionaries or MyThes packages on Linux. Language resources must be installed through the Linux distribution's package manager.

Include examples for Debian/Ubuntu only when the package names are known and verified.

For example:

```bash
sudo apt install hunspell-es mythes-es
```

may be documented for Spanish if confirmed.

Make clear that the command is executed manually by the user, not by GuitarChordStudio.

---

# 99. Windows documentation

Document that Windows uses:

```text
Hunspell 1.7.3
built with Microsoft Visual Studio/MSVC
Release_dll
x64
```

and that the application loads:

```text
libhunspell.dll
```

Do not imply that Microsoft distributes Hunspell.

---

# 100. README for reusable package

Create documentation inside the linguistic package explaining basic usage.

For example:

```python
checker = SpellChecker("en_US")

if checker.check("hello"):
    ...
```

and:

```python
editor = SpellTextEdit()
editor.set_spell_language("en_US")
```

The examples should be English-first.

---

# 101. Tests without native resources

Components such as:

```text
tokenizer
platform capabilities
locale handling
resource registry
MyThes parser
path logic
```

should be testable independently where possible.

Use dependency injection/mocks appropriately.

---

# 102. Tests with actual system resources

On Linux:

If system Hunspell/MyThes resources are installed, run integration tests against them.

If an optional language is missing:

```text
SKIP
```

with an explicit reason.

Do not download it during the test.

On Windows:

If the bundled `libhunspell.dll` and relevant managed dictionaries are present, run native integration tests.

---

# 103. Git safety

Before modifying:

```bash
git status
```

Do not run destructive commands such as:

```bash
git reset --hard
git clean -fd
```

Do not discard existing user changes.

Do not delete the compiled Windows Hunspell DLL.

---

# 104. Work in phases

## Phase 1 — Audit

Inspect the current repository.

Report briefly:

* current spell-check architecture;
* current thesaurus architecture;
* current Linux behavior;
* current Windows behavior;
* current dictionary locations;
* current MyThes locations;
* ChordFlow/ChordPages code sharing;
* current build/deployment logic.

Then continue.

---

## Phase 2 — Common models and providers

Implement:

```text
platform provider abstraction
LinuxSystemProvider
WindowsManagedProvider
macOS extension point
capabilities
resource models
locale handling
diagnostics
```

Tests.

---

## Phase 3 — Native Hunspell layer

Implement:

```text
cross-platform native-library resolver
ctypes API
encoding
lifecycle
suggestion memory management
```

Tests.

---

## Phase 4 — Spell-check engine

Implement:

```text
SpellChecker
dictionary resolution
tokenization
chord filtering
cache
personal dictionaries
```

Tests.

---

## Phase 5 — MyThes/thesaurus

Implement:

```text
ThesaurusEngine
MyThes parser/backend
resource resolution
meaning models
```

Tests.

---

## Phase 6 — Reusable PyQt6 layer

Implement:

```text
SpellHighlighter
SpellTextEdit
SpellPlainTextEdit
context menu
language menu
resource dialog
synonyms
```

All source UI strings must be English and translatable.

---

## Phase 7 — ChordFlow migration

Migrate ChordFlow to the common infrastructure.

Test existing behavior.

---

## Phase 8 — ChordPages migration

Migrate ChordPages.

Do not duplicate linguistic code.

---

## Phase 9 — Linux validation

Validate on Linux using system-installed resources only.

Do not install anything automatically.

Report what packages/resources were actually detected.

---

## Phase 10 — Windows validation

Validate using:

```text
libhunspell.dll
```

and application-managed resources.

Verify Windows 10/11 x64 deployment assumptions.

---

## Phase 11 — Nuitka

Ensure Windows builds include the required native DLL/resources.

Ensure Linux builds do not accidentally bundle the Windows DLL.

---

# 105. Final report

At completion provide:

## Previous architecture

Brief summary.

## New architecture

Include a diagram.

## Files created

List.

## Files modified

List.

## Linux provider

Report:

```text
Hunspell library detected:
Hunspell dictionaries detected:
MyThes resources detected:
Resource management mode: system/read-only
```

Do not invent results.

## Windows provider

Report:

```text
Hunspell DLL:
Architecture:
Dictionaries:
Thesauri:
Resource management mode: application-managed
```

## macOS

Report exactly what was implemented and what remains pending.

## Spanish test

Report actual results for:

```text
Canta
Toda
maravillas
creación
Señor
marabillas
creasión
```

## Other languages

Report only languages actually tested.

## Thesaurus

Show a real lookup if a compatible thesaurus was available.

## Chord filtering

Report test results.

## Tests

Commands and results.

## Nuitka

Report whether the Windows DLL/resources are correctly packaged.

## Pending issues

List anything that could not be verified.

---

# 106. Non-negotiable Linux rule

The following architecture is REQUIRED:

```text
GNU/Linux
    │
    ▼
GuitarChordStudio
    │
    ├── reads system Hunspell library
    ├── reads system Hunspell dictionaries
    ├── reads system MyThes resources
    │
    └── may write only application-owned data
         ├── personal dictionary
         └── preferences
```

GuitarChordStudio MUST NOT install or modify Linux system linguistic packages.

---

# 107. Non-negotiable Windows rule

The following architecture is REQUIRED:

```text
Windows 10/11 x64
    │
    ▼
GuitarChordStudio
    │
    ├── bundled libhunspell.dll
    ├── application-managed dictionaries
    ├── application-managed thesauri
    └── application-owned personal dictionaries
```

No global Hunspell installation should be required.

---

# 108. Final architectural target

The final architecture should conceptually be:

```text
                         ChordFlow
                             │
                         ChordPages
                             │
                    Future PyQt6 programs
                             │
                             ▼
                 Common PyQt6 Linguistics API
                             │
               ┌─────────────┴─────────────┐
               │                           │
        SpellChecker                 ThesaurusEngine
               │                           │
               ▼                           ▼
        Hunspell backend              MyThes backend
               │                           │
               └─────────────┬─────────────┘
                             │
                    Resource Provider
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
        Linux              Windows            macOS
          │                  │                  │
          ▼                  ▼                  ▼
 System-managed       Application-managed    Provider
 Hunspell/MyThes      linguistic resources   extension
          │                  │
          ▼                  ▼
 libhunspell.so       libhunspell.dll
 /usr/share/...       AppData/resources
```

The applications must have **one common linguistic API**.

The operating systems may have **different resource providers and deployment policies**.

That is intentional.

---

# 109. Core design principle

Do not solve Windows by breaking Linux.

Do not solve Linux by forcing Windows to behave like Debian.

Do not duplicate ChordFlow and ChordPages linguistic code.

The goal is:

> **One reusable PyQt6 linguistic infrastructure, one public API, platform-specific resource providers, system-managed linguistic resources on Linux, application-managed linguistic resources on Windows, and an English-first translatable user interface.**

