# Round 3 — Regime analysis, then the learning path's model and optimizer

**Status: pre-registration, 2026-10-30.** Committed with `config.ROUND3` before any Round 3 number
exists. Every number below is a Round 2 result, cited from `RESULTS.md` or `results/20_*` /
`results/21_*`, or a target the resume claims.

Harry decided two things on 2026-10-30:

- **Regimes use the dynamic cut D only.** That is the rolling 252-day tercile.
- **Part B follows his learning path.** The course notes are at
  `Career_Preparation/Leetcode/database/finance/strategies/paths/cta-strategy/`, chapters 01, 07, 08
  and 09. They fix what happens after the model is trained: μ̂ → Σ̂ → the optimizer with λ and γ →
  λ and γ chosen on validation → apply → evaluate.

This replaces the outline of 2026-10-29 (commits `94c4aca` to `efe3a3e`). Its hand-written
revision menu (VS / RF / TC) is retired. In the course pipeline each piece has a home: regime
features enter **the model**, volatility scaling is **the optimizer's risk term**, and turnover
control is **its γ term**.

## 1. The starting line: what Round 2 left open

Round 2 (`ROUND2.md`) built the strategy the resume describes: the paper's time-series momentum,
executed realistically. Bullets 3 and 4 are about what happened **after** that point. The regime
analysis came next, and the revisions were built from it. Round 3 is that second half.

| Bullet | Round 2 measured | Left for Round 3 |
| --- | --- | --- |
| 2: over 25% lost to execution | T0's haircut: 23% of the next-close naive return before Test (35% against same-close); 12% (17%) over the record | Recompute for the final book. The turnover term should win part of it back |
| 3: trend works best in high-volume, low-volatility regimes | **Volatility half, market level:** T0 earns +17% a year in the low-VIX tercile, +16% mid and −21% high (596 / 336 / 426 days), but these are same-day states (A3). **Volume half, per asset:** HV/LV − LV/HV is +0.82% a month, t 1.35, positive in 4 of 6 periods. Before Test the 3 × 3 map is not monotone: high-volume / mid-σ is the worst cell (−1.52% a month, t −1.70) | Part A |
| 4: +8% OOS Sharpe and −14% turnover from regime features, vol scaling and turnover controls | Volatility scaling (T1) moves the Sharpe from 0.32 to 0.46, 90% CI of the change −0.04 to +0.34. Cutting leverage on a high-VIX state lowered the Sharpe every time it was tried. Turnover stays near 11 turns a year | Part B |

## 2. The question

Start from the execution-aware baseline, the strategy whose haircut is bullet 2. Does a regime
analysis, and then the learning path's model and optimizer built on it, raise the out-of-sample
Sharpe and cut annual turnover? Each answer is reported as:

- ΔSR, absolute, and as a percentage only under C20's rule;
- ΔTO%;
- a CI;
- the sample and the observation count.

## 3. What is fixed

| Item | Value |
| --- | --- |
| Baseline R0 | **T0**: sign of the 12-month excess return, × 40%/σ, / S, monthly, caps 0.5 per asset and 3× gross. Decided 2026-10-30. T1 is printed beside it |
| Data, prices, returns | as Round 2: 37 ETFs, daily, total-return prices, excess of DTB3, the split-adjusted copy (DATA § 4) |
| Execution | signal at the month's last close, trade at the next close; 5 bp per side + 2 bp slippage; $1 of capital |
| Turnover | executed turnover per unit gross, per year, as in Round 2 |
| Asset classes | the four of `config.UNIVERSE_CATEGORY`: equity 21, bonds 7, commodities 6, alternatives 3. Chapter 100's six-way table splits equity into U.S. broad 5, U.S. sectors 11 and international 5 |
| Regime cut | **D only**: the value's percentile among the trailing 252 trading days, including today (126 to start), split at 1/3 and 2/3 |

## 4. Part A — the regime analysis

Descriptive only. It runs on **2021-02 → 2025-06**, which excludes Test. It explains what Part B
should find; it chooses nothing in Part B, whose grids are fixed in § 5.

### A1. Measures, all computed from data through t − 1 (indices through t)

| Measure | Definition | Level |
| --- | --- | --- |
| V, volume | 21-day mean volume, D-ranked against the asset's own past. DATA § 3: one venue feed, so never compared across assets | per asset |
| σ, volatility | 21-day realised volatility, D-ranked against the asset's own past; σ_fast / σ_slow (EWMA com 10 / 60) beside | per asset |
| VIX, MOVE | D terciles. The 7 bond ETFs are labelled by MOVE, the other 30 by VIX: a rate sleeve labelled by VIX is labelled wrongly (course, *Volatility Signals*) | market |
| Market volume | cross-sectional mean of the per-asset V percentiles, D-ranked | market |
| Correlation | average pairwise 63-day correlation of the 37 ETFs, D-ranked | market |
| Trend strength | 12-month excess return / (σ × √1 year), in z units | per asset |

### A2. The cut

**D only** (Harry, 2026-10-30). The static cuts were compared in Round 1 and Round 2 (DATA § 6.1,
`results/20_regime_returns.csv`), and that comparison is not repeated.

### A3. Timing: every table in two alignments

| Alignment | State | Return | Answers |
| --- | --- | --- | --- |
| Contemporaneous | the state on day t | the book's return on day t | when the book loses: descriptive only |
| Predictive | the state known at the decision close (month-end t, or t − 1 for a daily rule) | the return after the trade | whether the state can be acted on |

**Only a predictive table can motivate a change.** Round 2's VIX-state table
(`results/20_regime_returns.csv`, the +17% / +16% / −21% row of `RESULTS.md`) joins the VIX close
of day t to the return of day t, so it is contemporaneous. That is why it looks strong while the
overlay it suggested chose m = 1.

### A4. The per-asset regime map (bullet 3)

- **Cells.** V tercile × σ tercile at each month-end. The outcome is sign × next-month excess
  return, with the book's version, sign × 40%/σ × return, beside it.
- **Counts.** Asset-months, months and episodes are printed in every cell.
- **The corner.** HV/LV − LV/HV, plus a pooled regression with a V × σ interaction and SEs
  clustered by month. The 37 assets in one month share one market shock, so they are not 37
  independent observations.
- **"Consistently".** C16's rule: the corner is positive in every period (2021, 2022, 2023, 2024,
  2025H1), and its episode-bootstrap CI excludes 0. Otherwise the fallback wording in `OUTLINE.md`
  applies.
- **By asset class.** Each of the four classes is a descriptive column. Alternatives holds 3
  assets, so its cells will often be too thin to read.

### A5. The book by market state

T0 and T1 are reported by VIX, MOVE, correlation and market-volume state, in both alignments, with
day and month counts. A 2-D VIX × market-volume table covers homework B's two-dimensional view.
Rows are compared by mean return with its error bar, not by Sharpe: a Sharpe carries the state's
own volatility in its denominator.

### A6. The regime lag

An event study: the cumulative excess return of T0 and T1 from 20 days before to 60 days after VIX
enters its high tercile, with the cross-asset mean σ_fast / σ_slow over the same window. It
measures why the month-end and daily state cuts of Round 2 arrived too late, and which estimate
reacts in time.

### A7. Is it new information?

T0 already sizes each asset by 1/σ, so part of any volatility regime is already spent. Chapter 04
§ 3.2 residualizes the label on what the book already uses. Here that means regressing the book's
signed next-month return (sign × 40%/σ × return) on the regime labels, with and without the sizing
σ and trend strength as controls, SEs clustered by month.

- A label whose effect disappears is recorded as "already in the book".
- Volume enters no sizing rule, so a volume effect that survives is new.

### A8. Where the turnover comes from

T0's and T1's Σ|Δw| at each rebalance is split into four sources:

- sign flips;
- per-asset σ resizing;
- book-leverage changes (T1 only);
- assets entering or leaving, and the caps.

Each source is also shown by VIX state. This shows what the optimizer's γ term has to work on: a
penalty can delay a resize cheaply, but a sign flip is the signal itself.

### A9. Output: findings, written 2026-10-30 after `run_30_round3_regimes.py`

Which features and which optimizer terms Part B should be expected to use, and why. This changes
nothing in § 5. The numbers are in `RESULTS.md` § Round 3, Part A.

| # | Finding | Part B should be expected to |
| --- | --- | --- |
| F1 | **The per-asset corner fails C16.** High-volume / low-σ beats low-volume / high-σ in only 2 of 5 periods, with a CI that spans 0. Neither the asset's own volume tercile nor its own σ tercile predicts its next-month trend return | give the V-rank and σ-rank features little weight; Lasso should zero them |
| F2 | **The market's implied-volatility state predicts the next month, with the sign opposite to the same-day table.** After a month-end in the high tercile of VIX (MOVE for bonds), trend returns are higher. The effect survives the sizing σ and trend strength as controls, so it is new information. It holds in each year where both states occur, but two months carry half of it | let index-rank and z12 × index-rank carry weight. Nothing here supports de-levering after a high-VIX month-end |
| F3 | **High market volume precedes better months, but only through 2022.** Without 2022 the gap is about zero | weak or no weight on corr-rank and market volume |
| F4 | **The regime lag is total.** Around VIX entering its high tercile, the book gains in the 20 days before, loses on the entry day itself, and is flat afterwards. σ_fast / σ_slow barely moves | no gain from regime timing. A label known at the close arrives after the loss, and Σ̂ lags as well |
| F5 | **Turnover is mostly sign flips.** In T0 they are 64% of the parts of the weight change. In T1, leverage changes are 40% | the γ term can only cut cheaply into sizing, cap and leverage trades. A −14% cut has to come from those, not from the flips, which are the signal itself |

## 5. Part B — the learning path at the paper's horizon

### B0. The eight steps, mapped

| Course step | Round 3 |
| --- | --- |
| 1 Clean | as Round 2 |
| 2 Build the signals | the features in B1, per asset, at each month-end F |
| 3 Test each signal | IC and bucket test of every feature, reported on pre-Test. **No feature is dropped on that sample**, because a pre-Test screen would leak into the walk-forward record. Selection is left to the model inside each rung (Lasso's zeros, a tree's splits), as chapter 01 step 5 allows |
| 4 Standardize | clip at ±3 sd, then z-score with the rung's training mean and sd (chapter 07) |
| 5 Combine: the model | B2 |
| 6 Walk-forward | B4 |
| 7 Score and scale | **the optimizer** of chapter 09, which replaces proportional scaling: B3 |
| 8 Trade and evaluate | next close, 5 + 2 bp; read the stitched apply quarters, then OV, then Test once (B5) |

### B1. Features

| Family | Feature | Definition |
| --- | --- | --- |
| Momentum | z1, z3, z6, z12 | k-month excess return / (σ_F × √(k/12)), with σ_F the paper's EWMA (com 60, × 261). The paper's look-backs; Round 2 found 6–12 earn and 1–3 lose |
| MACD | macd | chapter 03's slowest pairing on its ladder, (21, 63): (EMA₂₁ − EMA₆₃) / P, divided by σ_F |
| Regime, D percentiles minus 0.5 | σ-rank, V-rank, index-rank, corr-rank | the A1 measures as continuous ranks; the index is VIX, or MOVE for the 7 bond ETFs |
| Interactions | z12 × each regime rank | lets the linear models condition the trend on the regime. Trees find this by themselves (chapter 08, *Why tree models*) |

"Regime features off" means Momentum + MACD only.

### B2. The model ladder (chapter 08)

- **Target.** y = next-month excess return / σ_F, pooled across assets, so that 37 assets with
  different volatility share one scale. The expected return is μ̂ = ŷ × σ_F, monthly.
- **Models.** Each has its inner grid; hyperparameters are chosen by validation MSE (homework C):

  | Model | Inner grid |
  | --- | --- |
  | **EW** | the mean of the standardized Momentum + MACD features, mapped to ŷ by a one-slope regression on train |
  | **Ridge** | α ∈ {0.1, 1, 10, 100} |
  | **Lasso** | α ∈ {0.01, 0.03, 0.1, 0.3} × α_max |
  | **CatBoost** | depth ∈ {2, 3}, 300 iterations, learning rate 0.03 |
  | **HistGradientBoosting** | max depth ∈ {2, 3}, 200 iterations, learning rate 0.05, min leaf 20 |

### B3. The optimizer (chapter 09)

$$ \max_w \ \hat\mu^\top w - \gamma \sum_i |w_i - w_{\text{prev},i}| \quad \text{s.t.} \quad w^\top \hat\Sigma w \le \sigma_0^2,\ \ |w_i| \le 0.5,\ \ \sum_i |w_i| \le 3,\ \ \mathbf{1}^\top w \le 1 $$

- **λ, as a risk budget σ₀.** Chapter 09 shows Form B (risk capped at σ₀) and the λ form reach the
  same book, one λ per σ₀. Two-fund separation makes λ a choice of how much risk to hold. The
  course's λ grid, {1e-4, 0.01, 0.1, 1}, is unit-dependent: here w* ≈ Σ⁻¹μ/(2λ) would put every
  value below 1 against the caps. So λ is written in the units it means: σ₀ ∈ {5%, 10%, 15%, 20%}
  a year, four values, as the course has four.
- **γ, the turnover penalty.** The course's grid, {1e-4, 0.01, 0.1, 1}, in monthly-return units per
  unit of capital traded. The trading cost itself is 0.0007.
- **Σ̂.** The EWMA covariance of daily excess returns (com 60) × 21, the estimate T1 already uses.
  Homework D's residual covariance is not used: a quarter of monthly residuals gives 3 to 12
  observations for a 37 × 37 matrix.
- **The constraints.** The per-asset and gross caps are T0's, so R0 and the optimizer differ only
  in how weights are formed (`OUTLINE.md` § 6.1). The net ≤ 100% bound is the course's.
- **w_prev.** The live book's weights. At the start of a validation quarter that is the book as
  the previous rung left it; before the first rung it is zero.

### B4. Walk-forward (chapters 01 and 07)

| Item | Rule |
| --- | --- |
| Segment | one calendar quarter (chapter 07: two to three months), by **holding month**. A position held in month m was formed at the end of m − 1 |
| Rung | train on 3 segments, validate on 1, apply to the next. Slide one segment. Apply quarters 2022Q1 → 2026Q2, 18 rungs. This is Round 1's ladder (`rr_split.rungs`) on monthly rows |
| Labels | at a fit date F, a training row is used only if its holding month ended by F. That is the monthly purge |
| Inner layer, per rung | (1) fit every model's grid on train; (2) choose its hyperparameter by validation MSE; (3) backtest the 16 (σ₀, γ) pairs over the validation quarter with that model's predictions; (4) refit on train + validation (chapter 07's second house style); (5) apply to the next quarter with the chosen pair |
| Choosing (σ₀, γ) | chapter 09: by the equity curve and the drawdown, the Sharpe only as a tie-break. Operationally: drop pairs whose validation max drawdown is deeper than the grid's median; of the rest, take the highest cumulative excess return; if the top two are within one SE of the mean daily return, the higher Sharpe |
| Outer layer, OV 2024Q3 → 2025Q2 | candidate procedures = 5 model classes × regime features off / on = **10**. Each is run unchanged through every rung; OV chooses one by the same rule |
| Test 2025Q3 → 2026Q2 | the chosen procedure, read once by a script committed before it runs (frozen-commit guard). **The third look at those quarters**, labelled so everywhere |

### B5. What is reported

| Book | What it isolates |
| --- | --- |
| R0 = T0 | the baseline |
| T1 | Round 2's rule-based volatility scaling |
| P, the chosen procedure | the learning path's book: **bullet 4's refined strategy** |
| P with regime features off | the regime-aware features' contribution |
| P with γ fixed at 1e-4 | the turnover term's contribution |
| All 10 procedures | the stitched train-ladder record, every one, so the OV choice can be seen against what it chose from |

## Amendment 1 — the three execution factors inside the optimizer (Harry, 2026-10-30)

Added after Part A and **before any Part B number existed**. Harry asked that the book anticipate
the three factors of bullet 2 when it chooses its weights. Before this amendment it only paid
them afterwards. The engine already charges all three on every fill. What changes is that the
optimizer now prices them in advance.

| Factor | In the engine (unchanged) | In the optimizer and the model (new) |
| --- | --- | --- |
| **Transaction cost** | c = 5 bp per side + s = 2 bp slippage on traded dollars | a cost term −φ Σᵢ κᵢ \|wᵢ − w_heldᵢ\|, with κᵢ = (c + s) / 10⁴ per dollar traded. **φ = 1, fixed**: a cost is an expense, not a preference, so it is not tuned |
| **Turnover** | — | the γ term, as before: a penalty on top of the cost, chosen on validation from the course's grid |
| **Execution delay** | the fill is d trading days after the decision close; d = 1 | the model is trained on the return from the fill F + d to the next month-end F′; the optimizer trades from **w_held**, the live book drifted at prices to the decision close |

So B3 becomes:

$$ \max_w \ \hat\mu^\top w - \sum_i (\varphi \kappa_i + \gamma)\,|w_i - w_{\text{held},i}| \quad \text{s.t.} \quad w^\top \hat\Sigma w \le \sigma_0^2,\ \ |w_i| \le 0.5,\ \ \sum_i |w_i| \le 3,\ \ \mathbf{1}^\top w \le 1 $$

- **With one cost rate for every ETF, φκ and γ add.** The cost is then a floor under γ: even at
  γ = 1e-4 a trade is made only if its expected gain beats 7 bp. The cost grid (§ 7) re-solves
  the optimizer at each cost rate, so the book always prices the cost it is charged.
- **The label is known at F′.** A training label ends at the next month-end close, not at the next
  fill, so at a fit date F every label ending by F is usable. No row is purged, and the label omits
  the first d days of its holding month and none after it.

**What is added to B5.** The chosen procedure P is also reported:

- with φ = 0, blind to costs, which the engine still charges;
- with γ = 1e-4;
- with both;
- at d = 2 and d = 3, re-run end to end and re-trained at that delay.

**What is added to § 7.** An execution waterfall for P beside R0, bullet 2's decomposition:

1. same-close and free (d = 0, non-executable);
2. next close (d = 1);
3. + 5 bp cost;
4. + 2 bp slippage.

This is reported with H₁ and H₀, and with how much of R0's haircut the cost-aware optimizer wins back.

## Amendment 2 — γ in the units it means (Harry, 2026-10-30, after the pre-Test run, before Test)

**Written after the pre-Test results of Part B were seen** (`RESULTS.md` § Round 3, Part B before
Test; `results/31_*` at `a8c48d7`). It is labelled so wherever its numbers appear. Test had not
been read.

**What was wrong.** B3 kept the course's γ grid, {1e-4, 0.01, 0.1, 1}, in monthly-return units per
dollar traded. Against a cost of 0.0007, that makes three of the four values forbid trading. In
the first run P's book therefore alternated between frozen quarters and full rebuilds, and its
turnover rose 55% against R0. This is the same unit problem B3 had already fixed for λ, left
unfixed for γ.

**The change, and nothing else.** γ is written as multiples of the trading cost:

$$ \gamma \in \{0,\ 0.5,\ 1,\ 2\} \times \kappa, \qquad \kappa = 7\ \text{bp per dollar traded} $$

That is 0 to 14 bp of expected gain demanded per dollar traded, on top of the fixed cost term φκ.

Everything else stays as pre-registered:

- the 3 / 1 / 1 quarterly ladder;
- the σ₀ grid;
- the models;
- the features;
- the OV rule.

**Where it lands.** The amended run writes `results/31b_*`. The first run's `results/31_*` stay as
the record of the pre-registered grid. Amendment 1's "γ = 1e-4" ablation becomes "γ = 0", the cost
term alone.

## 6. Samples, and the caveat

| Sample | Quarters | Status in the course's terms |
| --- | --- | --- |
| Stitched apply quarters | 2022Q1 → 2024Q2, 10 quarters, 30 monthly rebalances | in-sample: the procedure was designed while looking at it |
| OV | 2024Q3 → 2025Q2, 4 quarters | out-of-sample selection: chooses the procedure, so its winner is flattered |
| Test | 2025Q3 → 2026Q2, 4 quarters | out of sample, but the third look at those quarters |
| Fresh data | 2026-07 onward, if extended (§ 9) | the only sample the Round 3 design has never seen |

**The design caveat, stated now.** The feature list and grids were written knowing Round 2's
results on all of 2021–2026. The parameters are out of sample on the walk-forward record; the
design is not. Only fresh data is clean on both.

## 7. Metrics and acceptance

These follow `OUTLINE.md` § 6.1 and § 6.3, re-based on R0 and the monthly record.

- **Sharpe.** ΔSR = SR(P) − SR(R0) on each sample of § 6, with a paired stationary-bootstrap CI
  (mean block 21 days, plus the sensitivity column). The percentage is quoted only if SR(R0)'s CI
  excludes 0 (C20).
- **Turnover.** ΔTO%, with a CI, split by A8's sources (C21).
- **Execution haircut.** H₁ and H₀ for P beside R0: how much of bullet 2's loss the turnover term
  wins back.
- **Robustness.** Each with its pass condition:
  - per-year sign count;
  - drop the best 5 and 10 days of |r_P − r_R0|;
  - the cost grid;
  - without the fixed-income ETFs;
  - data truncated at 2025-12-04.
- **Deflated Sharpe** on OV's winner. N = 10 procedures × each one's inner grid, counted by the
  script, not by hand.
- **The course's sanity line.** A weekly-or-slower book above a Sharpe of about 1 is suspected of
  look-ahead before it is credited (chapter 09).

**Power, stated now.** Test's 12 months give SE(SR) ≈ 1.0; the 54-month walk-forward record gives
≈ 0.47. For paired books with ρ = 0.9–0.95, SE(ΔSR) over the record is ≈ 0.15–0.21, so the
minimum detectable ΔSR at 80% power is about 0.4–0.5. **+8% of a 0.3 Sharpe is about 0.025.** No
result on this sample can confirm "+8%" as such; the quotable form is an absolute ΔSR with its CI.
Turnover is mechanical and measured almost without noise, so −14% is a fair test.

## 8. Deliverables and order

| Step | Produces | Gate |
| --- | --- | --- |
| 0 | this file and `config.ROUND3` | committed before any Round 3 number exists |
| 1 | `rr_round3.py` (measures, features, monthly rungs, models, optimizer) and tests in `tests/` | tests pass; a no-look-ahead test on every new measure |
| 2 | `run_30_round3_regimes.py` → Part A, `results/30_*` | pre-Test only |
| 3 | A9's findings, written up in this file | before step 4 |
| 4 | `run_31_round3_pipeline.py` → all 10 procedures through OV, the OV choice, `results/31_*` | pre-Test only |
| 5 | `run_32_round3_test.py`: the Test read, `results/32_*` | script committed first; frozen-commit guard |
| 6 | `run_33_round3_reconcile.py` → `RESULTS.md` § Round 3; the C13, C16, C20 and C21 ledger rows in `OUTLINE.md` | the T13 "Done when" |
| 7 | Figures `rr3-*`: regime map with counts, regime lag, turnover sources, the procedure comparison, equity curves | `nature-figure` pass, then the `figures` and `colors` skills; both axes labelled |

## 9. Decisions and open items

| # | Question | Status |
| --- | --- | --- |
| Q1 | Baseline T0 or T1? | **T0**, with T1 printed beside it. Recommended 2026-10-29, accepted 2026-10-30 |
| Q2 | Extend the data past 2026-06-29? | **Open.** It needs Harry's Databento pull; Yahoo would change the volume feed |
| Q3 | The course's model step? | **In**, as Part B: Harry asked on 2026-10-30 that Round 3 follow the learning path |
| Q4 | MACD back? | **In**, as the B1 feature `macd` |
| — | Regime cut | **D only**, Harry 2026-10-30 |

## Status after the Test read (2026-10-30)

Test was read once, at `7e00439`, by `run_32_round3_test.py`. The numbers are in `RESULTS.md`
§ Round 3, Part B — the Test read. In short, after costs and in excess of bills:

| Book | Test Sharpe | WF 2022Q1–2026Q2 Sharpe | WF turnover |
| --- | --- | --- | --- |
| R0 = T0 | 1.06 | 0.12 | 11.6 |
| T1 | 1.23 | 0.34 | 12.0 |
| P = CatBoost with regime features | −0.27 | 0.36 | 37.8 |

- **The learning-path book does not beat the paper's rule out of sample.** On Test, P − R0 is
  −1.33 of Sharpe, 90% CI −2.98 to +0.20.
- **Over the whole record P leads R0, but not significantly.** The gap is +0.24, CI −0.65 to +1.07,
  and it disappears without the 5 days on which the two books differ most.
- **Turnover is about three times R0's.** Within the pipeline, the γ and cost terms cut it by 24%
  against an optimizer blind to trading.

Round 2's T1 remains the best book. Any further change is post-Test: Test has now been read three
times.
