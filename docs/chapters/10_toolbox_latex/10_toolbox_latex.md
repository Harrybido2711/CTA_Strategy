# 10 · Toolbox: LaTeX → PDF

> - **Answers:** what actually happens between a `.tex` file and the PDF it produces, and how this repo's build drives it.
> - **Prerequisites:** none — reference material.
> - **Related:** [05 · Modelling](../../05_modelling/05_modelling.md), the chapter this build typesets.

---

## 1. What a TeX run is

### 1.1 The source is a program

**Definition (Engine).** A *TeX engine* — `pdflatex`, `xelatex`, `lualatex` — is an interpreter. It
reads a `.tex` file as a stream of tokens, executes each one in order, and emits pages as they fill.
It is not a converter that inspects a document and decides how to render it.

**Definition (LaTeX).** *LaTeX* is a macro package written in TeX. `\section`, `\begin{figure}`,
`\ref` are not engine primitives; they are macros that expand into primitives. This is why a LaTeX
error can surface as a complaint about a primitive the source never mentions.

The practical consequence of "interpreter, not converter" is that the run is **stateful and
strictly forward**. At any moment the engine knows only what it has already read. A counter has the
value the preceding tokens gave it; a page number exists only once the page has been shipped out.
Nothing later in the file can inform anything earlier in the same pass.

### 1.2 The chain

```text
  source            engine                 driver              output
  ------            ------                 ------              ------
  chapter.tex  -->  pdflatex          -------------------->    chapter.pdf
                    (writes PDF directly)

  chapter.tex  -->  xelatex  -->  chapter.xdv  -->  xdvipdfmx  -->  chapter.pdf
                    (typesets)     (page geometry,   (embeds fonts,
                                    no fonts yet)     writes PDF)
```

`pdflatex` produces the PDF itself. `xelatex` typesets into an intermediate XDV file — page
geometry with references to fonts rather than the fonts themselves — and then hands it to
`xdvipdfmx`, which embeds the fonts and writes the PDF. Both are single commands from the outside;
the difference matters only when a build leaves an `.xdv` behind, or when the failure is in the
second half of the chain.

---

## 2. Why the engine runs twice

This is the one mechanism worth understanding before any other, because every auxiliary file in
§ 3 exists to serve it.

**Claim.** A single run cannot in general typeset a correct cross-reference.

**Proof.** Let `\ref{L}` occur at token position $i$ and `\label{L}` at position $j$. The engine
reads tokens in increasing position, so at the moment `\ref{L}` must expand to a printable string,
it has read only positions $1 \ldots i$. If $j > i$, the label has not been seen and no value
exists. If $j < i$, the label has been seen, but the value `\label` records includes the page
number of position $j$ — and a page number is fixed only when the output routine ships that page,
which may not have happened, because TeX accumulates material and breaks pages after the fact.
In neither case is the value available at position $i$. Hence a correct value cannot be produced
in one forward pass.

The way out is to record rather than resolve. During the run the engine writes everything a later
run would need — labels, their numbers, their pages, the table-of-contents lines — into auxiliary
files, and typesets a placeholder in the text. The next run reads those files at the start, so the
values are known before the body is processed.

**Example.** Compiling [05 · Modelling](../../05_modelling/05_modelling.md) exactly once, then reading back the
result, gives the state after pass one:

```text
$ pdflatex -interaction=nonstopmode probe.tex     # one pass only
$ pdftotext probe.pdf - | grep -c '??'
18
$ wc -l probe.toc
20
```

Eighteen unresolved references printed as `??`, and a 20-line `.toc` that was written but never
read — the contents page in that PDF holds only the heading "Contents". The log says so plainly:

```text
LaTeX Warning: Reference `sec:ladder' on page 3 undefined on input line 85.
LaTeX Warning: There were undefined references.
LaTeX Warning: Label(s) may have changed. Rerun to get cross-references right.
(rerunfilecheck)                Rerun to get outlines right
```

A second pass over the same source, with those files now on disk, resolves all eighteen and fills
the contents page. The build log after two passes contains no `Warning: Reference` line and no
`Rerun to get` line at all.

**Definition (Fixed point).** Pass $n$ reads the auxiliary files pass $n-1$ wrote and writes a new
set. The document is *converged* when the set it writes equals the set it read — nothing further
can change.

**Note.** Two passes are not guaranteed. Replacing `??` with `4.3` makes a line wider, which can
force a different line break, which can push a paragraph onto the next page, which changes a page
number some other reference points at. When that happens the second pass emits `Rerun to get
cross-references right` again and a third is needed. Documents with page-number-sensitive content
converge in two in practice; the honest general rule is to run until the warning stops, which is
exactly what `latexmk` automates (§ 6.6).

---

## 3. The auxiliary files

Everything below is disposable: deleting all of it and rebuilding reproduces the same PDF, at the
cost of the extra passes needed to rebuild the state.

| File | Written by | Read by | Carries |
| --- | --- | --- | --- |
| `.aux` | every pass | the next pass | label values, counters, and the instructions that populate `.toc` |
| `.toc` | the `.aux` replay | `\tableofcontents` on the next pass | one line per heading, with its number and page |
| `.out` | `hyperref` | the next pass | the PDF bookmark tree shown in a viewer's sidebar |
| `.log` | every pass | you | the full transcript: packages, fonts, warnings, errors |
| `.pdf` | the final pass | the reader | the only output that matters |
| `.xdv` | `xelatex` only | `xdvipdfmx` | the typeset pages before fonts are embedded |
| `.fls`, `.fdb_latexmk` | `latexmk` only | `latexmk` | which files the run touched, so it can tell what changed |
| `.synctex.gz` | any engine, with `-synctex=1` | an editor | source line ↔ PDF position, for click-to-jump |

The `.aux` is the interesting one, because it is a TeX file that the next run simply executes.
Three real lines from `docs/tex/_build/05-modelling-light.aux`:

```text
\@writefile{toc}{\contentsline {section}{\numberline {1}Why one split is not a backtest}{2}{section.1}\protected@file@percent }
\newlabel{sec:one-split}{{1}{2}{Why one split is not a backtest}{section.1}{}}
\newlabel{def:split}{{1}{2}{Split}{definition.1}{}}
```

The first says: when you next reach this point, append that line to the `.toc`. The other two record
that `sec:one-split` resolves to number 1 on page 2, and that `def:split` resolves to Definition 1
on page 2 — which is how `\secref` and a `\ref` to a definition print a number the author never
typed. The `.toc` those `\@writefile` lines produce is plainer:

```text
\contentsline {section}{\numberline {1}Why one split is not a backtest}{2}{section.1}%
\contentsline {subsection}{\numberline {1.1}The textbook split}{2}{subsection.1.1}%
```

**Note.** A `.aux` outliving its source is the classic stale-state bug. Rename a label and rebuild,
and pass one still reads the old `.aux`, which defines the old name — the error can point anywhere
or nowhere. Deleting the auxiliary files and rebuilding is the first thing to try on an
inexplicable failure, and it is cheap.

---

## 4. Choosing an engine

### 4.1 The three engines

| | `pdflatex` | `xelatex` | `lualatex` |
| --- | --- | --- | --- |
| Input encoding | 8-bit; Unicode needs `inputenc` and breaks outside Latin-1 | native UTF-8 | native UTF-8 |
| System fonts | no — only TeX font formats | yes, via `fontspec` | yes, via `fontspec` |
| Output | PDF directly | XDV, then `xdvipdfmx` | PDF directly |
| Scripting | TeX macros only | TeX macros only | embedded Lua |
| Speed | fastest | slower — font shaping at runtime | slowest |
| Use it when | the fonts are TeX's own and the text is Latin | you need a system font or non-Latin script | you need to compute something a macro cannot |

### 4.2 Why `pdflatex` is enough here

[`docs/tex/build.sh`](../../tex/build.sh) checks for `pdflatex` and calls it. That is a consequence of
what [`docs/tex/preamble.tex`](../../tex/preamble.tex) asks for: `amsthm, amssymb, amsmath` and the stock
Computer Modern face, with no `fontspec` and no `\setmainfont` anywhere. Nothing in the layout needs
a system font, so the fastest engine is also the sufficient one — a full light build of
[05 · Modelling](../../05_modelling/05_modelling.md), thirteen pages and two passes, takes about two seconds.

**Note.** The choice is a property of the preamble, not a preference. Adding one
`\setmainfont` line would make `pdflatex` fail at that line, and the build would have to move to
`xelatex` — at which point the `.xdv` step in § 1.2 becomes visible and the two-pass logic of § 2
carries over unchanged.

---

## 5. Reading the log

### 5.1 Finding the real error

A failing run prints hundreds of lines and one of them matters. The rules:

- **An error line starts with `!` in column one.** Nothing else does. Searching for `^!` finds
  every error and no noise.
- **The `l.<n>` line under it is the source line**, echoed and split at the exact token where the
  engine gave up. What sits at the break is the culprit.
- **Only the first error is trustworthy.** Under `-interaction=nonstopmode` the engine keeps going
  in a state it already knows is wrong, so later errors are usually consequences.

Two real errors, from a deliberately broken file compiled against this repo's preamble:

```text
! Undefined control sequence.
l.4 Text with \badmacro
                       {} in it.
--
! LaTeX Error: \begin{claim} on input line 5 ended by \end{document}.
```

The first names the offending macro at the break point. The second is the shape a missing `\end`
takes: the complaint arrives at `\end{document}`, far from line 5 where the unclosed environment
actually opened, and the useful information is `on input line 5`, not where the error was raised.

### 5.2 Warnings that are not failures

**Definition (Overfull hbox).** A line the engine could not fit inside the text measure and set too
wide anyway, because no legal break existed. It reports the overflow in points:

```text
Overfull \hbox (52.797pt too wide) in paragraph at lines 3--4
```

That run exits `0`. It is a typographic complaint, not a failure — a long unbreakable identifier in
a code span is the usual cause, and the fix is in the source, not the build.

**Claim.** The exit code, not the log, decides whether a build succeeded.

**Proof.** A clean run of this chapter's source still emits several hundred lines of package and
font chatter, and a run with a 52pt overfull box exits `0` while producing a correct PDF. Meanwhile
`-halt-on-error` makes the engine stop at the first `!` and exit non-zero. So the log's contents
are a poor signal in both directions, and the exit status is exact by construction.

This is why [`build.sh`](../../tex/build.sh) tests the exit status and only then reaches into the log,
printing the first `!` and the four lines after it — automating precisely the § 5.1 move:

```bash
pdflatex -interaction=nonstopmode -halt-on-error \
         -output-directory="$WORK" "$WORK/$JOB.tex" > "$WORK/$JOB.log" 2>&1 \
  || { echo "xxx $JOB failed:" >&2; grep -A4 '^!' "$WORK/$JOB.log" | head -30 >&2; exit 1; }
```

**Note.** `-interaction=nonstopmode` and `-halt-on-error` look contradictory and are not.
Without the first, an error opens a prompt and the build hangs forever waiting for a keystroke that
a script will never send. The first says *never ask*; the second says *and do not soldier on*.

---

## 6. The build in this repo

### 6.1 The preamble/body split

The hand-written route keeps layout and content in separate files:

| File | Layer | Holds |
| --- | --- | --- |
| [`docs/tex/preamble.tex`](../../tex/preamble.tex) | layout | `\documentclass`, geometry, colours, theorem environments, every custom macro |
| [`docs/tex/05-modelling.tex`](../../tex/05-modelling.tex) | body | `\section`, `\begin{definition}`, `\fig`, text — and no formatting commands at all |
| [`docs/tex/build.sh`](../../tex/build.sh) | driver | joins the two and runs the engine |

**Definition (Body-only fragment).** A chapter `.tex` here is *not* a compilable document. It has
no `\documentclass`, no `\begin{document}` and no preamble; it opens directly at `\title` and
`\maketitle`. Compiling it on its own fails immediately.

The gain is that restyling the whole series is a one-file edit, and it is real: the body files
contain no colour, no font size and no spacing. The cost is that a fragment needs something to wrap
it, which is what the driver supplies.

`preamble.tex` states the interface the body layer is allowed to use, so a replacement layout must
keep providing it:

| Provided | What it is |
| --- | --- |
| `definition` / `claim` / `example` | numbered environments sharing one counter, so numbers read in document order |
| `note` | unnumbered — a caveat is not a result and nothing refers back to it |
| `proof` | `amsthm`, with the head set bold rather than italic |
| `\fig{stem}{caption}{label}` | includes `figures/<stem>-<theme>.png` for the theme being built |
| `\chapref{text}{stem}` | link to a sibling chapter's PDF |
| `\secref{label}` | a clickable `§` cross-reference |
| `checklist` / `\checkitem` | the closing checkbox list |
| `\ifdark` | the theme switch, set from outside |

### 6.2 The wrapper

For each chapter and theme, `build.sh` writes a wrapper into `docs/tex/_build/` and compiles *that*,
never the chapter file directly. The light wrapper is four lines:

```text
\input{preamble}
\begin{document}
\input{05-modelling}
\end{document}
```

and the dark wrapper is the same with one line prepended:

```text
\def\DARKMODE{}
\input{preamble}
\begin{document}
\input{05-modelling}
\end{document}
```

`build.sh` does `cd "$TEXDIR"` before the loop, and both `\input`s depend on it: they name
`preamble` and `05-modelling` with no path, so they resolve relative to the working directory, not
to the wrapper's location in `_build/`. The preamble's `\graphicspath{{../figures/}}` is relative to
the same place. Running the engine from anywhere else finds neither.

### 6.3 How the theme reaches the preamble

**Claim.** `\def\DARKMODE{}` must be emitted before `\input{preamble}`, and there is no other place
it could go.

**Proof.** `preamble.tex` decides the theme with

```text
\newif\ifdark
\ifdefined\DARKMODE \darktrue \fi
```

which is executed as the preamble is read. `\ifdefined` tests the state at that moment, so the
definition has to already exist — anything after `\input{preamble}` is too late. It also cannot go
inside `preamble.tex`, which is the file being parameterised, nor inside the chapter body, which is
read after `\begin{document}` and therefore after `\documentclass` has already been expanded with a
fixed page colour. The wrapper is the only file that runs earlier than the preamble, so it is the
only place the flag can be set.

Everything downstream reads that one boolean: the colour definitions, the `pagecolor` and
`\arrayrulecolor` calls that fire only in dark, and `\figvariant`, which flips `-light` to `-dark`
so `\fig` pulls the matching PNG.

### 6.4 Two themes are two builds

**Claim.** A dark PDF cannot be made by recolouring a light one after the fact.

**Proof.** The theme changes what is *included*, not only what is painted: `\fig` resolves to a
different file — `walk-forward-ladder-dark.png` rather than `walk-forward-ladder-light.png` — and those PNGs
are separately rendered, not inversions of each other. A post-hoc colour transform would have to
replace an embedded raster with a different image, which is not a recolouring. So each theme needs
its own engine run.

Each run is a separate job, `05-modelling-light` and `05-modelling-dark`, with its own `.aux`,
`.toc`, `.out` and `.log` under `docs/tex/_build/`. Only the finished PDFs are copied out, to
`docs/_pdf/<stem>-<theme>.pdf`.

### 6.5 Running it

```bash
./docs/tex/build.sh 05-modelling            # both themes
./docs/tex/build.sh 05-modelling --light    # one
./docs/tex/build.sh --all                   # every numbered .tex in docs/tex/
```

Output goes to `docs/_pdf/`, and the script echoes the page count of each PDF it wrote. Both
`docs/_pdf/` and `docs/tex/_build/` are gitignored — the PDF is a build product, and the chapter
source is what the repo keeps.

**Note.** The page count comes from `pdfinfo`, which ships with poppler rather than with a TeX
distribution. The build itself does not depend on it; without it the arrow line simply reports no
page count.

### 6.6 `latexmk`, and why it is not used here

`latexmk` wraps the engine and runs it until the auxiliary files stop changing — the § 2 fixed point,
found rather than assumed. It also cleans up: `latexmk -c` removes the auxiliary files and keeps the
PDF, `latexmk -C` removes the PDF too.

`build.sh` instead hard-codes the loop:

```bash
for _ in 1 2; do
  pdflatex ... || { ...; exit 1; }
done
```

Two passes are enough for these chapters, verified rather than assumed: the log after the second
pass contains no `Rerun to get` line. A fixed count is the simpler thing to write when the document
is known to converge, and it makes the § 2 mechanism visible in the script instead of hiding it
inside a tool. The trade is that a chapter which ever needs a third pass would ship with stale
numbers and no error — the warning is in the log, but nothing reads it.

---

## 7. The other route: markdown through pandoc

[`docs/to_pdf.sh`](../../to_pdf.sh) typesets a `.md` chapter without making LaTeX the source. It runs as
a pipeline:

```text
  NN-chapter.md
        |
        |  perl preprocessing        <picture> -> one image, chosen by theme
        |                            <details>/<summary> -> bold lead-in, body inlined
        |                            [label](other.md) -> label
        v
  cleaned markdown
        |
        |  pandoc --from=gfm+tex_math_dollars+raw_tex
        |         --include-in-header=<generated preamble>
        |         --resource-path --toc
        v
  generated .tex  ->  xelatex  ->  NN-chapter.pdf
```

Each preprocessing rule exists because print has no equivalent of a browser behaviour: a
`<picture>` element chooses its variant from the reader's theme, which a PDF cannot do, so the
theme is chosen at build time; `<details>` collapses, and a page has nothing to collapse; and a link
to `04-volatility-regimes.md` would be a live link to a file that does not exist beside the PDF, so
only its label survives.

**Note.** Pandoc does not replace LaTeX. It *generates* a `.tex` file and hands it to the same
engine, which is why `to_pdf.sh` takes `--pdf-engine=xelatex`, why it can emit that intermediate
with `--keep-tex`, and why everything in §§ 1–5 still applies to a failure in this route.

The two routes answer different questions:

| | markdown route | hand-written route |
| --- | --- | --- |
| Source of truth | `docs/NN-*.md` — what GitHub renders | `docs/tex/NN-*.tex` |
| Driver | [`to_pdf.sh`](../../to_pdf.sh) | [`tex/build.sh`](../../tex/build.sh) |
| Engine | `xelatex`, via pandoc | `pdflatex`, directly |
| Layout lives in | a preamble the script generates inline | [`tex/preamble.tex`](../../tex/preamble.tex) |
| Numbering | typed by hand in the markdown | `\section` counters |
| Cross-references | typed by hand, and can go stale | `\secref` — renumber themselves |
| Theorem environments | bold text conventions | real `definition` / `claim` / `note` |
| Needs installed | `pandoc` and `xelatex` | `pdflatex` |
| Use it for | keeping one source that reads well on GitHub | a chapter that wants numbering and `\ref` to be automatic |

**Note.** `pandoc` is not currently installed on this machine, so the markdown route cannot be run
here as it stands; `to_pdf.sh` exits with its own `pandoc not found` message rather than failing
obscurely. The hand-written route needs only MacTeX.

---

## 8. Failures that are not LaTeX's fault

| Symptom | Cause | Fix |
| --- | --- | --- |
| `! Undefined control sequence` at `\setmainfont` | `fontspec` under `pdflatex` | build with `xelatex`, or drop the system font |
| `! LaTeX Error: File ... not found` for a figure | wrong working directory — `\graphicspath{{../figures/}}` is relative | run from `docs/tex/`, as `build.sh` does |
| `\input{preamble}` not found | same cause, one file earlier | same fix |
| A `\ref` prints `??` in a finished PDF | only one pass ran | run again, or use `latexmk` |
| An error naming a label that no longer exists | stale `.aux` from before a rename | delete `_build/` and rebuild |
| Non-Latin characters vanish or error | `pdflatex` outside Latin-1 | `xelatex` or `lualatex` |
| The build hangs with no output | an error opened a prompt | `-interaction=nonstopmode` |
| Dark PNG on a white page | theme flag set for one but not the other | build through `build.sh`, which sets both together |

---

## Background

### What is the difference between TeX, LaTeX, and a distribution like MacTeX?

Three layers, often all called "LaTeX" in conversation:

```text
  MacTeX / TeX Live      the distribution: engines, packages, fonts, tools
      |
      +-- LaTeX          a macro package: \section, \begin{figure}, \ref
              |
              +-- TeX    the language and the typesetting algorithms
```

- **TeX** — Knuth's language and its line-breaking and page-breaking algorithms. Almost nobody writes
  raw TeX.
- **LaTeX** — the macro layer everybody actually writes. Document classes, sectioning, floats,
  cross-references.
- **MacTeX / TeX Live** — the shipped bundle: the engines (`pdflatex`, `xelatex`, `lualatex`),
  `latexmk`, thousands of packages, and the fonts. On this machine it lives in `/Library/TeX/texbin`
  and reports `pdfTeX 3.141592653-2.6-1.40.26 (TeX Live 2024)`.

A package such as `amsthm` or `hyperref` is none of the three — it is a third-party macro file the
distribution happens to ship.

### What is a "preamble"?

Everything between `\documentclass` and `\begin{document}`. It is executed before any text is
typeset, and it is where configuration has to go, because most of it cannot take effect afterwards.

- `\documentclass` — the base layout (`article`, `book`, …). Exactly one, first.
- `\usepackage` — load a package. Order occasionally matters; `hyperref` conventionally goes last.
- Definitions — `\newcommand`, `\newtheorem`, `\definecolor`, geometry and spacing settings.

In this repo the preamble is pulled out into its own file, so "the preamble" and
[`docs/tex/preamble.tex`](../../tex/preamble.tex) are the same thing.

### Why is there a DVI or XDV step at all?

DVI — *device independent* — predates PDF. TeX was written when the output device was a specific
printer, so the engine produced a device-neutral description of where every glyph goes, and a
separate driver turned that into whatever the hardware wanted.

That separation survives in `xelatex`, whose XDV is DVI extended to carry references to modern
fonts, finished by `xdvipdfmx`. `pdflatex` collapsed the two steps and writes PDF directly, which is
why it leaves no intermediate behind. The distinction is visible mainly in failure: an error about
glyphs or font embedding comes from the driver half, after the typesetting half already succeeded.

### What does pandoc actually do?

Pandoc is a document converter, not a typesetter. It parses an input format into an internal
document tree and renders that tree into an output format.

- Asked for PDF, it renders the tree to **LaTeX**, then invokes a TeX engine on it. The PDF is
  LaTeX's work; pandoc's contribution ends at the `.tex`.
- `--include-in-header` injects raw LaTeX into the preamble of that generated file — the hook for
  anything pandoc has no notion of, such as a page colour.
- `--keep-tex` writes out the intermediate, which is the way to see what it generated when the
  build fails inside the engine.

This is why the markdown route in § 7 is not an alternative to LaTeX. It is a way of *writing*
LaTeX indirectly, and it inherits every mechanism in this chapter.

---

Reference chapter — no next step. The build it describes typesets
[05 · Modelling](../../05_modelling/05_modelling.md).

[← 09](../../09_ic_and_r_squared/09_ic_and_r_squared.md) · [How a Strategy Is Built](../../00_pipeline/00_pipeline.md) · reference: [08 · Toolbox: pandas](../../08_toolbox_pandas/08_toolbox_pandas.md)
