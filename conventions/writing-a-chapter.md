# Writing a chapter

The editorial rules for `docs/chapters/`. Routed to from [`AGENTS.md`](../AGENTS.md) § 3, tasks
**T1** (new chapter), **T2** (revise) and **T4** (migrate from Markdown).

`AGENTS.md` § 4 lists the *markup* — which environments exist. This file is about the *writing*:
what earns a proof, how a section is shaped, what closes a chapter.

> **Two golden notes, and they do not conflict.**
>
> - **Logic and format:** [`01_what_is_cta`](../docs/chapters/01_what_is_cta/) — read it before
>   writing or revising anything. Where it and this file seem to disagree, it wins.
> - **Markup:** [`05_modelling.tex`](../docs/chapters/05_modelling/05_modelling.tex) — the worked
>   example of what a converted chapter looks like.

---

## 1. Labels: state a thing, then discharge it

Write in the shape of a mathematical text.

| Environment | Use for |
| --- | --- |
| `definition` | Introducing a term. State what it *is*, not why it matters |
| `claim` | An assertion that can be argued. **Never leave one standing alone** |
| `proof` | The argument discharging a claim, when it is genuinely deductive — an identity, an algebraic consequence, a bound |
| `note` | A caveat, a consequence, something true but not definitional |
| `example` | A concrete worked case with numbers |

**One labelled entry per block.** Never run two together. Even a one-clause definition gets its own
environment.

**Every claim is followed by its justification.** If the justification is deductive, use `proof`
and make each step follow from the last. If it is empirical or a judgement call ("symmetry matters
most"), leave it as unlabelled prose — **do not dress an opinion up as a proof**. A claim whose
argument is an appeal to authority is a `note`, not a claim.

**`note` is for caveats, not for paragraphs.** Reserve it for something that cuts against what was
just said, or a consequence the reader would otherwise miss. When a passage is simply the next step
of the exposition — describing a figure, introducing a table, walking a procedure — write it as
prose. A section where every paragraph is a `note` has a label that means nothing, and the genuine
caveats stop standing out. Two or three per section is plenty.

**Not every claim earns a full derivation.** Reserve a step-by-step proof for results that are
load-bearing or genuinely surprising. Where the result is intuitive once stated, give the reason in
one or two sentences plus a single formula and move on. Three stacked display blocks to reach an
obvious conclusion tires the reader and hides which proofs actually matter.

---

## 2. Structure: what → why → how

**One arc per chapter, not per section.**

| Stage | Delivers | Typical form |
| --- | --- | --- |
| **What** | The object, stated precisely enough to be unambiguous | `definition`, a formula, a comparison table |
| **Why** | Why it exists, why it is true, or what breaks without it | `claim` + `proof`, or a failure mode |
| **How** | How it is actually computed | a worked `example`, a figure, a mechanism |

**This is a default, not a quota.** Some material has no *why* yet (an open empirical question) or
no *how* (a concept with no code behind it). **Omit the stage** — do not manufacture a weak proof
or a token snippet to fill the slot. A short section beats a padded one.

The *how* stage stays at the level of **mechanism** ("carry the position as a signed quantity"),
not this repo's code. **When a passage starts naming variables from a `.py` file, move it** into
`Backtest_prototype/Backtests.md`.

Section headings are phrased as the question being answered — "Why futures rather than ETFs", "Why
the short leg is the fragile one", "How a short is represented" — not as topics.

When a chapter feels long, check whether it is repeating a stage rather than advancing.

---

## 3. Format: prefer tables, bullets and figures

Prose is the default **only for arguments**.

- **Table** — comparing ≥ 2 things along the same axes (instruments, portfolios, pitfalls,
  participants), or any ticker/field/parameter reference. Use `tabularx`, or `xltabular` when it
  may break across pages.
- **Bullets** — enumerating independent reasons, mechanisms or steps.
- **Prose** — only where the logic is sequential, following a `claim`.

A paragraph listing three parallel things should be a table. Do not pad a table into prose to sound
more formal.

### Figures

Draw one when the point is about a **shape** — a distribution, a monotone relationship, a timeline,
a plateau versus a spike. The procedure is `AGENTS.md` **T3**; the rules that govern the content:

- **Figures are schematics, not measurements.** Illustrative numbers are fine and preferred — the
  bucket chart uses invented values precisely because the monotone staircase is the point, not the
  bar heights. Only plot real numbers when the *claim itself* is about this dataset. Say
  "illustrative" in the caption so it is never mistaken for a result.
- **Label both axes**, naming the quantity with the chapter's own symbols. Schematics included.
- **Never paste a screenshot.** A photographed whiteboard or a screen capture is *source material*,
  not a figure. Redraw it and let the original go.
- **Never render a formula into an image.** Image text is neither selectable nor searchable.

---

## 4. Symbols: explain each one twice

**First where it appears** — immediately after the display formula that introduces it, folded into
a sentence ("where $s$ indexes the asset and $t$ the date") for one or two symbols, or as a table
when a formula introduces many at once.

**Then again in the closing `Appendix · Notation` table**, giving every symbol, its meaning, and
the section it first appeared in. Close the appendix with a `note` on any genuine collision — the
same letter standing for two things here or in another chapter.

**Prefer renaming to overloading**: `$n_f, n_s$` for the MACD spans, not `$f, s$`, which would
collide with `$s$` the asset.

---

## 5. The `Background` section

Optional, and placed **before** the notation appendix. It holds **general finance knowledge** a
reader needs in order to follow the chapter but which is not the chapter's subject — market
structure, terminology, how an instrument works.

**Write it as Q&A.** Each sub-heading is the literal question a learner would ask:

```
\subsection*{What is the relationship between futures/options and asset classes?}
\subsection*{Why do CTAs use futures rather than options?}
```

This is the one place where headings are questions rather than statements. Answer in **note
register**: short, heavy on bullets and tables, and **no** `definition` / `claim` environments —
this is orientation, not formal notes.

**Harry specifies what a chapter's Background covers. Do not invent topics for it.** `01`'s is the
reference.

---

## 6. Chapter skeleton

In order, as `05_modelling.tex` lays it out:

```
\chapterhead{NN}{Title}{NN_slug}

\section{...}\label{sec:...}        numbered sections, decimal subsections
\subsection{...}\label{sec:...}
  ...

\section*{Background}               optional  — before the appendix
\section*{Appendix \midot{} Notation}
\section*{Common pitfalls}          optional
\section*{Open questions}           optional
\section*{Next $\rightarrow$ ...}   one concrete exercise
\begin{checklist} ... \end{checklist}
```

**Split a section only when it holds more than one movement**; short ones stay flat. A bolded
lead-in marks a beat inside a movement — when that beat outgrows a few paragraphs, promote it to a
`\subsection` and drop the bold.

**Every section carries a `\label`**, and cross-references cite the sub-section: `\secref` at the
level that actually contains the material.

`Common pitfalls` and `Open questions` are optional — a pitfalls list that only restates the
chapter is weight without information. Drop it rather than pad it.

**Orientation documents carry none of this.** `00_pipeline` is a map, not a lesson: title, content,
nothing else. No checklist, no `Next`, nothing to prepare for.

---

## 7. Language

- Chapter bodies: **English only.** No Chinese.
- `99_glossary`: bilingual EN↔ZH by design — exempt.
- `preamble.tex` and `build.sh` header comments: Chinese is fine; they are Harry's own scaffolding.
- When converting content that was in Chinese, **translate the idea into English; do not delete
  it.**

---

## 8. Length

**There is no line budget.** `01`'s ~225 lines is what that chapter's material happened to need,
not a quota. A chapter covering eleven topics runs longer, and that is fine.

The test is **repetition, not length**. Ask whether a passage advances the argument or restates one
already made. A chapter that never repeats itself has earned every line it has.

When a section does run long, **compress it into a table rather than cutting the idea**, and cut
restatement before substance. **Never delete a derivation, a worked example or a figure to hit a
number.**
