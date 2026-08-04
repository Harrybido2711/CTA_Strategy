# CLAUDE.md

Study notes and a backtest prototype for CTA (managed-futures) strategies. `docs/` is the
teaching material; `Backtest_prototype/` and `analyze_cta_data.py` are the code it describes.

## Writing conventions for `docs/`

These chapters are **formal notes**. Terms are defined sharply and kept separate from commentary.

### Labels

Use inline bold labels, no numbering:

| Label | Use for |
| --- | --- |
| `**Definition (Term).**` | Introducing a term. State what it *is*, not why it matters. |
| `**Claim.**` | An assertion that can be argued. Follow it with the argument in prose. |
| `**Note.**` / `**Note (Topic).**` | Caveats, consequences, things that are true but not definitional. |
| `**Example.**` | A concrete worked case with numbers. |

Do **not** use `Def 1.1`-style numbering, `∎`, or theorem environments.

### Format: prefer tables and bullets

Prose is the default only for arguments. Whenever content is **parallel or comparative**, use a
table or a bullet list instead — they are usually the better record:

- **Table** — comparing ≥ 2 things along the same axes (instruments, portfolios, pitfalls,
  participants), or any ticker/field/parameter reference.
- **Bullets** — enumerating independent reasons, mechanisms, or steps.
- **Prose** — only for the reasoning that follows a `**Claim.**`, where the logic is sequential.

A paragraph listing three parallel things should be a table. Do not pad a table into prose to
sound more formal.

### Language

- `docs/01` – `docs/08`: **English only.** No Chinese.
- `docs/99-glossary.md`: bilingual EN↔ZH by design — exempt.
- When rewriting content that was in Chinese, translate the idea into English; do not delete it.

### Chapter skeleton

Each chapter opens with the `> **Answers:** / **Prerequisites:** / **After reading:**` block and
closes with `Common pitfalls`, `Open questions` (if any), a `Next →` pointer with a concrete
exercise, and a checklist. Keep cross-references as relative links: `[04](04-from-signal-to-position.md)`.

### Length

Chapters should stay tight. If a section runs long, compress it into a table rather than cutting
the idea.

## Git

After completing a modification, `git add`, `git commit`, and `git push` to `origin main` without
being asked. One commit per coherent unit of work; the message should say what changed
conceptually, not "update files". Force-push, history rewriting, and branch deletion still need
explicit approval.

## Data

`CTA_data/` holds 37 daily OHLCV CSVs — all **ETFs**, standing in for the futures a real CTA would
trade. Prices are not dividend-adjusted. Five sector SPDRs (XLB, XLE, XLK, XLU, XLY) still carry
an **unadjusted 2-for-1 split** effective 2025-12-05; see [docs/02](docs/02-data-and-corporate-actions.md)
before trusting any result that spans that date. Unadjusted originals live in
`CTA_data/_unadjusted_raw/`, deliberately outside the `*_ohlcv_1d.csv` glob.
