# Resume_Reproduction/OUTLINE.md — Build plan and claims ledger

Owner: Harry. Date: 2026-10-23. Status: plan, nothing measured. Lens: a reproducible pipeline that **extends** `Backtest_prototype/backtest.py`; it never replaces it, and a parity test keeps the two in agreement.

## 1. Purpose and scope

Reproduce, with numbers this repository produces, the four resume bullets (Harry's words, pasted in the brief): an execution-aware CTA strategy on momentum and MACD; a transparent backtester reporting cumulative returns, Sharpe, drawdown, turnover, IC and signal win rate; "over 25% of naive backtest returns disappeared" under realistic execution; rolling volume/volatility regimes where trend signals work best in high-volume, low-volatility states; and a regime-aware rebuild giving +8% out-of-sample Sharpe and −14% annual turnover versus the baseline.

**The rule.** Every claim gets one measurement, one denominator, one sample and one acceptance test, fixed here before anything runs. A claim that fails is reported as failed with the fallback wording from the ledger; nothing is re-tuned on test to rescue it, and no illustrative number from `docs/chapters/00_pipeline/00_pipeline.md` (costs 11 / slippage 7 / delay 8; +2 bp to +38 bp; +8% / −14%) is ever quoted as measured.

Out of scope: the QFA "12% Sharpe / 15% drawdown" bullet (not in this repo; see § 3).

## 2. Claims ledger

All rows: status **unmeasured** today. Sample codes: FULL = 2020-04-01 → 2026-06-29 after warm-up (data fixed per § 4.5); VAL = 2024-01-02 → 2024-12-31; TEST = 2025-01-02 → 2026-06-29; WF = stitched walk-forward test segments inside 2020–2023 (§ 4.4).

| # | Claim (resume words) | Measurement that supports it | Base / denominator | Sample | Accept when | Fallback wording if it fails |
| --- | --- | --- | --- | --- | --- | --- |
| C1 | Transparent Python backtesting engine | `rr_engine.simulate` passes `tests/test_parity.py` against `backtest.backtester` and `tests/test_alignment.py` (no look-ahead) | — | FULL | both tests green | — (engineering, cannot fail) |
| C2 | Momentum and MACD signals | Bucket test G1..G5 with SE for MOM21 and MACD; G5−G1 spread, t-score | forward 5-day return, bp | FULL (descriptive), VAL for choices | spread > 2 SE for at least one of the two | "momentum and MACD signals (MACD added no edge beyond momentum)" |
| C3 | Visualize cumulative returns | `figures/equity-curves-{light,dark}.png` for naive, realistic, baseline, rebuilt, SPY | — | FULL + TEST | both themes build | — |
| C4 | Sharpe ratio | § 4.1 definition, r_f = 0 for the dollar-neutral book, T-bill series for the 150/50 book | annualized | all | reported with SE | — |
| C5 | Drawdown | max drawdown of cumulative PnL per unit capital | fraction of capital | all | reported | — |
| C6 | Turnover | executed one-way turnover, annualized, multiple of capital | capital | all | reported | — |
| C7 | IC | mean per-date Spearman(signal, fwd 5d return), ICIR, t deflated by h=5 | — | all | reported; plausible band 0.02–0.05 | — |
| C8 | Signal win rate | share of (asset, date) with sign(signal) = sign(fwd 5d return) | non-zero signal obs | all | reported | — |
| C9 | Execution-aware: costs, delay, turnover constraints, slippage | each as a parameter of `simulate`; waterfall table `results/03_haircut_waterfall.csv` | — | FULL | each drag measured separately | — |
| C10 | >25% of naive backtest returns disappeared | (R_naive − R_realistic) / R_naive, R = annualized arithmetic return (= cumulative PnL ÷ years, identical ratio) | naive run: delay 0, close execution, 0 bp, no deadband | FULL (primary), TEST (secondary) | ratio ≥ 0.25 **and** R_naive > 0 with naive Sharpe ≥ 0.3 at 5 bp cost + 5 bp slippage + 1-day delay | "realistic execution removed X bp/yr, Y% of the naive return" with the measured X, Y; if R_naive ≤ 0: "execution assumptions cost X bp/yr against a signal with no naive edge" |
| C11 | Rolling volume and volatility measures classify regimes | 21-day rolling dollar volume and realized vol per asset; tercile labels, rolling and static cuts, counts per cell | — | FULL | counts printed; every cell ≥ 300 obs or marked unmeasurable | — |
| C12 | Trend signals consistently more effective in high-volume, low-vol | G5−G1 spread per 3×3 cell; "consistently" = same ordering under both cuts and in ≥ 4 of 6 calendar years | bp of fwd 5d return | FULL | hi-vol/lo-vol cell is the max and the grid is monotone along both axes under the rolling cut | "trend signals were more effective in [the measured cell]" or "regime effect not robust across years" |
| C13 | Regime-aware features, vol scaling, turnover controls | three switches in `rr_portfolio` chosen on VAL only | — | VAL → TEST | each switch's marginal effect logged | — |
| C14 | +8% OOS Sharpe vs baseline | (SR_rebuilt − SR_base) / SR_base, same split, same engine, same costs | SR_base on TEST and on WF | TEST (headline), WF (support) | point estimate ≥ +8% **and** block-bootstrap CI (§ 6) reported beside it | "improved out-of-sample Sharpe by X% (95% CI a..b)" with measured X; if CI covers 0, say so on the resume or drop the percentage |
| C15 | −14% annual turnover vs baseline | (TO_rebuilt − TO_base) / TO_base, executed turnover | TO_base on TEST | TEST | ≤ −14% | "reducing annual turnover by X%" with measured X |
| C16 | QFA 12% Sharpe / 15% drawdown | none here | — | — | — | out of scope: unverifiable from this repo |

## 3. Red-flag resolutions

| Flag | Decision |
| --- | --- |
| QFA 12% / 15% | Out of scope. Recorded as unverified; no support fabricated. Harry decides the resume wording separately. |
| Regime threshold static vs dynamic | Run **three** cuts: (A) rolling trailing 126-day terciles per asset (dynamic, no look-ahead); (B') static cutpoints estimated on 2020–2023 only, frozen for VAL/TEST (static, no look-ahead on OOS); (B) full-sample terciles (static, **look-ahead**, reported only to show the size of the leak). Every quoted number names its cut; the headline uses (A). Harry's answer to the mentor becomes: "measures rolling; thresholds rolling trailing quantiles; a frozen-cutpoint variant gives [result]". |
| 25% of what | Annualized arithmetic return of the naive run on FULL. Because PnL is per unit capital and additive, cumulative PnL ÷ years is the same ratio. Not Sharpe. Guarded by the R_naive > 0 condition in C10. |
| 8% survives? | § 6 protocol. Baseline Sharpe recorded first in `results/04_baseline_metrics.csv`; the 8% is reported with a block-bootstrap CI and the variant count. Expected honest outcome on ~370 test days: Sharpe SE ≈ 0.8, so the CI will be wide — the resume then carries the CI or a reworded claim. |
| Data / instruments / frequency | 37 US-listed ETFs (5 broad equity, 11 sectors, 5 international, 7 fixed income, 6 commodities, 3 alternatives), daily OHLCV, 2020-01-02 → 2026-06-29, ~1630 bars, dividends unadjusted. Stated verbatim in `Results.md` § 0. |
| Bucket count and observations | 3×3 per-asset grid (9 cells) plus 3-state market grid for VIX; counts printed in every table; cells under 300 (asset, date) observations or under 60 distinct dates are shown as "n/a (n=…)". |

## 4. Fixed definitions

All constants live in `Resume_Reproduction/config.py`; scripts never hard-code them.

### 4.1 Metrics (`rr_metrics.py`)

| Metric | Definition | Function |
| --- | --- | --- |
| Daily return r_t | ΔPnL_t per unit capital (capital = 1.0, additive, no compounding) | `daily_returns(pnl)` |
| Sharpe | mean(r_t − rf_t) / std(r_t − rf_t) × √252; `rf_t` = 0 for the dollar-neutral book (net 0); FRED DTB3/252 for the 150/50 book (fallback: 0, flagged `rf=zero_flag`) | `sharpe(r, rf)` |
| Sharpe SE | √((1 + SR²/2)/T_years) | `sharpe_se` |
| Max drawdown | min(PnL_t − cummax PnL_t), fraction of capital | `max_drawdown` |
| Executed turnover | TO_t = Σ_s \|traded dollars_{s,t}\| / capital; annual = mean × 252 | `turnover(trades)` |
| Target turnover | Σ_s \|w_{s,t} − w_{s,t−1}\| on held weights (diagnostic only) | `target_turnover(w)` |
| IC | per-date Spearman(signal_{·,t}, fwd 5d return_{·,t}); mean, ICIR, t = ICIR × √(T/5) | `ic_series`, `ic_summary` |
| Signal win rate | P[sign(signal) = sign(fwd 5d return)], zeros excluded, pooled over (asset, date) | `signal_win_rate` |
| Hit rate | P[r_t > 0] on portfolio days | `hit_rate` |
| Per-year | all of the above by calendar year | `by_year` |

### 4.2 Execution model (`rr_engine.py`)

| Parameter | Naive | Realistic (headline) | Sensitivity grid |
| --- | --- | --- | --- |
| `delay` (trading days from signal close to execution) | 0 | 1 | 0, 1, 2 |
| `exec_price` | `close` of signal day | `twap` = (open+close)/2 of execution day | close, twap |
| `cost_bp` (one-way, on \|traded dollars\|) | 0 | 5 | 0, 2, 5, 10, 20 |
| `slip_bp` (price moved against the trade) | 0 | 5 | 0, 5, 10 |
| impact model (optional) | off | off | 0.1·σ_daily·√(participation), notional $10M, ADV = 21-day volume |
| `deadband` η (skip trade if \|Δw\| < η) | 0 | 0 in baseline; tuned on VAL in rebuild | 0, 0.02, 0.05, 0.10 |
| shares | recomputed daily from weight × capital (constant-dollar, as the prototype) | same | — |

The prototype's `delay=timedelta(days=1)` plus `.shift()` is, in trading rows, execution at the TWAP **two** rows after the signal; `tests/test_parity.py` must show `simulate(delay=2, exec_price="twap", cost_bp=0)` equals `backtester()` to 1e-9 before anything else is trusted.

### 4.3 Signals and sizing (`rr_signals.py`, `rr_portfolio.py`)

| Object | Definition |
| --- | --- |
| MOM21 | trailing 21-day mean of daily returns (prototype); risk-adjusted: ÷ trailing 63-day σ; standardized by trailing 252-day percentile |
| MACD(n_f, n_s, n_sig) | EMA_{n_f}(P) − EMA_{n_s}(P), in return units ÷ P_t; signal line EMA_{n_sig}; histogram; standardized like MOM |
| Grid | n_f ∈ {5, 8, 12, 21}, n_s ∈ {13, 21, 26, 42, 63, 126} with n_s/n_f ≥ 1.5; n_sig ∈ {5, 9, 13} |
| Rules | zero-line (sign MACD), crossover (sign hist), proportional (standardized value as weight) |
| Smoother | EMA span m ∈ {2, 3, 5, 8}, m < n_f, applied to the standardized signal |
| Prop-signal book | w_{s,t} = x_{s,t} / Σ_s \|x_{s,t}\| × 2.0 (gross 2, net ≈ 0 after cross-sectional demeaning) |
| P1, P2 | as `backtest.py` (150/50; median-relative 2/N) |
| Vol scaling | w_{s,t} ∝ x_{s,t} / σ_{s,t}, renormalized to gross 2.0 |
| Hold | 5-day overlap = `rolling(5).mean()` of targets, unchanged |
| Forward return for tests | 5-day close-to-close starting the day after the signal (gap g = 0 after executability) |

### 4.4 Sample split (`rr_split.py`)

| Block | Dates | Role |
| --- | --- | --- |
| Warm-up | 2020-01-02 → 2020-03-31 | signals, σ, regime windows fill (126-day quantile window, min 63) |
| Ladder region | 2020-01-02 → 2023-12-31 | 16 quarterly segments (≈63 days); rung k: train k..k+2, val k+3, test k+4; rungs 1..12; refit on train+val |
| VAL (outer) | 2024-01-02 → 2024-12-31 | picks model class, λ, γ, cap, deadband, smoother, MACD cell, regime switches |
| TEST | 2025-01-02 → 2026-06-29 | touched once per claim; spans 2025-12-05 |

Rule-based claims (C10, C12, C14, C15) select on VAL and report on TEST, with WF as a second, larger OOS sample. Model claims (Part C) use the ladder with MSE/MAE for selection.

### 4.5 Data treatment (`rr_data.py`)

Decision: **adjust and clamp**, do not truncate (truncation would delete most of TEST). `CTA_data/` is not modified; adjusted copies go to `Resume_Reproduction/data/adjusted/`.

| Step | Rule |
| --- | --- |
| Split fix | XLB, XLE, XLK, XLU, XLY: rows < 2025-12-05 → OHLC ÷ 2, volume × 2 |
| Split-day bar | open := previous adjusted close; high := max(open, close, low) with the original low kept; flag column `bar_fixed=1` |
| Checks | no gaps vs union calendar beyond holidays; no \|pct_change\| > 0.4 except USO 2020-04-21; OHLC consistency; UNG/USO already adjusted (verify factors) |
| Output | `data/adjusted/*.csv`, `results/00_data_checks.csv` (one row per ticker: n_rows, max_abs_move, date_of_max, split_fixed, bar_fixed) |

### 4.6 Regimes (`rr_regimes.py`)

| Measure | Definition | Labels |
| --- | --- | --- |
| V_{s,t} | 21-day rolling mean of close × volume (dollar volume) | terciles, cuts A / B' / B (§ 3) |
| σ_{s,t} | 21-day rolling std of daily returns × √252 | terciles, same three cuts |
| VIX, MOVE (market-wide) | (i) g_t = ⌈2 ln VIX_t⌉ (= ⌈ln VIX²⌉); (ii) rolling trailing 126-day quintile | 2-D table for (i); for (ii) regress VIX-beta on MOM-beta, bar-plot the residual |

## 5. Workstreams

### 5.0 File layout

| Path | Role |
| --- | --- |
| `Resume_Reproduction/OUTLINE.md` | this plan and ledger |
| `requirements.txt` | pins for Python 3.8.7 (§ 5.1) |
| `config.py` | dates, grids, bp, windows, seed, paths |
| `rr_io.py` | `save(df, name, params)` → `results/<name>.csv` + `results/<name>.json` (params, git hash, timestamp); `load_adjusted()` |
| `rr_data.py`, `rr_signals.py`, `rr_regimes.py`, `rr_portfolio.py`, `rr_engine.py`, `rr_metrics.py`, `rr_split.py`, `rr_models.py`, `rr_optimizer.py`, `rr_robustness.py` | library modules, importable, no side effects |
| `run_00_data.py` … `run_09_reconcile.py` | one script per workstream; each regenerates its own `results/NN_*.csv` from scratch |
| `tests/test_parity.py`, `tests/test_alignment.py`, `tests/test_metrics.py` | pytest |
| `results/` | committed CSV + JSON; `variants_log.csv` appended by every selection run |
| `figures/` | `<name>-light.png` / `<name>-dark.png` via the `figures` skill, `make_rr_figures.py` |
| `Results.md` | measured numbers and reproduction snippets, cross-linked from `Backtest_prototype/Backtests.md` |

DataFrame conventions: wide frames = `DatetimeIndex` (tz-naive dates) × tickers for `open`, `close`, `volume`, `ret`, every signal, `w_target`, `w_held`, `trades`, `pnl_*`; panel frames = `MultiIndex(date, ticker)` with columns `signal`, `fwd_ret`, `regime_*` for bucket and IC tests.

### 5.1 WS-0 Environment and data (stage 0; feeds C1, every claim)

| Item | Detail |
| --- | --- |
| Interpreter | `python3` = 3.8.7; `.venv` exists and is empty: `python3 -m venv .venv && .venv/bin/pip install -r Resume_Reproduction/requirements.txt` |
| Pins (last releases supporting 3.8) | `numpy==1.24.4`, `pandas==2.0.3`, `matplotlib==3.7.5`, `scipy==1.10.1`, `scikit-learn==1.3.2`, `statsmodels==0.14.1`, `pytest==7.4.4`; optional `cvxpy==1.4.3` (1.5 drops 3.8; SLSQP is the primary optimizer so cvxpy is not required) |
| Downloads | stdlib `urllib` only; no yfinance (3.8 support uncertain) |
| Data fix | `run_00_data.py` applies § 4.5, writes `data/adjusted/` and `results/00_data_checks.csv` |
| VIX / MOVE | ask Harry for the class file → `data/external/vix_move.csv` (columns date, vix, move). Fallback: VIX from CBOE `VIX_History.csv` or FRED `VIXCLS`; MOVE has no free CSV — fallback proxy = TLT 21-day realized vol, labelled `move_proxy=TLT_rv21` in every output |
| r_f | FRED `DTB3` → `data/external/dtb3.csv`; fallback 0 with flag |
| Done when | `pytest tests/` green; checks CSV shows 5 split fixes, 0 unexplained jumps > 0.4; commit |

### 5.2 WS-1 Engine extension (stage 3; feeds C1, C9)

| Function | Inputs | Outputs |
| --- | --- | --- |
| `simulate(open, close, w_target, delay, exec_price, cost_bp, slip_bp, deadband, capital, impact=None)` | wide frames | dict of wide frames: `w_held`, `shares`, `trades` ($), `pnl_gross`, `cost`, `slip`, `pnl_net`; plus `total` (DataFrame: pnl_gross, cost, slip, pnl_net, turnover by date) |
| `apply_deadband(w_target, eta)` | wide | wide (held weight unchanged when \|Δw\| < η, applied per asset after overlap) |
| `tests/test_parity.py` | — | asserts `simulate(delay=2, "twap", 0, 0, 0)` ≡ `backtest.backtester` per asset and in sum |
| `tests/test_alignment.py` | synthetic price with a known jump | asserts PnL responds only after `delay` rows; shifting `w_target` forward by one row must change nothing before the jump |

Mechanics: order size = w_target_{t−delay} × capital / exec_price_t − shares_{t−1}; `trades = Δshares × exec_price`; `cost = |trades| × cost_bp/1e4`; `slip = |trades| × slip_bp/1e4`; `pnl_gross_t = shares_{t−1} × (close_t − close_{t−1}) + Δshares_t × (close_t − exec_price_t)`. Done when both tests pass and `backtest.py` is untouched.

### 5.3 WS-2 Signals, MACD grid, smoother (stages 1, 5; homework A2–A4; feeds C2, C7, C8)

| Script | Procedure | Writes |
| --- | --- | --- |
| `run_01_signals.py` | MOM21 raw / risk-adjusted / percentile; MACD for every grid cell; `bucket_test(panel)` → G1..G5 mean fwd 5d return, SE, N, G5−G1, t; IC and win rate per signal | `results/01_bucket_mom.csv`, `01_macd_grid.csv` (one row per (n_f, n_s, n_sig, rule): spread, t, IC, win rate, implied turnover, on ladder region and on VAL separately), `01_smoother_grid.csv` |
| Selection | Read `01_macd_grid` as a heat map on the ladder region; keep the contiguous warm band (several cells allowed, ratio ≈ 2:1 expected); confirm on VAL; log every cell tried to `variants_log.csv` | `results/01_selected_signals.json` |
| Figures | `bucket-mom`, `macd-heatmap`, `smoother-tradeoff` (spread vs turnover), both themes | `figures/` |

Done when MOM and the chosen MACD cells have bucket tables with N per bucket and the smoother choice is justified by spread-per-unit-turnover on VAL, not by the maximum.

### 5.4 WS-3 Portfolios and baseline (stage 2; homework A1, A3; feeds C3–C8, C14 denominator)

| Script | Procedure | Writes |
| --- | --- | --- |
| `run_02_portfolios.py` | books: prop-signal (MOM), prop-signal (MACD), P1, P2, L/S MACD rules; overlap 5; `simulate` under realistic execution; metrics § 4.1, per-year, IC, win rate | `results/02_portfolio_metrics.csv` (rows = books × blocks FULL/VAL/TEST/WF), `02_equity_curves.csv` |
| Baseline freeze | **Baseline = MOM21 risk-adjusted, prop-signal dollar-neutral book, overlap 5, realistic execution, no deadband, no vol scaling, no regime feature.** Frozen in `config.BASELINE` before WS-5 starts. | `results/04_baseline_metrics.csv` |
| Figures | `equity-curves` (naive, realistic, SPY) | `figures/` |

### 5.5 WS-4 Execution haircut (stage 3–4; feeds C9, C10)

| Script | Procedure | Writes |
| --- | --- | --- |
| `run_03_haircut.py` | Same baseline weights; run the ladder of assumptions cumulatively: naive → +delay 1 → +TWAP → +cost 5 bp → +slippage 5 bp → +deadband (0 in baseline); and each assumption alone; full sensitivity grid of § 4.2 | `results/03_haircut_waterfall.csv` (step, ann_return, cum_pnl, sharpe, turnover, drag_bp_yr, share_of_naive), `03_cost_sensitivity.csv` (cost_bp × slip_bp × delay) |
| Guard | compute `share_of_naive` only if R_naive > 0; otherwise write NaN and the fallback wording from C10 | — |
| Figure | `execution-haircut` waterfall from measured rows | `figures/` |

Done when the waterfall sums exactly to naive − realistic and the sensitivity grid shows at which cost level the 25% is crossed.

### 5.6 WS-5 Regimes (stage 5; homework B; feeds C11, C12)

| Script | Procedure | Writes |
| --- | --- | --- |
| `run_04_regimes.py` | V, σ per asset; labels under cuts A, B', B; two-way sort of the MOM bucket test → 3×3 grid of G5−G1 spread, SE, N (asset-dates and distinct dates) per cell; per-year repeat; monotonicity check along both axes | `results/04_regime_grid_{A,Bprime,B}.csv`, `04_regime_by_year.csv`, `04_regime_counts.csv` |
| VIX/MOVE | log-ceiling buckets (c = 2) → 2-D table (VIX bucket × MOVE bucket) of baseline-book return and the MOM spread; rolling-quintile route: per-date MOM beta and VIX beta from cross-sectional regressions, regress VIX beta on MOM beta, bar-plot residual against forward return | `results/04_vix_move_table.csv`, `04_vix_residual_bucket.csv` |
| Figure | `regime-map` 3×3 heat map with counts printed in each cell, both themes | `figures/` |

Done when every cell carries N, the thin cells are marked n/a, and the ordering under cut A is stated as monotone / not monotone with the per-year count supporting "consistently".

### 5.7 WS-6 Rebuild (stage 6; feeds C13, C14, C15)

| Script | Procedure | Writes |
| --- | --- | --- |
| `run_05_rebuild.py` | Three switches, one at a time then combined, on the frozen baseline: (1) regime-aware feature = signal × multiplier by cut-A cell (multipliers from the ladder-region grid, frozen), (2) vol scaling x/σ, (3) deadband η; select η and the multiplier map on VAL by Sharpe-per-turnover; evaluate once on TEST and on WF | `results/05_rebuild_ablation.csv` (variant × block: sharpe, se, turnover, mdd, ic), `05_rebuild_vs_baseline.csv` (ΔSharpe %, ΔTO %) |
| Log | every variant evaluated on VAL appended to `variants_log.csv` (this is the deflation count N_v) | — |
| Figure | `rebuild-scorecard` from measured rows | `figures/` |

Done when the comparison is baseline-vs-rebuilt on identical split, engine and costs, and § 6 has run.

### 5.8 WS-7 Models (stage 7; homework C; feeds C7, and a model variant of C14)

| Script | Procedure | Writes |
| --- | --- | --- |
| `run_06_models.py` | Features per (asset, date): MOM_z, MACD_z, hist_z, σ_z, V_z, regime cell dummies, VIX bucket; winsorize at rolling 60-day 1/99 on the raw series; standardize with train-window stats only; target = fwd 5d return. Models: `EqualWeights` (sign-aligned mean of z-features), `Ridge`, `Lasso` (λ ∈ {0.1, 0.5, 0.7, 1}, select then OLS refit on survivors), `GradientBoostingRegressor` (depth ≤ 3) and `RandomForestRegressor`. Ladder of § 4.4; per rung record MSE, MAE, IC on the inner validation and test segments; pick class and λ on VAL by MSE (MAE as tiebreak) | `results/06_model_ladder.csv` (rung × model: mse, mae, ic), `06_model_selection.csv`, `06_predictions.csv` (panel of OOS predictions) |
| Sanity | pooled R² must be < 0.1 or the target shift is wrong; abort with message | — |

### 5.9 WS-8 Optimizer (homework D, E; feeds the modelled book in C14/C15)

| Script | Procedure | Writes |
| --- | --- | --- |
| `run_07_optimizer.py` | Inputs are vectors/matrices, never scalars: μ_t (N) = model prediction; Σ_t (N×N) = Ledoit-Wolf covariance of the model's residuals over the refit window; solve max_w μᵀw − γ wᵀΣw s.t. Σw = 1, Σ\|w\| ≤ 2, \|w_i\| ≤ cap with `scipy.optimize.minimize(method="SLSQP")`; γ ∈ {0.5, 1, 2, 5, 10}, cap ∈ {0.2, 0.25, 0.3} on VAL; chosen (γ, cap) once on TEST through `simulate` | `results/07_optimizer_grid.csv`, `07_optimized_book_metrics.csv`, `07_weights.csv` |
| Interface | `optimize(mu: Series, sigma: DataFrame, gamma, cap, net=1.0, gross=2.0) -> Series` so a later optimizer swaps in without touching the callers | — |

### 5.10 WS-9 Robustness, write-up, reconciliation (feeds every claim)

| Script | Procedure | Writes |
| --- | --- | --- |
| `run_08_robustness.py` | § 6 in full | `results/08_bootstrap_delta_sharpe.csv`, `08_by_year.csv`, `08_by_fold.csv`, `08_deflation.csv`, `08_haircut_sensitivity.csv` |
| `run_09_reconcile.py` | reads every `results/*.csv`, fills the ledger status column, writes the claim-by-claim verdict table | `results/09_claims_ledger.csv` |
| `Results.md` | sample statement, every measured number with the snippet that regenerates it (`python3 run_NN_*.py` + the CSV cell), figures embedded; `Backtest_prototype/Backtests.md` gets a pointer; chapters untouched | — |
| Resume reconciliation | per claim: keep / reword (fallback column) / drop; Harry decides; the five submitted resumes are listed with the differences | `Results.md` § 9 |

## 6. Robustness protocol

| Claim | Test | Specification |
| --- | --- | --- |
| C14 / C15 | Paired block bootstrap | daily (r_base, r_rebuilt) pairs on TEST; circular blocks of 21 days; 5000 resamples; report 95% CI of ΔSharpe and of ΔSharpe/SR_base, and of ΔTO% |
| C14 | Per-year, per-fold | ΔSharpe for 2025, 2026 and for each WF rung; count of periods where the sign agrees |
| C14 | Deflation | N_v from `variants_log.csv`; Deflated Sharpe Ratio (Bailey & López de Prado) of the rebuilt book given N_v, skew, kurtosis; also the Bonferroni-style haircut on the bootstrap p-value |
| C14 | Placebo | the same three switches with the regime multipliers shuffled across cells; the real map must beat ≥ 95% of 200 shuffles on VAL |
| C10 | Cost sensitivity | cost_bp × slip_bp × delay grid; report the smallest cost level at which the haircut reaches 25% and the haircut at 2, 5, 10, 20 bp |
| C10 | Per-year | haircut per calendar year; sign stability |
| C12 | Both cuts, per year | grid ordering under A and B'; a year counts only if the top cell has ≥ 60 distinct dates |
| All | Honest SE | every Sharpe carries `sharpe_se`; a relative change smaller than its SE is written as "within noise" in `Results.md` |

## 7. Execution order, dependencies, effort

| Order | Workstream | Depends on | Parallel with | Effort |
| --- | --- | --- | --- | --- |
| 1 | WS-0 environment + data fix | — | — | 3 h |
| 2 | WS-1 engine + parity test | WS-0 | WS-2 (signals need no engine) | 6 h |
| 3 | WS-2 signals, MACD grid, smoother | WS-0 | WS-1 | 6 h |
| 4 | WS-3 portfolios, baseline freeze | WS-1, WS-2 | — | 4 h |
| 5 | WS-4 haircut waterfall | WS-3 | WS-5 | 3 h |
| 6 | WS-5 regimes + VIX/MOVE | WS-2, VIX file | WS-4 | 6 h (+2 h if MOVE must be proxied) |
| 7 | WS-6 rebuild | WS-3, WS-5 | — | 5 h |
| 8 | WS-7 models | WS-2, WS-5, `rr_split` | WS-6 | 8 h |
| 9 | WS-8 optimizer | WS-7 | — | 6 h |
| 10 | WS-9 robustness, Results.md, reconciliation | all | — | 6 h |

Blocking facts: nothing after WS-1 is trusted until `test_parity` passes; nothing spanning TEST is trusted until `run_00_data.py` reports the five fixes; the VIX/MOVE table waits on the file (§ 9) but the per-asset regime grid does not. Figures via the `figures` skill after the `nature-figure` pass, both themes, both axes labelled. Each workstream ends with `check_sync.py`, a named-file `git add`, commit, push — one commit per workstream, no AI attribution per repo rule.

## 8. Where things live

| What | Where |
| --- | --- |
| Scripts, tests, results CSV/JSON, figures, `Results.md` | `Resume_Reproduction/` |
| Adjusted data copies, external VIX/MOVE/DTB3 | `Resume_Reproduction/data/` (`CTA_data/` untouched; chapter 100 updated only if Harry chooses the in-place fix, § 9) |
| Pointer to measured numbers | `Backtest_prototype/Backtests.md` → `Resume_Reproduction/Results.md` |
| Theory cited, never numbers | `docs/chapters/02…05, 09, 100`; `00_pipeline.md` keeps its story with its existing "deliberately behind" note until WS-9 replaces the illustrative figures with measured ones |
| The prototype | `Backtest_prototype/backtest.py`, unchanged, imported by the parity test |

## 9. Open questions for Harry

| Question | Why it changes the work |
| --- | --- |
| Where is the class VIX + MOVE file? If MOVE is unavailable, is the TLT realized-vol proxy acceptable, or should Part B report VIX only? | Decides whether the 2-D table is VIX × MOVE or VIX × proxy, and must be labelled on the resume as such |
| Cost level: 5 bp one-way + 5 bp slippage as the headline, or a different number (ETF spreads are 1–3 bp for SPY, 5–10 bp for DBA/UNG)? Per-asset bp from a spread table instead of one number? | Moves the 25% directly; the sensitivity grid runs regardless |
| Apply the 2025-12-05 fix in place in `CTA_data/` (and update chapter 100) or keep the adjusted copy in `Resume_Reproduction/data/`? | Affects every other script in the repo and the T6 done-when |
| Baseline definition: the dollar-neutral prop-signal MOM book (r_f = 0 is then exact), or the 150/50 P1 book (needs the T-bill series)? | Fixes the denominator of C14/C15 before any variant is run |
| If C10 or C14 fails on TEST, is the resume reworded with the measured number and CI, or is the bullet dropped? | Determines what `Results.md` § 9 recommends and whether the five submitted resumes need a correction note |
| Acceptable deflation: report the Deflated Sharpe beside the raw +X%, or require it to be positive for the claim to stand? | Sets the acceptance threshold of C14 |
| Is the QFA bullet handled in a separate session? | Nothing here can support it |