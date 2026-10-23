# Data decision — what the reproduction runs on

Decided 2026-10-23. This file overrides any data, sample-split or capital convention in
`OUTLINE.md` or `drafts/` that disagrees with it. Every number below was measured on 2026-10-23
by an ad-hoc audit of `CTA_data/`. Workstream W1 (the data script) must regenerate each one
before it is quoted anywhere.

---

## 1. Sources

| Series | Source | Status | Use |
| --- | --- | --- | --- |
| **Prices and volume, 37 ETFs** | `CTA_data/*_ohlcv_1d.csv` (Databento `ohlcv-1d`, publisher 43, one instrument id per file) | In repo. Daily, 2020-01-02 → 2026-06-29, 1630 trading days, no weekends | Signals, returns, execution, per-asset volume and volatility regimes |
| **VIX** | Class handout, `CTA_data/_indices/VIX_index_1d_2020_now.csv`, received 2026-10-23. 1654 rows, 2020-01-02 → 2026-07-31 | In repo. Matches Cboe's official close on all but three days, which are corrected (§ 4). No ETF trading day is missing. One extra row, 2026-05-25, is a market holiday and is dropped | Market-wide equity regime, homework B. `Close` only |
| **MOVE** | Class handout, `CTA_data/_indices/MOVE_index_1d_2020_now.csv`, received 2026-10-23. 1632 rows, 2020-01-02 → 2026-07-17 | In repo. Identical to Yahoo `^MOVE` on every common day, so it is Yahoo-sourced. ICE publishes no free official history to check it against. 11 ETF trading days are missing, all bond-market holidays | Market-wide rates regime, homework B. `Close` only: the first half of the file has open = high = low = close, and later opens repeat the prior close |
| VIX cross-checks | Cboe `VIX_History.csv` (the official source) and FRED `VIXCLS` | Both downloaded 2026-10-23 and identical to each other | Arbitrate the handout's three disagreements |
| **Risk-free rate** | FRED `DTB3`, 3-month T-bill, annualized percent | Checked available. Mean over the sample is 2.82% | Excess return in every Sharpe |
| Consolidated prices and volume | Yahoo chart API | Robustness only, never primary | Checks of the volume and close fields below |

The ETFs stand in for futures. **Resume and interview wording must say "37 liquid US-listed ETFs
as futures proxies", never "futures".**

## 2. Universe

All 37 tickers, kept whole: US broad equity (5), US sectors (11), international equity (5), fixed
income (7), commodities (6), alternatives (3). Every ticker covers the full sample. No ticker is
dropped, because dropping one after seeing results is itself a search the robustness protocol
would have to deflate.

## 3. Sample blocks

| Block | Dates | Trading days | Use |
| --- | --- | --- | --- |
| Warm-up | 2020-01-02 → 2020-12-31 | 253 | Fills the 252-day rolling windows. Never scored, never fitted |
| Train-ladder quarters | 2021-01-04 → 2024-06-28 | 877 | 14 calendar quarters of 61–64 days. 2021 seeds the first rung; 2022Q1 → 2024Q2 are its 10 walk-forward test quarters |
| Outer validation | 2024-07-01 → 2025-06-30 | 250 | Four more walk-forward quarters. Also where the outer layer is chosen: model class, λ, tree settings, optimizer cap, τ and γ |
| Test | 2025-07-01 → 2026-06-29 | 250 | Four more walk-forward quarters, produced with the outer layer frozen and read once |

**The split is a walk-forward ladder, not three fixed blocks** (Harry, 2026-10-23; `OUTLINE.md` § 4.5). Every quarter from 2022Q1 to 2026Q2 is traded by choices re-made from the quarters before it: train on three quarters, validate on the next, refit, test on the one after, then slide one quarter. The blocks above only label which quarters are which.

**One exception to the warm-up rule.** The log-ceiling regime cut uses no data, so descriptive
regime tables may include 2020. That is the only place the 2020 crash appears. Each such table
says so in its title.

## 4. Cleaning decisions

| Defect | Evidence | Decision |
| --- | --- | --- |
| **XLB, XLE, XLK, XLU, XLY: unadjusted 2-for-1 split on 2025-12-05** | The five closes fall −49.6% to −50.3% that day. No other split-sized move exists | **Adjust, do not truncate.** The test block contains the date, so truncating would cut it to five months. Before 2025-12-05: OHLC ÷ 2, volume × 2. On the split day: open := close, high := max(low, close). Write to `Resume_Reproduction/data/adjusted/` and leave `CTA_data/` untouched |
| **Vendor gap, 2022-11-21 → 2022-12-09** | IEF misses 8 days, TLT 7, SHY 5, QQQ 4 | Keep the days missing, and carry each asset's position and cumulative PnL across them with no trade. The current engine sums cumulative per-asset PnL while skipping missing values. That drops total PnL by up to 6.6% of capital for a day and back, on 12 days |
| **Volume covers only one venue feed** | Against consolidated volume, the feed holds 19–25% of SPY, 11–13% of TLT and 24–29% of GLD, and the share drifts by year. The 21-day rolling log volume still correlates 0.93–0.97 with the consolidated series | Use volume only as each asset's **rank against its own trailing 252 days**. Never compare volume levels across assets, and never use it as average daily volume for impact or capacity |
| **Close is not the official close** | Bars aggregate by UTC date. Against the consolidated close: median 8–10 bp, 95th percentile 39–57 bp, max 246–390 bp | Acceptable for daily signals. Close-to-close is the return everywhere |
| **Open is probably a pre-market print** | SPY open against the regular-session open: median 20 bp, 95th percentile 96 bp | **The primary fill is the next day's close.** The prototype's (open + close) / 2 survives only as a sensitivity variant and for the parity test against `backtest.py` |
| Dividends unadjusted | Stated in `docs/chapters/100_dataset/`. Yahoo distribution events exist for all 37 tickers. 33 pay; GLD, SLV, USO and UNG do not. Approximate yield over the sample: HYG 5.3%/yr, VNQ 3.7%, LQD 3.5%, TIP 3.5%, down to about 0.4% for XLK and XLY | Price return stays primary. Every headline is re-run on total return as a robustness row. The yields of the five split SPDRs are understated here, because Yahoo's amounts are split-adjusted and the pre-split closes are not |
| UNG, USO reverse splits | Already adjusted. Remaining large moves are real: USO −27.4% on 2020-04-21, UNG −25.7% on 2026-02-02 | Keep as is. **Chapter 100 prints both as positive.** Correct it under task T6 in W1 |
| **VIX handout: three wrong closes** | Against Cboe's official close: 2021-08-11 handout 16.17, Cboe 16.06. 2021-10-01 handout 21.10, Cboe 21.15. 2026-02-06 handout 20.37, Cboe 17.76 | Replace the three closes with Cboe's values in `Resume_Reproduction/data/adjusted/`, and leave the handout file as received. The 2026-02-06 error is large enough to move that test-block day from the calm bucket to the elevated one |

## 5. Capital and return conventions

**The engine trades a constant $1 of notional.** Each asset's dollar target is weight × $1, set
fresh every day against the original $1, not against current equity. Nothing is reinvested.

| Quantity | Definition | Why |
| --- | --- | --- |
| Capital | $1, constant | Results are scale-free: shares are fractional, costs are in bp, and there is no size-dependent impact. $1 and $10M give identical percentages |
| Daily return | Change in cumulative PnL ÷ $1 | Additive, so the cost drag is exactly γ × turnover. That is what lets the 25% haircut split into costs, slippage and delay with no ordering problem |
| **Growth, headline** | Cumulative PnL per $1 of initial capital, simple, not compounded | Matches what the engine does |
| Annualized return | Mean daily return × 252 | Arithmetic, consistent with the additive accounting |
| CAGR | Only from a separate rerun that sizes on prior-day equity | Compounding a $1-notional PnL series mixes two conventions |
| Excess return | Daily return − DTB3 × net exposure | Capital not deployed earns the bill rate, and capital borrowed pays it. For a net-zero book this term vanishes |
| Max drawdown | Largest fall of cumulative PnL from its running peak, **in units of initial capital** | Consistent with the $1 base. Percent of peak equity is printed beside it |
| Annual turnover | Σ\|Δw\| per year, in multiples of the $1 book | Defined fully in `OUTLINE.md` |

**What the existing prototype shows under these conventions** (`backtest.py`, frictionless, full
sample, split unfixed unless stated):

| Book | Gross / net exposure (median) | Cumulative PnL per $1 | Annualized | Sharpe, r_f = 0 | Sharpe, DTB3 charged | Max drawdown |
| --- | --- | --- | --- | --- | --- | --- |
| P1, long 150 / short 50 | 1.76 / +1.00 | +0.490 (+0.526 split fixed) | +7.6% | 0.42 (0.45 split fixed) | 0.27 | −0.415, 2022-06-07 → 2023-11-09 |
| P2, median long/short | 1.65 / +0.05 | +0.210 | +3.2% | 0.27 | 0.26 | −0.224, 2022-03-08 → 2023-11-13 |

Two consequences:

- **`Backtest_prototype/Backtests.md` says both books post near-zero Sharpe. That is wrong for the
  current code and data.** It needs a correction under task T5.
- **P1's Sharpe is mostly market beta.** Its net exposure is +100% through a rising market, and
  a third of it disappears once the bill rate is charged. The resume baseline should be the
  net-zero book, or P1 quoted with DTB3 charged.

## 6. Regime data: days per bucket

Log-ceiling cut, g = ⌈ln VIX²⌉ = ⌈2 ln VIX⌉, with cuts at e^(k/2). Counts use the corrected handout. Uncorrected, one test day moves from the calm row to the elevated row:

| VIX bucket | Level | All 2020–2026 | Ladder | Outer validation | Test |
| --- | --- | --- | --- | --- | --- |
| g ≤ 6, calm | ≤ 20.1 | 932 | 520 | 175 | 202 |
| g = 7, elevated | 20.1–33.1 | 617 | 347 | 67 | 48 |
| g ≥ 8, stressed and crisis | > 33.1 | 81 | 10 | 8 | 0 |

| MOVE bucket | Level | All 2020–2026 | Ladder | Outer validation | Test |
| --- | --- | --- | --- | --- | --- |
| g ≤ 9 | ≤ 90.0 | 784 | 289 | 25 | 236 |
| g = 10 | 90.0–148.4 | 810 | 554 | 225 | 14 |
| g = 11 | > 148.4 | 36 | 34 | 0 | 0 |

**Decision: three buckets per index, merged as above.** The raw cut gives five VIX buckets, and
the two outer ones hold 10 and 14 days.

What the counts rule out:

- **No day with VIX above 54.6 is ever out of sample.** All 14 fall in 2020, inside the warm-up.
- **The stressed VIX row has 10 days in the ladder.** Any mean computed there is reported as
  "unmeasurable", not as zero.
- **The test block cannot evaluate regime behaviour.** It holds no stressed VIX day, and 236 of its
  250 days sit in one MOVE bucket. Regime claims are evidenced on the ladder's out-of-sample
  quarters. The test block only confirms the final strategy.

The rolling-quantile cut uses a trailing 252-day window, so it starts in 2021. Every regime number
is labelled with the cut that produced it.

### 6.1 Dynamic versus static cuts

Harry asked on 2026-10-23 for one dynamic cut and three static cuts, run side by side. The four
cuts, each into three buckets so they can be compared:

| Cut | Thresholds come from | A label means | Look-ahead |
| --- | --- | --- | --- |
| **D**, rolling 252-day rank | The trailing year, re-estimated every day | Higher or lower than the recent past | None |
| **S1**, data-free fixed cut | Nothing: e^3 and e^3.5, which are 20.1 and 33.1 on VIX | An absolute level of fear, the same in every year | None |
| **S2**, frozen | One training window. Shown here frozen once on 2021-01 → 2024-06: 16.8 and 21.4 on VIX. In the plan it is re-frozen at the start of every rung | High or low against the training window | None, when frozen per rung |
| **S3**, full sample | All of 2020-01 → 2026-06: 16.9 and 21.9 on VIX | High or low against the whole history | **Yes.** Diagnostic only |

VIX days in the low, mid and high bucket, using the corrected handout:

| Cut | Train | OV | Test | 2022 alone | 2023-06 → 2024-06, calm |
| --- | --- | --- | --- | --- | --- |
| D | 513 / 168 / 196 | 13 / 75 / 162 | 82 / 97 / 71 | 37 / 63 / 151 | 201 / 51 / 19 |
| S1 | 520 / 347 / 10 | 175 / 67 / 8 | 202 / 48 / 0 | 24 / 218 / 9 | 265 / 6 / 0 |
| S2 | 294 / 292 / 291 | 98 / 97 / 55 | 111 / 105 / 34 | 1 / 45 / 205 | 230 / 40 / 1 |
| S3 | 299 / 315 / 263 | 99 / 104 / 47 | 115 / 104 / 31 | 1 / 54 / 196 | 231 / 40 / 0 |

What the table shows:

- **The two families disagree on half the days.** D puts a day in the same bucket as S1 on 45%
  of days, as S2 on 52% and as S3 on 51%. Chance alone gives 33%. Static versus dynamic is
  therefore a different question, not a detail.
- **D forgets a persistent regime.** Through 2022, when VIX sat between 20 and 35 all year, S2
  calls 205 days high and D only 151. As the level persists, the trailing year catches up with
  it and D stops calling it high.
- **D flags modest rises after a calm stretch.** In OV, VIX was mostly 13–20 but above the very
  calm 2023–24 year before it. D calls 162 of 250 OV days high, S2 calls 55.
- **S1 is coarse.** Its top bucket holds 10 Train days and no Test day, and it calls almost all
  of 2022 mid.
- **Static cuts on per-asset volatility label the asset, not the regime.** With S1 applied to
  each asset's annualized σ, 76% of asset-days carry that asset's usual label, and AGG, IEF, LQD,
  SHY and TIP are always "low". Under D the figure is 40%. Per-asset regimes therefore use D, or
  per-asset S2 and S3 cutpoints, never one fixed cut across assets. Volume has no fixed cut at
  all: no volume level means the same thing across ETFs, and the feed covers a drifting share of
  the market.

## 7. Timing

| Item | Rule |
| --- | --- |
| Signal on date t | Uses closes through t |
| Regime label on date t | Uses the index close on t or earlier. Rolling cuts are trailing, never full-sample |
| Fill | Close of t + 1 (one trading day of delay). Naive benchmark: close of t, no cost |
| VIX/MOVE alignment | On the calendar date, forward-filled at most one day, and fills counted. MOVE needs 11 fills, on the bond-market holidays 2020-10-12, 2020-11-11, 2021-10-11, 2021-11-11, 2022-10-10, 2022-11-11, 2023-10-09, 2024-10-14, 2024-11-11, 2025-10-13 and 2025-11-11. VIX needs none |
| DTB3 | Forward-filled over bank holidays |

## 8. Open items for Harry

1. **The GitHub repository is public.** May DTB3, the Cboe VIX history and the Yahoo
   distribution histories be committed under `Resume_Reproduction/data/external/`, and may this
   folder be committed at all? It is the same question as `OUTLINE.md` Q1. The VIX/MOVE source
   question is closed: the class handout arrived on 2026-10-23 and is in `CTA_data/_indices/`.
