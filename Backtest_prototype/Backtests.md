# Backtest Prototype — Implementation Notes

This file keeps only what is **tied to this particular implementation**: design choices,
results, and caveats. The reusable concepts have moved into the series and are not repeated here:

| Looking for | Chapter |
| --- | --- |
| What each column means, why timing is offset, look-ahead bias | [05 · Understanding Backtesting](../docs/05-understanding-backtesting.md) |
| The momentum signal, overlapping holding periods, portfolio weights | [04 · From Signal to Position](../docs/04-from-signal-to-position.md) |
| Unadjusted prices, splits, data-quality checks | [02 · Data & Corporate Actions](../docs/02-data-and-corporate-actions.md) |

Code: [`backtest.py`](backtest.py). The multi-asset version introduces no new trading logic —
it loops the single-asset backtester over all 37 assets and sums the per-asset PnL.
用循环把单资产回测跑 37 遍再加总。

---

## Design Insights

The non-obvious ideas that make this assignment clean — worth internalizing.

1. **Reuse, don't rewrite — loop the single-asset backtester.** The multi-asset
   engine adds *zero* new trading logic; it just calls the existing
   `backtester` once per asset and sums the per-asset PnL. Single-asset already
   handles shares/TWAP/cash, so multi-asset is a `for` loop.
   信号和执行彻底解耦，换信号不用碰回测，换回测不用碰信号。

2. **Overlap = `rolling(5).mean()` — the core "aha".** A 5-day hold with a fresh
   daily signal means you always carry 5 tranches of 1/5 each, so the held
   weight *is* the 5-day mean of target weights. This one line **is** the
   holding-period rule (smoothing and low turnover are just side effects), not a
   cosmetic filter. 这是作业真正想让你悟到的点。

3. **Weights are money, not shares.** Working in capital fractions makes 37
   assets at wildly different prices comparable; price only enters at
   `shares = dollar / close`. Equal-weight legs sum to their target (150% / 50%)
   **by construction**, an identity rather than a coincidence.

4. **Vectorize the cross-section with a boolean mask.** `(mom>0)` as 1/0 divided
   by the daily count `n_pos` builds the whole equal-weight long leg in one
   expression — no per-asset `if`. The mask *is* the membership; the count *is*
   the denominator. `(mom>0)/n_pos*1.5` does the entire long side at once.

5. **Median, not mean, for relative MOM (Portfolio 2).** Only the cross-sectional
   median reproduces the brief's +66/+66/−66 example (2 long, 1 short); the mean
   would give 1 long / 2 short. Matching the spec's own example pins down the
   ambiguous wording. 小细节，但决定对不对得上题目。

6. **Know which total moves under overlap: net is invariant, gross shrinks.**
   Because `Σ mean = mean Σ`, net exposure stays exactly +100%; but
   `|mean| ≤ mean|·|`, so gross drifts below 200% whenever an asset flips sign
   within the 5-day window. Expecting a clean 2.0 and "fixing" it would be a
   mistake — the drift is the honest footprint of smooth rebalancing.

7. **A short is just a negative share count.** No special code path — allow
   `curr_shrs < 0`, value it at `curr_shrs × close`, and the accounting
   (negative asset value + positive cash from the sale) handles the rest.

8. **Let timing be explicit, not implicit.** The `delay` + `.shift()` offsets
   encode "a signal known at today's close can't trade at today's earlier
   prices" — avoiding look-ahead bias is a design choice you can point to, not
   an accident.

## Results & Caveats

Over 2020-01 → 2026-06 both portfolios post near-zero Sharpe (a fast, weekly
cross-sectional momentum on 37 ETFs is not expected to be profitable — the
exercise is about the mechanics).

**Vertical steps in the equity curve come from the data, not from a code bug.** With
unadjusted prices, a split manufactures a fake return on the split date. Status as of 2026-07-31:

- ✅ **Fixed** — UNG (1-for-4, 2024-01-24) and USO (1-for-8, 2020-04-29) now use split-adjusted
  data; the phantom +300% / +700% jumps are gone.
- ⚠️ **Not fixed** — XLB / XLE / XLK / XLU / XLY had a 2-for-1 forward split on 2025-12-05 and
  still carry a phantom ≈ −50% return. On top of that, the `open` and `high` of the split-date
  bar are themselves corrupt for those five, which a split adjustment alone will not repair.
- Dividends are unadjusted throughout.

Evidence and detail: [02 · Data & Corporate Actions](../docs/02-data-and-corporate-actions.md).
Until those five are fixed, no conclusion spanning December 2025 is trustworthy.

## Next Steps

Assigned work, in order. The existing pipeline stays as-is — only the signal changes, and each
step reuses the same plotting and backtest path.

1. **Re-plot portfolio performance** using the risk-adjusted signal bucketed by rolling quantile
   instead of raw value. See [03 §§ 6–7](../docs/03-building-signals.md).
2. **Add a MACD-style fast momentum leg** to the grid search, and read the result as a heat map
   rather than picking the maximum. See [03 § 8](../docs/03-building-signals.md) and
   [07 § 4](../docs/07-overfitting-and-robustness.md).
3. **Smooth the fast leg** to suppress volatility-clustering churn — with a window shorter than
   the signal's own period, or it just becomes another slow signal. See
   [03 § 10](../docs/03-building-signals.md).
4. **Run the new signal through the existing pipeline** and produce the corresponding charts.

Looking further ahead: a volatility *forecast*, rather than trailing realized volatility, as the
noise filter — that is where the next session is heading.
