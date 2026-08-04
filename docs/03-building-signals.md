# 03 · Building Your Own Signal

> **This chapter answers:** how to go from a market intuition to a signal you can compute, and how to tell whether it carries information before you ever run a backtest.
> **Prerequisites:** [02 · Data &amp; Corporate Actions](02-data-and-corporate-actions.md) — a signal built on bad data is worse than no signal.
> **After reading you can:** state a signal as a hypothesis, test it with a bucketed bar chart, normalize it so values compare across assets and time, and combine horizons without drowning in noise.

---

## 1. A signal is a hypothesis, not a formula

Start by writing down the claim you are making about the world. For momentum:

$$
\textbf{signal:}\quad MOM_t \;=\; \operatorname{Avg}\big(r_{s,\,t-i}\big),\qquad i = 1 \ldots N
$$

$$
\textbf{hypothesis:}\quad MOM \uparrow \;\Longrightarrow\; \text{return} \uparrow
\qquad\qquad
\textbf{consequence:}\quad MOM_t \;\propto\; w \;\propto\; \text{return}
$$

The third line is what makes it tradeable: if the hypothesis holds, the signal is not just
correlated with return, it tells you **how much** to allocate. Higher momentum → larger weight.
That proportionality is the bridge into [04 · From Signal to Position](04-from-signal-to-position.md).

Writing the hypothesis first matters because it tells you what would falsify it. A signal you
cannot falsify is not a signal — it is a plot you will rationalize either way.

## 2. Horizons travel — but check that they do

If a signal works at the yearly horizon, the working assumption is that it also works at
neighbouring horizons — monthly, quarterly — because a long trend is built out of shorter
fluctuations accumulating in the same direction. That is a reasonable prior, not a fact.

So when a horizon test comes back **without** the expected low-to-high monotone ordering, the
first move is not to discard the signal. Go back and re-read the assumptions in the paper you
took it from: what universe, what period, what skip, what weighting. Most "the signal doesn't
work" results are really "I implemented a different signal than the one that was tested."

## 3. Why the scatter plot disappoints

The instinct is to plot signal against forward return and look for a slope. Do it once, so you
know what it looks like, then stop relying on it.

A visible pattern in a scatter plot needs a correlation somewhere around 30% before the eye can
pick it out — closer to 40–50% to be convincing, and 80% to be obvious. **Real quantitative
signals run about 10–15%.** At that level the scatter is an undifferentiated cloud whether the
signal works or not. The absence of a visible trend is not evidence against the signal, which
makes the whole exercise uninformative.

The problem is not the signal. It is that a scatter plot spends all its resolution on individual
noisy observations instead of on the average behavior you actually care about.

## 4. The bucketed bar chart — the core method

Instead of looking at every point, average away the noise:

1. Sort all observations by signal value.
2. Split them into groups — G1 (lowest) through G5 (highest).
3. Compute the **mean forward return** of each group.
4. Plot those means as bars, **with error bars**.

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

**How to read it.** If the bars rise monotonically from G1 to G5, the signal carries information.
That monotonicity is the real test — not the size of any single bar. A signal that is strong in
G5 but scrambled across G1–G4 is usually a small-sample artifact, not an edge.

**It also prices the trade.** The chart tells you roughly what a long/short book earns: long the
top bucket, short the bottom, and the expected spread is the difference between those two bars.
If G5 averages +2% and G1 averages −1%, the long/short combination is worth about 3%.

**Why it beats the scatter.** Each bucket average is effectively a cross-sectional portfolio held
at every point in time, then averaged down the time axis. So the chart is answering "how often
does this signal get the ranking right?" rather than "can I see a line in this cloud?" — which is
the question that actually determines whether the strategy makes money.

The error bars are not decoration. They are what stops you from reading a 2-point bucket as a
result.

## 5. Reversal — why the lowest bucket misbehaves

*(from the whiteboard, 2026-07-05)*

When you first build the bucket chart on raw momentum you will often see the staircase break at
the **bottom** bucket: the biggest losers do not keep losing, they bounce.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/reversal-buckets-dark.png">
  <img alt="Two bucket charts side by side. Left, expected: mean forward return rises monotonically G1 to G5. Right, observed: G1 lifts above zero instead of being the most negative bucket, breaking the staircase — annotated 'reversal'" src="figures/reversal-buckets-light.png">
</picture>

This is **reversal**: over short horizons, extreme moves tend to partially undo themselves. It
shows up more strongly the higher the data frequency — at fine resolution prices zigzag rather
than trend.

**The standard fix, and why not to copy it blindly.** The AQR convention is to skip the most
recent month when computing momentum, on the reasoning that a trend must first *form* before it
is tradeable. That skip is a real effect, but treating it as settled has drawn plenty of pushback
— reversal is not noise to be discarded, it is a second source of return. **Momentum money and
reversal money are both money.** The reasonable position is that you should try to earn both.

**Make the skip an empirical question.** The fix is a `shift` on the signal, but the size of the
shift is yours to determine by experiment, not to inherit from a paper:

```text
shift = 1 day?   1 week?   1 month?
```

Run the bucket chart at each and look at what happens to G1. The right shift is the one your data
supports, on your universe, over your sample.

**The whiteboard's other note — `risk-adjusted MOM → rolling quantile`.** The two techniques in
§6 and §7 below are the direct answer to a broken bucket chart: standardize the signal so values
are comparable, then bucket it by rolling historical quantile rather than by raw value.

## 6. Risk-adjusted momentum

Raw momentum values are not comparable across time or across assets.

Two percent of monthly momentum in the high-inflation regime of 2021 is unremarkable — everything
was moving. The same two percent during the 2023 rate-hike drawdown is a genuinely strong reading.
The number is identical; its meaning is not. The same problem holds across assets: 2% means
something very different for SHY than for UNG.

The fix is to divide by volatility:

$$
MOM^{\text{risk-adj}}_t \;=\; \operatorname{Avg}\!\left(\frac{r_{s,\,t-i}}{\sigma}\right),\qquad i = 1 \ldots N
$$

This puts every asset and every period on a common scale — approximately a standard normal
distribution — so the values can finally be compared side by side. The analogy from the lecture:
two students both score 80, but on different exams against different cohorts. Without a common
baseline the two 80s are not the same achievement.

## 7. The bucketing trap, and the rolling-quantile fix

Once the signal is standardized, the obvious move is to bucket it on fixed intervals — say −2 to
+2 in equal steps. **Don't.** A normal distribution puts almost everything in the middle, so the
tail buckets end up with a handful of observations while the central buckets hold thousands. The
two buckets you care about most — the extremes, the ones you would actually trade — become the
least reliable bars on the chart, and a single event can swing them.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/signal-distribution-dark.png">
  <img alt="Two standard-normal density curves. Left, cut at fixed intervals of one sigma: the tail groups hold 11 and 12 observations while the central groups hold 1,290 each. Right, cut at rolling quantiles: every group holds 635" src="figures/signal-distribution-light.png">
</picture>

The obvious fix is to rank the entire history and cut it into equal-sized groups. **That is
worse**, because it leaks the future. Whether today's signal counts as "high" would depend on
whether a more extreme value shows up next year. The chart would look clean and be meaningless.

**The correct method: at each time `t`, rank the signal only against the history available
strictly before `t`** — a **rolling quantile**, expanding or fixed-window. This keeps the
comparison honest and still gives more balanced group sizes than fixed normal intervals — though
not perfectly equal ones, and it does discard some of the information carried by the raw
magnitudes.

So no single view is sufficient. Produce all three and cross-check:

| View                     | What it shows                   | What it hides                           |
| ------------------------ | ------------------------------- | --------------------------------------- |
| Raw-value buckets        | The signal at its natural scale | Not comparable across regimes or assets |
| Standardized buckets     | Regime-neutral comparison       | Sparse, unreliable tails                |
| Rolling-quantile buckets | No look-ahead, balanced groups  | Loses magnitude information             |

A cross-sectional ranking — each asset against its peers on the same day, rather than against its
own past — is a fourth angle worth adding. That is exactly the difference between Portfolio 1 and
Portfolio 2 in [04](04-from-signal-to-position.md).

## 8. Combining a slow and a fast horizon

A single lookback forces one choice: slow enough to be stable, or fast enough to be timely. You
do not have to choose. Use a **fast momentum to time the turns in a slow momentum** — the same
structure as MACD, where a short EMA crossing a long EMA marks the entry earlier than the long
one alone would.

**On the ratio.** The conventional slow:fast ratio is roughly **2:1** — MACD's 26 and 12 are the
familiar instance. Treat that as a starting point, not an answer: find the actual pairing with a
**grid search** over both lookbacks and read the result as a **heat map**. A real edge shows up
as a contiguous warm region; a single hot cell surrounded by cold ones is an artifact.

**Where it works best.** This structure pays off most in **commodities**, where big supply-and-
demand cycles drive long, persistent trends. Equities are second. Bonds are weakest — they are
the most heavily arbitraged, so deviations get closed fastest.

## 9. EWMA instead of a simple moving average

A simple moving average weights a price from 60 days ago exactly as much as yesterday's. If you
want the signal to respond to recent prices more than distant ones, use an **exponentially
weighted moving average** instead.

```python
signal = returns.ewm(halflife=H).mean()
```

The parameter to tune is the **half-life** — how long until a observation's weight has decayed by
half. Candidate values are naturally expressed as fractions of the lookback: 1/2, 1/3, 1/5, 1/8.
Grid-search them.

Note what MACD's own "9-day signal line" is: an **empirical solution** — a value that happened to
work on historical data, and nothing more. That is the honest status of every parameter here.
Something that fit the past carries no guarantee about the future, which is why these choices
belong in [07 · Overfitting &amp; Robustness](07-overfitting-and-robustness.md) rather than being
accepted on authority.

## 10. Volatility clustering, and smoothing the fast leg

Volatility arrives in clusters — quiet stretches and violent stretches, not an even sprinkling.
A fast momentum signal is especially exposed to this: a burst of short-lived noise flips it back
and forth between long and short, and the resulting churn eats the return in transaction costs
before any edge is realized.

The fix is to **smooth the fast signal**, filtering out the shortest cycles.

**The constraint that makes this work:** the smoothing window must be **shorter than the period of
the underlying signal**. Smooth a fast signal with a long window and you have not filtered it —
you have simply built another slow momentum signal, and lost the timeliness that was the whole
reason for having a fast leg.

## 11. Information availability

Everything above assumes the signal at time `t` uses only data knowable at `t`. This is where
look-ahead bias is actually born — the execution offsets in
[05 · Understanding Backtesting](05-understanding-backtesting.md) are only the second line of
defense, and they cannot rescue a signal that was contaminated at construction time.

The rolling-quantile rule in §7 is one instance of this discipline. The train/validation/test
split in [07 · Overfitting &amp; Robustness](07-overfitting-and-robustness.md) is another.

---

## Common pitfalls

- **Reading a scatter plot as evidence.** At a realistic 10–15% correlation, a scatter plot looks the same whether the signal works or not. Absence of a visible trend proves nothing.
- **Judging a bucket chart by its best bar.** Monotonicity across all buckets is the test. A tall G5 with noise elsewhere is usually small-sample luck.
- **Dropping the error bars.** Without them you cannot tell a 2-observation bucket from a 2,000-observation one, and the extreme buckets are exactly where samples are thinnest.
- **Discarding a signal the moment the buckets are not monotone.** Re-check the assumptions of the source first — universe, period, skip, weighting. A non-monotone G1 usually means reversal, not a dead signal.
- **Inheriting AQR's one-month skip without testing it.** The skip is a real effect, but the right lag for your data might be a day or a week. Make it a parameter you measure.
- **Treating reversal as noise to be filtered away.** It is a second source of return, not a defect in momentum.
- **Bucketing a standardized signal on fixed intervals.** The tails — the part you trade — end up with almost no data.
- **Ranking against the full history.** Clean-looking, and pure look-ahead: "is this value high?" must not depend on data from the future.
- **Comparing raw momentum across regimes or assets.** 2% in 2021 and 2% in 2023 are not the same signal, and 2% for SHY is not 2% for UNG.
- **Smoothing a fast signal with a long window.** That does not denoise it — it converts it into a slow signal and throws away the timeliness you built it for.
- **Reading MACD's 26/12/9 as theory.** Those are empirical values fitted to past data. So are yours.

## Open questions

- Which volatility estimate belongs in the denominator of the risk adjustment — trailing realized over the same lookback, a longer window, or something slower? The choice changes the signal, and the lecture did not pin it down.
- What is the right reversal skip on this 37-ETF universe — a day, a week, a month? It has to be measured, and the answer may differ by asset class.
- How many buckets? Five is conventional, but with 37 assets a single day only fills each bucket with ~7 names. Does the choice change the monotonicity conclusion?
- How long should the rolling-quantile window be? Too short and the ranking is noisy; too long and it spans regimes the standardization was meant to separate.
- Does the bucket spread survive the transaction costs implied by trading it? The chart prices the gross edge only.
- Can a volatility *forecast* (rather than trailing realized vol) filter the noise better and lift the combined portfolio? That is the direction the next session points to.
