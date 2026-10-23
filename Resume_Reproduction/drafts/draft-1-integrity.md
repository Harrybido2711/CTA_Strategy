# Resume Reproduction — Execution Outline

Folder: `Resume_Reproduction/` (this file, the scripts and the result tables live here). Owner: Harry.
Date: 2026-10-23. Status of every number below: **unmeasured**. Nothing in this file is a result.

## 1. Purpose and scope

Four resume bullets, already sent to Citadel (x2), Morgan Stanley HK, BofA HK and AmEx, claim
numbers the repository has never produced:

> Developed an execution-aware CTA strategy using momentum and MACD signals, building a transparent
> Python backtesting engine to visualize cumulative returns and evaluate Sharpe ratio, drawdown,
> turnover, IC, and signal win rate. / Evaluated the impact of transaction costs, execution delay,
> turnover constraints, and slippage, demonstrating that over 25% of naive backtest returns
> disappeared after incorporating realistic execution assumptions. / Constructed rolling volume and
> volatility measures to classify market regimes, revealing that trend-following signals were
> consistently more effective in high-volume, low-volatility environments than under adverse market
> conditions. / Refined trading signals using regime-aware feature engineering, volatility scaling,
> and turnover controls, improving out-of-sample Sharpe ratio by 8% while reducing annual turnover
> by 14% relative to the baseline strategy.

| Rule | Consequence |
| --- | --- |
| Every quoted number traces to **one** measurement with a stated base, sample, instrument set, frequency and observation count | The claims ledger (§ 2) is the contract; a number without a ledger row is not quoted |
| A claim that does not reproduce is reported as such and the resume changes | Fallback wording is written now (§ 2), not after the fact |
| Nothing is tuned on the test block; no full-sample quantile is quoted | § 4.5 and § 6 |
| Measured numbers live here and in `Backtest_prototype/Backtests.md`, never in a chapter | § 8; the illustrative numbers already in `docs/chapters/00_pipeline/00_pipeline.md` are **not** measurements and are never cited as such |
| The 2025-12-05 split is fixed before any number spanning it is read | § 4.6, workstream W1 |

What the repository has today (`Backtest_prototype/backtest.py`): a single-asset dollar-to-shares
simulator with TWAP = (open + close)/2 and a one-calendar-day `merge_asof` delay **plus** a one-row
`.shift()` (so the effective lag is two rows, three across a weekend — audited in W2), a 37-asset
loop, 21-day momentum = rolling mean of daily returns, two portfolios (P1 150/50, P2 median-relative
2/N), 5-day overlap via `rolling(5).mean()`, and `perf_stats` (final PnL, annualized return and
volatility, Sharpe with r_f = 0, max drawdown). It has **no** costs, slippage, turnover metric, IC,
win rate, regime label, MACD, smoother, model, optimizer or walk-forward split.

## 2. Claims ledger

Sample conventions used by every row: 37 ETFs (`CTA_data/*_ohlcv_1d.csv`, ETFs standing in for
futures), daily bars, 2020-01-02 to 2026-06-29 (~1630 rows), split-adjusted per § 4.6; "OOS" means
the series defined in § 4.5. Status column is uniformly **unmeasured**; it is updated in place as
results land. Acceptance is decided before the run, here.

### 2.1 Bullet 1 — the engine and its metrics

| # | Claim | Supporting measurement | Base / sample | Acceptance | Fallback wording if it fails |
| --- | --- | --- | --- | --- | --- |
| C1 | "transparent Python backtesting engine … visualize cumulative returns" | `engine.py` extends `backtest.py`; equity-curve figure per book | Full sample | Engine reproduces `backtest.py`'s P1/P2 PnL to 1e-9 with costs = 0 before anything is added | None needed — already true |
| C2 | "evaluate Sharpe ratio" | § 4.1 Sharpe on daily book returns, r_f per book type | Per book, per block | Computed, with r_f convention printed beside it | None needed |
| C3 | "drawdown" | Max peak-to-trough of cumulative PnL per unit capital | Per book, per block | Computed | None needed |
| C4 | "turnover" | Annual turnover per § 4.1, on **held** weights after delay | Per book, per block | Computed | None needed |
| C5 | "IC" | Mean daily cross-sectional Spearman IC, ICIR, t-stat deflated by h = 5 | Per signal, 37 names per date, N_dates per block | Computed; mean IC within 0.02–0.05 plausibility band, or explained | "signal IC" stays; a mean IC outside the band is a bug to find, not a result |
| C6 | "signal win rate" | § 4.1: share of non-zero positions whose next-period PnL > 0; hit rate reported separately | Per book, per block, count of asset-days printed | Computed | None needed |
| C7 | "momentum … signals" | 21-day risk-adjusted momentum, bar plot G1–G5 with SE | Ladder training segments only | Computed; monotone or not, it is reported | None needed |
| C8 | "MACD signals" | MACD grid (§ W3), bar plot of the chosen band | Ladder training segments only | A contiguous warm band exists; if not, MACD still enters as a tested signal | "momentum and MACD signals (MACD tested, not retained)" |

### 2.2 Bullet 2 — the execution haircut

| # | Claim | Supporting measurement | Base / sample | Acceptance | Fallback wording if it fails |
| --- | --- | --- | --- | --- | --- |
| C9 | "transaction costs" modelled | Proportional cost c bp per dollar traded, § 4.2 | — | Implemented, c swept {1, 2, 5, 10, 20} | None needed |
| C10 | "execution delay" | Delay d in trading rows, single parameter, d ∈ {0, 1, 2} | — | Implemented; current double lag removed | None needed |
| C11 | "turnover constraints" | Deadband η on weight change; optional daily-turnover cap | — | Implemented | None needed |
| C12 | "slippage" | Adverse fill s bp off TWAP, fixed and volatility-scaled variants, § 4.2 | — | Implemented, s swept {0, 2, 5, 10} | None needed |
| C13 | "over 25% of naive backtest returns disappeared" | **Haircut H = 1 − PnL_realistic / PnL_naive**, PnL = cumulative return per unit capital over identical dates; naive = d 0, c 0, s 0, fills at close; realistic = d 1, c 5, s 2, η 0 (§ 4.2 defaults). Also reported: the same ratio on annualized return, and the Sharpe ratio haircut, so "25% of what" has one answer and two companions | Strategy S (§ 4.3), full sample net of warm-up, and separately on OOS | H ≥ 0.25 at the default cost set **and** PnL_naive > 0 **and** PnL_naive > 2 × \|PnL_naive − PnL_realistic\| (ratio is unstable otherwise) **and** H ≥ 0.25 holds across c ∈ {2, 5, 10} | If naive PnL ≈ 0: quote the drag in absolute terms — "execution assumptions cost X bp of annual return, Y turns of annual turnover" — and drop the percentage. If H < 25% at c = 5: quote the measured H with its cost level, "roughly a fifth at 5 bp per side" |

### 2.3 Bullet 3 — regimes

| # | Claim | Supporting measurement | Base / sample | Acceptance | Fallback wording if it fails |
| --- | --- | --- | --- | --- | --- |
| C14 | "rolling volume and volatility measures" | V_{s,t} = 21-day mean volume, σ_{s,t} = 21-day realized vol, both through t−1, per asset | Full sample | Computed | None needed |
| C15 | "classify market regimes" | Tercile labels per § 4.4: rolling trailing 252-day (quoted) and full-sample (diagnostic, look-ahead) | Per asset-date | 3×3 grid with counts printed per cell | None needed |
| C16 | "consistently more effective in high-volume, low-volatility" | G5−G1 spread of the signal's bar plot inside each of 9 cells, with SE and N; "consistently" = the HV/LV cell beats the LV/HV cell in ≥ 4 of 6 calendar years, and the block-bootstrap 90% CI of the cell difference excludes 0 | Ladder training + outer validation (not test); cells with < 60 distinct dates or < 500 asset-days are marked "not measurable" | Both conditions, under the rolling cut | "more effective in high-volume, low-volatility environments in most years" (drop "consistently") or, if the ordering fails, "mapped where the signal's edge concentrated by regime" with the measured grid |

### 2.4 Bullet 4 — the rebuild

| # | Claim | Supporting measurement | Base / sample | Acceptance | Fallback wording if it fails |
| --- | --- | --- | --- | --- | --- |
| C17 | "regime-aware feature engineering" | Regime multiplier m(g) on exposure, g from § 4.4 | — | Implemented | None needed |
| C18 | "volatility scaling" | w ∝ x_{s,t}/σ_{s,t}, renormalized to gross 1 | — | Implemented | None needed |
| C19 | "turnover controls" | Deadband η, chosen per § 4.5 | — | Implemented | None needed |
| C20 | "+8% out-of-sample Sharpe vs baseline" | ΔSR% = (SR_rebuild − SR_base)/\|SR_base\| on the **primary OOS series**, same baseline, same split, same cost set | OOS series (~880 days), plus per-fold and per-year | Point estimate ≥ +8% **and** SR_base > 0 (a ratio to a negative or near-zero base is meaningless) **and** Δ > 0 in ≥ 60% of folds **and** 90% block-bootstrap CI on ΔSR reported; deflated for N_v | If CI contains 0: "a modest Sharpe improvement (+x%, within sampling error) with annual turnover reduced y%". If SR_base ≤ 0: quote the absolute ΔSR and annual return difference, no percentage |
| C21 | "−14% annual turnover" | ΔTO% = (TO_rebuild − TO_base)/TO_base, § 4.1 definition, same OOS series | Same | Point estimate ≤ −14%; this one is near-deterministic and is the defensible half | Quote the measured percentage; the direction is guaranteed by the deadband, the magnitude is not |

### 2.5 Outside this repository

| # | Claim | Decision |
| --- | --- | --- |
| C22 | QFA "12% Sharpe / 15% drawdown" | **Out of scope and unverified.** Not a CTA claim, no data here, Harry says someone else added it. Recorded so that no part of this work is mistaken for support of it. Resume action is Harry's (§ 9 Q6) |

### 2.6 The interview answers this plan produces

| Question | Answered by | Artefact |
| --- | --- | --- |
| "25% of what?" | C13: cumulative return per unit capital, naive vs realistic, same dates | `results/haircut_waterfall.csv` |
| "What was the baseline Sharpe?" | C20: SR_base printed with r_f convention, block, N days | `results/scorecard.csv` |
| "Static or rolling threshold?" | § 3 flag 2: per-asset terciles are rolling trailing 252-day; VIX buckets are fixed log-ceiling cuts that use no data; a full-sample cut was run only as a labelled look-ahead diagnostic | `results/regime_grid_rolling.csv`, `_static.csv` |
| "How many days in the crisis cell?" | C15/C16 and § 4.4: counts per cell printed; cells under the floor marked not measurable | `results/regime_grid_*.csv` (N column) |
| "Which instruments, what frequency, how long?" | § 2 header: 37 ETFs, daily, 2020-01 to 2026-06, ~1630 rows, ETFs for futures | this file |
| "Is 8% just a few good days?" | § 6: per-year, per-fold, bootstrap CI, drop-best-5-days check, deflated SR | `results/robustness_8pct.csv` |
| "How many variants did you try?" | § 6 run ledger N_v | `results/run_ledger.csv` |

## 3. Red-flag resolutions

| # | Flag | Decision | Where it is discharged |
| --- | --- | --- | --- |
| 1 | QFA 12% / 15% | Out of scope, unverified; recorded in C22; Harry decides the resume action (§ 9) | § 2.5 |
| 2 | Regime threshold static vs dynamic | **Run both.** Quoted numbers use the **rolling trailing** tercile (per-asset, 252-day window, through t−1). The full-sample tercile is run as a diagnostic, labelled look-ahead, never quoted. The VIX/MOVE log-ceiling bucket is a **fixed** cut using no data — static *and* look-ahead-free; this is the honest sense in which "static" was true. Interview answer: the three sentences in § 2.6 | W5, W6 |
| 3 | 25% of what | Base fixed as cumulative return per unit capital (C13); companions reported; acceptance requires the ratio to be stable | W4 |
| 4 | 8% robustness | Baseline Sharpe printed first; § 6 protocol runs before the number is quoted; fallback wording pre-written | W7, W10 |
| 5 | Data / instruments / frequency | Stated once (§ 2 header) and printed in every result file's header row | W1 |
| 6 | Bucket count and observations | 3 per axis, 9 cells; VIX log-ceiling with c = 2 (5 occupied buckets expected); counts per cell printed; floors in § 4.4; thin cells reported as unknown, not zero | W5, W6 |

## 4. Fixed definitions, decided once

### 4.1 Metrics

| Metric | Definition | Convention |
| --- | --- | --- |
| Daily book return r_t | ΔPnL_t per unit capital (capital = 1, non-compounding, as in `perf_stats`) | — |
| Sharpe | mean(r_t − rf_t) × 252 / (std(r_t) × √252) | Strategy S is cross-sectionally demeaned (net ≈ 0) so **r_f = 0** is correct per chapter 02; any net-long variant (P1 150/50) subtracts the 3-month T-bill series (FRED `DTB3`, daily, /252) on its net exposure. Printed beside every Sharpe: `rf=0` or `rf=DTB3` |
| Max drawdown | min_t (PnL_t − max_{u≤t} PnL_u), units of capital | Same for every book |
| Daily turnover TO_t | Σ_s \|w_{s,t} − w_{s,t−1}\| on **held** weights (after overlap, after delay) | gross = 1 so one unit = one book turned |
| Annual turnover | mean(TO_t) × 252, in turns of book per year | C21's quantity |
| IC | per-date Spearman between signal at t and 5-day forward return starting at t + d; mean IC, ICIR = mean/std, t = ICIR × √(N_dates/5) | Cross-sectional across 37 names; time-series IC per asset reported as secondary |
| Signal win rate | share of asset-days with w_{s,t} ≠ 0 and w_{s,t} × r_{s,t+1} > 0; N asset-days printed | C6 |
| Hit rate | share of days with r_t > 0 | Reported with C6, never conflated |
| Bucket spread | G5 − G1 mean forward return with SE of each mean | Signal-stage metric; no Sharpe at the signal stage |

### 4.2 Execution model

| Element | Definition | Default | Sweep |
| --- | --- | --- | --- |
| Delay d | signal uses closes through t; trade on row t + d at that row's TWAP | 1 | {0, 1, 2} |
| Naive fill | d = 0 at the close of t (the look-ahead-free but frictionless case) | — | — |
| Execution price | TWAP = (open + close)/2 of the fill row | as now | — |
| Cost c | c bp × \|traded dollars\|, charged on the fill row | 5 | {1, 2, 5, 10, 20} |
| Slippage s | fill moved adversely by s bp of price, direction of the trade | 2 | {0, 2, 5, 10}; variant s_t = κ σ_{s,t}, κ = 0.1 |
| Deadband η | no trade when \|w_target − w_held\| < η | 0 (baseline) | chosen per § 4.5, grid {0.005, 0.01, 0.02, 0.05} |
| Turnover cap | optional: scale the day's trade so TO_t ≤ cap | off | reported only |
| Overlap | 5-day `rolling(5).mean()` of targets | kept | — |
| Haircut decomposition | each element alone vs naive, and all together; the waterfall figure uses the order costs → slippage → delay and says so | — | — |

### 4.3 Signals and books

| Object | Definition |
| --- | --- |
| MOM | 21-day mean of daily returns / σ_{s,t} (σ through t−1), then percentile against the asset's own trailing 252 days |
| MACD | EMA_{n_f}(P) − EMA_{n_s}(P), signal line EMA_9, histogram; standardized by trailing σ of the MACD line; grid in W3 |
| Smoother | EMA of span m applied to the standardized MACD, m < n_f |
| Strategy S (baseline B0) | equal-weight average of standardized MOM and MACD (= homework C's Equal Weights model); w_{s,t} ∝ score, cross-sectionally demeaned, scaled to gross 1; 5-day overlap; d 1, c 5, s 2, η 0 |
| Rebuild B1 | B0 with w ∝ score/σ_{s,t}, times regime multiplier m(g_t), deadband η; η and m chosen per § 4.5 |
| Single-signal books | MOM-only and MACD-only versions of B0, reported alongside |
| Winsorization | rolling 60-day 1%/99% clip computed on the raw series, never written back |

### 4.4 Regime measures

| Measure | Definition | Counts |
| --- | --- | --- |
| V_{s,t} | 21-day mean share volume through t−1, per asset (volume ×2 pre-split for the five SPDRs) | — |
| σ_{s,t} | 21-day realized vol of daily returns through t−1 | — |
| Rolling tercile (quoted) | rank of today's value against the asset's own trailing 252 days, cut at 1/3, 2/3 | expected ≈ N/9 asset-days per cell |
| Full-sample tercile (diagnostic) | cut on the asset's entire history; **look-ahead**, labelled so in every file name | — |
| Floors | a cell is quoted only with ≥ 500 asset-days and ≥ 60 distinct dates; otherwise "not measurable" | printed per cell |
| VIX bucket (i) | g_t = ⌈2 ln VIX_t⌉, cuts at e^{k/2}: 12.2, 20.1, 33.1, 54.6 | counts printed; expect the top bucket to be a few percent |
| MOVE bucket (i) | g_t = ⌈2 ln MOVE_t⌉, cuts at 90.0, 148.4, 244.7 | counts printed |
| VIX / MOVE bucket (ii) | rolling trailing 252-day quintile of the index | — |
| Residual test | regress the VIX-derived beta series on the MOM beta series (both from chapter 02's beta method); bar-plot the residual; "orthogonal is not independent" check with \|MOM\| added as a regressor | — |

### 4.5 Sample split

| Block | Trading rows (approx. dates; exact boundaries fixed from the index by `split.py` and printed) | Use |
| --- | --- | --- |
| Warm-up | 2020-01-02 → 2020-12-31 (~252) | rolling windows only, never scored |
| Ladder | 2021-01 → 2024-06 (~882 = 14 segments × 63) | rungs train 3 / val 1 / test 1 → 10 rungs, 10 OOS test segments (~630 days) |
| Outer validation | 2024-07 → 2025-06 (~252 = 4 segments) | model class, λ, η, m(g), optimizer γ and cap |
| Test | 2025-07 → 2026-06-29 (~250) | touched once, after everything else is frozen; contains 2025-12-05 |
| **Primary OOS series** (C20, C21) | ladder test segments ∪ test block (~880 days), each scored under parameters chosen only on data before it | per-fold and per-year breakdown on the same series |

Segment = 63 trading rows (one quarter). Rung k: train segments k..k+2, validation k+3, test k+4;
the inner validation picks features and (for B1) η and m(g); refit on train + validation; apply
once to test. Signal grids (W3) run on ladder training segments only.

### 4.6 Data treatment

| Item | Decision |
| --- | --- |
| XLB, XLE, XLK, XLU, XLY 2-for-1 on 2025-12-05 | **Adjust**: rows before 2025-12-05 get OHLC/2 and volume ×2, written to `Resume_Reproduction/data_adjusted/` (CTA_data untouched). Split-day bar: set open := close and high := max(low, close) for the five, and log it |
| Robustness | every test-block number is also run with the sample truncated at 2025-12-04; a sign change is reported |
| UNG, USO | already adjusted in CTA_data; verified by the `|pct_change| > 0.4` scan in W1 |
| Dividends | unadjusted throughout; stated in every result header |
| Calendar | UTC-dated bars; VIX/MOVE (US-dated) aligned on the date part, forward-filled at most one day, mismatches counted |

## 5. Workstreams

| WS | Stage / step | Inputs | Procedure | Outputs | Done when | Feeds |
| --- | --- | --- | --- | --- | --- | --- |
| W0 Environment | — | python 3.8.7 | create `.venv`; `pip install scipy==1.10.1 scikit-learn==1.3.2 statsmodels==0.14.1`; cvxpy optional (scipy SLSQP is the fallback); pin in `requirements.txt` | `requirements.txt` | `python -c "import sklearn, scipy, statsmodels"` passes | all |
| W1 Data fix | 0 | CTA_data, chapter 100 | split adjustment and split-day clamp per § 4.6; re-run the jump scan; row counts per ticker; truncated copy | `data_adjusted/`, `results/data_validation.csv` | scan finds no \|r\| > 0.4 except USO 2020-04-21 and UNG 2024-01 | every number spanning Dec 2025 |
| W2 Engine | 3, 4 | `backtest.py` | `engine.py`: vectorized multi-asset simulator with d, c, s, η as parameters; metrics module per § 4.1; regression test against `backtest.py` at c = s = 0, η = 0 with the same (double) lag, then the lag collapsed to one parameter and the difference documented | `engine.py`, `metrics.py`, `tests/test_engine.py` | regression test to 1e-9; turnover, IC, win rate, hit rate unit-tested on toy data | C1–C6, C9–C12 |
| W3 Signals | 1 / A1–A4 | W1, chapters 02, 03 | MOM risk-adjusted + percentile; bar plots G1–G5 with SE at gap g ∈ {0, 1, 5}; MACD grid n_f, n_s ∈ {5, 10, 21, 63, 126}, n_f < n_s, heat map of G5−G1 with SE; smoother m ∈ {none, 3, 5, 9} with m < n_f; pick a **band** (ratio ≈ 2:1), not one cell; the chosen set may be several | `signals.py`, `results/macd_grid.csv`, `figures/bar_*`, `figures/macd_heatmap` | grids run on ladder training rows only; every chosen pair has warm neighbours | C7, C8 |
| W4 Baseline and haircut | 2, 3, 4 / A1 | W2, W3 | build S (B0) and single-signal books; run naive and realistic; sweep c, s, d; waterfall and marginal-alone table; stability check of the ratio | `results/haircut_waterfall.csv`, `results/haircut_sensitivity.csv`, `figures/haircut_waterfall`, `figures/equity_curves` | C13 acceptance evaluated and recorded either way | C13, C2–C6 |
| W5 Regimes | 5 | W1, W3 | V, σ, rolling and full-sample terciles; 3×3 grid of bucket spread with SE and N per cell; per-year ordering table; cell-difference bootstrap | `regimes.py`, `results/regime_grid_rolling.csv`, `results/regime_grid_static_LOOKAHEAD.csv`, `figures/regime_map` | counts printed; floors applied; both cuts in the file | C14–C16, flag 2, flag 6 |
| W6 VIX / MOVE | 5 / B | class file; fallback VIX = FRED `VIXCLS` or CBOE `VIX_History.csv`; MOVE = Yahoo `^MOVE` via `yfinance` (no FRED series) | buckets (i) and (ii); 2-D table of S's performance per bucket with N; beta regression and residual bar plot | `results/vix_move_table.csv`, `figures/vix_residual_bar` | counts printed; residual verdict recorded | C16 (companion), homework B |
| W7 Rebuild and walk-forward | 6 / A | W4, W5 | B1 per § 4.3; `split.py` per § 4.5; per rung choose η and m(g) on the validation segment from the fixed grids; stitch OOS; per-fold and per-year scorecards; log every configuration run | `rebuild.py`, `walkforward.py`, `results/scorecard.csv`, `results/scorecard_by_fold.csv`, `results/run_ledger.csv`, `figures/rebuild_scorecard` | C20/C21 acceptance evaluated; N_v recorded | C17–C21 |
| W8 Models | 7 / C | W7 | targets = 5-day forward return; features = standardized MOM, MACD, σ, V, regime; Equal Weights, Ridge and Lasso (select-then-refit), one tree model (GBM or random forest, shallow); select on outer validation by MSE/MAE; IC per model | `models.py`, `results/model_selection.csv` | selected model named with its validation MSE; test untouched | homework C; C5 companion |
| W9 Optimizer | 7 / D, E | W8 | mean–variance max E[r] − γ Var with Σw = 1, Σ\|w\| ≤ 2, \|w_i\| ≤ cap; covariance from model residuals (shrunk); vector inputs throughout; γ and cap grid on outer validation; one run on test | `optimizer.py`, `results/optimizer_grid.csv`, `results/test_block.csv` | γ chosen and stated; test run once | homework D, E |
| W10 Robustness | 5 | W4, W7 | § 6 in full | `results/robustness_8pct.csv`, `results/robustness_haircut.csv` | every C13/C20/C21 number has its CI, deflation and breakdown | C13, C20, C21 |
| W11 Write-up | — | all | fill the ledger status column; `Backtests.md` section with reproduction snippets; figures via the `figures` skill in both themes; resume reconciliation table (claim → measured → wording used) | this file, `Backtests.md`, `RESUME_RECONCILIATION.md` | each resume bullet has one of: reproduced / reworded / withdrawn | all |

## 6. Robustness protocol

### 6.1 For C20 (+8% Sharpe) and C21 (−14% turnover)

| Step | What | Pass condition for quoting the resume number |
| --- | --- | --- |
| Same everything | B0 and B1 share data, split, cost set, overlap, delay; only § 4.3's three changes differ; B0 is never re-tuned | Diff of config files shows exactly those three keys |
| Baseline first | SR_base, TO_base, N days, r_f convention printed before SR_rebuild | SR_base > 0 |
| Stationary block bootstrap | paired daily returns (r_base, r_rebuild), block length 10, B = 2000; CI on ΔSR and on ΔSR/\|SR_base\| | 90% CI reported; claim is "supported" only if it excludes 0, else fallback wording |
| Per-fold | ΔSR and ΔTO per ladder test segment and for the test block | Δ > 0 in ≥ 60% of folds |
| Per-year | 2021–2026 calendar years | Δ sign and size per year; "8% is two good days" is answered by the drop-best-k test below |
| Drop best days | recompute ΔSR with the 5 best and the 5 worst days of B1 removed | Sign of Δ unchanged |
| Cost sensitivity | ΔSR at c ∈ {2, 5, 10}, s ∈ {0, 2, 5} | Sign unchanged; magnitude table reported |
| Deflation | N_v = rows in `run_ledger.csv` (every η, m(g), smoother, grid cell run while building B1); deflated Sharpe ratio (Bailey–López de Prado) for SR_rebuild using N_v and the variance of Sharpes across trials | Deflated SR reported next to the raw one |
| Truncated sample | all of the above with data ending 2025-12-04 | Sign unchanged |
| Decomposition | B1 minus each of its three changes in turn | The turnover fall comes from η; the Sharpe change is attributed, not asserted |

### 6.2 For C13 (25% haircut)

| Step | What | Pass condition |
| --- | --- | --- |
| Base stability | H at c ∈ {1, 2, 5, 10, 20}, s ∈ {0, 2, 5, 10}, d ∈ {0, 1, 2} | H ≥ 0.25 at the default set and at c ∈ {2, 5, 10} |
| Marginal vs joint | each element alone and all together; interaction = joint − sum of marginals | Reported; the waterfall order is stated |
| Bootstrap | block bootstrap of the daily (naive, realistic) pair; CI on H | 90% CI reported |
| Per-year | H per calendar year | Reported; a year with negative naive return is marked "ratio undefined" |
| Turnover link | H regressed on annual turnover across the single-signal and combined books | Drag scales with turnover, as chapter 00's claim says; if not, say so |

## 7. Execution order, dependencies, effort

| Order | Workstream | Blocked by | Parallel with | Effort (focused hours) |
| --- | --- | --- | --- | --- |
| 1 | W0 Environment | — | W1 | 1 |
| 1 | W1 Data fix | — | W0 | 3 |
| 2 | W2 Engine | W0 | W3 (signal code needs only pandas) | 10 |
| 2 | W3 Signals | W1 | W2 | 8 |
| 3 | W4 Baseline and haircut | W2, W3 | W5 | 5 |
| 3 | W5 Regimes | W1, W3 | W4, W6 | 6 |
| 3 | W6 VIX / MOVE | W5's bucket code, data source (§ 9 Q1) | W4 | 5 |
| 4 | W7 Rebuild and walk-forward | W4, W5 | — | 10 |
| 5 | W10 Robustness | W4, W7 | W8 | 6 |
| 5 | W8 Models | W7's split | W10 | 8 |
| 6 | W9 Optimizer | W8 | — | 8 |
| 7 | W11 Write-up and reconciliation | all | — | 6 |
| | **Total** | | | **~76** |

Critical path: W1 → W3 → W4 → W7 → W10 → W11 (~43 h). The resume claims are closed at the end of
W10; W8 and W9 are homework C–E and feed no resume number. If time is short, the teacher's rule
applies: finish A and B fully before C. Each workstream ends with the repo's closing pass
(`check_sync.py --impact` before, `check_sync.py` after, named `git add`, commit, push; no AI
attribution trailer per `AGENTS.md`).

## 8. Where things live

| Thing | Location | Rule |
| --- | --- | --- |
| This plan and ledger | `Resume_Reproduction/OUTLINE.md` | status column updated as results land |
| Scripts | `Resume_Reproduction/*.py` (`engine.py`, `metrics.py`, `signals.py`, `regimes.py`, `rebuild.py`, `walkforward.py`, `models.py`, `optimizer.py`, `split.py`) | import `Backtest_prototype/backtest.py` for the regression test; do not modify it |
| Adjusted data | `Resume_Reproduction/data_adjusted/` | `CTA_data/` untouched |
| Result tables | `Resume_Reproduction/results/*.csv` | header row states instruments, frequency, dates, N, r_f convention, cost set |
| Figures | `Resume_Reproduction/figures/` via the `figures` skill, light and dark PNGs | both axes labelled; the design pass first |
| Reproduction snippets and measured numbers | `Backtest_prototype/Backtests.md` (new section "Resume reproduction") and `Resume_Reproduction/RESUME_RECONCILIATION.md` | measured numbers never enter `docs/chapters/` |
| Theory cited | chapters 02 (bucket test, risk adjustment, r_f), 03 (MACD, grid as a band, smoother), 04 (log-ceiling vs rolling quantile, counts per cell, residualizing), 05 and `market_knowledge/walk-forward-modelling.md` (ladder, two layers, winsorize, standardize), 09 (IC, deflation), 100 (split) | chapters are linked, not edited, by this work |
| Chapter 00 story | `docs/chapters/00_pipeline/00_pipeline.md` | its 11/7/8, +2…+38 bp and +8%/−14% are illustrative; after W11 either the measured values replace them (a T2 revision) or the chapter's note is sharpened to say they are schematic — Harry's call (§ 9 Q5) |

## 9. Open questions for Harry

| # | Question | Why it changes the work |
| --- | --- | --- |
| Q1 | Where is the class VIX + MOVE file? If unavailable, approve the fallback (FRED `VIXCLS`; Yahoo `^MOVE` via `yfinance`, which needs an install and a network call) | W6 cannot start without one; the fallback changes provenance that must be stated |
| Q2 | Cost level: is 5 bp per side plus 2 bp slippage the right default for liquid US ETFs, or should the headline use 2 bp? | The 25% claim is read at the default set; the sweep covers the rest |
| Q3 | Is the resume's "strategy" the combined MOM + MACD book (S) or momentum alone? | Fixes which book C13, C20 and C21 are measured on; both are run, one is quoted |
| Q4 | May `DTB3` be downloaded from FRED for the net-long variants' r_f? | Otherwise net-long Sharpes are reported at r_f = 0 and labelled so |
| Q5 | If a number fails its acceptance: reword the resume with the measured value, or withdraw the bullet? Default proposed: reword using the fallback column of § 2 | Decides W11's reconciliation output |
| Q6 | QFA 12% / 15%: this work cannot support it; does the resume keep it? | Outside scope; recorded so the decision is visible |
| Q7 | Split-day bar: clamp (proposed) or NaN for the five SPDRs on 2025-12-05? | Changes one day of five tickers inside the test block |
| Q8 | Package installs into `.venv` (sklearn, scipy, statsmodels, optionally cvxpy and yfinance) are approved? | W0, W8, W9 depend on them |