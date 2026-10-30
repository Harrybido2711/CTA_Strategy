# Resume Reproduction — Results

Two rounds were run on 2026-10-23. **Round 2 is the current answer.**

- **Round 1** tested short-horizon cross-sectional momentum: a 21-day signal, a five-day hold,
  ranked across assets every day. It is kept below as a record.
- **Round 2** tests time-series momentum as the paper in `References/` defines it: Moskowitz, Ooi
  and Pedersen (2012), a 12-month look-back and a 1-month hold. It adds the volatility targeting
  and regime analysis Harry asked for. Its plan is `ROUND2.md`, committed before any Round 2 number
  existed.
- **Round 3** follows Harry's learning path. Its plan is `ROUND3.md`, pre-registered at `5d94bc8`.
  Part A, the regime analysis under the dynamic cut, has run (below). Part B, the model and the
  optimizer, has not.

**Sample:** 37 liquid US-listed ETFs as futures proxies, daily, total-return prices, returns in
excess of the 3-month bill (DTB3 × net exposure). **Execution:** next-close fill, 5 bp per side
plus 2 bp slippage, $1 of capital. **Record:** 2021-02 → 2026-06, 65 monthly rebalances.
**Test:** 2025-07 → 2026-06, read at commit `deeeb61`. That is the second look at those quarters:
Round 1 read them first, for different books.

## Round 3, Part A — the regime analysis (2026-10-30)

**Sample:** pre-Test only, 2021-02 → 2025-06. That gives 53 month-ends (2021-01-29 → 2025-05-30)
and 1,954 asset-months; returns after 2025-06-30 are masked. **Cut:** dynamic D only: the
percentile among the trailing 252 trading days, split into terciles. **Books:** T0 and T1 of Round 2,
realistic execution, in excess of bills. Script `run_30_round3_regimes.py`, tables
`results/30_*`. What each finding implies for Part B is in `ROUND3.md` A9.

### Bullet 3, as worded: not supported per asset

High-volume / low-σ minus low-volume / high-σ, as sign × next-month excess return
(`30_regime_corner`):

| Statistic | Value |
| --- | --- |
| Corner | **+0.62% a month**, t 0.75 |
| Months with both cells present | 20 |
| Periods positive | 2 of 5 (2021 +1.74%, 2022 −0.25%, 2023 +3.47%, 2024 −1.72%, 2025H1 −2.04%) |
| 90% CI (stationary bootstrap over months, widest of mean block 1, 3, 6) | −0.71% to +1.89% |

**C16 fails on both counts.** Neither of an asset's own terciles predicts its next-month trend
return: by own volume, low +0.26%, mid +0.44%, high −0.20% a month; by own σ, +0.25%, −0.51%,
+0.37%. All |t| < 1.4 (`30_regime_marginals`).

### What does predict: the market's implied-volatility state, with the opposite sign

| T0, by VIX state | Low | Mid | High |
| --- | --- | --- | --- |
| Same day (state t, return t), a year | +12.4% (513 days) | +6.0% (240) | −14.0% (355) |
| **Next month (state at the month-end, return over the following month), a year** | **−6.3%** (24 months) | −10.1% (8) | **+17.5%** (21, t 2.0) |

The same-day row reproduces Round 2's table to the decimal. The next-month row reverses it: a
high-VIX month-end is followed by a **better** month for trend. T1 shows the same pattern, at
−3.3% after low and +12.7% after high (t 2.1).

Per asset, the risk-scaled trend return (sign × 40%/σ × return) is **+3.49% a month higher** after
the asset's index (VIX, or MOVE for the 7 bond ETFs) closes a month in its high tercile than after
it closes in its low one. That is t 2.83 with SEs clustered by month. Adding the sizing σ and
trend strength as controls leaves it at t 2.87, so it is not information the 1/σ sizing already
uses (`30_regime_regressions`).

**How fragile** (`30_book_predictive_checks`). T0's high-minus-low gap is +1.98% a month:

- by year, +4.92% in 2021, +5.76% in 2022 and +0.92% in 2024; each other year has only one of the
  two states;
- with any one year left out, +1.66% to +2.41%;
- without the two best high-VIX months, 2021-11 and 2022-02, +1.15%.

21 high months is a thin base. The finding is descriptive.

**Market volume** leans the resume's way but rests on 2022. T0 earns +14.8% a year after a
high-volume month-end (t 2.1, 22 months) against +0.5% after a low one (17). Year by year the gap is
+1.11%, +3.07%, −1.36% and −1.56% a month in 2021–2024, and with 2022 left out it is +0.03%.

### The regime lag (`30_regime_lag`, `30_regime_lag_windows`)

17 events between 2021-05 and 2025-03 in which VIX entered its high tercile, at least 21 trading
days apart:

| Window | T0, mean of events | T1 |
| --- | --- | --- |
| Days −20 to −1 | +2.64% (SE 0.73) | +1.76% |
| **Entry day 0** | **−1.02%** (SE 0.30; 15 of 17 negative) | −0.70% |
| Days 1 to 20 | +0.25% (SE 1.23) | +0.12% |
| Days 21 to 60 | −0.56% (SE 1.39) | −0.23% |

The loss is booked on the day the label flips, and the book is flat afterwards. A label known at
that close cannot avoid it, which is why Round 2's month-end and daily cuts both chose m = 1.
Across assets the trailing σ_fast / σ_slow moves only from 0.95 to 1.00. The average VIX rises
from 18.4 to 21.0: under the dynamic cut, "entering high" is usually a modest rise after a calm
stretch.

### Where the turnover comes from (`30_turnover_sources`)

| Book | Weight changes a year | Parts of the change |
| --- | --- | --- |
| T0 | 9.8 (engine-executed on the record: 10.5) | sign flips 64%, sizing 19%, caps 17%, entries and 1/S 0% |
| T1 | 10.3 (10.6) | T0's own change 50%, leverage changes 40%, caps 11% |

Turnover runs faster after high-VIX month-ends: T0 trades at 11.1 a year then, against 8.9 after
low ones. Sign flips are the signal itself. A turnover penalty can only cut cheaply into the
sizing, cap and leverage trades: 36% of T0's parts and 51% of T1's.

### Regenerate Part A

```bash
.venv/bin/python Resume_Reproduction/run_30_round3_regimes.py
```

## Round 2 — time-series momentum

### Bottom line

- **The paper's strategy works on this data.** T0, the sign of each ETF's 12-month excess return
  sized at 40% / σ and held a month, earns +4.8% a year in excess of bills after costs. Its Sharpe
  is 0.32 over 2021-02 → 2026-06 and 1.06 on Test. Look-backs of 6–12 months earn; 1–3 months lose,
  as in the paper.
- **Execution now costs a defined share of the return.** It costs 12% of the next-close naive
  return over the record, and 23% before Test. Against the same-close naive return the figures are
  17% and 35%.
- **Volatility targeting is the leverage adjustment that works.** T1 scales the whole book to 10%
  ex-ante volatility. That lifts the Sharpe from 0.32 to 0.46 and halves the drawdown, from −0.42
  to −0.22.
- **Cutting leverage on a high-VIX state does not work.** That holds whether the cut is set at
  month-ends (T2) or every day (T3). T0 does lose heavily while VIX is high, but by the time the
  state reads high the drawdown has happened.

### Books, after costs, in excess of bills

| Book | Record: excess return | Record: Sharpe | Record: max drawdown | Test: Sharpe | Turnover a year | Mean gross |
| --- | --- | --- | --- | --- | --- | --- |
| T0, the paper, before costs | +5.6% | 0.37 | −0.41 | 1.13 | 11.1 | 2.84 |
| **T0, the paper** | **+4.8%** | **0.32** | **−0.42** | **1.06** | 11.1 | 2.84 |
| **T1, 10% volatility target** | **+4.5%** | **0.46** | **−0.22** | **1.23** | 11.0 | 2.00 |
| T2, T1 + month-end VIX cut (m = 1) + deadband | +4.5% | 0.45 | −0.23 | 1.25 | 10.7 | 2.00 |
| T3, daily leverage, VIX cut (m = 1) | +4.3% | 0.43 | −0.23 | 1.25 | 12.0 | 1.99 |

On the pre-Test window alone, 2021-02 → 2025-06, T0's Sharpe is 0.17 and T1's 0.28. The record's
standard error on a Sharpe is about 0.43, so these are point estimates, not proofs. T0's 90%
bootstrap CI runs from −0.35 to +1.01, and T1's from −0.22 to +1.17.

### The four bullets, measured again

| Resume claim | Round 2 measurement | Verdict |
| --- | --- | --- |
| Momentum and MACD signals, engine with Sharpe, drawdown, turnover, IC, win rate | TSMOM per the paper, with every metric computed. MACD is not part of Round 2 | the momentum half holds |
| Over 25% of naive returns lost to execution | 23% of the next-close naive return (35% against same-close) before Test; 12% (17%) over the record; 5% (2%) on Test | **holds before Test against the same-close base; about 12–17% over the whole record** |
| Trend works best in high-volume, low-volatility regimes | Market level: T0 earns +17% a year when VIX is low, +16% mid, −21% high (426 days). Per asset: high-volume / low-σ beats low-volume / high-σ by +0.82% a month, t 1.35, positive in 4 of 6 periods | **the volatility half is strongly supported; the volume half leans the right way but is not "consistent"** |
| +8% out-of-sample Sharpe from regime-aware features, volatility scaling and turnover controls | T1 − T0: +0.14 of Sharpe over the record (+44% relative), 90% CI −0.04 to +0.34. On Test: +0.17, CI +0.003 to +0.35 | **volatility scaling more than covers +8%, but the record's CI touches zero; the regime overlay added nothing** |
| −14% annual turnover | T1 leaves turnover unchanged (CI −9.6% to +7.2%); T2's deadband trims it 2–3% | **not reproduced: monthly rebalancing already keeps turnover at about 11 turns a year** |

### Regime analysis (Harry's request)

| VIX state | Days | T0 excess a year | T0 Sharpe | T1 excess a year | T1 Sharpe |
| --- | --- | --- | --- | --- | --- |
| low tercile of the trailing year | 596 | +17% | 1.45 | +13% | 1.76 |
| mid | 336 | +16% | 1.10 | +15% | 1.60 |
| high | 426 | −21% | −1.12 | −15% | −1.13 |

- **The pattern holds on Test alone.** Low: +46.5%, mid: +41.9%, high: −58.6% a year, on 83, 96 and 71 days.
- **T1 already de-levers in loud markets.** Its gross fell to about 1× in late 2022 while T0 stayed
  between 2× and 3×; see `figures/rr2-leverage-path`.
- **A further cut on high-VIX days lowered the Sharpe every time it was tried.** With m = 0.5, T3's
  pre-Test Sharpe falls from +0.25 to −0.18 and turnover rises from 11 to 28 turns a year. The
  loss happens while VIX is rising; cutting after the state flips sells the bottom and misses the
  recovery.

### Robustness

| Check | T0 Sharpe, record | T1 Sharpe, record |
| --- | --- | --- |
| Headline | 0.32 | 0.46 |
| Cost grid: 2–10 bp, slip 0–5 bp, borrow 0–50 bp/yr | 0.22 to 0.35 | 0.32 to 0.51 |
| Price return, no distributions | 0.47 | 0.64 |
| Without the 7 bond ETFs | 0.33 | 0.44 |
| Data truncated at 2025-12-04 | 0.25 | 0.38 |

Every row stays positive. The full paper grid (k × h) on every sample is
`results/21_tsmom_grid.csv`: Sharpe 0.32–0.39 for k = 6–12 months, negative for k = 1.

### Figures

| Figure | Shows |
| --- | --- |
| `figures/rr2-equity-curves-{light,dark}.png` | T0 before and after costs, T1, T3 |
| `figures/rr2-regime-bars-{light,dark}.png` | excess return by VIX state |
| `figures/rr2-leverage-path-{light,dark}.png` | T0 and T1 gross exposure, high-VIX days shaded |
| `figures/rr2-tsmom-grid-{light,dark}.png` | the paper's look-back × holding grid, Sharpe after costs |
| `figures/rr2-haircut-{light,dark}.png` | T0's return after each execution assumption |

### Regenerate Round 2

```bash
.venv/bin/python Resume_Reproduction/run_20_round2.py          # pre-Test: grid, T0, T1, regimes, m for T2
.venv/bin/python Resume_Reproduction/run_20b_round2_t3.py      # pre-Test: amendment 1, m for T3
.venv/bin/python Resume_Reproduction/run_21_round2_test.py     # the Test read and robustness
.venv/bin/python Resume_Reproduction/run_22_round2_reconcile.py
.venv/bin/python Resume_Reproduction/make_rr_figures.py
```

---

# Round 1 — short-horizon cross-sectional momentum (superseded)

Measured on 2026-10-23. **Sample:** 37 liquid US-listed ETFs as futures proxies, daily bars,
2020-01-02 → 2026-06-29, split-adjusted copy, price returns. **Out of sample:** 18 walk-forward
quarters, 2022Q1 → 2026Q2. Each quarter is traded by choices made from the quarters before it
(`OUTLINE.md` § 4.5). **Test:** 2025Q3 → 2026Q2, read once at 14:49 against commit `36e86c4`.
**Execution:** next-close fill, 5 bp per side plus 2 bp slippage, $1 of constant notional, net 0,
gross 2.

This file is the authoritative home of every measured number. `OUTLINE.md` § 2 carries each
claim's one-line status, and `results/` carries the tables behind it.

## Round 1 bottom line

None of the four resume bullets reproduces on this data. The reasons are measurable:

- **There is no edge to keep.** At a five-day horizon the momentum signal has no edge over
  2022–2026: G5 − G1 is −0.19% per five days (t −0.93). Every MACD cell is mildly negative. Before
  costs B0 returns −1.2% a year, with a 90% CI of −11% to +9%.
- **Friction is the whole story.** B0 turns its gross book over 39 times a year. At 7 bp per side
  that costs about 500 bp a year, and turns a zero edge into −6.3% a year.
- **The rebuild changes turnover, not performance.** B1 cuts turnover 4.5% (CI −7.9% to −0.9%).
  Its Sharpe change is −0.04, with a CI of −0.52 to +0.43.
- **Turnover control is the lever that works.** The only book that survives costs is the
  turnover-penalised optimizer: +2.2% a year over 18 quarters (Sharpe 0.20) and +5.6% on Test, on
  15 turns a year.

## Claimed versus measured

| Resume claim | Measured | Where |
| --- | --- | --- |
| Momentum and MACD signals | MOM's G5 − G1 is −0.19% per 5 days (t −0.93), not monotone. One of 18 rungs found a MACD band, and none passed validation, so B0 traded MOM only | `01_bucket_mom`, `09_selected_signals_all_rungs` |
| Engine reports Sharpe, drawdown, turnover, IC, win rate | All computed. B0: Sharpe −0.41 (CI −1.07 to +0.23), drawdown −0.50 of capital, 38.9 turns a year, IC −0.014, win rate 0.502 against a base rate of 0.522 | `06_scorecard`, `01_signal_quality` |
| Over 25% of the naive return lost to execution | **Undefined as a ratio**, because the naive return is not positive (−1.2% a year). Friction costs 509 bp a year. On the train-ladder quarters alone, where the naive return was +3.3% a year, costs took 149% of it | `03_haircut_waterfall_test`, `11_waterfall_wf` |
| Trend signals work best in high-volume, low-volatility regimes | **Not supported.** HV/LV minus LV/HV is −3.8 bp per 5 days (t −0.32). The difference is positive in 2 of 5 periods, and its CI runs from −26 to +17 bp. The frozen cut gives the opposite sign | `04_regime_by_period_with_test`, `04_regime_bootstrap` |
| +8% out-of-sample Sharpe | **Not supported.** ΔSR is −0.04 over 18 quarters (CI −0.52 to +0.43) and −0.18 on Test. B0's Sharpe CI includes zero, so a percentage change is undefined | `06_scorecard`, `08_robustness_rebuild_bootstrap` |
| −14% annual turnover | **Partly.** Turnover falls −4.5% over 18 quarters (CI −7.9% to −0.9%), but rises 1.5% on Test | same |

## The numbers behind it

18 walk-forward quarters, realistic execution unless the row says otherwise:

| Book | Annual return | Volatility | Sharpe | Max drawdown | Turnover per unit gross |
| --- | --- | --- | --- | --- | --- |
| B0, before costs | −1.2% | 15.4% | −0.08 | −0.31 | 38.9 |
| B0 | −6.3% | 15.4% | −0.41 | −0.50 | 38.9 |
| B1 | −4.7% | 10.4% | −0.45 | −0.41 | 37.2 |
| MACD 12/26 prop-signal | −0.4% | 16.5% | −0.02 | −0.30 | 26.0 |
| Optimizer, net 0 | +2.2% | 10.9% | +0.20 | −0.17 | 15.1 |
| P1 150/50 (prototype) | −2.4% | 17.1% | −0.14 (−0.38 after DTB3) | −0.51 | 40.4 |

On Test alone, B0 returns −7.0% (Sharpe −0.45) and B1 −5.2% (Sharpe −0.63). The optimizer returns
+5.6% (Sharpe 0.70), and P1 +5.7%, with a Sharpe of 0.31 that falls to 0.10 after DTB3.

**Execution haircut, B0, all 18 quarters.** Each line adds one assumption, in this order:

| Step | Annual return |
| --- | --- |
| Same close, no cost | −191 bp |
| + one-day delay | +74 bp (the delay helps: five-day returns reverse) |
| + 5 bp cost | −363 bp |
| + 2 bp slippage | −145 bp |
| Realistic | −625 bp |

**Models (homework C).** The OV quarters chose Equal Weights by MSE under the one-SE rule. Ridge
(λ 0.1) had the lowest OV MSE, but Equal Weights, OLS, every Ridge and two Lassos were within one SE
of it. On Test, Equal Weights beats a zero forecast by 0.13% of MSE, with an IC of 0.031. Ridge
(λ 10) would have done slightly better on Test. The boosted trees overfit.

**Optimizer (homework D, E).** The risk preference was set as a 10% annual volatility. Every cap
and turnover-penalty pair reached for γ = 5, the top of the grid, and still ran at 13.5–14.9% on
OV, because the gross limit sets the volatility. The chosen configuration is γ 5, cap 0.20, and a
turnover penalty of twice the cost. Without the penalty the same optimizer trades 89–100 times a
year and loses 6–7% a year.

**VIX and MOVE (homework B).** B0 earns +7 bp a day when VIX is in its lowest fifth of the past
year (t 1.54), and loses in the middle three fifths. The homework's ceil(ln VIX²) cut leaves cells
of 0–15 days; Test holds no stressed VIX day. Lecture 5's residual test does not pass: G5 − G1 is
+0.09% (t 0.84), not monotone, with an IC of −0.040.

## Figures

| Figure | Shows |
| --- | --- |
| `figures/rr-equity-curves-{light,dark}.png` | B0 before and after costs, B1, the optimizer, with OV and Test shaded |
| `figures/rr-execution-haircut-{light,dark}.png` | The haircut table above as a waterfall |
| `figures/rr-regime-map-{light,dark}.png` | 3×3 volume × volatility grid with every cell's count |
| `figures/rr-rebuild-scorecard-{light,dark}.png` | B1 − B0 Sharpe and turnover with bootstrap CIs |
| `figures/rr-macd-heatmap-{light,dark}.png` | t of G5 − G1 across the MACD grid |

All five pass a panel-alignment gate, a 5 pt glyph floor and a rendered collision audit. They are
PNG pairs, which is the repository's figure contract; vector export is not part of it.

## Where the plan changed after it was written

Each change is in the run ledger or the outline, and none was made to move a number toward the
resume:

| Change | Why |
| --- | --- |
| The regime cell statistic became the signal-weighted return | The pre-registered per-date G5 − G1 inside a cell was not computable: about four assets per cell per date |
| The win-rate base rate is pooled over the sample | A per-date majority is an oracle that knows each day's market |
| Lasso's λ is a fraction of λ_max | The lecture's absolute values zero every coefficient on daily returns |
| A display flag marks VIX/MOVE states under 60 days | Cells of 0–15 days were being shown without one |
| γ stayed at the top of the pre-set grid | The 10% target was not reachable; the grid was not widened |

## Open threads for the next round

The evidence points at three levers, none of them tried yet:

- **Trade less.** Every book that survives costs is a book that trades less: the optimizer with a
  turnover penalty, and to a lesser degree MACD 12/26 at 26 turns a year. B0's score is a daily
  re-ranked percentile, and that is what drives its 39 turns.
- **Match the horizon to the signal.** At a five-day horizon these series reverse, which is why the
  one-day delay helps. A trend signal is usually scored, and held, over weeks to months.
- **Treat the regime result as cut-dependent.** The rolling, frozen and full-sample cuts disagree on
  sign. No single cut should carry a claim.

## Regenerate

```bash
.venv/bin/pip install -r Resume_Reproduction/requirements.txt
.venv/bin/python Resume_Reproduction/run_00_data.py          # W1 data fix and checks
.venv/bin/python -m pytest -q Resume_Reproduction/tests      # 30 tests, incl. parity with backtest.py
.venv/bin/python Resume_Reproduction/run_01_signals.py       # W3
.venv/bin/python Resume_Reproduction/run_02_portfolios.py    # W4
.venv/bin/python Resume_Reproduction/run_03_haircut.py       # W4
.venv/bin/python Resume_Reproduction/run_04_regimes.py       # W5
.venv/bin/python Resume_Reproduction/run_05_vix_move.py      # W6
.venv/bin/python Resume_Reproduction/run_06_rebuild.py       # W7
.venv/bin/python Resume_Reproduction/run_07_models.py        # W8
.venv/bin/python Resume_Reproduction/run_08_optimizer.py     # W9
.venv/bin/python Resume_Reproduction/run_09_test.py          # W10, the Test read
.venv/bin/python Resume_Reproduction/run_10_robustness.py    # W10
.venv/bin/python Resume_Reproduction/run_11_reconcile.py     # W11, plot data and ledger status
.venv/bin/python Resume_Reproduction/make_rr_figures.py      # W11, figures
```

Every script is deterministic, and every result file carries its sample statement and a JSON
sidecar with the commit it ran at.
