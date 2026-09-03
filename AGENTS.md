# AGENTS.md

**Read this file before touching anything.** It is the entry point for any coding agent working in
this repository, and it is the only place the project's conventions are written down.

---

## 1. What this repository is

A ground-up **course on CTA (managed-futures) strategies**, written as a series of formal notes with
runnable code behind them. It is not a library and not a product — nothing here is imported by
anything else, and there is no public API to keep stable.

**The deliverable is the teaching material.** Code exists to produce the numbers and figures the
notes rely on. When a change would improve the code but make a chapter harder to follow, the chapter
wins.

The author is learning this material as he writes it, so **explanations must be derivable, not
asserted**. A claim in `docs/` should come with the argument that discharges it, or be marked as an
open question.

Start with [README.md](README.md) for the chapter list, then [docs/00-index.md](docs/00-index.md)
for the reading order.

---

## 2. Layout: what goes where

| Path | Holds |
| --- | --- |
| `docs/` | **Learning theory** — concepts that stay true regardless of this repo |
| `docs/chapters/<stem>/` | One folder per chapter: `<stem>.tex` (the body) and its `_build/` scratch |
| `docs/figures/<NN>_figures/` | One folder per chapter: that chapter's generator script and the PNGs it emits |
| `docs/figures/_style.py`, `_data.py` | Shared design tokens, drawing primitives, and dataset access |
| `docs/preamble.tex` | The layout layer — the only file that decides what a chapter looks like |
| `docs/build.sh` | The only build entry point |
| `docs/read_only_chapters/` | The published per-chapter PDFs, one per chapter, light theme |
| `docs/all_chapters.tex`, `all_chapters.pdf` | Every chapter bound into one document |
| `Backtest_prototype/` | The first practical part: `Backtests.md` (write-up) + `backtest.py` (code) |
| `CTA_data/` | 37 daily OHLCV CSVs — **ETFs**, standing in for the futures a real CTA would trade |
| `analyze_cta_data.py`, `backtester.ipynb` | Exploratory scratch, not part of the course spine |
| `output/` | Generated artefacts |

The split between theory and practice is strict:

| Content | Home |
| --- | --- |
| Definitions, proofs, mechanisms, market structure | `docs/` |
| Derivations over code variables, measured results, reproduction snippets, defects in a particular run | that part's own `.md` |

The what→why→how *how* stage still belongs in `docs/`, but stated as **mechanism** ("carry the
position as a signed quantity"), not as this repo's code. **When a chapter starts naming variables
from a `.py` file, move the passage** into that part's `.md`.

Link straight at files — `[Implementation Notes](Backtest_prototype/Backtests.md)`, or at the `.py`
itself. No index or indirection layer in between. Cross-link both ways: `docs/` points forward with
`→`, the part's `.md` points back at the chapter that owns the concept.

---

## 3. Routing: what to read before you act

| If you are about to… | Read first |
| --- | --- |
| Write or revise a `docs/` chapter | § 4 below, then [`docs/chapters/01_what_is_cta/01_what_is_cta.md`](docs/chapters/01_what_is_cta/01_what_is_cta.md) end to end |
| Add or change a figure | § 5 below, then [`docs/figures/_style.py`](docs/figures/_style.py) |
| Use a repo skill (`colors`, `figures`, …) | [`skills/INDEX.md`](skills/INDEX.md) |
| Write a formula | § 4.4 — the renderer rejects a lot of ordinary LaTeX |
| Build or read a local LaTeX PDF | § 4.10, then [`docs/build.sh`](docs/build.sh) |
| Touch the data | § 6 — there is an unadjusted split in five files |
| Commit | § 7 |

---

## 4. Writing a `docs/` chapter

> [`docs/chapters/01_what_is_cta/01_what_is_cta.md`](docs/chapters/01_what_is_cta/01_what_is_cta.md) **is the golden note.** Read it before writing
> or revising any chapter and match its format and logic. The rules below are a summary; ch01 is the
> worked example and it wins where the two seem to disagree.

These are **formal notes**. Terms are defined sharply and kept separate from commentary.

### 4.1 Labels

State a thing, then discharge it. Inline bold labels, no numbering, no `∎`, no LaTeX theorem
environments.

| Label | Use for |
| --- | --- |
| `**Definition (Term).**` | Introducing a term. What it *is*, not why it matters |
| `**Claim.**` | An assertion that can be argued. Never leave one standing alone |
| `**Proof.**` | The argument discharging a claim, when it is genuinely deductive |
| `**Note.**` / `**Note (Topic).**` | Caveats and consequences — see the limit below |
| `**Example.**` | A concrete worked case with numbers |

**One labelled entry per paragraph.** Never run two together on one line; a second bold label
mid-paragraph reads as emphasis and the first definition loses its boundary.

**Every `**Claim.**` is followed by its justification.** Deductive → label it `**Proof.**`.
Empirical or a judgement call → leave it as unlabelled prose; do not dress an opinion as a proof.
An appeal to authority is a `**Note.**`, not a claim.

**`**Note.**` is for caveats, not for paragraphs.** Reserve it for something that cuts against what
was just said, or a consequence a reader would miss. Describing a figure, introducing a table or
walking a procedure is plain prose. Two or three notes per section is plenty; a section where every
paragraph is a `**Note.**` has a label that means nothing.

**Not every claim earns a full derivation.** Reserve step-by-step proofs for results that are
load-bearing or surprising. Where the result is intuitive once stated, give the reason in one or two
sentences plus a single formula and move on.

### 4.2 Structure: what → why → how

One arc **per chapter**, not per section: `## 1. What`, `## 2. Why`, `## 3. How`, then any
standalone context section. Sub-headings are phrased as the question being answered — "Why futures
rather than ETFs", "How a short is represented".

| Stage | Delivers | Typical form |
| --- | --- | --- |
| **What** | The object, stated precisely enough to be unambiguous | `**Definition.**`, a formula, a comparison table |
| **Why** | Why it exists, why it is true, what breaks without it | `**Claim.**` + `**Proof.**`, or a failure mode |
| **How** | How it is actually computed | code, a worked `**Example.**`, a figure |

**This is a default, not a quota.** Some material has no *why* yet, or no *how*. Omit the stage
rather than manufacturing a weak proof or a token snippet.

### 4.3 Format: prefer tables, bullets and figures

Prose is the default **only for arguments**.

- **Table** — comparing ≥ 2 things along the same axes, or any ticker/field/parameter reference
- **Bullets** — enumerating independent reasons, mechanisms or steps
- **Prose** — the reasoning after a `**Claim.**`, where the logic is sequential

A paragraph listing three parallel things should be a table.

### 4.4 Formulas: LaTeX in a restricted dialect

`$…$` inline, `$$…$$` for display. Backticked pseudo-maths is for identifiers and code, never
equations. Keep formulas in the markdown — text rendered into an image is neither selectable nor
searchable.

The renderer imposes two hard constraints. Both were hit in practice.

**Never use `\` followed by punctuation.** Markdown backslash-escaping runs first and eats it.

| Banned | Renders as | Use instead |
| --- | --- | --- |
| `\;` `\,` `\!` `\:` | `;` `,` `!` `:` | a plain space, or `\quad` / `\qquad` |
| `\%` | `%`, then starts a TeX comment that eats the rest of the line | a decimal, or put the `%` outside the math |
| `\_` | `_`, then starts a subscript | identifiers belong in backticks anyway |
| `\\` | `\`, breaking the block | avoid `aligned`; use a `text` code block for derivations |

**Macros are allowlisted.** `\operatorname` is rejected outright. The set known to work here:
`\frac`, `\sum`, `\text`, `\textbf`, `\left(` `\right)`, `\quad`, `\qquad`, `\to`, `\infty`,
`\geq`, `\in`, `\approx`, `\propto`, `\ldots`, `\uparrow`, `\Longrightarrow`, and Greek letters.
Write `\text{Var}`, never `\operatorname{Var}`. **`\sqrt` is not in the set** — write `x^{1/2}`.

**Escape currency as `\$`** — the one case where the escape is wanted, since a bare `$500 … $600` on
one line can be swallowed as a math span.

### 4.5 Symbols: explain each one twice

- **Where it appears** — immediately after the display formula that introduces it, folded into a
  sentence (`where $s$ indexes the asset and $t$ the date, …`) for one or two symbols, or as a table
  when a formula introduces many at once.
- **In a `## Appendix · Notation` table** closing the chapter, giving every symbol, its meaning, and
  the section it first appeared in. Close it with a `**Note.**` on any genuine collision — the same
  letter standing for two things here or in another chapter.

**Prefer renaming to overloading.** `$n_f, n_s$` for MACD spans, not `$f, s$`, which would collide
with `$s$` the asset.

### 4.6 The `Background` section

Optional, placed after the numbered sections and before `## Appendix · Notation`. It holds **general
finance knowledge** a reader needs to follow the chapter but which is not the chapter's subject.

**Write it as Q&A** — each `###` is the literal question a learner would ask:

```markdown
### What is the relationship between futures/options and asset classes?
### Why do CTAs use futures rather than options?
```

This is the one place headings are questions. Answer in Notion-note register: short, heavy on
bullets and tables, **no** `**Definition.**` / `**Claim.**` labels. The author specifies what each
chapter's Background covers — do not invent topics for it.

### 4.7 Chapter skeleton

**Sub-headings are numbered decimally.** `## 3.` for a section, `### 3.2` for a movement inside it,
`#### 3.2.1` for a stage inside that — `docs/chapters/02_testing_a_signal/02_testing_a_signal.md` is the worked example. Split
only sections that hold more than one movement; short ones stay flat. `### N.0` is reserved for a
setup preamble, as in 02's `### 1.0 The three objects`. A bolded lead-in such as `**Ratio.**` marks
a beat inside a movement — when that beat outgrows a few paragraphs, promote it to `### N.M` and
drop the bold. Cite the sub-section in cross-references and in the notation appendix: `§ 3.2`, not
`§ 3`.

**Numbered chapters only.** Orientation docs such as `00-pipeline.md` carry none of it — title,
content, `[← Index]` footer. They are maps, not lessons.

A numbered chapter opens with a **bulleted** blockquote header:

```markdown
> - **Answers:** …
> - **Prerequisites:** …
> - **After reading:** …
```

Bullets, not plain `>` lines — a single newline is a soft break in CommonMark and plain lines
collapse into one paragraph.

Then the numbered sections, then `## Background` and `## Appendix · Notation` in that order, then a
`Next →` pointer carrying a concrete exercise, then a checklist. `Common pitfalls` and
`Open questions` are **optional** — a pitfalls list that only restates the chapter is weight without
information, so drop it rather than pad it.

Cross-references are relative links: `[04](04-from-signal-to-position.md)`.

### 4.8 Language

- `docs/01` – `docs/08`: **English only.** No Chinese.
- `docs/chapters/99_glossary/99_glossary.md`: bilingual EN↔ZH by design — exempt.
- When rewriting content that was in Chinese, translate the idea; do not delete it.

### 4.9 Length

**There is no line budget.** Ch01's ~225 lines is what one chapter's material happened to need, not
a quota. A chapter covering eleven topics will run longer, and that is fine.

The test is **repetition, not length**. Ask whether a passage advances the argument or restates one
already made. When a section runs long, compress it into a table rather than cutting the idea, and
cut restatement before substance. **Never delete a derivation, a worked example or a figure to hit a
number.**

### 4.10 Local LaTeX PDF workflow

Use **VS Code + LaTeX Workshop + TeX Live** to read a hand-written `.tex` chapter as its typeset
PDF. The `.tex` file is the editable source; the PDF and TeX build files are generated artefacts.

Before diagnosing a build, verify that the active TeX installation supplies the compiler:

```bash
which pdflatex
pdflatex --version
```

Every chapter is built through one script, [`docs/build.sh`](docs/build.sh), from the repository
root:

```bash
./docs/build.sh 05_modelling            # one chapter, light
./docs/build.sh 05_modelling --dark     # the same chapter, dark page and dark figures
./docs/build.sh --all                   # every chapter under docs/chapters/
./docs/build.sh --book                  # docs/all_chapters.pdf, the bound edition
./docs/build.sh --figures --all         # regenerate the PNGs first, then typeset
```

The script runs `pdflatex` **twice** per target, because pass one writes the `.toc` and the `\ref`
targets and pass two reads them back; skip the second pass and every cross-reference prints `??`.

A chapter `.tex` is a **body-only fragment** — no `\documentclass`, no `document` environment, and
no layout instruction of any kind. `build.sh` wraps it around
[`docs/preamble.tex`](docs/preamble.tex) for a standalone build, and
[`docs/all_chapters.tex`](docs/all_chapters.tex) `\input`s the same fragment for the bound edition.
That is why swapping the preamble moves every chapter at once, and why the same body renders both
as its own PDF and as a chapter inside the book.

Output lands in exactly two places:

| Artefact | Path | In git |
| --- | --- | --- |
| Published chapter PDF | `docs/read_only_chapters/<stem>.pdf` | yes |
| Bound edition | `docs/all_chapters.pdf` | yes |
| Wrapper, `.aux`, `.log`, `.toc`, dark PDF | `docs/chapters/<stem>/_build/` | no |

A chapter PDF lives in `read_only_chapters/` and nowhere else — never leave a copy beside the
`.tex`. Never commit a TeX auxiliary.

If the build reports `File 'xxx.sty' not found`, the missing TeX Live package must be installed
before retrying; do not change the document merely to conceal a machine setup problem.

---

## 5. Figures

When a point is about a *shape* — a distribution, a monotone relationship, a timeline, a plateau
versus a spike — draw it.

**Never paste a screenshot.** A photographed whiteboard or screen capture is *source material*, not
a figure: unreadable in dark mode, unsearchable, and drifting out of the design system. Redraw it
and let the original go. Anything under an `image/` directory beside a chapter is a paste that
escaped — turn it into a figure and delete it. Never hand-draw ASCII art as a figure either.

**Figures are schematics, not measurements.** The job is to make the shape legible, so illustrative
numbers are fine and preferred. Do not spend effort on pixel accuracy or on sourcing exact data for
a figure that is explaining a concept. Plot real numbers only when the *claim itself* is about this
dataset, and label a schematic as illustrative in its subtitle so it is never mistaken for a result.

**One folder per chapter under `docs/figures/`**, holding that chapter's generator script and the
PNGs it emits — so a chapter's figures and the code that draws them sit together, and regenerating
one chapter cannot touch another's:

| Chapter | Figure folder | Script |
| --- | --- | --- |
| `01_what_is_cta` | `docs/figures/01_figures/` | `make_01_what_is_cta.py` |
| `02_testing_a_signal` | `docs/figures/02_figures/` | `make_02_testing_a_signal.py` |
| … | `docs/figures/<NN>_figures/` | `make_<chapter-stem>.py` |

A script announces its own output directory with `set_out(Path(__file__).resolve().parent)` right
after the imports; `save()` writes there. PNG names are unique across chapters, so `\fig{stem}` in
a chapter body never has to say which folder its figure is in — `\graphicspath` in the preamble
searches all of them.

Shared design tokens and drawing primitives (`THEMES`, `rounded_bar`, `style_axes`, `titles`,
`save`) live in [`docs/figures/_style.py`](docs/figures/_style.py) and are imported by every chapter
script. **Never re-declare a colour inside a chapter script** — change the token in `_style.py` and
every chapter moves together. That single home is what keeps the figures one visual system. The
semantic meaning of each colour — blue for the strategy, green for validation, violet for the crux —
is documented in [`skills/colors.md`](skills/colors.md); read it before choosing a colour for a new
figure. Reusable skills are indexed in [`skills/INDEX.md`](skills/INDEX.md).

To add a figure:

1. Add a function to *that chapter's* script, following the existing tokens — single-hue marks,
   hairline gridlines, labels in ink tokens never the series colour — and register it in the
   script's `FIGURES` tuple.
2. Emit **both** `-light.png` and `-dark.png`, stepped for their own surface rather than
   colour-flipped.
3. Reference it from the chapter body as `\fig{stem}{caption}{label}` — the macro picks the
   `-light` or `-dark` variant to match the build, so figure and page always agree.
4. Re-run only that script — `python docs/figures/02_figures/make_02_testing_a_signal.py` — and
   commit the regenerated PNGs. Editing one chapter's figure must not churn another's.

A new chapter gets a new script; copy an existing docstring's shape, which lists every figure the
script produces and one line on what each shows.

---

## 6. Code and data

`Backtest_prototype/backtest.py` is the prototype; `Backtests.md` beside it is its write-up and the
home for measured results, reproduction snippets and defects in a particular run.

`CTA_data/` holds 37 daily OHLCV CSVs, all **ETFs**, standing in for futures. **Prices are not
dividend-adjusted.** Five sector SPDRs (XLB, XLE, XLK, XLU, XLY) still carry an **unadjusted
2-for-1 split** effective 2025-12-05 — see [`docs/chapters/100_dataset/100_dataset.md`](docs/chapters/100_dataset/100_dataset.md) before
trusting any result that spans that date. Unadjusted originals live in `CTA_data/_unadjusted_raw/`,
deliberately outside the `*_ohlcv_1d.csv` glob.

---

## 7. Git

After completing a modification, `git add`, `git commit` and `git push` to `origin main` without
being asked. One commit per coherent unit of work; the message says what changed **conceptually**,
not "update files".

- **No AI attribution in commit messages.** No `Co-Authored-By: Claude` trailer, no "generated by".
- `CLAUDE.md` and `.claude/` are gitignored — never re-add them.
- Force-push, history rewriting and branch deletion need explicit approval.

---

## 8. Traps that have already bitten

The markdown in this repo passes through a formatter that reflows tables. It has eaten real content
more than once.

| Trap | Symptom | Avoid it by |
| --- | --- | --- |
| Inline math mid-cell in a table | `asset $s$ over` becomes `asset$s$ over` | Keep the Means/description columns math-free; put `$…$` only at the start of a cell |
| Bold mid-cell in a table | `sort on **volatility**` becomes `sort on**volatility**` | Lead the cell with the bold label |
| A `$…$` span broken across a line | A stray `$` appears and the block stops rendering | Keep every math span on one line |
| `\%` inside math | Silently comments out the rest of the line | Write percentages outside the math |

Two more, not formatter-related:

- **A figure the chapter no longer references is dead code.** Delete the function, its `FIGURES`
  entry, its docstring line and both PNGs together.
- **Renumbering a chapter's sections breaks other files.** `§ N` references live in `docs/00-*.md`,
  sibling chapters and `Backtest_prototype/Backtests.md`. Grep for `02 § ` and friends after any
  renumber.

---

## 9. How to know you are done

- The chapter reads like [`docs/chapters/01_what_is_cta/01_what_is_cta.md`](docs/chapters/01_what_is_cta/01_what_is_cta.md).
- Every claim is discharged, every symbol is glossed twice, every figure exists in both themes.
- The generator script for that chapter runs clean and the PNGs are committed.
- No section reference anywhere in the repo points at a heading that no longer exists.
- The commit message says what changed conceptually.
