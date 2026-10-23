# Round 2 — Time-series momentum, as the paper defines it

Written and committed 2026-10-23, **before any Round 2 number was computed**. `config.ROUND2`
holds every parameter.

## Why a second round

Round 1 (`RESULTS.md`) tested the wrong object. Its B0 ranked 37 ETFs against each other every
day on a 21-day signal and held for five days. That is short-horizon **cross-sectional** momentum.
At that horizon these series reverse, and turnover of 39× a year buried any edge under friction.

The strategy the resume describes is **time-series** momentum, as defined in the paper in
`References/`. Each asset is long when its own past 12-month excess return is positive and short
when it is negative. Its position is scaled to a constant ex-ante volatility, and it is held for a
month. The paper finds the effect strongest for look-backs of 9–12 months and holding periods of
1–3 months (Table 2, Panel A: t = 6.61 at k = 12, h = 1). It weakens past 24 months.

## What is fixed, and by whom

| Item | Value | Source |
| --- | --- | --- |
| Signal | sign of the past 12-month excess return | paper § 4 |
| Holding period | 1 month: signal at the month's last close, trade at the next close | paper § 4 |
| Asset sizing | 40% / σ_s, with σ an EWMA of squared daily returns, centre of mass 60 days, × 261 | paper eq. (1) and § 4.1 |
| Aggregation | 1 / S over the assets with a signal | paper § 4.1 |
| Grid, descriptive only | look-back 1, 3, 6, 9, 12 months × holding 1, 3 months | paper Table 2, truncated |
| Returns | total-return prices minus DTB3 | ETFs stand in for futures, whose returns are excess returns |
| Costs | 5 bp per side + 2 bp slippage, no borrow fee; 25 and 50 bp/yr borrow as robustness | Round 1, approved by Harry |
| Per-asset cap, gross cap | 0.5 of capital, 3× gross | ours: an ETF margin account, not futures |
| Book volatility target | 10% annual, EWMA covariance with centre of mass 60 days | ours, after Harry's request |
| Regime overlay | multiply T1's leverage by m in the high-VIX tercile (rolling 252-day cut) | ours, after Harry's request |
| m | chosen from {1, 0.75, 0.5, 0.25} on 2021-02 → 2024-06 by Sharpe, one-SE rule toward 1 | the only parameter chosen on data |

Look-backs past 12 months cannot be tested properly: the data start in 2020-01, so a 24-month
signal would exist only from 2022.

## The books

| Book | Definition | Plays the resume's role of |
| --- | --- | --- |
| **T0**, the paper | sign(12-month excess return) × 40%/σ_s / S, monthly, with caps | the baseline |
| **T1**, vol-targeted | T0 × L_t, with L_t = 10% / ex-ante book volatility, gross ≤ 3 | volatility scaling |
| **T2**, regime-aware | T1 × m in the high-VIX tercile, plus a 0.5% deadband on rebalance trades | regime-aware leverage and turnover control |

## The regime analysis (Harry, 2026-10-23)

On 2021-02 → 2025-06, which excludes Test, five steps:

1. **T0 and T1 excess returns by state.** States are VIX and MOVE terciles under the dynamic cut and
   the three static cuts of Round 1, plus the book's own trailing 63-day volatility tercile. Day
   and month counts are printed for every state.
2. **The leverage path.** Show how T1's leverage moves with volatility, and how often the gross
   cap binds.
3. **The per-asset regime map.** Recompute the volume × volatility grid with the TSMOM signal and
   the next-month return, which is bullet 3 at the paper's horizon.
4. **Choose m.** Pick the high-VIX multiplier on 2021-02 → 2024-06, and confirm it on OV.
5. **Execution haircut.** Compute T0's haircut from naive to realistic execution, which is bullet 2.

## Samples, and the Test caveat

| Sample | Dates | Use |
| --- | --- | --- |
| Fixed-parameter record | 2021-02 → 2025-06 | T0 and T1 have no data-chosen parameter, so all of it is out of sample for them |
| Choice window for m | 2021-02 → 2024-06 | T2's only fitted parameter |
| OV | 2024-07 → 2025-06 | confirms m |
| Test | 2025-07 → 2026-06 | read once at the end |

**Test was already read once, in Round 1**, for different books. The market's path over those
four quarters is therefore known. Every Round 2 parameter comes from the paper, or is fixed in this
file, or is chosen on pre-Test data. Even so, a second look at the same quarters is weaker
evidence than a first, and the results say so.

## Power, stated now

2021-02 → 2026-06 holds 65 monthly rebalances. Test holds 12.

- **Sharpe.** At 65 months the standard error of an annualised Sharpe is about 0.43. At 12 months
  it is about 1.0. Only a Sharpe above about 0.7 over the full record would be distinguishable
  from zero at 90%.
- **Regime splits.** A regime tercile holds about 20 months. Treat every regime comparison as
  descriptive unless its CI says otherwise.

## Amendment 1 — T3, added after the pre-Test regime analysis (2026-10-23)

**What the pre-Test analysis showed.** T0 earns +12.4% a year when VIX is in the low tercile of
its trailing year and −14.0% in the high tercile (`results/20_regime_returns.csv`). Yet the
pre-registered rule chose m = 1 for T2: cutting leverage at month-ends in the high-VIX state
lowered the Sharpe. A month-end state does not predict the next month, because the losses happen
while VIX is high.

**What was added.** T3 keeps T0's monthly directions and per-asset sizing, but re-sets two things
every day from that close's information: the book leverage, to 10% ex-ante volatility, and the
high-VIX multiplier m. A 0.5% deadband limits the trading. m comes from the same grid by the same
one-SE rule on the same pre-Test window.

**Result, pre-Test** (`results/20b_t3_multiplier.csv`). The rule again chooses m = 1, so T3 is
daily volatility targeting with no VIX overlay. Any m below 1 lowers the Sharpe and raises
turnover: m = 0.5 gives a Sharpe of −0.18 against +0.25, on 28 turns a year against 11. In this
sample, de-leveraging on a VIX state cuts exposure after the drawdown and misses the recovery.
Continuous inverse-volatility scaling, in T1 and T3, is the adjustment that helps.

T3 was frozen with m = 1 before Test was read. It is reported beside T0–T2 and labelled as an
amendment.

## Status after the Test read (2026-10-23)

The read ran at commit `deeeb61`; the numbers are in `RESULTS.md` § Round 2. In short, over
2021-02 → 2026-06, after costs and in excess of bills:

| Book | Excess return | Sharpe | Max drawdown | Sharpe on Test |
| --- | --- | --- | --- | --- |
| T0, the paper | +4.8% | 0.32 | −0.42 | 1.06 |
| T1, 10% volatility target | +4.5% | 0.46 | −0.22 | 1.23 |
| T2 / T3, the VIX overlays (m = 1) | +4.3% to +4.5% | 0.43 to 0.45 | −0.23 | 1.25 |

T1 − T0 in Sharpe has a 90% bootstrap CI of −0.04 to +0.34 over the record, and +0.003 to +0.35 on
Test. Monthly rebalancing holds turnover near 11 turns a year, so a deadband has little left to
trim.
