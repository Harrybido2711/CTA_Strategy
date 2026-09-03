# LaTeX formatting — the house template

The layout layer in [`docs/preamble.tex`](../docs/preamble.tex) is not invented: its skeleton is
Harry's own homework template, [`docs/math.tex`](../docs/math.tex). This file records **what that
template does**, so that a later change to `preamble.tex` is a deliberate departure rather than an
accident.

Read it with `docs/preamble.tex` open beside it. One rule governs everything below: **a chapter
body carries no layout instruction of its own** — every decision here lives in the preamble, and
swapping the preamble must move all chapters at once.

---

## 1. The page

| Setting | `math.tex` | Why it is there | In `preamble.tex` |
| --- | --- | --- | --- |
| `\documentclass[..]{article}` | `12pt` | Homework read at arm's length | **`10pt`** — notes are read on screen and are far longer than a problem set |
| `\usepackage[margin=1in]{geometry}` | 1 in all round | Wide enough for a marker's pen | kept |
| `\setlength\parindent{0em}` | never indent | Indentation and blank-line spacing are two ways to mark a paragraph; using both is redundant | kept |
| `\setlength{\parskip}{1em}` | a full line between paragraphs | Makes each paragraph a visible block — the note-taking register, not the essay register | kept |

**The `parskip` choice is load-bearing.** A full `1em` between paragraphs is what makes a run-in
`\textbf{Base Case: }` read as a new beat rather than as emphasis mid-flow. It also has two side
effects that must be repaired, both of them in `preamble.tex` and not in any chapter:

- the table of contents inherits the skip and spills a page — `\tableofcontents` is wrapped so the
  skip is zeroed for its duration only;
- `\parskip` does not reach inside a `tabular`, so rows come out tighter than the surrounding
  text — `\arraystretch` is raised to `1.25` to compensate.

## 2. The packages, and what each one buys

| Package | Bought for | Kept? |
| --- | --- | --- |
| `amsmath, amsthm, amssymb` | `align`, `\[ \]`, theorem environments, `\qed` | yes — the base of everything |
| `hyperref` with `colorlinks=true` | Clickable, coloured, **no box** around the link | yes, but the colour is a theme token (`allcolors=linkcol`), not a hard-coded `blue` |
| `enumerate` | `\begin{enumerate}[(a)]` — lettered sub-parts | yes |
| `xcolor` | The named palette below | yes, loaded as `[table]` so table rules can be recoloured for the dark build |
| `graphicx` | — (unused in `math.tex`) | added — the chapter figures |
| `tabularx`, `xltabular`, `array` | — | added — a text column that fills the line and may break across pages |
| `tcolorbox` | Coloured callout boxes | carried over |
| `tikz` | Hand-drawn diagrams inside the document | **not carried over** — figures here are generated PNGs from `docs/figures/`, so the drawing happens in Python |
| `relsize`, `mathrsfs` | `\mathscr` for power sets, relative sizing | not carried over — no chapter needs them yet |

## 3. The palette

`math.tex` defines six pastel fills as hex constants:

| Name | Hex |
| --- | --- |
| `mypink2` | `#F67599` |
| `mypink` | `#F8A3BC` |
| `mypurple` | `#EEDAEA` |
| `mygreen` | `#D9EA9A` |
| `myblue` | `#A4DBE8` |
| `myyellow` | `#FBDD7A` |

`preamble.tex` replaces them with **semantic** tokens — `pagebg`, `ink`, `linkcol`, `rulecol`,
`boxbg` — each defined twice, once per theme, and selected by the `\ifdark` switch that `build.sh`
sets. The reason is the same one that governs `docs/figures/_style.py`: a name that says *what a
colour is for* can be re-pointed for a dark build; a name that says what it *looks like* cannot.

## 4. Structure macros

`math.tex` runs on one counter and two commands:

```latex
\newcounter{HWcounter}\setcounter{HWcounter}{1}
\newcommand{\problem}{\textbf{Problem \theHWcounter.} \addtocounter{HWcounter}{1}}
\newcommand{\answer}{\vspace{2em} \textbf{Solution. }}
```

The shape worth keeping is the **run-in bold head**: `\textbf{Problem 1.}` opens the paragraph it
labels instead of sitting on its own line. `preamble.tex` reproduces exactly that shape with
`\newtheoremstyle{notes}` — bold head, `.` after it, a plain space so it runs in — and then swaps
the homework counter for the note environments:

| `math.tex` | `preamble.tex` |
| --- | --- |
| `\problem` (numbered, one counter) | `definition` / `claim` / `example`, numbered off **one shared counter** so they read in document order |
| `\answer` (unnumbered lead-in) | `note` (unnumbered) and `proof` (`amsthm`, head forced bold rather than italic) |
| `\qed` typed by hand at the end of a proof | `proof` closes itself |

The four set shorthands — `\R \Z \Q \N` for `\mathbb{R}` etc. — are carried over verbatim.

## 5. Body conventions observed in `math.tex`

These are habits of the document body rather than preamble settings. They transfer to a chapter
`.tex` unchanged, with one exception noted below.

| Habit | Example | Verdict |
| --- | --- | --- |
| Display maths as `\[ … \]` | `\[ \sum_{n=0}^k r^n = \dfrac{1-r^{k+1}}{1-r} \]` | keep — `\[ \]` over `$$…$$` |
| A bold run-in label opens a beat | `\textbf{Base Case: }`, `\textbf{Inductive Step: }` | keep |
| Lettered sub-parts for a proof plan | `\begin{enumerate}[(a)]` | keep |
| A `center` environment around a figure | `\begin{center}\begin{tikzpicture}…` | keep the centring; the content is a `\fig{}` PNG, not TikZ |
| `\newpage` between units | one problem per page | **drop** — a chapter is continuous prose; forcing page breaks fights the flow |
| `\\` and `\vspace` for vertical air | `\\ \\ \vspace*{2cm}` | **drop** — this is exactly the per-body layout instruction the preamble exists to remove. `\parskip` already provides the air |

## 6. What a chapter may say

Everything a chapter body is allowed to use is listed in `AGENTS.md` § 4 — `\chapterhead`, the five
environments, `\fig`, `\secref`, `\chapref`, `\pointer`, `checklist`. If a chapter needs something
that is not on that list, the fix is a new command **in the preamble**, never a raw
`\usepackage`, `\vspace` or colour in the body.
