# Brief: execution outline for reproducing the CTA resume bullets

Repository: /Users/harrychen/Career_Preparation/CTA_Strategy (read AGENTS.md first; it is injected).
Owner: Harry. Date: 2026-10-23. Output language: English.

## 1. The core task, in Harry's words

"复刻这个简历的成果" — reproduce the outcomes claimed in these four resume bullets with numbers this
repository actually produces:

> Developed an execution-aware CTA strategy using momentum and MACD signals, building a transparent
> Python backtesting engine to visualize cumulative returns and evaluate Sharpe ratio, drawdown,
> turnover, IC, and signal win rate.
> - Evaluated the impact of transaction costs, execution delay, turnover constraints, and slippage,
>   demonstrating that over 25% of naive backtest returns disappeared after incorporating realistic
>   execution assumptions.
> - Constructed rolling volume and volatility measures to classify market regimes, revealing that
>   trend-following signals were consistently more effective in high-volume, low-volatility
>   environments than under adverse market conditions.
> - Refined trading signals using regime-aware feature engineering, volatility scaling, and turnover
>   controls, improving out-of-sample Sharpe ratio by 8% while reducing annual turnover by 14%
>   relative to the baseline strategy.

These numbers are already on resumes sent to Citadel (x2), Morgan Stanley HK, BofA HK and AmEx.
Nothing in the repo has measured any of them yet. The outline must make every one of them either
reproducible or explicitly marked as "not supported, resume must change".

## 2. Red flags Harry wants closed (from a resume-audit session), priority order

| Flag | What was said | Priority |
| --- | --- | --- |
| QFA "12% Sharpe / 15% drawdown" | Added by someone else; Harry: "I may not have improved the portfolio". In five submitted resumes. **Outside this repo** — the outline records it as unverified and out of scope; never fabricate support. | red, first |
| CTA regime threshold static vs dynamic | Harry told the mentor "static"; the Q&A bank says rolling trailing quantiles and calls a full-sample cutoff look-ahead. Only one can be true. | red |
| CTA "25%" | 25% of what — naive cumulative return, annualized return, or Sharpe? No base is recorded. | high |
| CTA "8%" | Baseline Sharpe unknown; does 8% survive robustness? Mentor: "8% is one or two good days in 250". | high |
| Data / instruments / frequency | Which instruments, what frequency, how long a sample — every number will be questioned to this level. | medium |
| Regime bucket count and observations per bucket | A thin bucket manufactures its own Sharpe; the second question any researcher asks. | medium |

## 3. The homework steps the plan must follow (lecture assignments, translated; keep this order)

**A. Signal to portfolio (after the momentum/MACD signal lectures)**
1. Build a portfolio from the signal the way the course found it works: weights proportional to the
   signal, i.e. use the signal directly as holdings. ("weights prop signal prop return")
2. Long/short MOM combinations using MACD: a table from a grid search over the parameters; the
   optimum may be several parameter sets, not one.
3. Put the MACD long/short signals through the bar plot (bucket test) and the backtester already
   written.
4. Add a smoother to MACD and find the best smoother layer.

**B. VIX and MOVE regimes (a VIX + MOVE index file was handed out in class; it is NOT in the repo)**
- Bucket VIX and MOVE two ways: (i) ceiling(log(VIX^2)); (ii) rolling quantile.
- After bucketing, see how the existing portfolio performs in each state.
- For (i): a 2-D table. For (ii): regress the VIX-derived beta on the MOM beta computed earlier;
  test whether the residual has any indication for return.
- Teacher's note: next class starts models; if the load is too much, finish the previous homework
  fully first — at minimum there must be signals to model on.

**C. Models.** Generalize the framework to more models: at least Equal Weights, at least one
regression model, at least one tree model. Choose the best model on the validation set of the whole
walk-forward backtest; use MSE/MAE for selection.

**D. Optimization framework.** Build the optimization framework. Estimate the covariance matrix
directly from residuals. Each input must be a vector, not a scalar (the optimizer will be changed
later).

**E. Finish the optimizer.** Choose the risk preference you want, then put it into the test set and
look at the result.

## 4. Repo facts established today (do not re-derive; cite them)

- Data: 37 daily ETF OHLCV CSVs in CTA_data/, 2020-01-02 to 2026-06-29, about 1630 rows each,
  UTC-dated, dividends unadjusted, volume in shares. Categories: US broad equity (5), US sectors
  (11), international equity (5), fixed income (7), commodities (6), alternatives (3). ETFs stand in
  for futures.
- Split trap: XLB, XLE, XLK, XLU, XLY carry an UNADJUSTED 2-for-1 split effective 2025-12-05, and
  that day's open/high bar is separately corrupt. Fix is OHLC/2 and volume*2 before 2025-12-05 plus
  a treatment of the split-day bar. Until fixed, nothing spanning Dec 2025 is trustworthy.
  Unadjusted originals live in CTA_data/_unadjusted_raw/. See docs/chapters/100_dataset/100_dataset.md.
- Code: Backtest_prototype/backtest.py — single-asset backtester (dollar target -> shares, TWAP =
  (open+close)/2, one-calendar-day delay via merge_asof), multi-asset loop summing PnL, 21-day
  momentum = rolling mean of daily returns, two portfolios (P1: long 150% of positive-MOM assets,
  short 50% of negative; P2: sign relative to cross-sectional median, 2/N each), 5-day overlapping
  hold = rolling(5).mean() of targets, perf_stats = final PnL, ann return, ann vol, Sharpe
  (r_f = 0), max drawdown. There are NO: transaction costs, slippage, turnover metric, IC, win rate,
  regime classification, MACD, smoother, model, optimizer, walk-forward split.
- Backtest_prototype/Backtests.md is the home for measured numbers and reproduction snippets.
  Chapters (docs/) are theory only; a chapter must never carry a measured number or a code
  variable name. Current result: both portfolios post near-zero Sharpe over 2020-01 to 2026-06.
- docs/chapters/00_pipeline/00_pipeline.md already narrates the resume outcomes as a story (the
  haircut waterfall: costs 11, slippage 7, delay 8 of 100; a 3x3 regime grid from +2 bp to +38 bp;
  scorecard +8% Sharpe, -14% turnover) and states that the prototype is behind the story.
  The eight-stage build order there is: 0 validate data, 1 compute a signal, 2 size positions,
  3 simulate under execution, 4 evaluate, 5 attack the result, 6 rebuild against the diagnosis,
  7 try a model.
- Course theory to cite (read these before drafting):
  - docs/chapters/02_testing_a_signal/02_testing_a_signal.tex: bucket (bar) plot G1..G5 with
    standard errors, the gap g between lookback and scored return, risk-adjusted momentum
    (divide by trailing sigma or percentile against own past), Sharpe is NOT the signal-stage
    metric, r_f for a 150/50 book is a time series not zero, information availability.
  - docs/chapters/03_shaping_the_lookback/03_shaping_the_lookback.tex: EWMA, fast/slow pairing
    found by a geometric-ladder grid read as a heat map (a band, not one hot cell; ratio ~2:1),
    MACD definition (EMA spans n_f < n_s, 9-day signal line, histogram), three rules (zero-line,
    crossover, proportional), smoother must be shorter than the signal's own period, deadband,
    volatility clustering causes whipsaw.
  - docs/chapters/04_volatility_regimes/04_volatility_regimes.tex: log-ceiling bucket
    g_t = ceil(c * ln v_t) (c=1 gives cuts at e^3=20.1 and e^4=54.6; the homework's
    ceil(log(VIX^2)) is c=2), vs rolling quantile; full-sample quantile is look-ahead; the
    two-way sort (conditioning) with counts printed per cell; residualizing a candidate on
    incumbents (MOM, MACD) and bar-plotting the residual; "orthogonal is not independent".
  - docs/chapters/05_modelling/05_modelling.tex and market_knowledge/walk-forward-modelling.md:
    walk-forward ladder with 2-3 month segments (train 1-3, val 4, test 5; slide by one), inner
    layer selects features, outer held-out validation block selects model class, lambda, and
    optimizer parameters (gamma, per-asset cap), test touched once; Lasso select-then-refit;
    winsorize with rolling quantiles computed on the raw series; standardize uniformly using
    only statistics available at the end of the fitting window. Mean-variance:
    max_w E[r_p] - gamma Var[r_p], sum w = 1, sum|w| <= 2, |w_i| <= 0.2 (cap tunable).
  - docs/chapters/09_ic_and_r_squared/09_ic_and_r_squared.md: IC = per-date cross-sectional
    Spearman between prediction and forward return; report mean IC, ICIR, t-stat deflated by
    horizon overlap; plausible mean rank IC 0.02-0.05; R^2 above 0.1 on daily data is a bug.
- Environment: python3 is 3.8.7 with pandas 2.0.3, numpy 1.24.4, matplotlib 3.7.5. scipy,
  scikit-learn, statsmodels, cvxpy are NOT installed. The .venv is empty. Installing packages is
  a step the outline must include (sklearn 1.3.x and scipy 1.10.x still support 3.8).
- References/Momentum_ssrn-2089463.pdf is the one paper in the repo.
- Repo rules that bind this work: every finished change is committed and pushed (no AI
  attribution trailer in this repo); measured numbers never go in a chapter; figures need both
  light and dark PNGs via the figures skill; new practical parts get their own folder with a .md
  and a .py (Backtest_prototype/ is the precedent).

## 5. What the outline file must be

Path: Resume_Reproduction/OUTLINE.md (a new top-level folder; it will later hold the scripts and
results of this work). Markdown, English, formal but readable. It is a plan and a claims ledger,
not a chapter: it may name files, variables, numbers and commands.

It must contain, in some sensible order:
1. Purpose and scope — what is being reproduced, in whose words, and the rule that a claim that
   does not reproduce is reported as such.
2. A claims ledger — one row per resume claim (there are more than four: the metric list in the
   first bullet is itself a set of claims), each with: the exact measurement that would support
   it, its base/denominator, the sample it is measured on, the acceptance criterion, current
   status (all unmeasured today), and the fallback wording if it fails.
3. Red-flag resolutions — a decision for each of the six flags in section 2 above, including the
   static-vs-rolling regime decision (the plan must run BOTH cuts and say which one each quoted
   number uses), and the QFA flag marked out of scope.
4. Fixed definitions, decided once — every metric (Sharpe incl. the r_f convention, max drawdown,
   turnover and its annualization, IC, signal win rate, hit rate), the execution model (delay,
   execution price, cost in bp, slippage model, turnover constraint/deadband), the regime
   measures (rolling window lengths, tercile method, counts), the sample split (dates for
   train / held-out validation / test; segment length for the ladder), and the data treatment
   of the 2025-12-05 split (decide: adjust and clamp, or truncate the sample at 2025-12-04 and
   say so).
5. Workstreams, each mapped to a pipeline stage (0-7) and to a homework step (A-E), with inputs,
   procedure, outputs (files, tables, figures), done-when, and which ledger claim it feeds.
   Include the environment setup, the data fix, the VIX/MOVE data acquisition (file not in repo;
   fallback source must be named), and the final write-up/resume reconciliation.
6. A robustness protocol for the +8% / -14% claim: same baseline, same split, bootstrap or
   block-bootstrap CI on the Sharpe difference, per-year and per-fold breakdown, and a deflation
   for the number of variants tried; plus the same for the 25% haircut (sensitivity to cost bp).
7. Execution order and dependencies — what blocks what, what can run in parallel, and an
   honest estimate of effort per workstream.
8. Where things live — Resume_Reproduction/ for scripts and results, links to Backtests.md and
   the chapters, no numbers in chapters.
9. Open questions for Harry — only those that change the work materially (e.g. the VIX/MOVE
   file, the cost level, what to do with the resume if a number fails).

Avoid: inventing results, quoting the story's illustrative numbers as if measured, proposing to
tune anything on the test set, or proposing a full-sample quantile cut without flagging it as
look-ahead. Prefer tables to prose. Keep it under about 450 lines.
