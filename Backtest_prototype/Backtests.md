# Backtest Prototype — Implementation Notes

Only what is **tied to this implementation**: design choices, results, caveats. Reusable concepts
live in the series:

| Looking for | Chapter |
| --- | --- |
| Column meanings, timing offsets, look-ahead bias | [04 · Understanding Backtesting](../docs/04-understanding-backtesting.md) |
| Momentum signal, overlapping holds, portfolio weights | [03 · From Signal to Position](../docs/03-from-signal-to-position.md) |
| Unadjusted prices, splits, data-quality checks | [100 · The Dataset](../docs/100-dataset.md) |

Code: [`backtest.py`](backtest.py). Multi-asset adds no trading logic — it loops the single-asset
backtester over 37 assets and sums the PnL. 用循环把单资产回测跑 37 遍再加总。

---

## Design Insights

1. **Reuse, don't rewrite.** Multi-asset adds *zero* trading logic — single-asset already handles
   shares/TWAP/cash, so multi-asset is a `for` loop.
   信号和执行彻底解耦，换信号不用碰回测。
2. **Overlap = `rolling(5).mean()` — the core "aha".** A 5-day hold with a fresh daily signal means
   5 tranches of 1/5 are always live, so the held weight *is* the 5-day mean of targets. That one
   line **is** the holding-period rule; smoothing and low turnover are side effects.
   这是作业真正想让你悟到的点。
3. **Weights are money, not shares.** Capital fractions make 37 differently-priced assets
   comparable; price enters only at `shares = dollar / close`. Equal-weight legs sum to 150%/50% by
   construction — an identity, not a coincidence.
4. **Vectorize the cross-section with a boolean mask.** `(mom>0)/n_pos*1.5` builds the entire
   equal-weight long leg in one expression — the mask *is* the membership, the count *is* the
   denominator. No per-asset `if`.
5. **Median, not mean, for relative MOM.** Only the median reproduces the brief's +66/+66/−66 (2
   long, 1 short); the mean gives 1 long / 2 short. 小细节，但决定对不对得上题目。
6. **Net is invariant, gross shrinks.** `Σ mean = mean Σ` holds net at exactly +100%, but
   `|mean| ≤ mean|·|` drags gross below 200% whenever an asset flips sign inside the window.
   "Fixing" that drift would be a mistake — it is the honest footprint of smooth rebalancing.
7. **A short is just a negative share count.** No special path: allow `curr_shrs < 0`, value at
   `curr_shrs × close`, and the accounting handles the rest.
8. **Make timing explicit.** `delay` + `.shift()` encode "a signal known at today's close can't
   trade at today's earlier prices" — a design choice you can point to, not an accident.

## Shorts as a Negative Share Count

Why insight 7 works, in this code. Concept side — bounded longs, unbounded shorts, borrowing
mechanics — is [01](../docs/01-what-is-cta.md).

**Claim.** In [`backtester`](backtest.py), a position with `curr_shrs < 0` gains exactly when the
close falls, with no branch special-casing shorts.

**Proof.** Open `s` shares at execution price `p₀`, hold to a close `p₁` with no further trades.
Following the code in order:

```text
cash_spend  = s · p₀                                     # traded_shrs × TWAP
net_cash    = −cumsum(cash_spend) = −s · p₀
asset_value = s · p₁                                     # curr_shrs × close
portfolio   = net_cash + asset_value = s (p₁ − p₀)
```

which is the ordinary payoff expression. For `s < 0`, `portfolio > 0` exactly when `p₁ < p₀`. The
sign of the share count carries the direction and the accounting needs no other case.

No borrowing, fees, or margin are modelled — shares are assumed always borrowable at zero cost.

### Constant-dollar exposure caps the short

`multi_asset_backtester` feeds a *weight × capital* dollar series, so the share count is recomputed
every day rather than frozen at entry. That silently bounds a losing short. Shorting \$1 of SPY
across the sample, as it rose ×2.28:

| Position | Final PnL | Why |
| --- | --- | --- |
| Static short — share count frozen at entry | **−1.2791** | The full `s(p₁ − p₀)` |
| Constant −\$1 exposure — what this code does | **−0.9385** | Exposure trimmed daily as the price rises |

Reproduce with:

```python
import pandas as pd
from datetime import timedelta
from backtest import load_assets, backtester

spy = load_assets()["SPY"]
dollar = pd.DataFrame({"ts_event": spy["ts_event"], "dollar": -1.0})
print(backtester(spy, dollar, delay=timedelta(days=1))["portfolio"].dropna().iloc[-1])
```

Worth being explicit about: the daily rebalance is an **implicit risk control the backtest gets for
free**, and a real short book only behaves this way if it is actually rebalanced that often.

## Results & Caveats

Over 2020-01 → 2026-06 both portfolios post near-zero Sharpe. Expected — a fast weekly
cross-sectional momentum on 37 ETFs is not supposed to be profitable; the exercise is the mechanics.

**Vertical steps in the equity curve come from the data, not a code bug.** Status as of 2026-07-31:

- ✅ **Fixed** — UNG (1-for-4, 2024-01-24) and USO (1-for-8, 2020-04-29) now split-adjusted; the
  phantom +300% / +700% jumps are gone.
- ⚠️ **Not fixed** — XLB / XLE / XLK / XLU / XLY had a 2-for-1 forward split on 2025-12-05 and still
  carry a phantom ≈ −50%. The split-date bar's `open` and `high` are separately corrupt, which a
  split adjustment alone will not repair.
- Dividends are unadjusted throughout.

Detail: [100](../docs/100-dataset.md). Until those five are fixed, no conclusion
spanning December 2025 is trustworthy.

## Next Steps

Assigned work. The pipeline stays as-is — only the signal changes.

1. **Re-plot performance** with the risk-adjusted signal bucketed by rolling quantile instead of raw
   value — [02 §§ 6–7](../docs/02-building-signals.md).
2. **Add a MACD-style fast leg** to the grid search; read the heat map, don't pick the maximum —
   [02 § 8](../docs/02-building-signals.md), [06 § 4](../docs/06-overfitting-and-robustness.md).
3. **Smooth the fast leg** with a window shorter than its own period, or it becomes another slow
   signal — [02 § 11](../docs/02-building-signals.md).
4. **Run it through the pipeline** and produce the charts.

Further ahead: a volatility *forecast* rather than trailing realized vol as the noise filter.
