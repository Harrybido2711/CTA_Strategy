# 03 · Shaping the Lookback

> - **Answers:** how long a lookback to use, how to weight the returns inside it, and what MACD is once the chart-package vocabulary is stripped away.
> - **Prerequisites:** [02 · Testing a Signal](02-testing-a-signal.md) — every section here hands you a knob, and 02's bar plot is the only gauge that reads one.
> - **After reading:** pair a fast horizon with a slow one, replace a boxcar average with an EWMA, read MACD as a weighted sum of past returns, and say why the fast leg has to be smoothed.

---

[02](02-testing-a-signal.md) left two blanks inside its own definition. Writing momentum as
$\text{Avg}(r_{s,t-i})$, $i = 1 \ldots N$ fixes neither the length of the window nor the weight each
return carries inside it — the average is a boxcar only because nobody said otherwise. This chapter
is about both blanks, and about MACD, which turns out to be the same object with the second one
filled in differently.

Every answer below is a **parameter**, and no parameter here is settled by convention. MACD's
26/12/9 fit somebody's historical data once; the fast/slow ratio and the half-life are grid-searched.
What settles them is 02's bar plot, which is why that chapter comes first.

## 1. Combining a slow and a fast horizon

One lookback forces a choice between stable and timely. A long window rides a trend without being
shaken out of it but arrives late at both ends; a short one turns on time, and turns on noise too.
Rather than choose, carry both and let the **fast window time the turns of the slow one**.

Each rule is still the sign of its own momentum, so each fires when its own line crosses zero. Draw
the two over the same price path and the short window crosses first at both ends — that gap, and
nothing else, is what the combination trades on.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/fast-times-slow-dark.png">
  <img alt="Two stacked panels sharing a trading-day axis. The upper panel plots price rebased to 100 over one path that falls, turns and rolls over, with a 20-day and a 40-day moving average drawn over it, and two horizontal bars underneath showing how long each rule holds. The lower panel plots the momentum each window produces against zero: the 20-day line crosses zero upward 10 days before the 40-day line does, and crosses back down 14 days before it, so the fast rule enters and exits earlier at both ends" src="figures/fast-times-slow-light.png">
</picture>

**What the early signal means.** A fast momentum turning up while the slow one is still negative is
not only an arithmetic consequence of the shorter window. It is the first evidence that flow has
changed direction — that whoever was selling has stopped, or something large has started buying —
while the move is still too small to register over a quarter. The same reading runs the other way
and matters more there: a fast leg rolling over while the slow one is still positive is what a large
holder beginning to leave looks like from outside. Waiting for the slow window to agree means
selling to them on the way out.

**Ratio.** The pairing is found by experiment, not chosen. Put the slow lookback $N_s$ on one axis
and the fast one $N_f$ on the other, run [02](02-testing-a-signal.md)'s bar-plot test in every cell,
and read the grid as a heat map.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/ratio-grid-dark.png">
  <img alt="A five-by-five grid with a geometric ladder of lookbacks — one day, one week, two weeks, one month, one quarter — on both axes: fast lookback across, slow lookback up. Every cell on and above the diagonal is greyed out and struck through, labelled the fast leg must be the shorter one. The remaining cells are shaded, and the darkest run in a diagonal band: two weeks against one week, one month against two weeks, and one quarter against one month. The first two are outlined and annotated approximately two to one" src="figures/ratio-grid-light.png">
</picture>

Two things are true of that grid before any data is collected. **Half of it is empty by
construction** — $N_f < N_s$ or there is no fast leg, so everything on and above the diagonal is
struck out. And the candidates should be spaced **geometrically** rather than evenly: a day, a week,
two weeks, a month, a quarter. Even spacing spends most of the grid on pairs that differ by a
rounding error.

**What a diagonal band means.** The warm cells run diagonally, and that shape is the finding rather
than any single cell in it. On a geometric ladder a diagonal is a constant **ratio**, so what
carries is $N_s / N_f$ and not either window on its own — which is why the answer is quoted as a
ratio at all. Research lands it near **2:1**, and MACD's 26/12 is one instance; for daily-to-weekly
holding the band shows up around two weeks against a month. An empirical regularity, not a law, and
[07](07-overfitting-and-robustness.md)'s subject the moment you start trusting it.

**Note (One hot cell is not a band).** A single dark square with pale neighbours is an artifact of
however many parameter combinations were tried, not an edge. What earns belief is a contiguous
warm region, because a real effect cannot switch off between one week and eight days.

**Where it pays.** Best in **commodities**, and the reason is what moves them. An equity price
answers to earnings, to the firm's own performance, to whoever is running it — many small
idiosyncratic forces, none of which trend for long. A commodity answers to global energy supply,
shipping, and whether the large participants are in the market at all, and it is far too large for
one fund to push on its own, so a move that starts tends to be everyone moving together. Equities
second. **Bonds** weakest: lean on one hard enough and someone takes the other side and presses it
back.

## 2. EWMA instead of a simple moving average

An SMA weights a price from 60 days ago exactly as much as yesterday's. To weight recent prices more:

```python
signal = returns.ewm(halflife=H).mean()
```

Tune the **half-life** $H$ — the lag at which a return's weight has decayed to half the weight given
to the newest one. Candidates are fractions of the lookback (1/2, 1/3, 1/5, 1/8). Grid-search them.

MACD's 9-day signal line is an **empirical solution** — a value that fit historical data, nothing
more. Every parameter here has that status, which is [07](07-overfitting-and-robustness.md)'s
subject rather than something to accept on authority.

## 3. MACD, stated precisely

Written out, MACD is three series built from two exponential moving averages of the **price**.

**Definition (MACD).** For a fast and a slow span $n_f < n_s$, each with its own smoothing constant
$\alpha = 2/(\text{span}+1)$:

$$
\text{MACD}_t = \text{EMA}_{n_f}(P)_t - \text{EMA}_{n_s}(P)_t , \qquad
\text{signal}_t = \text{EMA}_9(\text{MACD})_t , \qquad
\text{hist}_t = \text{MACD}_t - \text{signal}_t
$$

where $P_t$ is the price on date $t$ and $\text{EMA}_n(P)_t$ its exponential moving average over
span $n$. The asset subscript is dropped throughout — MACD is computed one asset at a time.
Conventionally $n_f = 12$, $n_s = 26$, and 9 for the signal line.

| Series                | Reads as                                 | Sign means                 |
| --------------------- | ---------------------------------------- | -------------------------- |
| **MACD line**   | recent average price versus a longer one | trend direction            |
| **Signal line** | a smoothed MACD                          | the level MACD is crossing |
| **Histogram**   | MACD minus its own smoothing             | trend acceleration         |

**Claim.** MACD is a momentum signal. It is a weighted sum of past returns, differing from a
lookback mean only in the shape of the weights.

<details>
<summary><b>Proof.</b> the two EMAs' weights cancel to a zero-sum kernel on one-period changes, hump-shaped rather than flat</summary>

Each EMA is a weighted average of past prices whose weights sum to one, so their
difference weights the price $i$ days ago by $c_i$, and those weights sum to **zero**:

$$
\text{MACD}_t = \sum_i c_i P_{t-i} , \qquad
c_i = \alpha_f (1-\alpha_f)^i - \alpha_s (1-\alpha_s)^i , \qquad \sum_i c_i = 0 .
$$

A zero-sum weighting is unchanged when every price shifts by a constant, so subtract $P_t$ from each
term and write $P_t - P_{t-i}$ as a sum of one-period changes
$\Delta_{t-j} = P_{t-j} - P_{t-j-1}$. Collecting the coefficient of the change at lag $j$ gives the
**kernel** $k_j$:

$$
\text{MACD}_t = \sum_j k_j \Delta_{t-j} , \qquad
k_j = \sum_{i \leq j} c_i = (1-\alpha_s)^{j+1} - (1-\alpha_f)^{j+1} .
$$

Since $\alpha_f > \alpha_s$, every $k_j \geq 0$: MACD is a non-negative weighted sum of past price
changes, exactly like a lookback mean.

</details>

**Note (What actually differs).** The kernel. A 21-day momentum weights the last 21 returns
equally and everything older at zero; MACD's weights rise from a small value at lag 0, peak around
lag 8, and decay without ever reaching zero. It therefore discounts *yesterday* relative to last
week — deliberately, since the newest return is the noisiest — and never fully forgets.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/signal-kernels-dark.png">
  <img alt="Weight given to each past daily return, against lag in trading days, for two signals normalised to the same total. A 21-day momentum is a flat box: equal weight for the last 21 days and zero beyond. MACD with spans 12 and 26 is a hump that starts low at lag zero, peaks around lag 8, then decays slowly and never reaches zero within sixty days" src="figures/signal-kernels-light.png">
</picture>

Three common rules, in increasing order of information kept. All
three still have to pass [02 § 3.2](02-testing-a-signal.md)'s bar plot before they earn a
backtest.

| Rule         | Go long when                            | Costs                                                            |
| ------------ | --------------------------------------- | ---------------------------------------------------------------- |
| Zero-line    | MACD is above zero                      | a slow trend filter, late                                        |
| Crossover    | the histogram is above zero             | earlier, noisier — the churn is § 4's subject                  |
| Proportional | always, sized by the standardized value | none of the magnitude, but see[04](04-from-signal-to-position.md) |

## 4. Volatility clustering, and smoothing the fast leg

Volatility arrives in clusters, and a fast signal is exposed: short-lived noise flips it
long/short, and the churn eats the return in transaction costs before any edge is realized. Fix:
**smooth the fast signal** to filter the shortest cycles.

**Constraint:** the smoothing window must be **shorter than the signal's own period**. Smooth with a
long one and you have not denoised the signal — you have built another slow one and lost the
timeliness the fast leg existed for.

## Appendix · Notation

Throughout, $t$ is the date. Everything in this chapter is computed one asset at a time, so the
asset subscript $s$ of [02](02-testing-a-signal.md) is dropped.

| Symbol | Means | First used |
| --- | --- | --- |
| $N_f$, $N_s$ | fast and slow lookback lengths, in periods | § 1 |
| $H$ | EWMA half-life, in periods | § 2 |
| $P_t$, $\Delta_{t-j}$ | price on that date, and the one-period change at that lag | § 3 |
| $n_f$, $n_s$ | fast and slow EMA spans, conventionally 12 and 26 | § 3 |
| $\alpha_f$, $\alpha_s$ | their smoothing constants, two over span plus one | § 3 |
| $c_i$, $k_j$ | MACD's net weight on the price at that lag, and its kernel weight on the price change | § 3 |

**Note (Collisions to watch).** $N_f, N_s$ are plain lookback lengths and $n_f, n_s$ are the EMA
spans that play the same two roles — case is the tell. $k_j$ is a kernel weight, not a portfolio weight — [02](02-testing-a-signal.md)
reserves $w_{s,t}$ for the latter, which is why the kernel is not written $w$. And $\alpha$ here is a
smoothing constant, not [02 § 3.1](02-testing-a-signal.md)'s `alpha` plotting keyword and not a
regression intercept; code font against maths is the tell.

---

## Next → [04 · From Signal to Position](04-from-signal-to-position.md)

Before moving on, **plot the kernel of your own signal** — the weight it places on the return at
each lag — beside a boxcar of the same total. If you cannot draw it, you do not yet know what your
signal is averaging.

You should be able to explain:

- [ ] Why a fast leg times the turns of a slow one, and why the ratio is grid-searched rather than assumed
- [ ] What a half-life is, and why an EWMA never fully forgets
- [ ] Why MACD is momentum with a hump-shaped kernel rather than a separate indicator
- [ ] Why the smoothing window must be shorter than the fast signal's own period

[← 02](02-testing-a-signal.md) · [Index](00-index.md) · reference: [08 · Toolbox](08-toolbox-pandas.md)
