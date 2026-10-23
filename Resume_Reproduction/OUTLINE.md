# Resume Reproduction — Execution Outline and Claims Ledger

Path: `Resume_Reproduction/OUTLINE.md`. Owner: Harry. Date: 2026-10-23. Status of every number below: **unmeasured**. Nothing in this file is a result; the resume's figures (over 25%, +8%, −14%) and chapter 00's story figures (11/7/8 of 100, +2 to +38 bp) appear only as the targets the resume claims. `Resume_Reproduction/DATA.md` is authoritative for data, sample-split and capital conventions; this outline adopts it in full and cites it by section. `drafts/` holds the three superseded drafts and is read-only.

Chapter citations use each `.tex` file's own `\section`/`\subsection` order: 02 §2.1 which return the signal is scored on, §3.2 the bucket (bar) test, §4 risk-adjusted momentum, §5 what to report, §6 information availability; 03 §2.2 pairing grid, §3.1 MACD, §3.3 rules, §4 smoother and deadband; 04 §2.5 level-to-label, §3.1 conditioning, §3.2 residualizing, §3.3 where the answer is spent; 05 §2.1 ladder, §2.2 one rung, §2.3 two layers, §3 preparing a signal; 09 §1–2 IC; 100 §1 the dataset; WF = `market_knowledge/walk-forward-modelling.md`; DATA = `Resume_Reproduction/DATA.md`.

## 1. Purpose and scope

Four resume bullets, already sent to Citadel (x2), Morgan Stanley HK, BofA HK and AmEx, claim numbers this repository has never produced:

> Developed an execution-aware CTA strategy using momentum and MACD signals, building a transparent Python backtesting engine to visualize cumulative returns and evaluate Sharpe ratio, drawdown, turnover, IC, and signal win rate. / Evaluated the impact of transaction costs, execution delay, turnover constraints, and slippage, demonstrating that over 25% of naive backtest returns disappeared after incorporating realistic execution assumptions. / Constructed rolling volume and volatility measures to classify market regimes, revealing that trend-following signals were consistently more effective in high-volume, low-volatility environments than under adverse market conditions. / Refined trading signals using regime-aware feature engineering, volatility scaling, and turnover controls, improving out-of-sample Sharpe ratio by 8% while reducing annual turnover by 14% relative to the baseline strategy.

| Rule | Consequence |
| --- | --- |
| Every quoted number traces to one measurement with a stated base, sample, instrument set, frequency and observation count | The ledger (§ 2) is the contract; a number without a ledger row is not quoted |
| A claim that does not reproduce is reported as "not supported, resume must change", with the fallback wording written now | No number is moved toward the resume; acceptance thresholds are never set by searching cost, η or a cell until the target appears |
| Nothing is tuned on the Test block; it is read once, after every choice is frozen and committed; no full-sample quantile is quoted | § 4.5, § 6 |
| The resume wording for every claim is decided from Train and OV, before Test is read, and written into the config sidecars | § 6.1 ablation row; a sentence chosen after reading Test is selection on Test |
| Measured numbers live in `Resume_Reproduction/` and `Backtest_prototype/Backtests.md`, never in a chapter (`AGENTS.md` § 2) | § 8; chapter 00's figures are schematic and are never cited as measured |
| The 2025-12-05 split is fixed before any number spanning it is read (`100` § 1.1; DATA § 4) | § 4.6, W1 |
| Homework A → E (brief § 3) is done in the lecturer's order; resume-only work is slotted at its pipeline stage; "a complete pipeline beats more signals" (WF § 7) | § 5, § 7 |
| Resume and interview wording says "37 liquid US-listed ETFs as futures proxies", never "futures" (DATA § 1) | W11 reconciliation |

**What exists today.** `Backtest_prototype/backtest.py`: single-asset dollar-to-shares simulator, shares sized at the previous row's close, filled at TWAP = (open + close)/2, a one-calendar-day `merge_asof` delay **plus** a one-row `.shift()` — two trading rows of lag in every case, weekends included (verified in W2); a 37-asset loop; 21-day momentum = rolling mean of daily returns; P1 (150/50) and P2 (median-relative, 2/N); 5-day overlap via `rolling(5).mean()`; `perf_stats` (final PnL, annualized return and vol, Sharpe at r_f = 0, max drawdown). It has **no** costs, slippage, turnover metric, IC, win rate, regime label, MACD, smoother, model, optimizer or split. **The prototype's Sharpe is disputed:** `Backtests.md` says both books post near-zero Sharpe over 2020-01 → 2026-06; DATA § 5 re-ran the same code on 2026-10-23 and finds both positive, P1's mostly market beta from its +100% net exposure and a third of it gone once DTB3 is charged. W4 re-measures both books under the frozen conventions and the T5 correction to `Backtests.md` is a W4 output. The C13 and C20 fallbacks below exist because the brief requires them, not because of either number. The documented momentum edge being tested is `References/Momentum_ssrn-2089463.pdf`.

## 2. Claims ledger

Conventions for every row: 37 liquid US-listed ETFs as futures proxies (`CTA_data/*_ohlcv_1d.csv`; 5 broad equity, 11 sectors, 5 international, 7 fixed income, 6 commodities, 3 alternatives), daily UTC-dated bars, 2020-01-02 → 2026-06-29, 1630 trading days, dividends unadjusted, volume in shares, split-adjusted copy per § 4.6, constant $1 notional (DATA § 5). Blocks per § 4.5: **Train** (ladder), **OV** (outer validation), **Test**. Status is updated in place by `run_11_reconcile.py`. Every CI is printed at the pre-registered two-sided 90% and beside it at 95%; the reconciliation states which claims survive only at 90%.

### 2.1 Bullet 1 — the engine and its metrics

| # | Claim | Measurement | Base / sample | Acceptance | Status | Fallback wording |
| --- | --- | --- | --- | --- | --- | --- |
| C1 | "transparent Python backtesting engine … visualize cumulative returns" | `rr_engine.simulate` extends `backtest.py`; parity test (W2) at the prototype's own settings (lag 2, TWAP, `prev_close`); equity-curve figure, both themes | — | Parity to 1e-9; alignment test and gap test pass | unmeasured | none needed |
| C2 | "Sharpe ratio" | § 4.1, r_f convention printed beside it | per book, per block | computed, with analytic SE and block-bootstrap CI | unmeasured | none needed |
| C3 | "drawdown" | § 4.1 max drawdown; vendor-gap rows carried, not dipped (§ 4.6) | per book, per block | computed | unmeasured | none needed |
| C4 | "turnover" | § 4.1 executed turnover, annualized, signal and drift components | per book, per block | computed | unmeasured | none needed |
| C5 | "IC" | § 4.1 cross-sectional Spearman; mean, ICIR, deflated t; alignment string in the header | per signal, per block | reported as measured; mean IC > 0.15 or pooled R² > 0.1 triggers a look-ahead audit (09 §2); any lower value is a result, not a defect | unmeasured | none needed |
| C6 | "signal win rate" | § 4.1 signal win rate beside its base rate and the share excluded; daily hit rate separate | per signal / per book | computed with excess over base rate | unmeasured | none needed |
| C7 | "momentum … signals" | bar plot G1–G5 of risk-adjusted MOM with per-date means and Newey–West SE (02 §3.2, §4) | each rung's training quarters (exploration); the reported bar plot is stitched over the WF record's test quarters | G5−G1 spread reported with SE; monotone or not, it is reported | unmeasured | "momentum signal tested and found weak" |
| C8 | "MACD signals" | MACD grid read as a band (03 §2.2), the band's bar plot; band and smoother re-chosen every rung (§ 4.3, § 4.5) | each rung's train and validation quarters; reported on the WF record | a contiguous warm band is found in most rungs and holds its sign on each rung's validation quarter. **Pre-registered branch, applied per rung:** a rung whose band fails its validation sign check trades MOM only for that quarter; the share of rungs that fell back is reported, and every rung's choice is in `run_ledger.csv` | unmeasured | "momentum and MACD signals (MACD tested, not retained)" |

### 2.2 Bullet 2 — the execution haircut

| # | Claim | Measurement | Base / sample | Acceptance | Status | Fallback wording |
| --- | --- | --- | --- | --- | --- | --- |
| C9 | "transaction costs" | c bp per side on traded dollars, measured alone and jointly (§ 4.2) | WF record headline; Test alone beside | implemented, swept | unmeasured | none needed |
| C10 | "execution delay" | lag d in trading rows: d = 1 → d = 2 is the delay component a practitioner accepts; d = 0 → d = 1 is the removal of a look-ahead and is labelled so | same | implemented; prototype's double lag replaced by one parameter | unmeasured | none needed |
| C11 | "turnover constraints" | deadband η on B0's held weights: ΔTO, Δreturn per η (`results/03_turnover_constraint.csv`); outside the headline waterfall because B0 has η = 0 | same | each η row measured | unmeasured | none needed |
| C12 | "slippage" | s bp adverse to the trade, fixed and vol-scaled variants | same | implemented, swept | unmeasured | none needed |
| C13 | "over 25% of naive backtest returns disappeared" | **H = 1 − PnL_realistic / PnL_naive** on **B0** (the combined dollar-neutral book, Harry's choice, Q4), PnL = cumulative return per $1 on identical dates (annualized-return ratio is identical since PnL is additive). **Two pre-registered bases:** H_1 (headline) against the feasible frictionless book d 1, close fill, c 0, s 0; H_0 (story companion, matches chapter 00, labelled non-executable) against the same-close naive d 0, c 0, s 0. Realistic = d 1, close_{t+1} fill, c 5, s 2, η 0 (DATA § 4, § 7). Companions: Sharpe haircut, drag in bp/yr, H on the MOM-only book (no grid selection, the clean companion), H on P1/P2. Funding of the net and borrow on the short gross are outside the measured haircut and said so | **headline: the WF record 2022Q1 → 2026Q2** (out of sample for B0: band and smoother re-chosen each rung from earlier quarters, cost set fixed a priori), finalised at the single Test read; rows for the Train-ladder, OV and Test quarters, Test alone always printed | naive mean daily return's 90% block-bootstrap CI excludes 0 on the headline sample **and** H_1 ≥ 0.25 at the pre-registered cost set **and** H_1's own CI reported; H at c ∈ {2, 5, 10} beside | unmeasured | naive edge indistinguishable from 0: "execution assumptions cost X bp/yr and Y turns of annual turnover" (no percentage); H < 25% at base: "roughly a fifth of the naive return at 5 bp per side, X% at 2 bp"; **H ≥ 1:** "execution assumptions exceeded the naive return: X bp/yr of drag against Y bp/yr gross". Whatever the value, the reconciliation replaces "over 25%" with the measured H_1 and its CI |

### 2.3 Bullet 3 — regimes

| # | Claim | Measurement | Base / sample | Acceptance | Status | Fallback wording |
| --- | --- | --- | --- | --- | --- | --- |
| C14 | "rolling volume and volatility measures" | V_{s,t}, σ_{s,t} per asset (§ 4.4) | all | computed; first labelled date printed | unmeasured | none needed |
| C15 | "classify market regimes" | per-asset terciles: D rolling trailing (quoted), S2 frozen per rung (secondary), S3 full-sample (diagnostic, labelled look-ahead) | Train, confirmed OV; Test descriptive after the Test read | 3×3 grid with N (distinct dates, asset-days, episodes) per cell and per tail bucket; cells under the § 4.4 floors marked "not measurable" | unmeasured | none needed |
| C16 | "consistently more effective in high-volume, low-volatility" | **MOM is the quoted signal**; G5−G1 spread (bp per 5-day window, Newey–West SE across per-date means) inside each cell; HV/LV corner vs LV/HV corner pre-specified; σ-normalized spread as companion; MACD and combined-score grids in the same file with their own counts | WF record, under D and under per-rung S2 (S3 as a diagnostic) | ordering HV/LV > LV/HV in **5 of 5** periods {2022, 2023, 2024H1, 2024H2–2025H1, 2025H2–2026H1} (sign test; P(5 of 5 | null) = 1/32 ≈ 0.03, P(≥ 4 of 5) = 6/32 ≈ 0.19, so 4 of 5 does not support "consistently"); periods labelled by block (three are Train-ladder quarters) **and**, binding, the episode-block bootstrap 90% CI of the corner difference excludes 0 (§ 6.3) | unmeasured | 4 of 5: "more effective in high-volume, low-volatility environments in most years" (drop "consistently"); if the ordering fails: "mapped where the signal's edge concentrated by regime" with the measured grid |

### 2.4 Bullet 4 — the rebuild

| # | Claim | Measurement | Base / sample | Acceptance | Status | Fallback wording |
| --- | --- | --- | --- | --- | --- | --- |
| C17 | "regime-aware feature engineering" | regime multiplier κ(g_{s,t}) in B1's sizing, rolling cut only, **and** regime labels as model features (W8) | pre-specified, OV sensitivity, Test-read | implemented; the OV ablation attributes its share; wording fixed from the OV ablation before Test | unmeasured | if only the sizing overlay moves the number on OV: "regime-conditioned position sizing" |
| C18 | "volatility scaling" | w ∝ score/σ_{s,t}, per-asset cap, re-demeaned, gross 2 | same | implemented; cap binding share, max \|w\|, Herfindahl and per-category PnL share printed | unmeasured | none needed |
| C19 | "turnover controls" | deadband η, set each rung from B0's turnover in that rung's training window (§ 4.3); the smoother is part of the signal in **both** books, re-chosen each rung (W3, homework A4), and is not a B0→B1 switch | same | implemented | unmeasured | none needed |
| C20 | "+8% out-of-sample Sharpe vs baseline" | primary: **absolute ΔSR = SR_B1 − SR_B0**, same data, split, costs, overlap, delay, net 0; percentage ΔSR/SR_B0 computed inside each bootstrap draw and quoted only as a band with its CI, only if SR_B0's 90% CI excludes 0 | **the WF record (18 quarters, about 1,125 days)**: every quarter is out of sample for both books (§ 4.5); Test alone beside; per quarter | ΔSR 90% paired block-bootstrap CI excludes 0 **and** SR_B0's CI excludes 0 **and** the percentage band's lower bound ≥ +8%; power line (§ 6.1) says now that the last condition is out of reach at this sample size; DSR on the OV Sharpe reported | unmeasured | **expected resume text:** "ΔSR = +x [lo, hi] on ~1,125 walk-forward out-of-sample days, +y bp/yr, with annual turnover reduced z%" (absolute, with CI, no percentage). The submitted "+8% out-of-sample" cannot be defended at this sample size whatever the data say (§ 6.1) |
| C21 | "−14% annual turnover vs baseline" | ΔTO% = (TO_B1 − TO_B0)/TO_B0 on § 4.1 executed turnover per unit gross; ΔTO reported separately for the signal and drift components with each one's share of the reduction | the WF record, same series; Test alone beside | ≤ −14% with 90% CI; sign holds in the Train-ladder, OV and Test quarters separately | unmeasured | "reducing annual turnover by X%" with the measured X; the direction is mechanical from η, the magnitude is not |

### 2.5 The interview answers this plan produces

| Question | Answer comes from | Artefact |
| --- | --- | --- |
| "25% of what?" | C13: cumulative return per $1, B0, feasible frictionless base (H_1) and same-close base (H_0), identical dates, stated cost set | `results/03_haircut_waterfall.csv` |
| "What exactly is your baseline, and which sample chose each part?" | § 4.3: `config.BASELINE` prints the block that chose every field | `config.BASELINE` sidecar |
| "What was the baseline Sharpe?" | C20: SR_B0 with CI, r_f convention, block, N days, printed before SR_B1 | `results/06_scorecard.csv` |
| "Could your design ever have supported 8%?" | § 6.1 power line: no, at one or two years; absolute ΔSR is what is quoted | `results/08_robustness_rebuild.csv` |
| "Static or rolling threshold?" | § 3 flag 2 | `results/04_regime_grid_{rolling,frozen,fullsample_LOOKAHEAD}.csv` |
| "How many days in the thin cell, and in G5 of that cell?" | § 4.4 floors; counts printed per cell and per tail bucket in dates, asset-days and episodes | N columns of every grid |
| "Which instruments, frequency, how long?" | § 2 header, repeated in every result file's header row | `results/00_data_checks.csv` |
| "Is 8% just two good days?" | § 6.1: paired drop-best-days, per-quarter, bootstrap CI at five block lengths, DSR | `results/08_robustness_rebuild.csv` |
| "Largest weight after vol scaling, and the bond sleeve's PnL share?" | § 4.1 concentration metrics for every book | `results/06_scorecard.csv` |
| "What does the short leg cost to carry?" | § 4.2 borrow row; outside the headline haircut, labelled sensitivity | `results/03_haircut_sensitivity.csv` |
| "How many variants did you try?" | `results/run_ledger.csv`, every OV read with a selection yes/no column; raw N_v and effective N_v at two cutoffs | `results/08_deflation.csv` |

## 3. Red-flag resolutions

| # | Flag | Decision | Discharged in |
| --- | --- | --- | --- |
| 1 | QFA 12% / 15% | Dropped from this work by Harry on 2026-10-23 | — |
| 2 | Regime threshold static vs dynamic | **Decided by Harry, 2026-10-23: run one dynamic cut and three static cuts, and compare them.** D = rolling trailing 252-day rank (no look-ahead, primary for bullet 3). S1 = data-free fixed cut (log-ceiling; VIX, MOVE and, as a demonstration only, per-asset σ). S2 = cutpoints fixed from each rung's training window and held through its validation and test quarters (no look-ahead). S3 = full-sample cutpoints (look-ahead, `_LOOKAHEAD` in every file name, never quoted; 04 §2.5 note). Every quoted number names its cut. What the two families measure differently is DATA § 6.1: they put only 45–52% of VIX days in the same tercile, and a data-free cut on per-asset σ labels the asset class rather than the regime. The interview answer is "I ran both, and the quoted number uses the rolling cut", with the static result beside it | W5, W6 |
| 3 | 25% of what | Base fixed as cumulative return per $1 on identical dates, two bases named (C13); the cost set is pre-registered (Q2), the cost level at which 25% is crossed is a sensitivity row, never the headline | W4, § 6.2 |
| 4 | 8% robustness | Absolute ΔSR is primary; the percentage needs a baseline distinguishable from zero and a CI of its own; the analytic power line in § 6.1 already says the percentage is unsupportable, so the fallback wording is the expected text; B1 is pre-specified so OV and Test both count | W7, W10 |
| 5 | Data / instruments / frequency | Stated once (§ 2 header, DATA § 1–3) and printed in every result file's header row | W1 |
| 6 | Bucket count and observations | 3 per axis, 9 cells per-asset; the unit of every count is stated (distinct dates for market-wide tables; dates, asset-days and episodes for per-asset grids); floors in § 4.4 apply to the tail buckets inside a cell, not only the cell; thin cells reported as "not measurable", never as zero (04 §3.1 note). **The market-wide prior is already known** (DATA § 6): the VIX log-ceiling cut collapses to three buckets per index, the stressed row is thin everywhere, no crisis day is ever out of sample, and Test holds no stressed VIX day and nearly all of its days in one MOVE bucket — so the VIX/MOVE Test table is "not measurable" by construction and market-wide regime evidence comes from Train's ladder OOS quarters + OV | W5, W6 |

## 4. Fixed definitions, decided once

### 4.1 Metrics (`rr_metrics.py`)

| Metric | Definition | Convention and reason |
| --- | --- | --- |
| Daily book return r_t | ΔPnL_t per $1 of constant notional (additive, not compounded, as `perf_stats`; DATA § 5) | — |
| Sharpe | mean(r_t − rf_t) / std(r_t − rf_t) × √252 | Headline book is dollar-neutral (net ≈ 0), so **r_f = 0 is correct, not a habit** (02 §5). Any book with net ≠ 0 subtracts FRED `DTB3`/252 × net exposure, a series never a constant. `rf=0` or `rf=DTB3` printed beside every Sharpe; mean and max \|net\| and mean gross printed for both books; if B1's \|net\| exceeds δ = 0.05, DTB3 is charged on net for both |
| Sharpe SE | √((1 + SR_ann²/504)/T_years), labelled "iid approximation" (Lo, per-period SR annualized); the block-bootstrap CI is the quoted interval | printed beside every Sharpe |
| Max drawdown | min_t (PnL_t − max_{u≤t} PnL_u), in units of initial capital; percent of peak equity beside it | not a percent of compounded equity; gross is 2 |
| Executed turnover TO_t | Σ_s \|traded dollars_{s,t}\| / capital, on the engine's trades (the quantity costs are charged on) | annual = mean × 252; **quoted per unit mean gross exposure** (turns of the book per year) so a gross change cannot masquerade as a turnover control; raw and weight-based Σ\|w_{s,t} − w_{s,t−1}\| as diagnostics; **drift (price-induced rebalancing) and signal turnover split into two columns**, and every ΔTO claim reports both |
| Concentration | max_t max_s \|w_{s,t}\|; mean over t of Herfindahl of \|w_{·,t}\|/gross; share of cumulative PnL from each category (bonds / equity / commodities / alternatives) | printed for every book; the answer to "is B1 a Treasury-ETF book" |
| Forward return for every signal-stage test | **alignment string, printed in every results header:** "signal uses returns through close_t; scored return close_{t+1} → close_{t+6} (h = 5); one skipped day, matching the d = 1 fill". In 02 §2.1's indexing this is g = 1, since the lookback ends at close_t and the day close_t → close_{t+1} is discarded | g ∈ {0, 5, 21} run once as diagnostics (g = 0 scores close_t → close_{t+5}); g = 1 fixed in advance; IC, win rate, bucket spread and model target all share the string |
| Bucket spread | G5 − G1 mean forward return, bp per 5-day window; buckets at fixed 0.2 cuts of the trailing percentile (data-free); **mean per date first, then mean and Newey–West SE (lag 4) across dates** | the signal-stage metric; no Sharpe at the signal stage (02 §5); raw N and distinct-date N printed |
| IC | per date, Spearman across the 37 assets between the continuous standardized signal (or model prediction) and the forward return; mean IC, ICIR = mean/std, t = ICIR × √(T/5) (09 §2) | sign rules (zero-line, crossover) get win rate only |
| Signal win rate | share of (asset, date) with sign(centred score) = sign(forward return, same alignment string); **pairs with \|centred score\| ≤ 0.1 excluded** as sign noise, share excluded printed; per date then across dates; beside base rate max(P(r>0), P(r<0)) and the excess over it | centred score = percentile − 0.5, in [−0.5, 0.5] |
| Daily hit rate | share of days with r_t > 0, book level | never conflated with win rate |
| Per-block, per-year, per-quarter | all of the above by block and calendar period, labelled Train / OV / Test | — |

### 4.2 Execution model (`rr_engine.py`)

| Element | Definition | Naive_0 (same-close) | Naive_1 (feasible frictionless) | Realistic (headline) | Sweep |
| --- | --- | --- | --- | --- | --- |
| Lag d (trading rows) | d = 0: fill at close_t ("same-close", infeasible by construction, benchmark only); d ≥ 1: fill on row t + d | 0 | 1 | 1 | 1, 2, 3 |
| Execution price | `close` of the fill row (primary, DATA § 4: the open is probably a pre-market print); TWAP = (open + close)/2 of the fill row as a labelled sensitivity and the parity-test setting | close | close | close | close, TWAP |
| Share sizing | `size_price='exec'` (weight × capital / fill price); `'prev_close'` reproduces the prototype | exec | exec | exec | — |
| Cost c | c bp × \|traded dollars\|, charged on the fill row | 0 | 0 | 5 | 0, 2, 5, 10, 20; tiered-by-category variant (equity index / sector / bond / commodity, fixed bp) as sensitivity; never tiered by this feed's volume (DATA § 4) |
| Slippage s | fill moved adversely by s bp of price | 0 | 0 | 2 | 0, 2, 5, 10; variant s_t = 0.1 σ_{s,t} |
| Borrow b | b bp/yr on the short gross, charged daily | 0 | 0 | 0 | 25, 50 as a labelled sensitivity; funding of the net and borrow are outside the measured haircut and C13 says so |
| Deadband η | no trade in asset s when \|w_target − w_held\| < η; **overlap first, then deadband on the held weight** | 0 | 0 | 0 in B0; B1 per § 4.3 | {0.25, 0.5, 1, 2} × median daily \|Δw_held\| of B0 in the rung's training window (printed per rung), share of asset-days bound reported |
| Overlap | 5-day `rolling(5).mean()` of targets | kept | kept | kept | — |
| Vendor gap | on an asset's missing row, position and cumulative PnL carried forward, no trade, no cost (DATA § 4) | same | same | same | — |
| Haircut attribution | **H_1 (headline):** switches cost and slippage from Naive_1 → Realistic (4 runs; both linear in traded dollars, so their split is a labelling convention and the caption says so); the delay component reported as d = 1 → d = 2 beside it. **H_0 (companion):** Shapley over three switches delay (0 → 1), cost, slippage from Naive_0 → Realistic, 8 runs, all 6 orders, the stated-order waterfall and min/max across orders beside. Execution price (close vs TWAP) is a labelled sensitivity row, never a switch | — | — | — | — |

Reason for c = 5, s = 2: a uniform prior that is conservative for SPY-class names and lenient for UNG/DBA/FXI, pre-registered before W4 runs and approved by Harry on 2026-10-23 (Q2); the sweep covers the rest. Reason for a single lag parameter in trading rows: the prototype's calendar-day `timedelta` gives the same two-row lag on every weekday, so rows are the honest unit.

### 4.3 Signals and books (`rr_signals.py`, `rr_portfolio.py`)

| Object | Definition |
| --- | --- |
| MOM | 21-day mean of daily returns / σ_{s,t} (σ through t−1; 02 §4), then **percentile against the asset's own trailing 252 days (min_periods 126)**, centred to [−0.5, 0.5] |
| MACD | EMA_{n_f}(P) − EMA_{n_s}(P) in return units (÷ P_t), signal line EMA_9, histogram (03 §3.1, Harry's definition: spans n_f < n_s, α = 2/(span + 1), signal line EMA_9, histogram = MACD − signal); the proportional rule uses the same trailing-252-day centred percentile; zero-line and crossover rules use the sign (03 §3.3). All three go through the bar plot before the engine |
| One scale, one way | both signals enter every average, book and feature as trailing percentiles (02 §4's second route); z-scores are used only inside W8 with fitting-window statistics. Reason: averaging a uniform score with a z-score is not equal weight |
| Smoother, span q | EMA of span q applied to the **MACD-in-return-units series before the trailing-252 percentile is taken**, q < n_f for each retained pair (03 §4: shorter than the signal's own period, or it becomes another slow leg); grid q ∈ {2, 3, 5, 9} ∩ {q < n_f}; pairs with n_f = 1 are run unsmoothed; **re-chosen every rung** from its training window by spread per unit implied turnover, not by the maximum; part of the signal in both B0 and B1, never re-chosen |
| Strategy S = baseline B0 | equal-weight average of centred MOM and the MACD score, where the MACD score is the equal-weight mean of the centred (smoothed) scores of every cell in the retained band; w ∝ score, cross-sectionally demeaned, scaled to **gross 2.0, net 0**; 5-day overlap; d 1, close fill, c 5, s 2, η 0, no cap, no vol scaling, no regime term. **The rule is frozen in `config.BASELINE` before any rung runs**: grids, band rule, smoother grid, costs and every other setting are fixed a priori. What each rung re-chooses, the band cells, q and the MOM-only fallback, comes from that rung's own training and validation quarters (§ 4.5) and is logged per rung in `run_ledger.csv`. Reason for net 0: r_f = 0 is then exact (02 §5) and it is the prototype's P2 mandate; the lecture's Σw = 1 book is run as a labelled variant against P1 with DTB3. (This B0 is not W8's Equal Weights model, which is a different object) |
| Rebuild B1 | B0 with exactly three switches, each followed by re-demeaning and renormalizing to gross 2: (1) w ∝ score/σ_{s,t} with per-asset cap \|w_{s,t}\| ≤ 0.20 of capital (the lecture's cap; cap-then-renormalize, repeated once; cap binding share printed — the cap is part of switch 1 so the ablation attributes it); (2) × κ(g_{s,t}), g_{s,t} **under the rolling cut only**; (3) deadband η. **Primary configuration pre-specified a priori and written to `config.REBUILD` before any rung runs:** η = 1 × median daily \|Δw_held\| of B0 in each rung's training window, κ = 0.5 on the scope "LV/HV corner" (the resume's "adverse conditions", fixed by the resume's wording before W5 runs; W5 can confirm or refute it but cannot move it). The OV grid η ∈ {0.25, 0.5, 1, 2} × median, κ ∈ {1, 0.75, 0.5, 0.25}, scope ∈ {LV/HV corner, high-σ row} is a **sensitivity table**, every row in `run_ledger.csv`; the plateau (cells within one SE of the best OV mean net return per unit gross) and its size are reported; the Test number is of the pre-specified configuration, not of a maximum |
| Single-signal books | MOM-only and MACD-only versions of B0, reported alongside |
| Selection criterion for the MACD band and combined book | bar-plot spread with its Newey–West SE on each rung's training window, sign-checked on its validation quarter; every candidate's row recorded in `run_ledger.csv` |
| Winsorization (W8 only) | rolling 252-day 1%/99% quantiles on the raw series, never written back (05 §3.1); share clipped printed |

### 4.4 Regime measures (`rr_regimes.py`)

| Measure | Definition | Counts and floors |
| --- | --- | --- |
| V_{s,t} | 21-day mean share volume through t−1, per asset (volume × 2 pre-split for the five SPDRs; one venue feed, so only ever ranked against the asset's own past, never compared across assets or used as ADV; DATA § 4, 100 §1) | — |
| σ_{s,t} | 21-day realized vol of daily returns through t−1; the same series used in risk-adjusted MOM, vol scaling and slippage, stated so | — |
| D, rolling tercile (quoted) | rank against the asset's own trailing 252 days (min_periods 126), cuts at 1/3, 2/3; first labelled date printed | corners are expected thin because V and σ co-move; rank correlation of the two series printed |
| S2, frozen tercile | per-asset cutpoints from each rung's training window, held fixed through that rung's validation and test quarters (§ 4.5); no look-ahead | — |
| S3, full-sample tercile (diagnostic) | per-asset cuts on the whole history; **look-ahead**, `_LOOKAHEAD` in every file name, never quoted | — |
| S1, data-free fixed cut on σ (demonstration) | g = ⌈2 ln σ_ann%⌉, merged to three like VIX; not run on V, since no volume level means the same thing across ETFs and the feed covers a drifting share of the market | reported only to show that a fixed absolute cut sorts assets, not regimes (DATA § 6.1); never used in a grid |
| Per-asset grid floor | applied to **each of G1 and G5 inside the cell**: ≥ 250 distinct dates, ≥ 1000 asset-days and ≥ 10 regime episodes (runs of consecutive dates in that cell) per tail bucket; otherwise the cell is "not measurable" | all counts printed per cell and per tail bucket |
| Cell statistic | G5−G1 spread in **bp per 5-day window**, mean per date within the cell then Newey–West SE (lag 4) across dates (quoted; 04 §3.1 reports bp, and the mechanical bias of bp toward high-σ rows works against the claim, not for it); σ-normalized companion = each asset's scored return ÷ (σ_{s,t} × √5) before bucketing; cell t-stat beside | MOM quoted; MACD and combined-score grids as companions in the same file |
| VIX bucket (i) = S1 | g_t = ⌈2 ln VIX_t⌉ (ln is the default reading of the homework's ceiling(log(VIX²)); 04 §2.5 with c = 2), cuts at e^{k/2}: 12.2, 20.1, 33.1, 54.6; **merged to three buckets** (calm ≤ 20.1, elevated, stressed-and-crisis > 33.1) per DATA § 6 | dates per bucket per block printed; descriptive log-ceiling tables may include 2020, labelled in the title (DATA § 3) |
| MOVE bucket (i) = S1 | g_t = ⌈2 ln MOVE_t⌉, cuts at 54.6, 90.0, 148.4, 244.7; merged to three (≤ 90.0, 90.0–148.4, > 148.4) per DATA § 6 | same |
| VIX / MOVE bucket (ii) = D | rolling trailing 252-day quintile of the index (homework), with the tercile version beside it so it lines up with S1–S3; S2 and S3 terciles of the index run as well | every table names its cut |
| Market-wide cell statistic | mean daily net return of S with Newey–West SE and N dates; Sharpe only as a labelled companion (04 §3.3 note); the 2-D VIX × MOVE table is evidenced on Train's ladder OOS quarters + OV; the Test table is "not measurable" by construction (DATA § 6) | unit of count = distinct dates |
| Alignment | g_t uses the index close of US date t joined on the date part of the UTC bar; forward-filled at most one day; mismatches counted and listed | — |
| Residual test (homework B ii) | **As defined in lecture 5** (`lecture_5.vtt`, around line 965–990: "用这个beta，我们去regress掉之前的beta一跟贝塔二 … 这个residual用来构建portfolio"). β^VIX_{s,t} = slope of r_{s,u} on Δln VIX_u over the trailing 126 days u ≤ t (63 as a sensitivity); "beta 1" and "beta 2" are the asset's centred MOM and MACD scores. Each date, a cross-sectional OLS across the 37 assets: β^VIX_{s,t} = a_t + b1_t MOM_{s,t} + b2_t MACD_{s,t} + ε_{s,t}. The residual ε_{s,t} is ranked into a trailing percentile, bar-plotted against the forward return (02 §3.2), and run through the engine as a prop-signal dollar-neutral book. \|MACD\| as an extra regressor is a companion (04 §3.2 "orthogonal is not independent"); MOVE beta the same way as a companion. A market-wide VIX feature regressed on per-asset signals is **not** used: it is identical across assets on a date, so its cross-sectional residual is just the negated fitted MOM/MACD combination | — |

### 4.5 Sample split and walk-forward protocol (`rr_split.py`)

Decided by Harry on 2026-10-23: the split follows the lecture's ladder (05 §2.1–2.3, WF § 2–3),
not three fixed blocks. Inside the history, every quarter is traded by choices re-made from the
quarters before it: train, validate, test, slide one quarter, and repeat.

| Piece | Definition |
| --- | --- |
| Segment | One calendar quarter, 61–64 trading days (05 §2.1: two to three months, about one regime) |
| Warm-up | 2020-01-02 → 2020-12-31 (253 rows). Rolling windows fill. Never scored, never fitted |
| Rung for test quarter q | Train on the three quarters q−4 … q−2, validate on q−1, then refit on train + validation and apply once to q (05 §2.2, the house style that refits on train plus validation). Purge h + 1 = 6 rows at every window boundary; `rr_split.py` prints the boundary dates and asserts no label crosses one |
| Walk-forward record (WF record) | Every quarter from 2022Q1 to 2026Q2: 18 quarters, about 1,125 trading days. 2021 is the first rung's training and validation history |
| Inner layer, re-chosen every rung from that rung's own quarters | MACD band cells and smoother q, chosen on train and sign-checked on validation, with a per-rung fallback to MOM only if the check fails; deadband η scale from B0's turnover in the training window; static S2 cutpoints, per asset and for VIX/MOVE, from the training window; model features (Lasso selection) and coefficients |
| Outer layer, fixed across rungs (05 §2.3) | Chosen once on the four OV quarters 2024Q3 → 2025Q2: model class, λ, tree settings, optimizer cap, τ and γ by target vol. **Fixed a priori, never chosen on data:** the grids, the band rule, the cost set, B1's three switches, κ = 0.5 and its scope, the 0.20 cap |
| Block labels inside the WF record | Train-ladder quarters 2022Q1 → 2024Q2 (10), OV quarters 2024Q3 → 2025Q2 (4), Test quarters 2025Q3 → 2026Q2 (4) |
| Test | Produced by the same sliding rungs with the outer layer frozen; **read once**, in W10, after `config.BASELINE` and `config.REBUILD` are committed. No Test-quarter number is looked at before then |
| Prediction rule | A rung predicting date t_p fits on rows t ≤ t_p − 6, so the last label ends before the prediction date. Scaler statistics, Equal-Weights signs and the residuals Σ̂ is built from follow the same rule (WF § 6). `tests/test_no_lookahead.py` shifts every price after t_p and asserts the prediction at t_p is unchanged |
| W1's Test read | `run_00_data.py` reads Test-quarter prices for data validation only. No signal, weight or PnL is looked at for any date after 2025-06-30 before W10 |

**Which sample supports which number.**

- **B0 and B1 (C13, C20, C21): the whole WF record.** Every quarter is out of sample for both
  books. Their per-rung choices use only earlier quarters, and their fixed settings were
  written before any data was read. Test alone is printed beside.
- **The OV sensitivity grid for B1 is a read, not a selection.** If any OV-grid variant is ever
  quoted, it is labelled "OV-selected" and gets Test only.
- **Models and the optimizer (W8, W9): Test only is fully out of sample.** Their outer layer was
  chosen on OV. Train-ladder quarters are reported labelled "class chosen later on OV".
- **Regimes (C16): the WF record, per period.** Test is labelled as read in W10.

### 4.6 Data treatment (`rr_data.py`)

| Item | Decision | Reason |
| --- | --- | --- |
| XLB, XLE, XLK, XLU, XLY 2-for-1 on 2025-12-05 | **Adjust, do not truncate** (DATA § 4): rows before 2025-12-05 get OHLC ÷ 2 and volume × 2; written to `Resume_Reproduction/data/adjusted/`, `CTA_data/` untouched; chapter 100 gains a pointer to the adjusted copy (T6 + T9), its "not yet adjusted" table stays true for `CTA_data/` | truncation would cut Test to five months; the shared data stays as the chapters describe it |
| Split-day bar | open := close and high := max(low, close) for the five on 2025-12-05 (DATA § 4); flagged `bar_fixed = 1`; excluded from the parity assertion; `RESULTS.md` says the five fills that day are priced on a reconstructed bar | chapter 100's clamp option |
| Vendor gap 2022-11-21 → 2022-12-09 | the missing rows DATA § 4 lists stay missing; position and cumulative PnL carried forward with no trade and no cost; the gap dates printed in `results/00_data_checks.csv`; excluded from the parity assertion; `tests/test_gap.py` asserts total PnL is continuous across them | the prototype's union-calendar sum dips and recovers on those days; max drawdown must not carry that artefact |
| Robustness | every Test number is also computed on the sample truncated at 2025-12-04; a sign change is reported | — |
| Checks (acceptance) | `|close.pct_change()| > 0.4` scan on the adjusted copy **must find nothing**; the largest remaining moves are reported in absolute value and must match chapter 100's UNG and USO figures (signs settled on 2026-10-23: USO 2020-04-21 is −27.4% and UNG 2026-02-02 is −25.7%; chapter 100 prints both as positive and is corrected in W1's closing pass, T6); OHLC consistency; calendar gaps vs the union calendar; first non-NaN date per series | `results/00_data_checks.csv` |
| Dividends | **Obtainable** (DATA § 4): Yahoo distribution events exist for all 37 tickers; 33 pay, at up to about 5.3%/yr (HYG). Price return stays primary, matching the course data and the chapters; **every headline number is re-run on total return** (distributions reinvested on the ex-date) as a robustness row, and the difference is reported; the bond-ETF-excluded row stays | the long and short legs receive and pay different yields, so a dollar-neutral book is not immune |
| VIX, MOVE | The class handout as received, `CTA_data/_indices/VIX_index_1d_2020_now.csv` and `MOVE_index_1d_2020_now.csv`; `Close` only. The three VIX closes that disagree with Cboe's official history are replaced by Cboe's values in `Resume_Reproduction/data/adjusted/` (DATA § 4) | the course's own file; MOVE has no independent official source and matches Yahoo `^MOVE` on every day |
| DTB3 | `Resume_Reproduction/data/external/`, download date in the file name and a sidecar (Q1) | the only external series left |

## 5. Workstreams

Stage = `00_pipeline.md` § 2 build order (0–7). HW = brief § 3 step. Every workstream starts with `python3 .claude/scripts/check_sync.py --impact <paths>` and ends with `check_sync.py`, a `code-review` pass on each new `rr_*.py`, a named-file `git add`, commit and push, per finished script or result file (`AGENTS.md` § 4; no AI attribution trailer). The first commit stages `OUTLINE.md`, `DATA.md` and `Backtests.md` by name, since `Backtests.md` already links here.

| W | Name | Stage | HW | Inputs | Procedure | Outputs | Done when | Feeds | h |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| W0 | Environment | — | — | python 3.8.7 (x86_64 under Rosetta on arm64) | **Done 2026-10-23, approved by Harry:** `.venv` holds `Resume_Reproduction/requirements.txt` (numpy 1.24.4, pandas 2.0.3, matplotlib 3.7.5, scipy 1.10.1, scikit-learn 1.3.2, statsmodels 0.14.1, pytest 7.4.4, catboost 1.2.10). xgboost and LightGBM install but cannot load: they need an x86_64 OpenMP and only the arm64 one is present, so they were removed. SLSQP is the optimizer; downloads via stdlib `urllib` | `requirements.txt` | every package imports; a CatBoost and a HistGradientBoosting fit run | all | 1 |
| W1 | Data fix | 0 | — | `CTA_data/`, chapter 100, DATA | § 4.6; jump scan; row counts; gap dates; first valid date per series; truncated copy for robustness; **closing pass includes the chapter 00 relabel (T2):** its note and three figures marked schematic, since nothing has been measured | `data/adjusted/*.csv`, `run_00_data.py`, `results/00_data_checks.csv`, chapter 100 pointer, chapter 00 note | scan clean; five fixes and five `bar_fixed` rows logged; gap dates logged; chapters updated and rebuilt | every number spanning Dec 2025 | 3 |
| W2 | Engine and metrics | 3, 4 | — | `backtest.py` (imported, never modified) | `rr_engine.simulate(open, close, w_target, lag, exec_price, size_price, cost_bp, slip_bp, borrow_bp, deadband, capital)` → `w_held, shares, trades, pnl_gross, cost, slip, pnl_net, turnover_signal, turnover_drift`; `rr_metrics.py` per § 4.1; `tests/test_parity.py`: `simulate(lag=2, 'twap', size_price='prev_close', 0, 0, 0, 0)` ≡ `backtest.backtester` per asset on that asset's calendar, `bar_fixed` and gap rows excluded, to 1e-9; `tests/test_alignment.py`: synthetic jump, PnL responds only after `lag` rows; `tests/test_gap.py`; metric unit tests on toy data | `rr_engine.py`, `rr_metrics.py`, `tests/` | all tests green; the prototype's two-row lag documented | C1–C6, C9–C12 | 10 |
| W3 | Signals, MACD grid, smoother, walk-forward selection | 1 | A2–A4 | W1, chapters 02, 03 | MOM risk-adjusted + percentile; bar plots G1–G5 with Newey–West SE at the § 4.1 alignment (g ∈ {0, 5, 21} diagnostic); MACD grid on chapter 03's own geometric ladder n_f, n_s ∈ {1, 5, 10, 21, 63} (a day, a week, two weeks, a month, a quarter), n_f < n_s, plus the conventional (12, 26) as one reference cell, as Harry's notes set it, rule ∈ {zero-line, crossover, proportional}; heat map of spread with SE in every rung's training window, and the same heat map stitched over the WF record; **keep the band** (ratio ≈ 2:1, several cells), re-chosen each rung; smoother q < n_f re-chosen each rung by spread per unit implied turnover; **`config.BASELINE` frozen before any rung runs**; each rung's band sign-checked on its validation quarter, falling back to MOM only for that quarter if it fails (C8); **`run_ledger.csv` created here** (columns fixed in `config.py`; W4–W9 append; one row per cell per rung and per OV read, with a selection yes/no column) | `rr_signals.py`, `run_01_signals.py`, `results/01_bucket_mom.csv`, `01_macd_grid.csv`, `01_smoother_grid.csv`, `01_selected_signals.json`, `config.BASELINE`, `results/run_ledger.csv`, figures `rr-bucket-mom`, `rr-macd-heatmap`, `rr-smoother-tradeoff` | every chosen pair has warm neighbours; every cell tried in every rung is in `run_ledger.csv`; `tests/test_no_lookahead.py` asserts each rung's choice uses only rows before its test quarter | C5–C8 | 8 |
| W4 | Portfolios, haircut, rebuild pre-specified | 2, 3 | A1, A3 | W2, W3 | books: prop-signal MOM, prop-signal MACD, combined S = B0, P1, P2, sign-rule MACD books; naive_0, naive_1 and realistic on the Train-ladder and OV quarters of the WF record; H_1 attribution (4 runs) and H_0 Shapley (8 runs, 6 orders); full c × s × d sensitivity with TWAP and borrow rows; η rows on B0 (C11); drift vs signal turnover; concentration metrics; P1/P2 re-measured under the frozen conventions and the T5 correction written to `Backtests.md`; **`config.REBUILD` written before any rung runs** (η rule from B0's turnover in each rung's training window, κ = 0.5, scope LV/HV corner, cap 0.20) | `rr_portfolio.py`, `run_02_portfolios.py`, `run_03_haircut.py`, `results/02_portfolio_metrics.csv` (Train-ladder and OV quarters only), `03_haircut_waterfall.csv`, `03_haircut_sensitivity.csv`, `03_turnover_constraint.csv`, `config.REBUILD`, figures `rr-equity-curves`, `rr-execution-haircut` | attribution sums to naive − realistic for both bases; C13 acceptance evaluated on the Train-ladder and OV quarters and recorded either way as provisional; no Test row exists; `Backtests.md` corrected | C2–C4, C9–C13 | 6 |
| W5 | Per-asset regimes | 5 | — (resume only; 04 §3.1 per asset) | W1, W3 | V, σ; three cuts; 3×3 grid of spread, Newey–West SE, N dates, N asset-days, N episodes per cell and per tail bucket, for MOM (quoted), MACD and combined score; σ-normalized companion; per-period ordering table labelled by block; episode-block bootstrap of the corner difference; bond-ETF-excluded rerun | `rr_regimes.py`, `run_04_regimes.py`, `results/04_regime_grid_{rolling,frozen,fullsample_LOOKAHEAD}.csv`, `04_regime_by_period.csv`, figure `rr-regime-map` (counts printed in cells) | floors applied; cut and signal named in every file and caption; Train-ladder and OV quarters only until W10; D and per-rung S2 side by side | C14–C16 | 6 |
| W6 | VIX / MOVE regimes | 5 | B | class handout in `CTA_data/_indices/` with the three VIX corrections of DATA § 4; MOVE forward-filled over its 11 bond-holiday gaps (DATA § 7); source stated beside every regime number | (i) S1 log-ceiling, three merged buckets per index → VIX × MOVE 2-D table, then the same table under D, S2 and S3 so static and dynamic can be compared cell by cell of S's mean net return, SE, N dates per cell on Train's ladder OOS quarters + OV, descriptive version including 2020 labelled; (ii) rolling 252-day quintiles → per-state table; residual test as § 4.4 defines it from lecture 5 | `run_05_vix_move.py`, `results/05_vix_move_table.csv`, `05_vix_residual.csv`, figure `rr-vix-residual-bar` | counts printed; merges stated; residual verdict recorded; Test table marked not measurable | companion to C16; C17 features | 5 |
| W7 | Rebuild through the ladder | 6 | — | W4, W5 | B1 per `config.REBUILD`; ablation ladder B0 → +η → +vol scaling with cap → +κ(g) on OV; **resume wording for C17–C21 decided from the OV ablation and written into the `config.REBUILD` sidecar**; OV sensitivity grid with plateau size; power line (§ 6.1) computed on OV; concentration metrics for B1 | `rr_rebuild.py`, `run_06_rebuild.py`, `results/06_rebuild_ablation_OV.csv`, `06_rebuild_grid_OV.csv`, `run_ledger.csv` rows | config diff between B0 and B1 shows exactly the three switches; N_v recorded; wording sidecar written; Test untouched | C17–C19 | 8 |
| W8 | Models on the ladder | 7 | C | W3, W5, W6, `rr_split` | features per (asset, date): MOM, MACD, hist, smoothed MACD, σ, V, regime cell dummies and VIX/MOVE labels **under the rolling cut only** (`rr_models.py` asserts the label columns come from `rr_regimes.rolling()`); winsorize per § 4.3, z-score with fitting-window statistics only under the § 4.5 label rule; target = forward return at the § 4.1 alignment; models, as Harry chose them on 2026-10-23: Equal Weights (sign per feature from the fitting window of each rung); **regressions** OLS, Ridge and Lasso (select-then-refit), compared to see which works best, with features and target z-scored on the fitting window and λ set as a fraction of λ_max (the smallest λ that zeroes every coefficient) over {0.05, 0.1, 0.5, 0.7}: the lecture's 0.1/0.5/0.7, with 1.0 dropped because it is the null model and 0.05 added, since on raw daily returns the lecture's absolute values zero every coefficient; Ridge α ∈ {0.1, 1, 10, 100} on the same scale; **boosted trees** CatBoost (depth 4, 300 iterations, lr 0.05) and scikit-learn HistGradientBoosting (max depth 3, 200 iterations, lr 0.05), settings fixed a priori; ladder of § 4.5; **model class and λ chosen on OV by MSE under a one-SE rule** (among models within one bootstrap SE of the best OV MSE, the simplest: fewest features, largest λ), MAE tiebreak; IC beside; pooled R² > 0.1 aborts with a target-shift audit (09 §2) | `rr_models.py`, `run_07_models.py`, `results/07_model_ladder.csv`, `07_model_selection.csv`, `07_predictions.csv`, coefficient-path figure | one model named with its OV MSE; losing alternatives logged; no-lookahead test green | C5, C17 | 8 |
| W9 | Optimizer | 2 | D, E | W8 predictions and residuals | `solve(mu, Sigma, w_prev, gamma, cap_vec, tau)`, every input a vector or matrix; Σ̂ = **plain sample covariance of model residuals** over the refit window under the § 4.5 label rule (as assigned), Ledoit–Wolf as a labelled OV variant; max μᵀw − γ wᵀΣ̂w − τ Σ\|w − w_prev\|, Σ\|w\| ≤ 2, \|w_i\| ≤ cap; **Σw = 0 for the model variant compared with B0** (same mandate, same r_f), Σw = 1 lecture variant compared with P1 under DTB3; **γ pre-specified by a target annualized book volatility** (the homework's "choose the risk preference you want"), the γ grid {0.3, 0.5, 1, 2, 5} shown as a sensitivity table; cap ∈ {0.2, 0.25, 0.3} and τ on OV under the one-SE rule; SLSQP | `rr_optimizer.py`, `run_08_optimizer.py`, `results/08_optimizer_grid_OV.csv`, unit test with vector caps | feasible w on every date; γ's target vol and the OV choices stated | homework D, E; model variant of C20 | 8 |
| W10 | Single Test read + robustness | 4, 5 | E | committed configs, W4–W9 | `config.BASELINE` and `config.REBUILD` committed before this step; `run_09_test.py` refuses to run if the working tree differs from that commit, writes the commit hash into every Test sidecar, opens Test once with a timestamp: B0, B1, ablation steps, haircut Test column, regime grid Test column, and the optimizer book **if W9 is finished** (the slot is pre-registered as possibly empty; an unfinished optimizer book is never Test-read and is reported on OV only, labelled); then § 6 in full | `run_09_test.py`, `run_10_robustness.py`, `results/06_scorecard.csv`, `06_scorecard_by_quarter.csv`, `03_haircut_waterfall.csv` (Test column), `08_robustness_rebuild.csv`, `08_robustness_haircut.csv`, `08_deflation.csv`, figure `rr-rebuild-scorecard` | every C13/C16/C20/C21 number has its CI at five block lengths, breakdown and deflation line; Test opened exactly once; sidecars carry the config commit hash | C13, C16, C20, C21 | 6 |
| W11 | Write-up and reconciliation | — | — | all | `run_11_reconcile.py` fills the ledger status column; `RESULTS.md` (sample statement, every number with the command and CSV cell that regenerates it); `Backtests.md` § "Resume reproduction" with headline numbers and snippets (T5 done-when); a claimed-versus-measured table in `RESULTS.md` (claim, measured value with CI, sample, the "futures proxies" rule, which claims survive only at 90%). Per Harry on 2026-10-23, no correction notes for submitted resumes: the deliverable is the results; chapter 00's note gains the link to `RESULTS.md` (T2); figures via the `figures` skill after the `nature-figure` pass, both themes, both axes labelled | `RESULTS.md`, `Backtests.md` diff, PNGs | each claim has a measured value, its CI and its sample, or is marked not measurable; `check_sync.py` clean | all | 6 |

Homework-to-resume mismatches, handled in the open: the resume's bullet 3 is per-asset V/σ (W5), the homework's Part B is market-wide VIX/MOVE (W6) — both are run, the VIX table is never substituted for the per-asset grid; the resume's "turnover controls" are the course's smoother (in both books, A4) + deadband (B1's switch); the resume never mentions the optimizer, whose Σw = 0 model variant is reported as a separate labelled line, not as the +8%; selection in W8 is by MSE/MAE with IC reported beside, as the lecturer set it.

## 6. Robustness protocol

### 6.1 C20 (+8% Sharpe) and C21 (−14% turnover)

| Step | What | Pass condition for quoting the resume number |
| --- | --- | --- |
| Same everything | B0 and B1 share data, split, cost set, overlap, lag, fill, net 0, gross 2, smoother q; only § 4.3's three switches differ; B0 never re-tuned | config diff shows exactly those keys |
| Baseline first | SR_B0, TO_B0, N days, r_f, mean and max \|net\|, mean gross, concentration, printed before SR_B1 | SR_B0 90% CI excludes 0 for any percentage to be quoted |
| Power line, analytic, written now | For T days of daily returns, SE(SR_ann) ≈ √(252/T): ≈ 1.0 at T = 250 (Test alone) and ≈ 0.47 at T = 1,125 (the WF record). For two books sharing signals with paired correlation ρ, SE(ΔSR) ≈ SE(SR) × √(2(1 − ρ)): at ρ = 0.95, ≈ 0.32 (T = 250) and ≈ 0.15 (T = 1,125). One-sided 5% critical value = 1.64 × SE(ΔSR) ≈ 0.52 / 0.25; **MDE at 80% power = (1.64 + 0.84) × SE(ΔSR) ≈ 2.5 × SE ≈ 0.79 / 0.37**. SR_B0's 90% CI excludes 0 only if SR_B0 ≳ 1.64 × SE(SR) ≈ 1.6 (T = 250) or ≈ 0.78 (T = 1,125). An 8% relative change on any plausible SR_B0 is an order of magnitude below the MDE. The bootstrap version is recomputed on OV before Test is read and printed beside these | **Consequence, stated now:** the "+8%" percentage cannot be supported at this sample size whatever the outcome; the C20 fallback (absolute ΔSR with CI, bp/yr, turnover change) is the expected resume text; `RESULTS.md` states that "+8%" is below what this sample can detect |
| Paired block bootstrap | stationary block bootstrap of paired daily (r_B0, r_B1), 2000 draws; **mean block 21 days quoted, CI also at {5, 10, 21, 42, 63} in a sensitivity column, the widest quoted if they disagree**; block length in every CI header; CI on ΔSR, on ΔTO% (signal and drift separately), and on the percentage ΔSR/SR_B0 computed inside each draw; two-sided 90% pre-registered, 95% printed beside | claim "supported" only if the CI excludes 0 |
| Per-fold | ΔSR, ΔTO per WF-record quarter (18), each labelled Train-ladder, OV or Test | sign agreement count reported |
| Per-period | 2024H2, 2025H1 (OV), 2025H2, 2026H1 (Test) | reported, labelled by block |
| Drop best days | remove the same dates from both books, chosen by largest \|r_B1 − r_B0\|, k = 5 and 10; share of cumulative ΔPnL earned on the top 5 Δ-days | sign of ΔSR unchanged — this is the answer to "8% is two good days" |
| Cost sensitivity | ΔSR at c ∈ {2, 5, 10}, s ∈ {0, 2, 5}, b ∈ {0, 25, 50} | sign unchanged; table reported |
| Deflation | raw N_v = rows of `run_ledger.csv` with selection = yes, every OV read counted (W3 sign check, W7 grid, W8 and W9 grids); effective N_v = clusters of variants whose OV return series correlate above a cutoff, **reported at cutoffs 0.8 and 0.9**; Deflated Sharpe (Bailey–López de Prado) at raw and both effective counts applied to the **OV** Sharpe of B1, which is in-sample for all of those reads; Test carries its plain CI and the single-evaluation statement | DSR printed beside the raw OV Sharpe |
| Ablation | B1 minus each switch in turn, on OV (where the wording is decided, before Test) and once on Test, reported in full | the turnover fall is attributed to η, the Sharpe change to its switch, on OV; if Test disagrees with OV on which switch moved the number, the disagreement is reported and the OV-based wording is softened, never sharpened |
| Truncated sample | all of the above with data ending 2025-12-04 | sign unchanged |
| Universe | all of the above excluding the 7 fixed-income ETFs; B1's bond-sleeve PnL share beside | sign unchanged, or the dividend bias is named in the reconciliation |

### 6.2 C13 (25% haircut)

| Step | What | Pass condition |
| --- | --- | --- |
| Base check | naive_1 mean daily return with Newey–West SE and block-bootstrap CI (block 21, sensitivity column) on the WF record; naive_0 beside | CI excludes 0, else bp/yr only |
| Joint bootstrap | block bootstrap of paired daily (naive_1, realistic), same blocks; CI on H_1; same for H_0 | reported |
| Cost grid | H at c ∈ {0, 2, 5, 10, 20}, s ∈ {0, 2, 5, 10}, d ∈ {1, 2, 3}, fill ∈ {close, TWAP}, b ∈ {0, 25, 50}; d = 0 rows marked "non-executable, benchmark only" | H_1 ≥ 0.25 at the pre-registered set; the crossing cost level is a sensitivity row, never the headline |
| Attribution | H_1: cost and slippage (labelling convention stated) with the d = 1 → 2 delay row; H_0: Shapley over three switches, min/max across the 6 orders, interaction = joint − sum of marginals | reported with the order stated |
| Per-block and per-period | H per block (Train, OV, Test; OV alone always printed) and per calendar period; a period with negative naive return is "ratio undefined" | reported |
| Turnover link | table of (annual executed turnover, bp of drag) for the single-signal, combined and η books and the cost-grid points; implied bp per turn | drag scales with turnover as chapter 00 §2.4 claims, or the table says it does not |

### 6.3 C16 (regime ordering)

Bootstrap of the HV/LV − LV/HV difference resampling **whole regime episodes** (cross-sections kept intact), with a date-block version at mean block 63 and the {5, 10, 21, 42, 63} sensitivity column, the widest quoted; this CI is the binding criterion. The per-period sign test of § 2.3 with its null probability printed beside it; the frozen cut as a second reading; bond-ETF-excluded rerun; the σ-normalized spread beside the bp spread; MACD and combined-score grids as companions; Test column added after the fact and labelled.

## 7. Execution order, dependencies, effort

| Order | Workstream | Blocked by | Parallel with | Hours |
| --- | --- | --- | --- | --- |
| 1 | W0 Environment | — | W1 | 1 |
| 1 | W1 Data fix | — (decided in DATA § 4) | W0 | 3 |
| 2 | W2 Engine | W0 | W3 | 10 |
| 2 | W3 Signals and baseline | W1 | W2 | 8 |
| 3 | W4 Haircut and rebuild config | W2, W3 | W5, W6 | 6 |
| 3 | W5 Per-asset regimes | W1, W3 | W4, W6 | 6 |
| 3 | W6 VIX / MOVE | W5's bucket code | W4 | 5 |
| 4 | W7 Rebuild on OV | W4, W5 | W8 | 8 |
| 4 | W8 Models | W3, W5, `rr_split` | W7 | 8 |
| 5 | W9 Optimizer | W8 | — | 8 |
| 6 | W10 Test read and robustness | W7; W9 if its book is to be Test-read | — | 6 |
| 7 | W11 Write-up | all | — | 6 |
| | **Total** | | | **~75** |

Longest chain for the resume claims: W1 → W3 → W4 → W7 → W10 → W11 ≈ 37 h (W0 → W2 → W4 is 17 h to the same point). Longest chain for the full homework, with the optimizer book in the single Test read: W1 → W3 → W5 → W8 → W9 → W10 → W11 ≈ 45 h; the "Test opened exactly once" rule puts W8 and W9 on that path, which is why W10 pre-registers the optimizer slot as possibly empty. If time is short, the lecturer's rule applies: A and B complete before C; W6 shrinks to the log-ceiling table only; W8 runs Equal Weights + Ridge + one tree, nothing more. Hard constraints: no Test row anywhere before W10; `config.BASELINE` and `config.REBUILD` frozen before any rung runs and committed before W10; every per-rung choice uses only rows before its test quarter; W5 and W6 cuts never mixed in one table.

## 8. Where things live

| Thing | Location | Rule |
| --- | --- | --- |
| This plan and ledger | `Resume_Reproduction/OUTLINE.md` | status column filled by `run_11_reconcile.py` |
| Data decisions | `Resume_Reproduction/DATA.md` | authoritative for data, sample-split and capital conventions; W1 regenerates every number in it before it is quoted |
| Superseded drafts | `Resume_Reproduction/drafts/` | read-only; nothing cites them |
| Config and library | `Resume_Reproduction/config.py` (dates, grids, bp, windows, seed, block-of-choice per field), `rr_data.py`, `rr_signals.py`, `rr_regimes.py`, `rr_portfolio.py`, `rr_engine.py`, `rr_metrics.py`, `rr_split.py`, `rr_rebuild.py`, `rr_models.py`, `rr_optimizer.py` | importable, no side effects; `backtest.py` imported by the parity test, never modified |
| Run scripts and tests | `run_00_data.py` … `run_11_reconcile.py`; `tests/test_parity.py`, `test_alignment.py`, `test_gap.py`, `test_no_lookahead.py`, `test_metrics.py` | one script per workstream, each regenerates its own `results/NN_*.csv` |
| Result tables | `Resume_Reproduction/results/*.csv` + `.json` sidecar (params, git hash, timestamp, alignment string, block length); header row states instruments, frequency, dates, N, r_f, cost set, cut, signal | — |
| Figures | `Resume_Reproduction/figures/rr-<name>-{light,dark}.png` via `make_rr_figures.py`, which imports `docs/figures/_style.py` and follows the `figures` skill after the `nature-figure` pass; the `rr-` prefix keeps them apart from chapter 00's schematic figures of the same subject | a deliberate exception to `docs/figures/<NN>_figures/`, since no chapter owns these |
| Measured numbers | `Resume_Reproduction/RESULTS.md` (authoritative), `Backtest_prototype/Backtests.md` § "Resume reproduction" (headline numbers and snippets, mirrored) | never in `docs/chapters/` |
| Data | `CTA_data/*_ohlcv_1d.csv` untouched; split-adjusted copy in `Resume_Reproduction/data/adjusted/`; VIX/MOVE handout as received in `CTA_data/_indices/` and the corrected VIX in `Resume_Reproduction/data/adjusted/`; DTB3 in `Resume_Reproduction/data/external/` | — |
| Theory cited, never edited with numbers | chapters 02, 03, 04, 05, 09, 100; WF; `References/Momentum_ssrn-2089463.pdf` | — |
| Chapter 00 story | `docs/chapters/00_pipeline/00_pipeline.md`: its note says the percentages were "measured on this sample", which is not true; W1's closing pass relabels the three figures and the note as schematic (T2), W11 adds the link to `RESULTS.md`. **No measured value enters the chapter** | T2 revision |
| Closing pass | per finished change: `check_sync.py --impact` before, rebuild if a `.tex` or figure moved, `check_sync.py` after, named `git add`, commit, push; no AI attribution | `AGENTS.md` § 4 |

## 9. Open questions for Harry

### 9.1 Decided on 2026-10-23

| # | Question | Decision |
| --- | --- | --- |
| Q2 | Cost set | c = 5 bp per side and s = 2 bp, approved by Harry. Fixed before W4 runs |
| Q3 | Static or dynamic regime cut | Run one dynamic cut and three static cuts and compare them (§ 3 flag 2, § 4.4, DATA § 6.1) |
| Q4 | Which book is "the strategy" | B0, the momentum + MACD dollar-neutral book. MACD as Harry defined it in chapter 03 (§ 4.3, W3) |
| Q7 | What "VIX beta on MOM beta" means, and which log | Settled from lecture 5 itself: each asset's sensitivity to VIX, regressed across assets on its MOM and MACD scores, with the residual made into a portfolio (§ 4.4). The log is natural, as chapter 04 defines the cut; base 10 would collapse the cut to two buckets |
| Q8 | Installs and dividends | Installs approved and done (W0). Distribution histories are obtainable, so every headline gets a total-return re-run (§ 4.6) |
| Q5 | Reword or withdraw, and correct submitted resumes? | Neither. No corrections; the deliverable is the measured results (W11) |
| Q6 | QFA 12% / 15% | Dropped from this work |
| Q9 | Tree models | CatBoost and scikit-learn HistGradientBoosting, confirmed |
| — | Split design | The lecture's walk-forward ladder, re-choosing every quarter, not three fixed blocks (§ 4.5) |
| — | Model set | Equal Weights; OLS, Ridge and Lasso compared; boosted trees CatBoost and HistGradientBoosting (W8) |
| — | VIX/MOVE source | The class handout (DATA § 1) |

### 9.2 Still open

| # | Question | Why it changes the work |
| --- | --- | --- |
| Q1 | Harry says the repository is private, but on 2026-10-23 GitHub's API reports `Harrybido2711/CTA_Strategy` as public and its page opens without logging in. Once it is private, `Resume_Reproduction/` and `data/external/` are committed in full | Nothing in this folder is pushed while the repository is public |

Decided elsewhere, no longer open: the split-fix location and the split-day bar (DATA § 4: adjusted copy, open := close, high := max(low, close)); the VIX/MOVE source, which is the class handout (DATA § 1).
