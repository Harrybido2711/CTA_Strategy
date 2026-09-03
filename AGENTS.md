# AGENTS.md

**You are working in this repository. Read this file end to end before your first tool call.**

This is the single entry point. Every other agent config here — `CLAUDE.md`,
`.github/copilot-instructions.md` — is a stub that points back at this file. Nothing is duplicated:
if a rule is not here or in a file this one names, it does not exist.

---

## 0. Protocol — do this before anything else

1. **Name the task type** from the dictionary in § 3. Say out loud which row you picked.
2. **Read that row's "Read first" column in full** before you edit anything.
3. **Follow that row's workflow in order.** Do not invent a different one.
4. **Verify the row's "Done when" column** before you claim to be finished.
5. **If no row fits, stop and ask Harry.** Never improvise a workflow.

Rule 5 is the important one. Most of the damage in this repository's history came from an agent
deciding for itself what a task meant.

---

## 1. What this repository is

A ground-up **course on CTA (managed-futures) strategies**, written as formal notes with runnable
code behind them. It is not a library and not a product: nothing here is imported by anything else,
and there is no public API to keep stable.

**The deliverable is the teaching material.** Code exists to produce the numbers and figures the
notes rely on. When a change would improve the code but make a chapter harder to follow, the
chapter wins.

Harry is learning this material as he writes it, so **explanations must be derivable, not
asserted**. A claim in a chapter comes with the argument that discharges it, or is marked as an
open question.

**LaTeX is the source.** Chapters are `.tex`; the PDFs in `docs/read_only_chapters/` are the
published form. Markdown survives only where noted in § 2, and the remaining `.md` chapters are
mid-migration — see **T4**.

---

## 2. Layout: what goes where

| Path | Holds | Format |
| --- | --- | --- |
| `docs/preamble.tex` | The layout layer — the one file that decides what everything looks like | LaTeX |
| `docs/chapters/<NN_slug>/<NN_slug>.tex` | One chapter's body. **A fragment**: no `\documentclass`, no `document` environment | LaTeX |
| `docs/chapters/<NN_slug>/_build/` | Wrapper, `.aux`, `.log`, `.toc` — scratch | gitignored |
| `docs/figures/<NN>_figures/` | That chapter's generator `make_<NN_slug>.py` and the `-light.png` / `-dark.png` pairs it emits | Python + PNG |
| `docs/figures/_style.py`, `_data.py` | Shared design tokens and data. **Never re-declare a colour in a chapter script** | Python |
| `docs/all_chapters.tex` → `docs/all_chapters.pdf` | The bound edition — one `\input` line per chapter | LaTeX |
| `docs/read_only_chapters/<NN_slug>.pdf` | The published PDF of each chapter. **The only place a chapter PDF lives** | committed |
| `docs/build.sh` | The only build entry point | bash |
| `market_knowledge/` | Lecture-sourced notes, each opening with a source blockquote. Not part of the course spine | Markdown |
| `Backtest_prototype/` | `backtest.py`, `analyze_cta_data.py`, `backtester.ipynb` + `Backtests.md` (its write-up) | Python + Markdown |
| `CTA_data/` | 37 daily OHLCV CSVs — **ETFs**, standing in for futures | CSV |
| `conventions/` | The long-form rules this file routes to | Markdown |
| `README.md` | The reader-facing map. **Owned by Harry; do not restructure it** | Markdown |

**The theory/practice split is strict.** `docs/` holds concepts that stay true regardless of this
repo — definitions, proofs, mechanisms. Measured results, derivations over code variables,
reproduction snippets and defects in a particular run go in `Backtest_prototype/Backtests.md`.
**When a chapter starts naming variables from a `.py` file, move that passage out.**

Link straight at files. No index or indirection layer between. Cross-link both ways: a chapter
points forward with `\pointer{...}`, the practical write-up points back at the chapter that owns
the concept.

---

## 3. The task dictionary

| # | Task | Workflow | Skills | Read first | Done when |
| --- | --- | --- | --- | --- | --- |
| **T1** | **New chapter** | 1. `docs/chapters/<NN_slug>/<NN_slug>.tex`, opening with `\chapterhead{NN}{Title}{NN_slug}` · 2. write it · 3. figures via T3 · 4. `./docs/build.sh <NN_slug>` · 5. uncomment its `\input` in `all_chapters.tex` · 6. `./docs/build.sh --book` | — | `conventions/writing-a-chapter.md`; `docs/chapters/05_modelling/05_modelling.tex` (markup); `docs/chapters/01_what_is_cta/01_what_is_cta.md` (logic) | Both builds clean; PDF in `read_only_chapters/`; no `??` in the PDF |
| **T2** | **Revise a chapter** | locate → edit → re-check the notation appendix → `grep -rn` for `\secref`/`\chapref` into the part you touched → rebuild chapter **and** book | — | same as T1 | Same as T1, plus no reference now points at a label that no longer exists |
| **T3** | **Figure** | 1. `nature-figure` design pass **before any plotting code** · 2. add the function to `docs/figures/<NN>_figures/make_<NN_slug>.py` and register it in `FIGURES` · 3. emit both `-light.png` and `-dark.png` · 4. if the chapter's figure dir is new, add it to `\graphicspath` in `preamble.tex` · 5. `\fig{stem}{caption}{fig:label}` · 6. rerun **only that script** | `nature-figure` → then `figures` + `colors` | `docs/figures/_style.py`; `.claude/skills/INDEX.md` | Both PNGs committed; both themes build; both axes labelled with the chapter's symbols |
| **T4** | **Migrate a chapter `.md` → `.tex`** | 1. `pandoc <NN_slug>.md -o draft.tex` as a **draft only** · 2. hand-convert to the house environments (§ 4) — pandoc emits `\textbf{Definition.}`, this repo wants `\begin{definition}` · 3. `<picture>` → `\fig`, chapter links → `\chapref`, `§ N` → `\secref` · 4. `./docs/build.sh <NN_slug>` · 5. **only after the PDF is verified**, delete the `.md` · 6. uncomment its `\input` in `all_chapters.tex` | — | `docs/chapters/05_modelling/05_modelling.tex` — the worked example of the target | PDF reads like 05; `.md` deleted; book builds with the new chapter in it |
| **T5** | **Code / backtest** | edit `.py` → run it → **measured numbers go in `Backtests.md`, never in a chapter** | `run`, `code-review` | `Backtest_prototype/Backtests.md` | The number is reproducible from a snippet in `Backtests.md` |
| **T6** | **Data** | validate → respect the split trap below | — | `docs/chapters/100_dataset/` | — |
| **T7** | **Lecture transcription** | `.vtt` → `market_knowledge/<topic>.md` with its source blockquote → theory worth keeping gets promoted into a chapter later, not now | — | any existing `market_knowledge/*.md` for the shape | Source and date stated; marked "not audited" |
| **T8** | **Build a PDF** | `./docs/build.sh <NN_slug>` · `--dark` · `--all` · `--book` · `--figures` first if a PNG is stale. **Nothing else.** No in-place `pdflatex`, no `latexmk` in `docs/` | — | the header comment of `docs/build.sh` | `read_only_chapters/` updated; nothing new appeared outside `_build/` |
| **T9** | **Repo hygiene / renumbering** | grep for every reference to the thing you are moving *before* moving it → move → repoint → grep again to prove zero dangling | `simplify` | `conventions/repo-hygiene.md` | The greps in that file all come back empty |
| **T10** | **Glossary** | add the bilingual row + a link to the chapter that owns the concept | — | `docs/chapters/99_glossary/` | — |
| **T11** | **Meta — skills, settings, permissions** | — | `update-config`, `fewer-permission-prompts` | `.claude/skills/INDEX.md` | — |

---

## 4. Chapter markup: the interface `preamble.tex` provides

A chapter body carries **no layout instruction of its own** — no font, no colour, no `\vspace`,
no `\usepackage`. Swapping `preamble.tex` must move every chapter at once. Use only these:

| Construct | Use for |
| --- | --- |
| `\chapterhead{NN}{Title}{NN_slug}` | Opens the chapter. Title page + TOC standalone; a book heading with renumbered sections in `--book` |
| `\begin{definition}[Term]` | Introducing a term. State what it *is*, not why it matters |
| `\begin{claim}` | An assertion that can be argued. **Never leave one standing alone** |
| `\begin{proof}` | Discharges a claim when the argument is genuinely deductive — an identity, an algebraic consequence, a bound |
| `\begin{example}` | A concrete worked case with numbers |
| `\begin{note}` | A caveat — something true that cuts against what was just said. **Not** a paragraph marker |
| `\fig{stem}{caption}{fig:label}` | A figure. Picks the `-light`/`-dark` variant to match the build |
| `\secref{sec:label}` | "§ 4.3", clickable |
| `\chapref{text}{NN_slug}` | Another chapter. Links to its PDF standalone, jumps within the book, degrades to plain text if that chapter is not converted yet |
| `\pointer{...}` | A forward arrow to another chapter or to code |
| `\begin{checklist}` + `\checkitem` | The closing checklist |

`definition`, `claim` and `example` share one counter, so they read in document order and can be
`\ref`'d. `note` is unnumbered — nothing refers back to a caveat.

The *editorial* rules — when a claim earns a proof, what → why → how, tables over prose, explaining
every symbol twice, the `Background` section, chapter length — are in
**`conventions/writing-a-chapter.md`**. Read it for T1, T2 and T4.

The *typographic* rules — what `preamble.tex` sets and why, which of them come from the homework
template `docs/math.tex`, and which of that template's habits are deliberately not carried over —
are in **`conventions/latex-formatting.md`**. Read it before changing `preamble.tex`.

---

## 5. Traps that have already bitten

| Trap | Symptom | Avoid it by |
| --- | --- | --- |
| **The 2025-12-05 split** | Five sector SPDRs (XLB, XLE, XLK, XLU, XLY) carry an **unadjusted 2-for-1 split** | Read `docs/chapters/100_dataset/` before trusting any result spanning that date. Unadjusted originals are in `CTA_data/_unadjusted_raw/`, deliberately outside the `*_ohlcv_1d.csv` glob |
| **A dead figure** | A figure no chapter references any more | Delete the function, its `FIGURES` entry, its docstring line and **both** PNGs together |
| **Renumbering** | `\secref`/`\chapref` targets vanish and the PDF prints `??` | T9. Grep before you move, grep after |
| **Build junk escaping** | `.aux`/`.log`/`.toc` appear outside `_build/` | Only ever `./docs/build.sh`. It is the reason those files stopped littering `docs/` |
| **Markdown table formatter** | In the surviving `.md` files only: `asset $s$ over` becomes `asset$s$ over`; `sort on **vol**` becomes `sort on**vol**` | Lead a cell with its bold label; keep inline math out of prose columns. **Does not apply to `.tex`** |

---

## 6. Git

After completing a modification, `git add`, `git commit` and `git push` to `origin main` without
being asked. One commit per coherent unit of work; the message says what changed **conceptually**,
not "update files".

- **No AI attribution.** No `Co-Authored-By: Claude` trailer, no "generated by".
- `CLAUDE.md`, `.claude/` and `chat_records/` are gitignored — never re-add them.
- The chapter PDFs in `read_only_chapters/` and `all_chapters.pdf` **are** committed: they are what
  a reader without a TeX install opens.
- Force-push, history rewriting and branch deletion need explicit approval.

---

## 7. First run on a new machine

`CLAUDE.md` is gitignored, so a fresh clone has no Claude Code entry point. Recreate it — this is
its entire contents:

```markdown
# CLAUDE.md

This repository's conventions live in AGENTS.md — the entry point and task dictionary.

@AGENTS.md
```

It carries no rules of its own. If you ever find yourself editing `CLAUDE.md` to record a
convention, you are creating a second source of truth: put it in this file instead.

---

## 8. How to know you are done

- You named a task type before you started, and followed that row.
- The chapter reads like `01_what_is_cta` in its logic and like `05_modelling` in its markup.
- Every claim is discharged, every symbol is glossed twice, every figure exists in both themes.
- `./docs/build.sh <chapter>` and `./docs/build.sh --book` both run clean, and no `??` survives.
- Nothing new appeared outside `_build/`.
- The commit message says what changed conceptually.
