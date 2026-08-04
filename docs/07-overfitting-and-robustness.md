# 07 · Overfitting & Robustness

> **Answers:** why a good backtest is weak evidence, and what makes it stronger.
> **Prerequisites:** [06 · Evaluating Performance](06-evaluating-performance.md).
> **After reading:** split a time series correctly, and state honestly how much of a result is signal and how much is search.

> 🟡 **Partly written.** §§ 1–2, 4 complete; §§ 3, 5–6 outline.

---

## 1. Train / Validation / Test

| Stage | Question it answers |
|---|---|
| **Train** | Does the hypothesis hold at all? Is the signal → return relationship linear, non-linear, or only present in the extremes? |
| **Validation** | Among candidate signal combinations, which is best? |
| **Test** | Does the validation choice generalize? |

Validation exists to stop you picking a strategy by hindsight on the training data. Choose the
winner and measure it on the data you chose it from, and you have measured your selection, not the
strategy.

| Segment | Period |
|---|---|
| Training | before 2024-06 |
| Validation | 2024-06 → 2025-06 |
| Test | 2025-06 → 2026-06 |
| *(full range)* | *2020-01 → 2026-06* |

```python
train = df.loc[: "2024-06"]
valid = df.loc["2024-06" : "2025-06"]
test  = df.loc["2025-06" :]
```

## 2. Never split a time series randomly

Standard ML shuffles rows before splitting. **For financial time series this is wrong**, and for
momentum it is fatal.

The cause is autocorrelation in the signal: a one-month momentum computed today and one computed
yesterday share 20 of 21 days of underlying returns, so they are not independent observations.
Shuffle them across train and test and the test set fills with near-duplicates of training rows —
the model looks like it generalizes when it has memorized.

That is forward-looking bias in subtle form: no row contains future data, but the **split** does.
Cut on time, never on shuffled rows. Same logic as the rolling-quantile rule in
[03 § 7](03-building-signals.md) — when you ask "is this value high?", the comparison set must
contain only the past.

## 3. Why a backtest overstates

*(outline)* — Every choice already made is a degree of freedom: 21-day lookback, 5-day hold, 150/50
split, median vs mean, the 37-ticker universe, the 2020–2026 window. Counting them honestly is the
first step.

## 4. Parameter sensitivity: read the heat map, not the maximum

Every parameter here — lookback, holding period, reversal skip, fast/slow ratio, EWMA half-life —
was chosen, and every choice is a place to overfit. **Grid-search the pair, plot a heat map, judge
the shape rather than the peak.**

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/param-heatmap-dark.png">
  <img alt="Two heat maps of Sharpe over fast lookback against slow lookback. Left, a plateau: a broad contiguous warm region where neighbouring parameters also perform. Right, a spike: one bright cell in an otherwise cold grid" src="figures/param-heatmap-light.png">
</picture>

A real edge is **contiguous** — neighbours also work, because the effect is not knife-edge sensitive
to an arbitrary integer. One hot cell in a cold grid is noise that lined up, and it will not survive
out-of-sample. Parameters sitting on a spike do not mean "found the optimum"; they mean the grid has
shown you nothing.

**Remember what these numbers are.** MACD's 26/12/9 are not theory — they are values that fit past
data, an *empirical solution*. Everything you select by grid search has the same status, which is
the entire reason this chapter exists.

## 5. Multiple testing

*(outline)* — Try 50 variants and the best looks good by construction. Deflated Sharpe,
Bonferroni-style haircuts, and the practical version: log everything you tried. Also survivorship —
these 37 ETFs all exist today.

## 6. Robustness checks worth running here

*(outline)*

- Drop the best-contributing asset and re-run.
- Shift the execution assumption (close-fill vs TWAP vs open-fill).
- Add realistic costs; find the breakeven cost level.
- Re-run the split-corrupted tickers before and after adjustment — a concrete measure of how much a data defect moves a result. See [02](02-data-and-corporate-actions.md).

---

## Common pitfalls

- **Shuffling rows before splitting.** Standard for tabular ML, invalid for time series, fatal for momentum.
- **Skipping validation.** Then the test set becomes the selection set and nothing is held out.
- **Treating 2020–2026 as one regime.** It contains COVID, a rate-hike cycle, and a commodity shock.
- **Forgetting the data is a choice.** Five tickers still carry a phantom −50% ([02](02-data-and-corporate-actions.md)); robustness testing on corrupted data measures the corruption.

## Open questions

- ~1 year each for validation and test against ~4.5 years training — enough to separate edge from noise at these Sharpe levels?
- Walk-forward (rolling the three windows) instead of one fixed cut?
- The *test* set's own observations also overlap. Does that inflate significance within the test period?

---

## Next → the assignment: [Backtest_prototype/Backtests.md](../Backtest_prototype/Backtests.md)

Before moving on, **cut the data into train / validation / test and re-run**, then grid-search the
lookback × holding-period pair and look at the *shape* of the heat map rather than its maximum.

You should be able to explain:

- [ ] Why shuffling rows is fatal for momentum specifically
- [ ] Why a plateau is trustworthy and a single hot cell is not
- [ ] How many degrees of freedom this strategy has already spent

[← 06](06-evaluating-performance.md) · [Index](00-index.md)
