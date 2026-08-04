# Lecture 01 · Momentum, Validation, and the Bucket Chart

> **Source:** Zoom recording "20260705 量化小班课" · 主讲 Andy · ~58 min
> **Standalone class summary.** This file records what the session covered, in the order it
> was covered. The concepts are developed properly in the numbered chapters — see the map below.

| Topic here | Developed in |
|---|---|
| Stock split / phantom returns | [02 · Data & Corporate Actions](02-data-and-corporate-actions.md) |
| Train / validation / test, no random splits | [07 · Overfitting & Robustness](07-overfitting-and-robustness.md) §§ 1–2 |
| Momentum definition, scatter, bucket chart, risk adjustment, rolling rank | [03 · Building Your Own Signal](03-building-signals.md) §§ 1, 3, 4, 6, 7 |
| Weekly 1/5 rolling positions | [04 · From Signal to Position](04-from-signal-to-position.md) |
| `SettingWithCopyWarning` | [08 · Toolbox: pandas](08-toolbox-pandas.md) |

---

## 1. Last assignment's data problem: phantom jumps from stock splits

Several students' submissions contained single-day moves of more than 70% on some tickers.

- For normal ETFs and commodity funds, a one-day move rarely exceeds 50–60% (a LUNA-style collapse
  aside). **Anything past 10% deserves a re-check.**
- Root cause: **USO and UNG had stock splits** (1 share → 8), and the raw vendor data was
  unadjusted, so the split date carried an artificial jump.
- Andy posted replacement **aggregated, back-adjusted** files to the group — drop in the new ones
  and delete the old.

> **Editor's note.** The adjusted files were installed on 2026-07-31. The measured ratios differ
> between the two: USO is 1-for-8 (2020-04-29), UNG is 1-for-4 (2024-01-24). The dataset also
> contains a split the session did not mention — XLB / XLE / XLK / XLU / XLY had a 2-for-1 forward
> split on 2025-12-05 and are **still unadjusted**. Evidence in
> [02 § 1.1](02-data-and-corporate-actions.md).

## 2. The three-stage research workflow

| Stage | The question it answers |
|---|---|
| **Train** | Does the hypothesis hold at all? What is the shape of the signal → return relationship — linear, non-linear, or only present in the extremes? |
| **Validation** | Among several candidate signal combinations, which one is best? |
| **Test** | Does the choice made in validation actually generalize? |

Validation exists specifically to avoid picking a strategy by hindsight on the training data
("事后诸葛亮"). Choose the winner and measure it on the same data you chose it from, and you have
measured your own selection, not the strategy.

## 3. Never split a time series randomly

Standard machine learning shuffles rows before splitting. **For financial time series this is
wrong**, and for momentum it is fatal.

The reason is **autocorrelation in the signal itself**: a one-month momentum computed today and
one computed yesterday share almost all of their underlying daily returns — the windows overlap by
20 of 21 days. Today and yesterday are not independent observations. Scatter them randomly across
train and test and the test set is full of near-duplicates of training rows, so the model looks
like it generalizes when it has only memorized. That is forward-looking bias in a subtle form: no
single row contains future data, but the *split* does.

The split used for this course's dataset:

| Segment | Period |
|---|---|
| Training | everything before 2024-06 |
| Validation | 2024-06 → 2025-06 |
| Test | 2025-06 → 2026-06 |
| *(full range)* | *2020-01 → 2026-06* |

In pandas this is just time indexing — `df.loc[:"2024-06"]` and so on.

## 4. Defining and testing the momentum signal

### 4.1 Definition and hypothesis

$$
MOM_t \;=\; \operatorname{Avg}\big(r_{s,\,t-i}\big),\qquad i = 1 \ldots N
$$

$$
\textbf{hypothesis:}\quad MOM \uparrow \;\Longrightarrow\; \text{return} \uparrow
\qquad\qquad
MOM_t \;\propto\; \text{weights} \;\propto\; \text{return}
$$

The proportionality is what makes it tradeable: higher momentum should mean a larger position.

### 4.2 Test one — the scatter plot (limited value)

Plotting signal against return is the obvious first step, but a real signal's correlation with
return is only about **10–15%**, and at that level the eye cannot pick a trend out of the cloud.
A scatter needs roughly 30% before a shape is visible, 40–50% to convince, 80% to be obvious —
levels a real quantitative signal rarely reaches. So the absence of a visible trend proves nothing.

### 4.3 Test two — the bucketed bar chart *(the key method of the session)*

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/bucket-chart-dark.png">
  <img alt="Bucketed bar chart: mean forward return rises monotonically from bucket G1 to G5, with error bars, and the G5 minus G1 spread annotated as the long/short edge" src="figures/bucket-chart-light.png">
</picture>

**The reasoning.** If signal and return were perfectly linearly related, then drawing a few points
at random and sorting them should produce a low-to-high monotone ordering.

**The method.** Sort all samples by signal value, cut them into groups (G1–G5, low to high),
compute each group's mean return, and plot with **error bars**.

**Reading it.** A monotone rise from G1 to G5 means the signal carries information. The chart also
prices the trade directly: long the top group, short the bottom, and the expected spread is the
difference between the two bars — if G5 is +2% and G1 is −1%, the long/short book is worth roughly
3%.

Another way to see it: each bar is a cross-sectional portfolio held at every point in time, then
averaged down the time axis. That reflects **how often the strategy is right at each moment**,
which a pile of scattered points does not.

### 4.4 Test three — risk-adjusted momentum (standardization)

**The problem.** Raw momentum is not comparable across periods or assets. 2% of momentum in the
high-inflation regime of 2021 is unremarkable; the same 2% during the 2023 rate-hike drawdown is
strong. The number is identical, the meaning is not.

**The fix.** Divide by volatility:

$$
MOM^{\text{risk-adj}}_t \;=\; \operatorname{Avg}\!\left(\frac{r_{s,\,t-i}}{\sigma}\right),\qquad i = 1 \ldots N
$$

This pulls every asset and period onto one scale — approximately a standard normal — so values can
finally be compared. The analogy: two students both score 80, but on different exams against
different cohorts. Without a common baseline the two 80s are not the same achievement.

### 4.5 The bucketing problem, and the rolling-history fix

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/signal-distribution-dark.png">
  <img alt="Two standard-normal density curves. Left, cut at fixed one-sigma intervals: the tail groups hold 11 and 12 observations while the central groups hold 1,290 each. Right, cut at rolling quantiles: every group holds 635" src="figures/signal-distribution-light.png">
</picture>

- **Fixed intervals fail.** Cutting a roughly normal signal at fixed steps (say −2 to +2) leaves
  the extreme groups with a handful of points while the middle holds thousands. The two bars you
  care about most become the least trustworthy, and one event can swing them.
- **Ranking the whole history fails worse.** It leaks the future: whether today's value counts as
  "high" would depend on whether something more extreme shows up next year.
- **The correct method:** at each time `t`, compare and rank only against the window of history
  *before* `t`. No look-ahead, and more balanced group sizes than fixed intervals — though not
  perfectly equal, and it does discard some of the information in the raw magnitudes.

**Recommendation:** produce all three views — raw-value buckets, standardized buckets,
rolling-rank buckets — and cross-check them. A cross-sectional ranking (each asset against its
peers on the same day) is a fourth useful angle.

## 5. Improving the assignment: the weekday effect and wasted signals

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/overlap-tranches-dark.png">
  <img alt="Gantt chart of five tranches, each 20% of the book, each held five trading days and each starting one day after the previous — so entry is spread across every weekday and all five are simultaneously live" src="figures/overlap-tranches-light.png">
</picture>

Rebalancing only on Mondays and holding to the next Monday has two problems:

1. **It throws signals away** — Tuesday through Friday each produce a fresh signal that is computed
   and discarded.
2. **It inherits the weekday effect.** Under weak-form efficiency, day-of-week effects persist:
   many funds close positions on Friday and re-establish on Monday to avoid weekend gap risk, which
   systematically lifts Monday returns and depresses Friday's. A strategy that always trades on one
   weekday absorbs that bias, and you cannot separate it from your signal's edge.

**The solution on the board:** split the book into five parts and open one on each trading day,
each held a week, rolling. Monday commits 20%, Tuesday another 20%, and so on; by the following
Monday the first tranche matures and rolls back in. Five tranches of 1/5 are live at any moment,
which both spreads the weekday bias and uses every day's signal.

## 6. Patrick's question — `SettingWithCopyWarning`

- **What happens:** with chained indexing (filter a subset, then assign into it), pandas cannot
  tell whether you meant to modify a view or a temporary copy, so it warns — and the write may not
  reach the original frame at all.
- **The right form:** address rows and columns in a single `.loc` call — `df.loc[cond, col] = val`.
- **Why it matters:** for throwaway backtest code it rarely bites, but once code is reused by
  others, a flood of meaningless warnings buries the one that mattered. Keep the output clean.
- Andy noted Patrick's assignment was well done overall.
