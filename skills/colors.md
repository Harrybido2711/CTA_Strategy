---
name: colors
description: The repo's figure colour system — semantic blue/green/violet, the tokens in _style.py, and usage rules
---

## When to use

Choosing or changing a colour in any `docs/figures/make_*.py` figure.

## The system

Colours live in `docs/figures/_style.py`'s `THEMES` — **never re-declared in a
chapter script**. Change a token there and every figure moves together. Box
text uses the theme `surface` colour (white on a light-theme fill, near-black
`#1a1a19` on a dark-theme fill); dark variants are stepped for their own
surface, never colour-flipped.

Semantic palette:

| Token | Meaning | Light theme | Dark theme |
| --- | --- | --- | --- |
| `ramp[5]` | **blue** — the strategy, the primary subject | `#184f95` | `#9ec5f4` |
| `ramp[4]` | **blue, lighter** — a related/secondary path | `#256abf` | `#6da7ec` |
| `validation` | **green** — what only measures the strategy | `#1f8f63` | `#35a37a` |
| `accent` | **violet** — the crux, what to look at first | `#6d28d9` | `#8b5cf6` |

## Procedure

1. Pull colours from `THEMES[mode]` — `t["ramp"][5]`, `t["validation"]`,
   `t["accent"]` — never hard-code a hex in a `make_*.py`.
2. Split blue / green / violet by role: the primary subject (blue), what
   measures or validates it (green), and the single thing to notice first
   (violet).
3. `make_00_pipeline.py` is the worked example — strategy stages blue,
   validation stages green, the signal and its node violet as the crux.

## Traps

- Re-declaring a hex in a chapter script (it drifts out of the shared system).
- Warm emphasis (amber/orange) — the user prefers cool blue/green/purple.

## Reference palettes

- **Ocean Breeze**: `#03045E` · `#0077B6` · `#00B4D8` · `#90E0EF` · `#CAF0F8`
- **Blue & Purple** (coolors.co/palettes/blue-and-purple)
- qtccolor article 680, schemes 4 / 6 / 8
