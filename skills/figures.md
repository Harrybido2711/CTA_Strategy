---
name: figures
description: How to add, style and regenerate a chapter figure in this repo
---

## When to use

Adding a new figure, restyling an existing one, or regenerating a chapter's
PNGs.

## The system

- One generator script per chapter: `docs/figures/make_<chapter-stem>.py`,
  importing shared tokens and primitives from `docs/figures/_style.py`. Never
  re-declare a colour — see [`colors.md`](colors.md).
- Every figure is emitted twice: `-light.png` and `-dark.png`, each stepped for
  its own surface.
- Chapters reference figures through a `<picture>` element (light/dark srcset)
  with a descriptive alt stating what the figure shows.

## Procedure

1. Add a function to the chapter's script using the tokens (`THEMES[mode]`) and
   primitives (`rounded_bar`, `style_axes`, `titles`, `save`); register it in
   the script's `FIGURES` tuple.
2. Emit both variants via `save(fig, t, f"<name>-{mode}.png")`.
3. Reference it from the chapter via `<picture>` with a descriptive alt.
4. Run only that script — `python docs/figures/make_<chapter>.py` — and commit
   the regenerated PNGs. Editing one chapter's figure must not churn another's.
5. Choose colours per [`colors.md`](colors.md).

## Traps

- A figure the chapter no longer references is dead code: delete the function,
  its `FIGURES` entry, its docstring line and both PNGs together.
- Re-declaring a colour in a chapter script.
- Non-ASCII glyphs (e.g. `→`) missing from the figure font (Helvetica Neue) —
  use mathtext (`$\rightarrow$`) or plain words.
