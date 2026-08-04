# 07 · Overfitting & Robustness

> **This chapter answers:** why a good backtest is weak evidence, and what to do to make it stronger.
> **Prerequisites:** [06 · Evaluating Performance](06-evaluating-performance.md).
> **After reading you can:** split a time series correctly, and state honestly how much of a result is signal and how much is search.

> 🟡 **Partly written.** §§ 1–2 and § 4 are complete; §§ 3, 5–6 are outline only.

---

## 1. Train / Validation / Test

Three stages, each answering a different question:

| Stage | Question it answers |
|---|---|
| **Train** | Does the hypothesis hold at all? What is the shape of the signal → return relationship — linear, non-linear, or only present in the extremes? |
| **Validation** | Among several candidate signal combinations, which one is best? |
| **Test** | Does the choice made in validation actually generalize? |

The validation stage exists specifically to stop you from picking a strategy by hindsight on the
training data. If you choose the winner and measure it on the same data you chose it from, the
measurement is meaningless — you have measured your own selection, not the strategy.

The split used for this course's dataset:

| Segment | Period |
|---|---|
| Training | everything before 2024-06 |
| Validation | 2024-06 → 2025-06 |
| Test | 2025-06 → 2026-06 |
| *(full range)* | *2020-01 → 2026-06* |

In pandas this is just time indexing:

```python
train = df.loc[: "2024-06"]
valid = df.loc["2024-06" : "2025-06"]
test  = df.loc["2025-06" :]
```

## 2. Never split a time series randomly

Standard machine-learning practice shuffles rows and splits at random. **For financial time series
this is wrong**, and for momentum it is fatal.

The reason is autocorrelation in the signal itself. A one-month momentum value computed today and
one computed yesterday share almost all of their underlying daily returns — the windows overlap by
20 of 21 days. So "today" and "yesterday" are not independent observations. Scatter them randomly
across train and test, and the test set is full of near-duplicates of training rows. The model
looks like it generalizes when it has really just memorized.

This is forward-looking bias in a subtle form: no single row contains future data, but the *split*
does. Always cut on time, never on shuffled rows.

The same logic drives the rolling-rank rule in [03 § 5](03-building-signals.md) — whenever you ask
"is this value high?", the comparison set must contain only the past.

## 3. Why a backtest overstates

*(outline — to be written)*

- Every choice already made is a degree of freedom: 21-day lookback, 5-day hold, 150/50 split,
  median vs mean, the 37-ticker universe, the 2020–2026 window.
- Counting those choices honestly is the first step.

## 4. Parameter sensitivity: read the heat map, not the maximum

Every parameter in this project — the lookback, the holding period, the reversal skip, the fast/slow
ratio, the EWMA half-life — was chosen, and every choice is a place to overfit.

The discipline is to **grid-search the pair and plot the result as a heat map**, then judge the
*shape* rather than the peak:

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/param-heatmap-dark.png">
  <img alt="Two heat maps of Sharpe over fast lookback against slow lookback. Left, a plateau: a broad contiguous warm region where neighbouring parameters also perform. Right, a spike: one bright cell in an otherwise cold grid" src="figures/param-heatmap-light.png">
</picture>

A real edge is **contiguous**: parameters near the best one also work, because the effect is not
knife-edge sensitive to an arbitrary integer. A single hot cell surrounded by cold ones is noise
that happened to line up, and it will not survive out-of-sample.

When your chosen parameters sit on a spike, the correct conclusion is not "I found the optimum" —
it is that the grid has not shown you an edge.

**Remember what these numbers are.** MACD's 26/12/9 are not theory; they are values that happened
to fit historical data — an *empirical solution*. Every parameter you select by grid search has
exactly the same status. Fitting the past implies nothing about the future, which is the entire
reason this chapter exists.

## 5. Multiple testing

*(outline — to be written)*

- If you try 50 variants, the best one looks good by construction. Deflated Sharpe,
  Bonferroni-style haircuts, and the practical version: keep a log of everything you tried.
- Survivorship and selection: these 37 ETFs all exist today.

## 6. Robustness checks worth running here

*(outline — to be written)*

- Drop the best-contributing asset and re-run.
- Shift the execution assumption (close-fill vs TWAP vs open-fill).
- Add realistic costs and find the breakeven cost level.
- Re-run on the split-corrupted tickers before and after adjustment — a concrete measure of how
  much a data defect can move a result. See [02](02-data-and-corporate-actions.md).

---

## Common pitfalls

- **Shuffling rows before splitting.** Standard for tabular ML, invalid for time series, fatal for momentum — overlapping lookback windows make adjacent rows near-duplicates.
- **Skipping validation and going straight from train to test.** Then the test set becomes the selection set, and you have no held-out data left.
- **Treating the 2020–2026 window as one regime.** It contains COVID, a rate-hike cycle, and a commodity shock. A single split cuts across regimes, not just across time.
- **Forgetting that the data itself is a choice.** Chapter 02 showed that five tickers still carry a phantom −50% return. Robustness testing on corrupted data measures the corruption.

## Open questions

- Only ~1 year each for validation and test, against ~4.5 years of training. Is that enough to distinguish a real edge from noise at the Sharpe levels involved?
- Should the split be re-cut as walk-forward (repeatedly rolling the three windows forward) rather than a single fixed cut?
- Momentum autocorrelation also means the *test* set's own observations overlap. Does that inflate apparent significance within the test period too?
