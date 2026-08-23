# Figure Colours — the repo's colour system

One rule above all: **colours live in `_style.py`, never re-declared in a
chapter script.** Change a token there and every figure moves together. This
file is the legend for what each colour *means*, so any figure can be decoded
without a legend of its own. Read it before adding or changing a colour in any
`docs/figures/make_*.py`.

## Semantic palette

| Token | Meaning | Light theme | Dark theme |
| --- | --- | --- | --- |
| `ramp[5]` | **blue** — the strategy, the primary subject | `#184f95` | `#9ec5f4` |
| `ramp[4]` | **blue, lighter** — a related/secondary path (e.g. the model loop) | `#256abf` | `#6da7ec` |
| `validation` | **green** — what only measures the strategy | `#1f8f63` | `#35a37a` |
| `accent` | **violet** — the crux, what to look at first | `#6d28d9` | `#8b5cf6` |

Convention: text on a filled box is the theme `surface` colour — white on a
light-theme fill, near-black (`#1a1a19`) on a dark-theme fill. Dark variants
are "stepped for their own surface", never colour-flipped from the light ones.

## How to use it

- Pull colours from `_style.py`'s `THEMES[mode]` — `t["ramp"][5]`,
  `t["validation"]`, `t["accent"]`, … — never hard-code a hex in a `make_*.py`.
- Use the blue / green / violet split to separate, in any figure: the primary
  subject (blue), what measures or validates it (green), and the single thing
  to notice first (violet).
- The `make_00_pipeline.py` figure is the worked example: stages 0–2 (strategy)
  blue, stages 3–5 (validation) green, stage 1 "the signal" + the signal node
  violet as the crux, stage 6 (model loop) `ramp[4]`.

## Reference palettes (user preference)

User likes **cool families — blue / green / purple**; avoid warm amber/orange
for emphasis. Sources of inspiration:

- **Ocean Breeze** (coolors.co/palette/03045e-0077b6-00b4d8-90e0ef-caf0f8):
  `#03045E` deep navy · `#0077B6` teal-blue · `#00B4D8` turquoise ·
  `#90E0EF` frosted blue · `#CAF0F8` light cyan
- **Blue & Purple** palettes (coolors.co/palettes/blue-and-purple)
- qtccolor article 680 (designer palettes), schemes 4 / 6 / 8

## Extending

To add a semantic colour, add the token to **both** `light` and `dark` in
`THEMES`, each value stepped for its own surface, then use the token in the
chapter script. Keep the table above in sync.
