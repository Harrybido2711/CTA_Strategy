# Round 3 — Regime analysis, and the revisions it motivates

**Status: outline, 2026-10-29. Nothing in Round 3 has been computed.** This file becomes the
pre-registration once Harry settles § 9 and `config.ROUND3` is committed beside it. Every number
below is a Round 2 result, cited from `RESULTS.md` or `results/20_*` / `results/21_*`, or a target
the resume claims.

## 1. The starting line: what Round 2 left open

Round 2 (`ROUND2.md`) built the strategy the resume describes: the paper's time-series momentum,
executed realistically. Bullets 3 and 4 are about what happened **after** that point. The regime
analysis came next, and the revisions were built from it. Round 3 is that second half.

| Bullet | Round 2 measured | Left for Round 3 |
| --- | --- | --- |
| 2: over 25% lost to execution | T0's haircut: 23% of the next-close naive return before Test (35% against same-close); 12% (17%) over the record | Recompute for every revision. Turnover controls should win part of it back |
| 3: trend works best in high-volume, low-volatility regimes | **Volatility half, market level:** T0 earns +17% a year in the low-VIX tercile, +16% mid and −21% high (596 / 336 / 426 days). **Volume half, per asset:** HV/LV − LV/HV is +0.82% a month, t 1.35, positive in 4 of 6 periods. Before Test the 3 × 3 map is not monotone: high-volume / mid-σ is the worst cell (−1.52% a month, t −1.70) | A full regime analysis: more measures, the regime lag, by asset class, by year, and turnover by regime |
| 4: +8% OOS Sharpe and −14% turnover from regime features, vol scaling and turnover controls | Volatility scaling (T1) moves the Sharpe from 0.32 to 0.46, 90% CI of the change −0.04 to +0.34. Cutting leverage on a high-VIX state lowered the Sharpe every time it was tried. Turnover stays near 11 turns a year; a 0.5% deadband trims 2–3% | Revisions aimed at what Part A finds: per-asset regime features, vol estimates that react faster, and controls on where the turnover actually comes from |

## 2. The question

Start from the execution-aware baseline, the strategy whose haircut is bullet 2. Does a regime
analysis point to revisions that raise the walk-forward out-of-sample Sharpe and cut annual
turnover? Each answer is reported as ΔSR (absolute, and as a percentage only under C20's rule),
ΔTO%, a CI, the sample and the observation count.

## 3. What is fixed

| Item | Value |
| --- | --- |
| Baseline R0 | **T0**: sign of the 12-month excess return, × 40%/σ, / S, monthly, caps 0.5 per asset and 3× gross (§ 9 Q1) |
| Data, prices, returns | as Round 2: 37 ETFs, daily, total-return prices, excess of DTB3, the split-adjusted copy (DATA § 4) |
| Execution | signal at the month's last close, trade at the next close; 5 bp per side + 2 bp slippage; $1 of capital |
| Turnover | executed turnover per unit gross, per year, as in Round 2 |
| Asset classes | the six of `config.UNIVERSE_CATEGORY`: U.S. broad equity, U.S. sectors, international equity, fixed income, commodities, alternatives |

## 4. Part A — the regime analysis

Descriptive only. It runs on **2021-02 → 2025-06**, which excludes Test. It explains the revisions;
it does not choose them (§ 5).

### A1. Measures, all computed from data through t − 1

| Measure | Definition | Level |
| --- | --- | --- |
| V, volume | 21-day mean volume, ranked against the asset's own trailing 252 days. DATA § 3: one venue feed, so never compared across assets | per asset |
| σ, volatility | 21-day realised volatility, ranked against the asset's own trailing 252 days; σ_fast / σ_slow (EWMA com 10 / 60) beside | per asset |
| VIX, MOVE | terciles. Equity and commodity ETFs are labelled by VIX, the fixed-income ETFs by MOVE: a rate sleeve labelled by VIX is labelled wrongly (course, *Volatility Signals*) | market |
| Market volume | cross-sectional mean of the per-asset V ranks | market |
| Correlation | average pairwise 63-day correlation of the 37 ETFs, terciles | market |
| Trend strength | 12-month excess return / (σ × √1 year), in z units | per asset |

### A2. Cuts

The dynamic cut D (rolling 252-day tercile) is quoted. The static cuts S1 (data-free ln-ceiling,
VIX only), S2 (frozen at each rung) and S3 (full sample, labelled look-ahead) are printed beside
it, with the share of days on which they agree with D. This is Round 1's comparison, run at the
monthly horizon.

### A3. Timing: every table in two alignments

| Alignment | State | Return | Answers |
| --- | --- | --- | --- |
| Contemporaneous | the state on day t | the book's return on day t | when the book loses: descriptive only |
| Predictive | the state known at the decision close (month-end t, or t − 1 for a daily rule) | the return after the trade | whether the state can be acted on |

**Only a predictive table can motivate a revision.** Round 2's VIX-state table
(`results/20_regime_returns.csv`, the +17% / +16% / −21% row of `RESULTS.md`) joins the VIX close
of day t to the return of day t, so it is contemporaneous. That is why it looks strong while the
overlay it suggested chose m = 1. Part A prints both alignments for every state, side by side.

### A4. The per-asset regime map (bullet 3)

- **Cells.** V tercile × σ tercile. The outcome is sign × next-month excess return.
- **Counts.** Asset-months, months and episodes are printed in every cell.
- **The corner.** HV/LV − LV/HV, plus a pooled regression with a V × σ interaction and SEs
  clustered by month. The 37 assets in one month share one market shock, so they are not 37
  independent observations.
- **"Consistently".** C16's rule: the corner is positive in every period (2021, 2022, 2023, 2024,
  2025H1), and its episode-bootstrap CI excludes 0. Otherwise the fallback wording in `OUTLINE.md`
  applies.
- **By asset class.** Each of the six classes is reported as a descriptive column.

### A5. The book by market state

T0 and T1 are reported by VIX, MOVE, correlation and market-volume state, in both alignments, with
day and month counts. A 2-D VIX × market-volume table covers homework B's two-dimensional view.
Rows are compared by mean return with its error bar, not by Sharpe: a Sharpe carries the state's
own volatility in its denominator.

### A6. The regime lag

An event study: the cumulative excess return of T0 and T1 from 20 days before to 60 days after VIX
enters its high tercile, with per-asset σ_fast and σ_slow over the same window. It measures why
the month-end and daily state cuts of Round 2 arrived too late, and which estimate reacts in time.

### A7. Is it new information?

T0 already sizes each asset by 1/σ, and T1 scales the whole book by its ex-ante volatility, so
part of any volatility regime is already spent. Chapter 04 § 3.2 residualizes the label on what
the book already uses. Here that means regressing the signed next-month return on the regime
labels with the sizing σ (and, for T1, the leverage) as controls.

- A label whose effect disappears gets no revision. It is recorded as "already in the book".
- Volume enters no sizing rule, so a volume effect that survives is new.

### A8. Where the turnover comes from

T0's and T1's Σ|Δw| is split into four sources:

- sign flips;
- per-asset σ resizing;
- book-leverage changes (T1 only);
- changes from 1/S and the caps.

Each source is also shown by regime. This decides which control could plausibly reach −14%: a
deadband cannot remove a sign flip.

### A9. Output

A table of findings → revisions. It fills the "motivated by" column of § 5 and is written up
before Part B runs.

## 5. Part B — the revisions

**The menu is fixed now, from Round 2's evidence, before Part A runs.** Part A explains each item;
it cannot add a winner. An item added later is a numbered amendment, labelled as such wherever its
number appears, as Round 2 did with T3. Every item is reported, including those that lose.

| Family | Item | Rule | Grid (chosen walk-forward, § 6) | Motivated by |
| --- | --- | --- | --- | --- |
| **VS**, volatility scaling | VS1 | book vol target 10% (= T1) | on / off | Round 2: the adjustment that worked |
| | VS2 | asset σ = max(σ_fast, σ_slow), so sizing reacts inside a volatility spike | com_fast ∈ {10, 20} | Round 2: state cuts lag; A6 |
| **RF**, regime-aware features | RF1 | per-asset multiplier by (V, σ) cell, fitted on the training window and shrunk toward 1 | multipliers ∈ {0.5, 1, 1.5}, shrinkage ∈ {0.5, 1} | bullet 3; A4, A7 |
| | RF2 | trend strength in place of the sign: clip(z / z₀, −1, 1) | z₀ ∈ {0.5, 1} | sign flips near zero; A8 |
| | RF3 | mean of the sign over 6, 9 and 12-month look-backs | on / off | paper Table 2 and Round 2's grid: 6–12 months all earn |
| | RF4 | slow MACD agreement: × 1 when chapter 03's slowest pairing agrees with the TSMOM sign, × a when it does not | a ∈ {0.5, 1} | bullet 1's "momentum + MACD" at the monthly horizon (§ 9 Q4) |
| | RF5 | optional: the course's model step, Ridge and CatBoost on the RF inputs plus V, σ and VIX ranks; target next-month return / σ | λ grid, depth grid | the course pipeline, chapter 08 (§ 9 Q3) |
| **TC**, turnover controls | TC1 | proportional no-trade band: trade asset s only when \|w* − w\| > b\|w*\| | b ∈ {0.1, 0.25, 0.5} | Round 2: the absolute 0.5% band had little to trim |
| | TC2 | partial adjustment w ← w + κ(w* − w) | κ ∈ {1, 0.5} | A8 resizing share |
| | TC3 | sign hysteresis: flip only when trend strength crosses ±h | h ∈ {0, 0.25, 0.5} | A8 sign-flip share |

### The ladder, and the ablation

| Book | Contents |
| --- | --- |
| R0 | T0, the baseline |
| R1 | R0 + VS |
| R2 | R1 + RF |
| **R3** | R2 + TC, **the refined strategy that bullet 4 describes** |

Each family is also run alone on R0, and R3 is run with each family left out. A family's
contribution therefore does not depend on the order of the ladder.

## 6. Out-of-sample protocol

The course's rule applies: the small validation window chooses hyperparameters, and the
procedure itself is fixed in advance. Here the procedure is the § 5 menu and the ladder.

| Step | Rule |
| --- | --- |
| Rungs | quarterly. **Expanding** window from 2021-02, not Round 1's rolling three quarters: a monthly book has three rebalances a quarter, too few to fit or validate on |
| Inside a rung q | inner validation = the last 4 quarters before q; inner train = everything earlier, with a 1-month purge. Each family picks its item and grid point by validation Sharpe, using the one-SE rule toward "off". Then refit on the whole window and trade quarter q |
| Record | first rung 2023Q1, which gives at least 11 training months. **Headline: 2023Q1 → 2025Q2**, 10 quarters, 30 monthly rebalances |
| Test | 2025Q3 → 2026Q2, read once by a script committed before it runs (the `frozen_commit` guard of `run_09` / `run_21`). **This is the third look at those quarters**, and it is labelled so everywhere |
| Fresh data | 2026-07 onward, if extended (§ 9 Q2). It is the only sample the Round 3 design has never seen |

**The design caveat, stated now.** The menu was built knowing Round 2's results on all of
2021–2026. The parameters are out of sample on the walk-forward record; the design is not. Only
fresh data is clean on both.

## 7. Metrics and acceptance

These follow `OUTLINE.md` § 6.1 and § 6.3, re-based on R0 and the monthly record.

- **Sharpe.** ΔSR = SR(R3) − SR(R0), with a paired stationary-bootstrap CI (mean block 21 days,
  plus the sensitivity column). The percentage is quoted only if SR(R0)'s CI excludes 0 (C20).
  Each family's contribution and each ablation row is reported.
- **Turnover.** ΔTO%, with a CI, split by A8's four sources (C21).
- **Execution haircut.** H₁ and H₀ for R3 beside R0: how much of bullet 2's loss the turnover
  controls win back.
- **Robustness.** Each with its pass condition:
  - per-year sign count;
  - drop the best 5 and 10 days of |r_R3 − r_R0|;
  - the cost grid;
  - the S2 cut in place of D;
  - without the fixed-income ETFs;
  - data truncated at 2025-12-04.
- **Deflated Sharpe.** N = every candidate in `config.ROUND3`'s grids, counted by the script, not
  by hand.

**Power, stated now.** 30 months is about 630 trading days, so SE(SR) ≈ √(252/630) ≈ 0.63. For
paired books with ρ = 0.9–0.95, SE(ΔSR) ≈ 0.20–0.28, so the minimum detectable ΔSR at 80% power
is about 0.5–0.7. **+8% of a 0.3 Sharpe is about 0.025, twenty to thirty times smaller.** No result
on this sample can confirm "+8%" as such. The quotable form is an absolute ΔSR with its CI.
Turnover is different: it is mechanical and measured almost without noise, so −14% is a fair test.

## 8. Deliverables and order

| Step | Produces | Gate |
| --- | --- | --- |
| 0 | `ROUND3.md` final, plus `config.ROUND3` | Harry settles § 9; committed before any Round 3 number exists |
| 1 | `rr_round3.py` (measures, revision rules, nested selection) and tests in `tests/` | tests pass; no-look-ahead test on every new measure |
| 2 | `run_30_round3_regimes.py` → Part A tables, `results/30_*` | pre-Test only |
| 3 | A9's findings table, written up in this file | before step 4 |
| 4 | `run_31_round3_revisions.py` → the ladder and ablation on the headline record, `results/31_*` | pre-Test only |
| 5 | `run_32_round3_test.py`: the Test and fresh-data read, `results/32_*` | script committed first; frozen-commit guard |
| 6 | `run_33_round3_reconcile.py` → `RESULTS.md` § Round 3; the C13, C16, C20 and C21 ledger rows in `OUTLINE.md` | the T13 "Done when" |
| 7 | Figures `rr3-*`: regime map with counts, regime lag, turnover sources, revision ladder (ΔSR against ΔTO with CIs), equity curves | `nature-figure` pass, then the `figures` and `colors` skills; both axes labelled |

## 9. Open questions for Harry

| # | Question | Recommendation |
| --- | --- | --- |
| Q1 | Baseline: T0, or T1 (already vol-scaled)? | **T0.** Bullet 4 lists volatility scaling as one of the revisions, and T0 is the strategy whose haircut bullet 2 measures. Increments over T1 are printed either way |
| Q2 | Extend the data past 2026-06-29 to the latest close? | **Yes, if the Databento pull is cheap.** About four months is too short to judge a Sharpe, but it is the only clean check of the sign and the turnover. Yahoo would change the volume feed, so it is not a substitute |
| Q3 | Include RF5, the course's model step (Ridge, CatBoost)? | **Rules first.** RF5 stays as one candidate if you want the course's model ladder represented. An inner train of roughly 400–1,500 asset-months is thin for trees |
| Q4 | Bring MACD back as RF4? | **Yes.** Bullet 1 says "momentum + MACD", and Round 2 has no MACD |
