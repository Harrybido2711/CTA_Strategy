# Repo hygiene

Routed to from [`AGENTS.md`](../AGENTS.md) § 3, task **T9** — moving, renaming, renumbering or
deleting anything that other files point at.

**The rule: grep before you move, grep after.** Every mess in this repository's history came from
moving a file and discovering the references weeks later. Run these from the repo root.

---

## 1. Before you move anything

Find every reference to the thing you are about to touch. Chapter stems appear in more places than
you expect — sibling chapters, the glossary, `all_chapters.tex`, `Backtests.md`, `README.md`,
figure-script docstrings.

```bash
STEM=05_modelling      # or a figure stem, or a filename
grep -rn "$STEM" --include='*.tex' --include='*.md' --include='*.py' --include='*.sh' \
  . | grep -v '^./.git' | grep -v '_build/'
```

Only after that list is empty or repointed is the move finished.

---

## 2. The checks that must come back empty

### A chapter that nothing can reach

Every `\chapref{text}{stem}` must name a real chapter directory.

```bash
grep -rho '\\chapref{[^}]*}{\([^}]*\)}' docs/chapters --include='*.tex' \
  | sed 's/.*}{\(.*\)}/\1/' | sort -u \
  | while read -r s; do [ -d "docs/chapters/$s" ] || echo "dangling chapref: $s"; done
```

`\chapref` degrades to plain text for an unconverted chapter rather than printing `??`, so a broken
one is **silent**. This grep is the only thing that catches it.

### A book line pointing at nothing

```bash
grep -v '^ *%' docs/all_chapters.tex | grep -o '\\input{chapters/[^}]*}' \
  | sed 's/\\input{\(.*\)}/\1/' \
  | while read -r p; do [ -f "docs/$p.tex" ] || echo "dangling \\input: $p"; done
```

`grep -v '^ *%'` drops the commented-out lines: `all_chapters.tex` keeps one `\input` per chapter
and comments out the ones still in Markdown, so an uncommented line is the only real reference.

### An unresolved cross-reference in a built PDF

```bash
grep -c 'Reference.*undefined\|LaTeX Warning: Label' docs/chapters/*/_build/*.log docs/_build/*.log
```

A `??` in the PDF always shows up here first. Two `pdflatex` passes are required precisely because
pass one has no labels yet — if `build.sh` was bypassed, this is what it looks like.

### A dead figure

A PNG that no chapter references any more. Delete the generator function, its `FIGURES` entry, its
docstring line and **both** PNGs together — a half-deleted figure is worse than a live one.

```bash
for f in docs/figures/*_figures/*-light.png; do
  s=$(basename "$f" -light.png)
  grep -rq "$s" docs/chapters --include='*.tex' --include='*.md' || echo "dead figure: $s"
done
```

The `--include='*.md'` matters until the migration is done: a figure referenced only from a chapter
still in Markdown is alive, not dead. Drop it once `docs/chapters/` holds no `.md`, at which point
the check tightens to `\fig{$s}` in `.tex` alone.

### A figure directory the preamble cannot see

`\graphicspath` in `preamble.tex` lists the search directories explicitly. A new chapter's figures
are invisible until its directory is added.

```bash
for d in docs/figures/*_figures/; do
  grep -q "$(basename "$d")" docs/preamble.tex || echo "not in graphicspath: $d"
done
```

### Build junk that escaped

Everything transient belongs in a `_build/`. If this prints anything, someone ran `pdflatex` by
hand instead of `./docs/build.sh`.

```bash
find docs -name '*.aux' -o -name '*.log' -o -name '*.toc' -o -name '*.out' \
     -o -name '*.fls' -o -name '*.fdb_latexmk' -o -name '*.synctex.gz' \
  | grep -v '_build/'
```

### A Markdown link to a file that no longer exists

Applies to `README.md`, `market_knowledge/`, `Backtests.md` and any chapter not yet converted.

```bash
grep -rno '](\([^)h][^)]*\.md\)' --include='*.md' . \
  | grep -v '^./.git' | grep -v chat_records
```

Resolve each against the directory of the file it appears in.

---

## 3. Renumbering a chapter

The stem appears in **five** places. Change all of them in one commit:

| Place | What to change |
| --- | --- |
| `docs/chapters/<NN_slug>/` | The directory **and** the `.tex` inside it — they must match |
| `docs/chapters/<NN_slug>/<NN_slug>.tex` | The `\chapterhead{NN}{Title}{NN_slug}` third argument |
| `docs/figures/<NN>_figures/` | The directory, its `make_<NN_slug>.py`, and `\graphicspath` in `preamble.tex` |
| `docs/all_chapters.tex` | Its `\input` line |
| `docs/read_only_chapters/` | The old PDF is now orphaned — delete it and rebuild |

Then rebuild **both** routes: `./docs/build.sh <new_stem>` and `./docs/build.sh --book`. A stale
`all_chapters.pdf` is the failure mode that survives every other check.

---

## 4. Deleting a chapter

Deleting the file is the easy half. The references are the work.

1. Run § 1's grep for the stem. Expect hits in sibling chapters, `99_glossary`, `README.md`,
   `all_chapters.tex` and possibly `Backtest_prototype/Backtests.md`.
2. For each hit, decide: does the *concept* still have a home? If yes, repoint. If no, the sentence
   that referenced it usually has to be rewritten, not just unlinked.
3. Delete the chapter directory, its `docs/figures/<NN>_figures/` directory, its `\graphicspath`
   entry, its `\input` line, and its PDF in `read_only_chapters/`.
4. Re-run every check in § 2.

---

## 5. Done

All of § 2 comes back empty, and both `./docs/build.sh --all` and `./docs/build.sh --book` run
clean.
