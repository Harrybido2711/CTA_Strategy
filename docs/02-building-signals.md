# 02 · Building Your Own Signal

> - **Answers:** how to turn an intuition into a computable signal, and how to tell whether it carries information before backtesting it.
> - **Prerequisites:** [01 · What Is a CTA Strategy](01-what-is-cta.md); the data it runs on is [100 · The Dataset](100-dataset.md).
> - **After reading:** state a signal as a hypothesis, test it with a bucket chart, normalize it, and combine horizons without drowning in noise.

---

## 1. A signal is a hypothesis, not a formula

$$
\textbf{signal:}\quad MOM_t  =  \text{Avg}\left(r_{s,t-i}\right),\qquad i = 1 \ldots N
$$

$$
\textbf{hypothesis:}\quad MOM \uparrow  \Longrightarrow  \text{return} \uparrow
\qquad\qquad
\textbf{consequence:}\quad MOM_t  \propto  w  \propto  \text{return}
$$

The third line makes it tradeable: the signal doesn't just correlate with return, it says **how much**
to allocate — the bridge into [03](03-from-signal-to-position.md).

Write the hypothesis first because it tells you what would falsify it. A signal you cannot falsify
is a plot you will rationalize either way.

## 2. Horizons travel — but verify

A signal that works yearly is assumed to work monthly and quarterly, since a long trend is short
fluctuations accumulating in one direction. That is a prior, not a fact.

When a horizon test comes back non-monotone, don't discard the signal — re-read the source paper's
assumptions (universe, period, skip, weighting). Most "it doesn't work" results are "I implemented
a different signal than the one tested."

## 3. Why the scatter plot disappoints

A scatter needs ~30% correlation before the eye picks out a trend, 40–50% to convince, 80% to be
obvious. **Real signals run 10–15%** — an undifferentiated cloud whether they work or not, so the
absence of a visible trend proves nothing.

The scatter spends all its resolution on individual noisy points instead of the average behaviour
that matters.

## 4. The bucketed bar chart — the core method

1. Sort observations by signal value.
2. Cut into groups G1 (low) → G5 (high).
3. Take each group's **mean forward return**.
4. Plot as bars **with error bars**.

```python
buckets = pd.qcut(signal.stack(), 5, labels=["G1","G2","G3","G4","G5"])
grouped = fwd_return.stack().groupby(buckets)
means, errs = grouped.mean(), grouped.sem()
means.plot.bar(yerr=errs)
```

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/bucket-chart-dark.png">
  <img alt="Bucketed bar chart: mean forward return rises monotonically from bucket G1 to G5, with error bars, and the G5−G1 spread annotated as the long/short edge" src="figures/bucket-chart-light.png">
</picture>

**Reading it.** Monotone G1 → G5 means the signal carries information. Monotonicity is the test, not
the height of any one bar — a tall G5 with G1–G4 scrambled is usually small-sample noise.

**It prices the trade.** Long the top bucket, short the bottom: the expected spread is the gap
between those bars. G5 at +2% and G1 at −1% is worth about 3%.

**Why it beats the scatter.** Each bar is a cross-sectional portfolio held at every date, averaged
down the time axis — so it answers "how often does this rank correctly?", which is what determines
whether the strategy earns.

Error bars are not decoration: they stop you reading a 2-observation bucket as a result.

## 5. Reversal — why the lowest bucket misbehaves

On raw momentum the staircase usually breaks at the **bottom** bucket: the biggest losers bounce
rather than keep losing.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/reversal-buckets-dark.png">
  <img alt="Two bucket charts side by side. Left, expected: mean forward return rises monotonically G1 to G5. Right, observed: G1 lifts above zero instead of being the most negative bucket, breaking the staircase — annotated 'reversal'" src="figures/reversal-buckets-light.png">
</picture>

**Reversal**: over short horizons extreme moves partially undo themselves, and it strengthens with
data frequency — at fine resolution prices zigzag rather than trend.

**The standard fix, and why not to copy it blindly.** AQR skips the most recent month, reasoning
that a trend must *form* before it is tradeable. The skip is real, but treating it as settled has
drawn pushback: reversal is a second source of return, not noise. **Momentum money and reversal
money are both money** — try to earn both.

**Make the skip empirical.** The fix is a `shift`, but its size is measured, not inherited — 1 day,
1 week, 1 month? Run the bucket chart at each and watch G1.

The whiteboard's other note, `risk-adjusted MOM → rolling quantile`, is the recipe for a broken
bucket chart: standardize (§6), then bucket by rolling quantile (§7).

## 6. Risk-adjusted momentum

Raw momentum is not comparable across time or assets. 2% monthly momentum in the 2021 inflation
regime is unremarkable; the same 2% in the 2023 rate-hike drawdown is strong. Same number, different
meaning — and 2% for SHY is not 2% for UNG.

Divide by volatility:

$$
MOM^{\text{risk-adj}}_t  =  \text{Avg}\left(\frac{r_{s,t-i}}{\sigma}\right),\qquad i = 1 \ldots N
$$

Every asset and period lands on one scale — approximately standard normal — so values compare. Two
students both score 80, but on different exams against different cohorts; without a common baseline
the two 80s are not the same achievement.

## 7. The bucketing trap, and the rolling-quantile fix

Bucketing the standardized signal on **fixed intervals** (−2 to +2 in equal steps) starves the tails:
a normal distribution puts almost everything in the middle, so the two buckets you actually trade
become the least reliable bars, and one event can swing them.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/signal-distribution-dark.png">
  <img alt="Two standard-normal density curves. Left, cut at fixed intervals of one sigma: the tail groups hold 11 and 12 observations while the central groups hold 1,290 each. Right, cut at rolling quantiles: every group holds 635" src="figures/signal-distribution-light.png">
</picture>

Ranking the **whole history** into equal groups is worse — it leaks the future, since whether today
counts as "high" would depend on next year's extremes. Clean-looking and meaningless.

**Correct: at each `t`, rank only against history strictly before `t`** — a **rolling quantile**,
expanding or fixed-window. Honest, and better balanced than fixed intervals, though not perfectly
equal and it discards some magnitude information.

No single view suffices; produce all three:

| View | Shows | Hides |
|---|---|---|
| Raw-value buckets | The signal at its natural scale | Not comparable across regimes or assets |
| Standardized buckets | Regime-neutral comparison | Sparse, unreliable tails |
| Rolling-quantile buckets | No look-ahead, balanced groups | Magnitude information |

A fourth angle: cross-sectional ranking — each asset against its peers that day rather than its own
past. That is the Portfolio 1 vs Portfolio 2 distinction in [03](03-from-signal-to-position.md).

## 8. Combining a slow and a fast horizon

One lookback forces a choice between stable and timely. Instead use a **fast momentum to time the
turns in a slow one** — MACD's structure, where a short EMA crossing a long one marks the entry
earlier.

**Ratio.** Conventionally about **2:1** (MACD's 26/12), but that is a starting point: find the pairing
by **grid search**, read as a **heat map**. A real edge is a contiguous warm region; one hot cell is
an artifact.

**Where it pays.** Best in **commodities** — supply-and-demand cycles drive long, persistent trends.
Equities second. **Bonds** weakest, being the most arbitraged, so deviations close fastest.

## 9. EWMA instead of a simple moving average

An SMA weights a price from 60 days ago exactly as much as yesterday's. To weight recent prices more:

```python
signal = returns.ewm(halflife=H).mean()
```

Tune the **half-life** — candidates are fractions of the lookback (1/2, 1/3, 1/5, 1/8). Grid-search them.

MACD's 9-day signal line is an **empirical solution** — a value that fit historical data, nothing
more. Every parameter here has that status, which is why they belong in
[06](06-overfitting-and-robustness.md) rather than being accepted on authority.

## 10. Volatility clustering, and smoothing the fast leg

Volatility arrives in clusters. A fast signal is exposed: short-lived noise flips it long/short, and
the churn eats the return in transaction costs before any edge is realized.

Fix: **smooth the fast signal** to filter the shortest cycles.

**Constraint:** the smoothing window must be **shorter than the signal's own period**. Smooth with a
long window and you have not denoised it — you have built another slow signal and lost the
timeliness the fast leg existed for.

## 11. Information availability

Everything above assumes the signal at `t` uses only data knowable at `t`. Look-ahead bias is born
here; the execution offsets in [04](04-understanding-backtesting.md) are the second line of defense
and cannot rescue a signal contaminated at construction. The rolling-quantile rule (§7) and the
train/validation/test split ([06](06-overfitting-and-robustness.md)) are the same discipline.

---

## Common pitfalls

- **Reading a scatter as evidence.** At 10–15% correlation it looks identical either way.
- **Judging a bucket chart by its best bar.** Monotonicity is the test.
- **Dropping the error bars.** The extreme buckets are where samples are thinnest.
- **Discarding a signal when buckets aren't monotone.** Check the source's assumptions first — a lifted G1 usually means reversal, not a dead signal.
- **Inheriting AQR's one-month skip untested.** Measure the right lag for your data.
- **Treating reversal as noise.** It is a second source of return.
- **Fixed-interval buckets on a standardized signal.** The tails you trade end up empty.
- **Ranking against the full history.** Pure look-ahead.
- **Comparing raw momentum across regimes or assets.** 2% in 2021 ≠ 2% in 2023; SHY ≠ UNG.
- **Smoothing a fast signal with a long window.** That converts it into a slow one.
- **Reading MACD's 26/12/9 as theory.** They are fitted values. So are yours.

## Open questions

- Which volatility estimate goes in the risk-adjustment denominator — trailing realized over the same lookback, longer, or slower? The lecture didn't pin it down.
- The right reversal skip for this 37-ETF universe, which may differ by asset class.
- How many buckets? With 37 assets, five leaves ~7 names per bucket per day.
- Rolling-quantile window length — too short is noisy, too long spans the regimes standardization was meant to separate.
- Does the bucket spread survive transaction costs? The chart prices the gross edge only.
- Would a volatility *forecast* filter noise better than trailing realized vol?

---

## Next → [03 · From Signal to Position](03-from-signal-to-position.md)

Before moving on, **build the 21-day momentum signal and plot its bucket chart three ways** — raw
values, standardized, and rolling quantile — then compare them. Chapter 03 assumes you have a signal
you already believe in.

You should be able to explain:

- [ ] Why a scatter plot proves nothing at a realistic 10–15% correlation
- [ ] Why the bottom bucket lifts, and how you would measure the right skip
- [ ] Why fixed-interval buckets starve the tails and full-history ranking leaks the future

[← 01](01-what-is-cta.md) · [Index](00-index.md) · reference: [07 · Toolbox](07-toolbox-pandas.md)
