# AGENTS.md

**You are working in this repository. Read this file before your first tool call.**

This is the single entry point, and it is a **dictionary, not a manual**. It says what this
repository is, where things live, and — for whatever you are about to do — which file tells you how
to do it. Every other agent config here (`CLAUDE.md`, `.github/copilot-instructions.md`) is a stub
pointing back at this one.

---

## 0. Protocol

1. **Name the task type** from the dictionary in § 3. Say which row you picked.
2. **Open that row's playbook and read it in full** before you edit anything.
3. **Follow it.** Do not invent a different procedure.
4. **Check the row's "Done when"** before claiming to be finished.
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
asserted**. A claim comes with the argument that discharges it, or is marked as an open question.

**LaTeX is the source.** Chapters are `.tex`; the PDFs in `docs/read_only_chapters/` are the
published form. The chapters still in Markdown are mid-migration — that is task **T4**.

---

## 2. Layout

| Path | Holds |
| --- | --- |
| `docs/preamble.tex` | The layout layer — the one file that decides what everything looks like |
| `docs/chapters/<NN_slug>/<NN_slug>.tex` | One chapter's body. **A fragment**: no `\documentclass`, no `document` environment |
| `docs/chapters/<NN_slug>/_build/` | Wrapper, `.aux`, `.log`, `.toc` — scratch, gitignored |
| `docs/figures/<NN>_figures/` | That chapter's `make_<NN_slug>.py` and the `-light.png` / `-dark.png` pairs it emits |
| `docs/figures/_style.py`, `_data.py` | Shared design tokens and data. **Never re-declare a colour in a chapter script** |
| `docs/all_chapters.tex` → `all_chapters.pdf` | The bound edition — one `\input` line per chapter |
| `docs/read_only_chapters/<NN_slug>.pdf` | The published PDF. **The only place a chapter PDF lives** |
| `docs/build.sh` | The only build entry point |
| `docs/math.tex` | Harry's original homework template — the ancestor of `preamble.tex`. Reference, not built |
| `market_knowledge/` | Lecture-sourced notes, each opening with a source blockquote. Not the course spine |
| `Backtest_prototype/` | `backtest.py`, `analyze_cta_data.py`, `backtester.ipynb` + `Backtests.md`, its write-up |
| `CTA_data/` | 37 daily OHLCV CSVs — **ETFs**, standing in for futures |
| `.claude/tasks/` | Every playbook in § 3 — one file per task. Local only, see § 5 |

**The theory/practice split is strict.** A chapter holds concepts that stay true regardless of this
repo — definitions, proofs, mechanisms. Measured results, derivations over code variables,
reproduction snippets and defects in a particular run go in `Backtest_prototype/Backtests.md`.
**When a chapter starts naming variables from a `.py` file, move that passage out.**

**One data trap, permanently.** Five sector SPDRs (XLB, XLE, XLK, XLU, XLY) carry an **unadjusted
2-for-1 split** effective 2025-12-05. Read `docs/chapters/100_dataset/` before trusting any result
spanning that date. Unadjusted originals are in `CTA_data/_unadjusted_raw/`, deliberately outside
the `*_ohlcv_1d.csv` glob.

---

## 3. The dictionary

| # | Task | Playbook — read it before acting | Skills | Done when |
| --- | --- | --- | --- | --- |
| **T1** | Write a new chapter | [`.claude/tasks/writing-a-chapter.md`](.claude/tasks/writing-a-chapter.md) | — | Chapter and book both build clean; no `??` in the PDF |
| **T2** | Revise a chapter | [`.claude/tasks/writing-a-chapter.md`](.claude/tasks/writing-a-chapter.md) | — | Same, plus no `\secref` / `\chapref` points at a label that no longer exists |
| **T3** | Add or change a figure | skill `figures`, after the `nature-figure` design pass | `nature-figure` → `figures` + `colors` | Both PNGs committed; both themes build; both axes labelled |
| **T4** | Migrate a chapter `.md` → `.tex` | [`.claude/tasks/md-to-tex-migration.md`](.claude/tasks/md-to-tex-migration.md) | — | PDF verified, `.md` deleted, book rebuilt with it |
| **T5** | Code / backtest | `Backtest_prototype/Backtests.md`. **Measured numbers go there, never in a chapter** | `run`, `code-review` | The number is reproducible from a snippet in `Backtests.md` |
| **T6** | Data | `docs/chapters/100_dataset/`, and the split trap in § 2 | — | The result is stated with which side of 2025-12-05 it spans |
| **T7** | Transcribe a lecture | Any existing `market_knowledge/*.md`, for the shape | — | Source file and date stated; marked "not audited" |
| **T8** | Build a PDF | [`.claude/tasks/building-pdfs.md`](.claude/tasks/building-pdfs.md) | — | `read_only_chapters/` updated; nothing new outside a `_build/` |
| **T9** | Move, rename, renumber or delete anything | [`.claude/tasks/repo-hygiene.md`](.claude/tasks/repo-hygiene.md) | `simplify` | Every grep in that file comes back empty |
| **T10** | Add a glossary term | `docs/chapters/99_glossary/` | — | Bilingual row, linked to the chapter that owns the concept |
| **T11** | Change the layout — fonts, margins, colours, a new macro | [`.claude/tasks/changing-the-layout.md`](.claude/tasks/changing-the-layout.md) | — | Every chapter still builds in both themes; no layout instruction leaked into a body |
| **T12** | Skills, settings, permissions, hooks | `.claude/skills/INDEX.md` | `update-config`, `fewer-permission-prompts` | — |

---

## 4. Git

After completing a modification, `git add`, `git commit` and `git push` to `origin main` without
being asked. **One commit per coherent unit of work** — stage the files you touched by name, never
`git add -A`, or you will sweep up work that is not yours. The message says what changed
**conceptually**, not "update files".

- **No AI attribution.** No `Co-Authored-By` trailer, no "generated by".
- `CLAUDE.md`, `.claude/` and `chat_records/` are gitignored — never re-add them.
- The PDFs in `read_only_chapters/` and `all_chapters.pdf` **are** committed: they are what a
  reader without a TeX install opens.
- Force-push, history rewriting and branch deletion need explicit approval.

---

## 5. On a new machine

`.claude/` and `CLAUDE.md` are gitignored, so a fresh clone has **neither the Claude Code entry
point nor the playbooks in § 3**. Recreate `CLAUDE.md` — this is its entire contents:

```markdown
# CLAUDE.md

This repository's conventions live in AGENTS.md — the entry point and task dictionary.

@AGENTS.md
```

It carries no rules of its own. If you ever find yourself writing a convention into `CLAUDE.md`,
you are creating a second source of truth: it belongs in this file, or in the playbook this file
routes to.
