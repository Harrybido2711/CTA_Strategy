# Resume_Reproduction/OUTLINE.md — Reproducing the CTA resume bullets, in the course's own order

Date: 2026-10-23. Owner: Harry. Status: plan and claims ledger; nothing below is measured yet.

## 1. Purpose and scope

| Item | Decision |
| --- | --- |
| What is reproduced | The four CTA bullets quoted in `brief.md` § 1, every number in them, with numbers this repository produces |
| In whose words | The resume's own wording is the claim; the course chapters (02–05, 09) supply the method; `Backtest_prototype/backtest.py` supplies the engine |
| The one rule | A claim that does not reproduce is reported as "not supported, resume must change", with the fallback wording from § 2. No number is adjusted toward the resume |
| Order of work | The five lecturer assignments A→E (`brief.md` § 3), in that order and in the lecturer's sense. Resume-only work (execution haircut, per-asset volume/vol regimes) is slotted at the pipeline stage it belongs to, never ahead of the next assignment |
| Lecturer's priority | "A complete research pipeline (signals → model → optimization) beats more signals" (`market_knowledge/walk-forward-modelling.md` § 7). If time runs short, A1–A3 and C–E are finished before A4 and B are polished; the resume numbers need the whole chain, not a better signal |
| Out of scope | The QFA "12% Sharpe / 15% drawdown" line — not in this repository, cannot be supported here, recorded as unverified (§ 3) |
| Where numbers live | `Resume_Reproduction/` (scripts, CSV outputs, RESULTS.md) and `Backtest_prototype/Backtests.md` (snippets). Chapters stay theory-only |

Chapter section numbers below follow the `\section`/`\subsection` order of each `.tex` file (02: §1 hypothesis, §2 hoped-vs-got, §3 two ways out, §4 risk-adjusted, §5 what to report, §6 information availability; 03: §1 EWMA, §2 fast/slow, §3 MACD, §4 volatility clustering; 04: §2.5 level-to-label, §3.1 conditioning, §3.2 residualizing, §3.3 where spent; 05: §2.1 ladder, §2.2 one rung, §2.3 two layers, §3 preparing a signal).

## 2. Claims ledger

Sample column: **Full** = 2020-01-02 → 2026-06-29 after the § 4 data fix; **Test** = the held-out test block of § 4.4; **OV** = outer validation block. All statuses are "unmeasured" today.

| # | Claim (resume wording) | Measurement that supports it | Base / denominator | Sample | Acceptance | Fallback wording if it fails |
| --- | --- | --- | --- | --- | --- | --- |
| C1 | "momentum ... signals" | Bar plot G1–G5 of risk-adjusted 21-day MOM, SE error bars (02 §3.2, §4) | — | Train | G5−G1 spread > 2 SE, ordering monotone or near | "momentum signal tested and found weak" |
| C2 | "MACD signals" | Bar plot of MACD rule chosen in A2–A4 (03 §3.3) | — | Train | same as C1 | "MACD tested; added no spread on top of momentum" |
| C3 | "transparent Python backtesting engine ... cumulative returns" | `backtest.py` extended, not rewritten; cumulative PnL per unit capital plotted | — | Full | Engine prints every assumption; plot in both themes | holds by construction |
| C4 | "Sharpe ratio" | § 4.1 definition, r_f convention stated | daily PnL per unit capital | Full, OV, Test | reported with block-bootstrap CI | holds by construction |
| C5 | "drawdown" | § 4.1 max drawdown of cumulative PnL | per unit capital | same | reported | holds |
| C6 | "turnover" | § 4.1 annual turnover of held weights | multiples of capital per year | same | reported | holds |
| C7 | "IC" | per-date cross-sectional Spearman, mean, ICIR, deflated t (09 §1–2) | 37 assets per date | OV, Test | mean rank IC in 0.02–0.05 is plausible; >0.15 is a bug | report whatever it is |
| C8 | "signal win rate" | § 4.1 signal win rate and daily hit rate, named apart | (asset, date) pairs; days | same | reported | holds |
| C9 | "transaction costs" | cost layer c bp per dollar traded, measured alone | naive final PnL | Full and Test | drag reported in bp/yr and % | holds |
| C10 | "execution delay" | delay=0-at-close vs delay=1-at-TWAP, measured alone | same | same | same | holds |
| C11 | "turnover constraints" | deadband η and overlap hold measured as turnover change | annual turnover | same | same | holds |
| C12 | "slippage" | slippage layer k·σ_{s,t}·\|Δw\|, measured alone | naive final PnL | same | same | holds |
| C13 | "over 25% of naive backtest returns disappeared" | (naive − traded) / naive **cumulative PnL per unit capital**, base cost level of § 4.2 | naive cumulative PnL | Full (headline) and Test | naive ann. return ≥ 2% so the ratio is meaningful, and haircut ≥ 25% at base cost | "costs, slippage and delay removed X bp/yr, Y% of the naive return" with the measured X, Y; if naive PnL ≈ 0, quote bp/yr only |
| C14 | "rolling volume and volatility measures to classify market regimes" | V_{s,t}, σ_{s,t} per asset, terciles, both cuts of § 4.3 | — | Train (exploration), Full (report) | counts per cell printed | holds by construction |
| C15 | "more effective in high-volume, low-volatility environments" | 3×3 grid of G5−G1 spread per cell (04 §3.1 applied per asset) | spread in bp with SE and N | Train, then confirmed on OV | HV-LV cell spread > opposite corner by > 2 SE; monotone along at least one axis | "the edge concentrated in cell X" with the real cell, or "no regime dependence found" |
| C16 | "consistently" | C15 per calendar year and per ladder fold | — | Train folds, OV | sign of HV-LV minus opposite corner holds in ≥ 2/3 of years | drop "consistently" |
| C17 | "regime-aware feature engineering" | regime labels and interactions as model features (C), selected by inner validation | — | Train, OV | feature survives Lasso selection in a majority of rungs | "regime labels tested as features; not selected" |
| C18 | "volatility scaling" | w ∝ x/σ_{s,t} in A1, and σ in optimizer risk term (D) | — | — | turnover and vol of book change as predicted | holds by construction |
| C19 | "turnover controls" | deadband η, overlap hold, turnover penalty in optimizer | annual turnover | OV | turnover falls vs baseline | holds if C21 holds |
| C20 | "improving out-of-sample Sharpe ratio by 8%" | (SR_rebuild − SR_base)/SR_base on Test, same split, same engine | baseline Sharpe | Test, once | baseline SR ≥ 0.3 so the % is meaningful; block-bootstrap 90% CI of ΔSR excludes 0; deflated for variants tried (§ 6) | "Sharpe unchanged within noise (ΔSR = x, CI [..])" or quote absolute ΔSR, not a % |
| C21 | "reducing annual turnover by 14%" | (TO_base − TO_rebuild)/TO_base on Test | baseline annual turnover | Test, once | ≥ 14% and the same sign on OV | "reduced annual turnover by X%" with measured X |
| C22 | "relative to the baseline strategy" | baseline frozen before Test is opened (§ 4.5) | — | — | baseline never re-tuned after OV | holds by construction |
| Q1 | QFA "12% Sharpe / 15% drawdown" | not measurable here | — | — | — | marked unverified; outside this repo |

## 3. Red-flag resolutions

| Flag | Decision | Where it is executed |
| --- | --- | --- |
| QFA 12% / 15% | Out of scope. Recorded as **unverified, added by someone else**. No support is manufactured; Harry decides separately whether to strike it from the five submitted resumes | RESULTS.md § "Not in scope" |
| Static vs rolling regime threshold | **Both are true, of different cuts, and both are run.** (i) VIX/MOVE log-ceiling g_t = ⌈c ln v_t⌉ is static by construction and uses no data, so it is not look-ahead (04 §2.5). (ii) Per-asset volume/vol terciles are **rolling trailing quantiles** (252-day window). (iii) A "static" per-asset cut is allowed only as thresholds **frozen at the end of the training block** and applied forward; a full-sample quantile is look-ahead and is run only as a labelled diagnostic (04 §2.5 note). Every quoted number names its cut. Resume bullet 3 uses (ii); the Q&A bank's "rolling trailing" is correct for bullet 3; "static" is correct for the VIX homework. Harry corrects the mentor conversation accordingly | W7 (VIX/MOVE), W9 (per asset) |
| 25% of what | **Cumulative PnL per unit capital, naive vs traded, over the full fixed sample, at the base cost of § 4.2.** Reported also on Test and across a cost grid. If naive cumulative PnL is near zero the percentage is declared meaningless and bp/yr is quoted instead | W8 |
| 8% Sharpe | Baseline is fixed and frozen (§ 4.5). The % is quoted only if the baseline Sharpe ≥ 0.3 and the bootstrap CI on ΔSR excludes zero; otherwise absolute ΔSR or "unchanged within noise". Mentor's objection is answered by § 6, not argued with | W12, W13 |
| Data / instruments / frequency | Stated once in § 4.4 and repeated in every table header: 37 US-listed ETFs standing in for futures, daily bars, 2020-01-02 → 2026-06-29, ~1630 rows each, dividends unadjusted, volume in shares | RESULTS.md header |
| Bucket count and observations per bucket | Every cell of every grid prints N and SE; a cell with N < 100 dates is reported "unmeasurable", never as zero (04 §3.1 note). Log-ceiling c = 2 on VIX gives cuts at 12.2 / 20.1 / 33.1 / 54.6; the > 54.6 bucket holds only a handful of March-2020 days and is merged into the one below, with the merge stated | W7, W9 |

## 4. Fixed definitions, decided once

### 4.1 Metrics

| Metric | Definition | Convention |
| --- | --- | --- |
| Daily PnL r_t | first difference of cumulative PnL per unit capital from `multi_asset_backtester` (CAPITAL = 1) | additive, not compounded, as the engine already does |
| Sharpe | (mean(r_t − r_f,t) / std(r_t)) · √252 | **Headline book is dollar-neutral (P2-style, net ≈ 0), so r_f = 0 is correct, not a habit** (02 §5). For any 150/50 run r_f,t = 3-month T-bill daily rate (FRED DTB3 / 252) is subtracted; never a constant |
| Max drawdown | min_t (PnL_t − cummax PnL_t) | per unit capital |
| Annual return / vol | mean(r_t)·252, std(r_t)·√252 | as `perf_stats` |
| Turnover TO_t | Σ_s \|w_{s,t} − w_{s,t−1}\| on **held** weights (after overlap, after deadband) | daily |
| Annual turnover | mean(TO_t) · 252 | multiples of capital per year — the resume's "annual turnover" |
| IC | per date, Spearman across the 37 assets between signal (or model prediction) and forward h-day return, h = 5 | mean IC, ICIR = mean/std, t = ICIR·√(T/h) (09 §2) |
| Signal win rate | share of (asset, date) pairs with sign(signal_{s,t}) = sign(forward 5-day return) | signal-level |
| Daily hit rate | share of days with r_t > 0 | portfolio-level; the two are never conflated |
| Bar-plot spread | mean forward return G5 − G1 with SE of each mean (02 §3.2.1–3.2.3) | the signal-stage metric; no Sharpe at the signal stage (02 §5) |

### 4.2 Execution model (stage 3)

| Component | Definition | Base value | Grid for sensitivity |
| --- | --- | --- | --- |
| Naive run | signal dated t trades at close_t, delay = 0, no cost, no slippage | — | — |
| Delay | signal dated t tradable after one calendar day (`merge_asof`, as in `backtest.py`), executed at TWAP = (open + close)/2 | 1 day | 0, 1, 2 days |
| Transaction cost | c · \|traded dollars\| per side | c = 5 bp | 0, 2, 5, 10, 20 bp |
| Slippage | k · σ_{s,t}^{daily} · \|traded dollars\|, σ from 21 trailing returns (ex-ante) | k = 0.1 | 0, 0.05, 0.1, 0.25 |
| Turnover constraint | deadband η: no trade in asset s unless \|target − held\| > η; overlap hold HOLD = 5 kept | η chosen on OV | 0, 0.5%, 1%, 2% of capital |
| Waterfall order | naive → +cost → +slippage → +delay, and the reverse order reported beside it, since components interact | — | — |

### 4.3 Regime measures

| Measure | Definition | Cut | Buckets | Counts |
| --- | --- | --- | --- | --- |
| Per-asset volume V_{s,t} | 21-day rolling mean volume, after the split fix | rolling trailing tercile over 252 days (primary); thresholds frozen at end of training (secondary, "static"); full-sample tercile (diagnostic only, labelled look-ahead) | 3 | printed per cell |
| Per-asset realized vol σ_{s,t} | 21-day rolling std of daily returns | same three cuts | 3 | printed |
| VIX, MOVE (market-wide) | daily close | (i) ⌈2 ln v_t⌉ (homework's ceiling(log(VIX²))); (ii) rolling trailing quintile, 252 days | (i) 5 nominal, top merged if N < 100; (ii) 5 | printed |
| Grid | signal buckets G1–G5 across, regime up (04 §3.1) | — | 3×5 or 3×3 | N and SE in every cell |

### 4.4 Sample and split

| Block | Dates | Role |
| --- | --- | --- |
| Full sample | 2020-01-02 → 2026-06-29 | data fix, naive-vs-traded waterfall (C13 headline), descriptive grids |
| Training block | 2020-01-02 → 2024-06-28 | the walk-forward ladder lives here: segments of 63 trading days (~3 months, 05 §2.1), 18 segments, 14 rungs (train 1–3, val 4, test 5, slide by one) |
| Outer validation block | 2024-07-01 → 2025-06-30 | chooses model class, λ, γ, cap, η, smoother span (05 §2.3) |
| Test block | 2025-07-01 → 2026-06-29 | **opened once**, after every choice is frozen; carries the 2025-12-05 split, so the data fix precedes everything |
| Refit style | train + validation segment, window ending at the prediction date (05 §2.2 note) | fixed now |

### 4.5 Baseline and rebuild (for C20–C22)

| Book | Content | Fixed when |
| --- | --- | --- |
| Baseline | best A-step book chosen on OV: risk-adjusted MOM + MACD (A2–A4 parameters), proportional weights, 5-day overlap, full execution model, **no** regime features, **no** σ-scaling in sizing beyond the signal's own risk adjustment, η = 0 | end of W6, before W10 |
| Rebuild | same signals + regime features (C), σ in the optimizer's risk term (D), turnover control η and/or turnover penalty (D/E), γ chosen on OV | end of W12 |
| Comparison | both run on Test once, same engine, same split, same cost | W12 |

### 4.6 Data treatment of 2025-12-05

| Decision | Detail |
| --- | --- |
| Adjust, do not truncate | For XLB, XLE, XLK, XLU, XLY, rows before 2025-12-05: OHLC ÷ 2, volume × 2 |
| Split-day bar | clamp `open` and `high` of 2025-12-05 to max(`low`, `close`) so TWAP sits on the post-split basis; the bar's `high` is then not a market fact, and this is stated |
| Robustness | every Test number is also computed on the sample truncated at 2025-12-04; if the two disagree by more than the bootstrap CI, the truncated figure is quoted |
| Provenance | corrected files written in place; originals already in `CTA_data/_unadjusted_raw/`; `100_dataset.md` table moved from "not yet adjusted" to "adjusted" (T6 + T9) |

## 5. Workstreams

Stage = pipeline stage of `00_pipeline.md` § 2. HW = lecturer assignment. Effort in focused hours.

| W | Name | Stage | HW | Inputs | Procedure | Outputs | Done when | Feeds | Effort |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| W0 | Environment | — | — | python 3.8.7, empty `.venv` | `pip install scikit-learn==1.3.2 scipy==1.10.1 statsmodels==0.14.1`; optimizer on `scipy.optimize.minimize(method="SLSQP")`, cvxpy optional; pin in `Resume_Reproduction/requirements.txt` | requirements.txt | `import sklearn, scipy` succeed | all | 1 |
| W1 | Data fix | 0 | — | `CTA_data/`, `100_dataset.md` | § 4.6; rerun `\|pct_change\| > 0.4` scan; verify Dec 4 / Dec 5 ratio ≈ 1 | corrected CSVs, `data_fix.py`, scan log | scan finds no split-sized jump; 100_dataset table updated | all | 2 |
| W2 | Shared library | 2–4 | — | `backtest.py` | `Resume_Reproduction/lib/`: `signals.py` (MOM, risk-adj MOM, MACD, smoother), `execution.py` (cost, slippage, deadband layered on `backtester`), `metrics.py` (§ 4.1), `regimes.py` (§ 4.3), `split.py` (§ 4.4), `barplot.py` (02 §3.2 bucket test, percentile buckets per asset pooled across assets, SE bars, N printed). Import `backtest.py`; never duplicate its accounting | lib + unit checks (shorts identity of Backtests.md, Σw net invariance) | prototype's P1/P2 numbers reproduce through the new path | all | 6 |
| W3 | **A1** Signal as weights | 1–2 | A1 | risk-adj MOM (02 §4) | w_{s,t} ∝ x_{s,t}, scaled to gross 2 and net 0 by demeaning across assets; 5-day overlap; through `multi_asset_backtester` and bar plot; compare to P1/P2 | table: P1, P2, proportional — bar-plot spread, Sharpe, TO; cumulative PnL figure | all three books reported with § 4.1 metrics on Train | C1, C3–C6, baseline candidate | 3 |
| W4 | **A2** MACD long/short grid | 1 | A2 | close matrix | n_f, n_s on geometric ladder {5, 10, 21, 42, 63, 126}, n_f < n_s (03 §2.2); rule ∈ {zero-line, crossover, proportional} (03 §3.3); cell = bar-plot G5−G1 spread with SE on Train; heat map per rule; keep **the band**, not the max — several optima recorded as a set | `macd_grid.csv`, heat-map figures (light/dark) | band identified; ≥ 2 parameter sets retained with their spread and SE | C2 | 4 |
| W5 | **A3** MACD through bar plot and backtester | 1–4 | A3 | retained MACD sets | each retained set → bar plot (02 §3.2) → proportional weights as W3 → backtester; also MOM + MACD combined (equal-risk sum of standardized signals) | table per set: spread, SE, N, Sharpe, TO, IC, win rate on Train | each retained set has a row; combined book chosen for W6 | C2, C7, C8 | 3 |
| W6 | **A4** Best smoother | 1 | A4 | W5's book | smoother = EMA of MACD with span m < n_f (03 §4; MACD's own 9-day line is m = 9); grid m ∈ {2, 3, 5, 9}; deadband η as the second local fix; select m on **inner** ladder validation spread, η on OV turnover-vs-spread | `smoother_grid.csv`, whipsaw count per m, figure | m chosen; **baseline frozen (§ 4.5)** and written to `baseline.json` | C11, C19, C22 | 3 |
| W7 | **B** VIX and MOVE regimes | 5 | B | VIX, MOVE daily closes (not in repo — see § 9; fallback: CBOE `VIX_History.csv` for VIX, Yahoo `^MOVE` via a one-off download script for MOVE) | (i) g_t = ⌈2 ln v_t⌉, (ii) rolling 252-day quintile (04 §2.5); W6 book's return and the bar plot inside each state; 2-D table regime × G1–G5 with N and SE for (i) (04 §3.1); for (ii): per-date VIX-bucket "beta" (mean forward return by VIX quintile, as the bar plot's β) regressed on the MOM beta from W3, residual ε_t bar-plotted (04 §3.2); check \|MACD\| as extra regressor (04 §3.2 note) | `vix_2d_table.csv`, `vix_residual_barplot` figure, counts | both cuts run; top log-ceiling bucket merged if N < 100 with the merge stated; residual verdict recorded as yes/no | C14 partially (market-wide), C17 features | 5 |
| W8 | Execution haircut waterfall | 3 | — (resume only) | W6 baseline | § 4.2 layers one at a time, both orders; cost grid; naive vs traded on Full and on Test; bp/yr and % | `haircut_waterfall.csv`, waterfall figure, cost-sensitivity figure | every layer's drag has a number; the denominator's sign and size are printed | C9–C13 | 3 |
| W9 | Per-asset volume / volatility regimes | 5 | — (resume only; 04 §3.1 method applied per asset) | V_{s,t}, σ_{s,t} | three cuts of § 4.3; 3×3 grid of G5−G1 spread on Train, confirmed on OV; per-year and per-fold sign table | `regime_grid_rolling.csv`, `_static.csv`, `_fullsample_lookahead.csv`, grid figure | all nine cells carry N and SE; which cut is which is in every filename and caption | C14–C16 | 4 |
| W10 | **C** Models on the ladder | 7 | C | standardized, winsorized features: risk-adj MOM, MACD, smoothed MACD, V and σ terciles, VIX/MOVE labels, interactions (05 §3.1–3.3: rolling 60-day 1/99 quantiles on the raw series; standardize with end-of-window statistics only) | models: Equal Weights (mean of standardized signals), Ridge and Lasso (select-then-refit, 05 §2.2), GradientBoosting/RandomForest tree; target = forward 5-day return; ladder of § 4.4; inner layer selects features; **outer block selects model class and λ by MSE and MAE**; IC reported beside | `model_selection.csv` (MSE, MAE, IC, ICIR per model on OV), coefficient-path figure | one model chosen on OV by MSE/MAE, choice logged with the losing alternatives | C7, C17 | 6 |
| W11 | **D** Optimization framework | 2 | D | W10 predictions p_t ∈ R³⁷, residuals ε from the chosen model | Σ̂_t = covariance of model residuals over the trailing training window (per lecturer: "directly from residuals"); solve max_w pᵀw − γ wᵀΣ̂w, Σw = 0 (dollar-neutral headline; Σw = 1 variant for the 150/50 book), Σ\|w\| ≤ 2, \|w_i\| ≤ cap; optional turnover penalty τ Σ\|w − w_prev\|; **every input a vector or matrix** (p, w_prev, cap vector, Σ̂), no scalars baked in, so the objective can be swapped | `optimizer.py` with a signature `solve(p, Sigma, w_prev, gamma, cap, tau)` | solver returns feasible w on every date; a unit test feeds vector caps | C18, C19 | 5 |
| W12 | **E** Choose γ, run Test once | 2–4 | E | W11 | grid γ ∈ {0.3, 0.5, 1, 2, 5}, cap ∈ {0.2, 0.25, 0.3}, τ and η on OV (05 §2.3); pick γ by OV Sharpe-vs-turnover frontier and state the preference; freeze; run baseline and rebuild on Test **once** | `scorecard.csv` (SR, DD, TO, IC, win rate; baseline vs rebuild; OV and Test), scorecard figure | Test opened exactly once; log records the timestamp | C20–C22 | 3 |
| W13 | Robustness protocol | 5 | — | W8, W12 outputs | § 6 | `robustness.csv`, CI figures | every quoted % has a CI and a deflation line | C13, C15, C16, C20, C21 | 4 |
| W14 | Write-up and reconciliation | — | — | all CSVs | `Resume_Reproduction/RESULTS.md`: ledger with measured values and status; reproduction snippets added to `Backtests.md`; figures through the `figures` skill (light + dark); `00_pipeline.md` note updated to say which story numbers are now measured and which are not; a one-page "resume wording that the numbers support" | RESULTS.md, Backtests.md diff, figure PNGs, resume_wording.md | every ledger row has a status; `check_sync.py` clean; commit and push per workstream | all | 4 |

Homework-to-resume mapping, and where they do not line up:

| HW step | Resume claim it evidences | Mismatch and how the plan handles it |
| --- | --- | --- |
| A1 signal as weights | C3–C6 (engine, Sharpe, DD, TO) | Resume does not mention proportional weights; this is the course's construction and becomes the baseline sizing |
| A2 MACD grid | C2 | Resume implies one MACD; course returns a band of parameter sets. RESULTS.md quotes the band |
| A3 MACD through bar plot + backtester | C2, C7, C8 | IC and win rate are not in the homework; computed in the same pass since the bar plot already holds signal and forward return |
| A4 smoother | C11, C19 | Resume calls this "turnover controls"; the course calls it smoother + deadband. Same object, both names recorded |
| B VIX/MOVE regimes | C14 partially, C17 | **Resume says rolling volume and volatility per asset; homework says VIX and MOVE market-wide.** Both are run: W7 is the homework, W9 is the resume. Bullet 3's numbers come from **W9 rolling-tercile per-asset grid**; the VIX/MOVE 2-D table is reported separately and never substituted for it |
| C models | C7, C17 | Resume's "regime-aware feature engineering" is the regime labels entering the model; selection by MSE/MAE is the lecturer's criterion and IC is reported beside, not used to select |
| D optimizer | C18, C19 | Resume never mentions an optimizer; the rebuild's volatility scaling and turnover control are implemented there, which is stated plainly in RESULTS.md |
| E γ and Test | C20–C22 | Homework asks to "look at the result"; the resume asks for +8% / −14%. The Test is run once either way; the resume number is whatever comes out |
| none | C9–C13 execution haircut | Not a homework step. Slotted at stage 3 after the baseline is frozen (W8), so the haircut is measured on the same book the course built |

## 6. Robustness protocol

Applies to C20/C21 (+8% / −14%) and to C13 (25% haircut). Same baseline, same split, same engine throughout.

| Check | Procedure | Reported as | Decision rule |
| --- | --- | --- | --- |
| Block bootstrap on ΔSharpe | stationary block bootstrap on paired daily (r_base, r_rebuild), block 21 days, 2 000 draws, on Test | 90% CI of SR_rebuild − SR_base and of the ratio | % quoted only if the CI lower bound > 0; else "unchanged within noise" |
| Same for ΔTurnover | same resample of daily TO pairs | 90% CI | % quoted if CI excludes 0 (expected, turnover is mechanical) |
| Per-year breakdown | SR and TO per calendar year, 2020–2026, both books | table | sign of ΔSR in each year; "consistently" needs ≥ 2/3 of years |
| Per-fold breakdown | SR and TO per ladder rung's test segment inside Train, and on OV | table | number of rungs where ΔSR > 0 |
| Deflation for variants tried | count every configuration evaluated on OV (smoother spans × η × models × λ × γ × caps); report Deflated Sharpe (Bailey–López de Prado) of the rebuild for that count, and the expected max of N null ΔSR | one line per quoted number | if the observed ΔSR < expected max under the null, the % is not quoted |
| Baseline strength | SR_base on Test | number | if SR_base < 0.3, the % form is abandoned for absolute ΔSR |
| Sample truncation | all of the above on the sample ending 2025-12-04 | parallel column | disagreement beyond the CI → truncated figure quoted |
| Haircut sensitivity | C13 across cost grid {0, 2, 5, 10, 20} bp × slippage k {0, 0.05, 0.1, 0.25} × delay {0, 1, 2} | surface table and figure | the cost level at which the haircut first reaches 25% is quoted, with the base-case value |
| Haircut denominator | naive annualized return and its bootstrap CI | number | if the CI includes zero, the % is not quoted and bp/yr is |
| Waterfall order | both orders of § 4.2 | two columns | the range across orders is reported, not one order |

## 7. Execution order and dependencies

| Phase | Workstreams | Blocks on | Parallel with | Hours |
| --- | --- | --- | --- | --- |
| 1 | W0, W1 | — | each other | 3 |
| 2 | W2 | W1 | — | 6 |
| 3 | W3 → W4 → W5 → W6 (homework A, in order) | W2 | W7's data acquisition can start now | 13 |
| 4 | W7 (homework B), W8, W9 | W6 (baseline frozen) | W7, W8, W9 in parallel | 12 |
| 5 | W10 → W11 → W12 (homework C, D, E in order) | W7, W9 (features) | — | 14 |
| 6 | W13 | W8, W12 | — | 4 |
| 7 | W14 | everything | — | 4 |
| Total | | | | ~56 |

Hard constraints: no Test run before W12; no OV read before W6's baseline is frozen; W8's headline haircut uses the frozen baseline, not a later model; W9's cuts and W7's cuts are never mixed in one table. If time is short, phase 4's W7 and W9 shrink to the rolling cut only, and phase 5 runs with Equal Weights + Ridge + one tree, nothing more — the lecturer's priority.

## 8. Where things live

| Thing | Path |
| --- | --- |
| This plan and the ledger | `Resume_Reproduction/OUTLINE.md` |
| Scripts | `Resume_Reproduction/lib/`, `Resume_Reproduction/run_<W>.py` one per workstream |
| Results | `Resume_Reproduction/results/*.csv`, `Resume_Reproduction/RESULTS.md` (measured ledger) |
| Figures | `docs/figures/<NN>_figures/` via the `figures` skill, light and dark; figure scripts import `_style.py` |
| Reproduction snippets | `Backtest_prototype/Backtests.md` (numbers, variables, snippets) |
| Theory cited | `docs/chapters/02…05`, `09`; chapters receive **no numbers and no variable names** |
| Story chapter | `docs/chapters/00_pipeline/00_pipeline.md`: its illustrative numbers (11/7/8, +2…+38 bp, +8%/−14%) are replaced only by measured ones or marked illustrative |
| Data | corrected `CTA_data/*_ohlcv_1d.csv`; VIX/MOVE under `Resume_Reproduction/data/` with source and download date |
| Closing pass | per workstream: `check_sync.py --impact`, rebuild if a `.tex` or figure moved, `check_sync.py`, commit by name, push |

## 9. Open questions for Harry

| # | Question | Why it changes the work |
| --- | --- | --- |
| 1 | Where is the VIX + MOVE file handed out in class? If unavailable, is the CBOE VIX history plus Yahoo `^MOVE` acceptable? | W7 cannot start without it; MOVE has no free official source |
| 2 | Base transaction cost: 5 bp per side, or the level the lecturer quoted? | C13's headline value depends on it; the grid covers the rest |
| 3 | Is "the strategy" the dollar-neutral book (r_f = 0) or the 150/50 book (r_f = T-bill series)? | Changes every Sharpe in the ledger and the r_f convention stated on the resume |
| 4 | Test block = last 12 months (contains the Dec-2025 split), or end the sample at 2025-12-04 and take the last 12 months before it? | Decides whether § 4.6's clamp is on the critical path |
| 5 | If C13, C20 or C21 fail acceptance, is the resume rewritten with the measured numbers, or are the bullets removed? | Determines what W14's `resume_wording.md` produces |
| 6 | Who removes the QFA line from the five submitted resumes, and when? | Outside this repo; recorded here only so it is not forgotten |
| 7 | Annual turnover unit on the resume: multiples of capital, or percent of gross? | C21's 14% is unit-free, but the absolute number beside it is not |