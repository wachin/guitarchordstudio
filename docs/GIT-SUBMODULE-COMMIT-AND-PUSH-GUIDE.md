# Git Add, Commit, and Push Guide for Nested Submodules

This guide explains the workflow used by GuitarChordStudio when changes exist
inside Git submodules. The essential rule is:

> Commit and push from the deepest changed repository first, then continue
> upward until the principal repository has been committed and pushed.

## Why the order matters

GuitarChordStudio contains this nested repository structure:

```text
guitarchordstudio                         principal repository
└── libs/pyqt6-linguistic-tools          submodule
    ├── libs/pythes                      nested submodule
    └── libs/spylls                      nested submodule
```

A parent repository does not store all the files contained in a submodule. It
stores only the exact commit identifier that the submodule should use.
Therefore, running `git add .` in GuitarChordStudio cannot commit uncommitted
files inside PyThes or `pyqt6-linguistic-tools`.

For example, when PyThes is changed, the required order is:

```text
PyThes commit
    ↓
pyqt6-linguistic-tools records the new PyThes commit
    ↓
GuitarChordStudio records the new pyqt6-linguistic-tools commit
```

## Before committing

Enter the repository that contains the actual changed files and inspect it:

```bash
git status
git branch --show-current
```

If `git branch --show-current` prints nothing, the submodule has a detached
`HEAD`. Switch to the branch used by that repository before committing:

```bash
git switch master
```

or, when its default branch is `main`:

```bash
git switch main
```

Uncommitted changes are normally preserved when the branch and detached
`HEAD` point to the same commit. If Git refuses the switch, do not use
`git reset --hard` or force the operation. Read the error and protect the
changes before continuing.

## Step 1: commit and push the deepest changed repository

For a change in PyThes:

```bash
cd ~/Dev/guitarchordstudio-Dev/guitarchordstudio/libs/pyqt6-linguistic-tools/libs/pythes

git switch master
git status
git add .
git status
git diff --cached
git commit -m "fix: describe the PyThes change"
git push origin master
git status
```

`git add .` stages every changed and untracked file belonging to the current
repository. Always review `git status` and preferably `git diff --cached`
before committing so that unrelated or generated files are not uploaded.

The final `git status` should report a clean working tree.

## Step 2: commit and push the containing submodule

After PyThes has a new commit, `pyqt6-linguistic-tools` sees its submodule
pointer as changed. Move to that repository and record it:

```bash
cd ~/Dev/guitarchordstudio-Dev/guitarchordstudio/libs/pyqt6-linguistic-tools

git switch main
git status
git add .
git status
git diff --cached
git commit -m "chore: update PyThes and linguistic tools"
git push origin main
git status
```

This commit can include both the new PyThes pointer and ordinary files that
belong directly to `pyqt6-linguistic-tools`.

## Step 3: commit and push the principal repository

Finally, GuitarChordStudio must record the new
`pyqt6-linguistic-tools` commit:

```bash
cd ~/Dev/guitarchordstudio-Dev/guitarchordstudio

git switch main
git status
git add .
git status
git diff --cached
git commit -m "chore: update pyqt6-linguistic-tools submodule"
git push origin main
git status
```

At this point all three repositories have been pushed in the correct order.

## Using a longer commit message

The first `-m` is normally a short summary. Additional `-m` options create
separate paragraphs in the commit description:

```bash
git commit -m "feat: add linguistic tooling" \
  -m "Add the reusable package structure and tests." \
  -m "Record the updated PyThes submodule commit."
```

Use messages that describe what changed in the current repository. A parent
repository usually records a submodule update, while the detailed engine fix
belongs in the engine repository's commit.

## When Spylls and PyThes both changed

They are sibling submodules, so commit and push each one first, in either
order. Then commit `pyqt6-linguistic-tools` once so it records both new commit
identifiers. Finally, commit GuitarChordStudio.

Do not create a commit in a clean submodule. If `git status` says there is
nothing to commit, continue with the repositories that actually changed.

## Final verification

From the GuitarChordStudio root, run:

```bash
git status
git submodule status --recursive
```

The principal working tree should be clean. A `+` before a submodule commit
means its checked-out commit differs from the commit recorded by its parent;
return to the parent repository and commit the updated submodule pointer.
A `-` means that the submodule has not been initialized.

After cloning the project on another computer, initialize every level with:

```bash
git submodule update --init --recursive
```

## Short checklist

For every changed repository, starting with the deepest one:

1. Enter the repository.
2. Switch from detached `HEAD` to its normal branch when necessary.
3. Run `git status`.
4. Run `git add .`.
5. Review the staged changes.
6. Run `git commit -m "message"`.
7. Run `git push` or `git push origin <branch>`.
8. Confirm that `git status` is clean.
9. Move one repository upward and repeat.
