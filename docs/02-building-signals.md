# 02 · Building Your Own Signal

> - **Answers:** how to turn an intuition into a computable signal, and how to tell whether it carries information before backtesting it.
> - **Prerequisites:** [01 · What Is a CTA Strategy](01-what-is-cta.md); the data it runs on is [100 · The Dataset](100-dataset.md).
> - **After reading:** state a signal as a hypothesis, test it with a bucket chart, normalize it, and combine horizons without drowning in noise.

---

## 1. A signal is a hypothesis, not a formula

### The simplest signal — the sign of the last return

**Definition (Binary momentum).** The simplest member of the family — carry the sign of last
period's return, and nothing else:

$$
MOM_{s,t}  =  \text{sign}\left( r_{s,t-1} \right)
$$

where $s$ indexes the asset and $t$ the date, $r_{s,t-1}$ is that asset's return over the period
just ended, and $MOM_{s,t}$ the signal it produces for today — either +1 (long) or −1 (short), with
nothing in between.

### Why the sign alone is not enough

Two assets that rose 20% and 10% over the same window produce the *same* signal, so a book built on
it holds them in the same size. Trend **strength** is thrown away; only trend **direction**
survives.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/binary-momentum-dark.png">
  <img alt="Left panel: two price paths rebased to 100 over one lookback window, the darker one climbing to 120 and the lighter one to 110. Right panel: the momentum signal each path produces, two bars of identical height at plus one, joined by an arrow labelled identical" src="figures/binary-momentum-light.png">
</picture>

### What to keep instead

Neither repair below is obviously right, and both are tested the same way — § 4's bucket chart.

- **Keep the value, not the sign** — the definition below, which stays proportional to how strongly
  the asset trended.
- **Make the value comparable first** — divide by volatility, so a 20% move in a quiet market
  outranks a 20% move in a violent one (§ 6).

**Definition (Momentum).** Averaging over $N$ periods rather than one, and keeping the value rather
than its sign:

$$
\textbf{signal:}\quad MOM_{s,t}  =  \text{Avg}\left(r_{s,t-i}\right),\qquad i = 1 \ldots N
$$

with $N$ the lookback length and $i$ the lag inside it — the average runs over the $N$ returns
ending yesterday.

$$
\textbf{hypothesis:}\quad MOM \uparrow  \Longrightarrow  \text{return} \uparrow
\qquad\qquad
\textbf{consequence:}\quad MOM_{s,t}  \propto  w_{s,t}  \propto  \text{return}
$$

Here $w_{s,t}$ is the **weight** — the position size given to asset $s$ on date $t$. That third
line is what makes the signal tradeable: it doesn't merely correlate with return, it says **how
much** to allocate; how far the magnitude reaches the position is
[03](03-from-signal-to-position.md)'s decision.

Write the hypothesis first: it names what would falsify the signal, and one you cannot falsify is a
plot you will rationalize either way.

## 2. What you hoped for, and what you get

### The plot everyone draws first

§ 1's hypothesis says forward return rises with the signal, so the first move is to plot one against
the other. The picture you had in mind is the leftmost panel below. What comes back — for well over
99% of the scatters you will ever draw — is the rightmost.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/scatter-ladder-dark.png">
  <img alt="Four scatter panels of forward return against a signal, the same 1,500 points redrawn at correlations of 80, 45, 30 and 12 percent. The 80 percent panel, labelled what you pictured, is a clear diagonal band; by 30 percent, labelled the eye's floor, the tilt is barely arguable; the 12 percent panel, underlined and labelled what you observe, is a formless round cloud" src="figures/scatter-ladder-light.png">
</picture>

### Why the real one is a cloud

**Claim.** The scatter can neither confirm nor refute a signal, because the correlation a working
signal carries sits below the threshold at which the eye resolves a trend.

**Proof.** Both numbers are readable off the panels above: the eye stops resolving a tilt somewhere
around 30%, and a working signal carries 10–15%. Since 15% < 30%, a signal that works and a signal
that does not produce the same picture — **the absence of a visible trend is not evidence of
anything.**

So why is the correlation only 10–15%? Because the quantity being plotted is mostly not the signal.

**Claim.** Split the forward return into the part the signal reaches and the part it does not,
$y = \beta x + \epsilon$. If $\epsilon$ is uncorrelated with $x$, the signal owns exactly
$\rho^2$ of the return's variance, where $\rho$ is their correlation.

**Proof.** Uncorrelated components add their variances,

$$
\text{Var}(y) = \beta^2 \text{Var}(x) + \text{Var}(\epsilon)
$$

and on one regressor with an intercept the explained share is $R^2 = \rho^2$. At $\rho = 0.12$,
$R^2 = 0.0144$ — which does not mean "right 1.4% of the time", but: of the variation in forward
return from one observation to the next, 1.44% is linear in the signal and 98.56% is not.

**Example.** With a daily return standard deviation of $\sigma_y = 0.012$ — 120 bp, typical for an
equity ETF, a **basis point** being 0.01%:

| Component             | Size                            | At 12% correlation |
| --------------------- | ------------------------------- | ------------------ |
| Total return          | $\sigma_y$                    | 120 bp             |
| What the signal moves | $\rho \sigma_y$               | **14.4 bp**  |
| What it does not      | $\sigma_y (1 - \rho^2)^{1/2}$ | **119 bp**   |

Across an x-axis running from $-2\sigma_x$ to $+2\sigma_x$ the trend line climbs about 58 bp end
to end, while at every $x$ the points scatter over roughly 476 bp. **A 0.6% slope inside a 4.8%
cloud** — that ratio *is* the picture.

**Note (And it is worse than that).** Part of those 119 bp is not the market's doing: pooling UNG
with SHY, and 2021 with 2023, adds spread that standardization (§ 6) removes. Nor is a larger
$\rho$ on offer — a predictor correlating 50% with next month's return would be arbitraged away
long before you found it in 37 liquid ETFs. 10–15% is a competitive market's ceiling, not a
shortfall in craft.

## 3. Two ways out of the cloud

The scatter is unreadable, but the signal may still be in it. There are two things to try, and only
the second one works.

### 3.1 Turn down `alpha`

`alpha` is a marker's opacity. At `alpha=0.01` a single point is invisible and only *overlap*
renders, so the chart becomes a density map instead of a mass of ink — below, the left panel is the
before and the other two are both the after.

**Note (Not the other alphas).** matplotlib's opacity keyword: not a regression intercept, not the
excess return a manager is paid for, not § 10's smoothing constant $\alpha$. Code font is the tell.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/alpha-opacity-dark.png">
  <img alt="Three scatter panels of forward return against a signal. Left, at full opacity, 55,000 points render as one solid disc with no internal structure. Middle, the same rendering at alpha 0.01 on a book where a high signal rules out deep losses: a soft density cloud with the bottom-right corner visibly bitten out, annotated high signal, no deep loss. Right, alpha 0.01 on the original points: a smooth round density with no thin region anywhere" src="figures/alpha-opacity-light.png">
</picture>

Sometimes it is enough — the middle panel, where high signal against a badly negative return has
thinned enough to read. A signal that only rules something *out* is still tradeable.

**Why it usually fails.** Three reasons that compound:

- **The density comes back smooth.** 55,000 asset-dates average into a clean bivariate blob, and
  opacity renders that faithfully. A smooth density has no feature.
- **The tilt is finer than the ink.** § 2's band is eight times taller than the trend line's whole
  rise, so the lean is smaller than the markers drawn over it.
- **It treats the symptom.** The scatter spends its resolution on individual noisy points when the
  claim is about their **average**; no rendering choice changes what is being rendered.

**Note (Look first anyway).** Always draw it. On the rare occasion something *is* readable — a
curve, an empty corner — it beats every statistic, because it gives the *shape*. The mistake is
concluding anything **from** a cloud.

### 3.2 Sort, then average

**The construction.** Six steps. Only the last one produces anything worth looking at.

1. **Draw** five observations at random — one observation being one asset on one date.
2. **Rank** those five by signal value, highest to lowest.
3. **Assign** them to slots: highest signal into G5, next into G4, down to G1.
4. **Record** the forward return each one went on to deliver, filed under its slot.
5. **Repeat** steps 1–4 a few hundred times.
6. **Average** everything filed under G1, then G2, and so on — five numbers, drawn as five bars
   with the error on each.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/bucket-construction-dark.png">
  <img alt="Six panels in two rows, each row running the same steps on a different world. Left column, the population with fifteen randomly drawn points marked in the same colour: on a perfect line they sit along it, on the real cloud they sit anywhere. Middle column, six draws of five plotted against rank slots G1 to G5: on the line every draw rises monotonically, on the cloud the six lines cross and tangle with no order at all. Right column, the average over 400 draws with error bars: a clean staircase on the line, and on the cloud a shorter staircase from a negative G1 to a positive G5 whose error bars are a third of the bar heights" src="figures/bucket-construction-light.png">
</picture>

**One draw tells you nothing; a few hundred do.** The top row of the figure runs the steps where
the answer is known — every observation on a line — and every draw of five comes out ordered. The
bottom row runs them on § 2's real scatter, where the six draws cross and tangle and not one is
monotone. At 12% correlation none should be. **The staircase belongs to step 6, never to a draw
inside it.**

**Claim.** Averaging within a group shrinks the noise and leaves the signal untouched, which is what
step 5 buys.

**Proof.** Take $m$ observations sharing a similar signal value. Their mean return still has
expectation $\beta$ times their mean signal, while the noise around it falls to
$\sigma_\epsilon / m^{1/2}$:

|        | One observation | Mean of 300                        |
| ------ | --------------- | ---------------------------------- |
| Signal | 14.4 bp         | 14.4 bp                            |
| Noise  | 119 bp          | $119 / 300^{1/2} \approx 6.9$ bp |
| Ratio  | 1 : 8           | **2 : 1**                    |

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/noise-shrinks-dark.png">
  <img alt="Four bucket charts of the same population at 12 percent correlation, computed from 5, 30, 300 and 3,000 observations per bucket. At m equals 5 the bars swing between minus 80 and plus 93 basis points and are not monotone; by m equals 300 they have settled into a monotone staircase from about minus 20 to plus 20 basis points, and at m equals 3,000 the error bars are barely visible" src="figures/noise-shrinks-light.png">
</picture>

The true bars are identical in all four panels — near −20 bp at G1 and +20 bp at G5. Only the error
moves, and at $m = 5$ it is larger than the whole staircase. **Sample size is not a detail of the
recipe; it is the reason the recipe works.**

**Note (Where that overstates it).** The $m^{1/2}$ assumes independence. Overlapping windows and
assets that move together push the effective count well below $m$, so the noise does not really
reach 7 bp. The logic survives: averaging cancels noise and leaves systematic signal.

Nothing in steps 1–6 ever used the hypothesis — only the *ranking* — so the bars read **backwards**:
the closer the truth is to the line § 1 proposed, the more completely the staircase returns. Flat or
scrambled bars are the same procedure answering "not close".

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

**Reading it.** Monotone G1 → G5 means the signal carries information. Monotonicity is the test,
not the height of any one bar — a tall G5 with G1–G4 scrambled is usually small-sample noise, which
is what the error bars exist to expose.

**What it buys you.**

- **It makes a 10–15% correlation legible.** § 3.2's arithmetic: 300 observations behind each bar
  turn a 1:8 signal-to-noise ratio into 2:1. The scatter asks one point to carry the argument; a
  bar asks 300 to share it.
- **It tests ordering, not linearity.** A long/short book needs the top bucket to beat the bottom;
  it does not need the relationship to be a line. A signal that saturates above some value has a
  poor correlation and a perfect staircase, and it trades perfectly well.
- **It is immune to the signal's scale.** Ranking survives any monotone transform — raw momentum,
  its log and its z-score bucket identically — and no single 10σ day can move it. A correlation has
  neither property, which is why [08](08-ic-and-r-squared.md) prefers rank IC to Pearson.
- **Five bars keep the shape that a scalar throws away.** Where a signal breaks is legible: a
  lifted G1 is reversal (§ 5), a lone tall G5 is a long-only edge, a flat G4–G5 is saturation.
- **Error bars separate "no edge" from "not enough data."** A correlation point estimate does not.
- **It prices the trade.** Long the top bucket, short the bottom: G5 at +2% against G1 at −1% is
  worth about 3%. That is a number you can size a position with — 0.12 is not.

**What it does not tell you.**

- **The spread is gross.** No transaction costs and no turnover, and the edge is small enough that
  costs can take all of it ([04](04-understanding-backtesting.md)).
- **The time axis is gone.** Sorting the whole sample at once cannot show whether the edge is spread
  evenly over ten years or comes entirely from March 2020. Ranking *within each date* instead makes
  every bar a portfolio actually held that day — § 7's cross-sectional angle, and
  [03](03-from-signal-to-position.md)'s Portfolio 1 versus Portfolio 2.
- **The error bars are optimistic.** § 3.2's caveat: overlapping windows and assets that move
  together push the effective count well below $m$.

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

## 6. Risk-adjusted momentum

Raw momentum is not comparable across time or assets. 2% monthly momentum in the 2021 inflation
regime is unremarkable; the same 2% in the 2023 rate-hike drawdown is strong. Same number, different
meaning — and 2% for SHY is not 2% for UNG.

Divide by volatility:

$$
MOM^{\text{risk-adj}}_{s,t}  =  \text{Avg}\left(\frac{r_{s,t-i}}{\sigma_{s,t}}\right),\qquad i = 1 \ldots N
$$

where $\sigma_{s,t}$ is that asset's volatility, estimated on data strictly before $t$ — a
denominator that peeks at the future contaminates the signal as surely as a numerator would (§ 12).

Every asset and period now lands on one scale, so values compare — two students both scoring 80 on
different exams against different cohorts have not achieved the same thing.

## 7. The bucketing trap, and the rolling-quantile fix

Bucketing the standardized signal on **fixed intervals** (−2 to +2 in equal steps) starves the tails:
a normal distribution puts almost everything in the middle, so the two buckets you actually trade
become the least reliable bars, and one event can swing them.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/signal-distribution-dark.png">
  <img alt="Two standard-normal density curves. Left, cut at fixed intervals of one sigma: the tail groups hold 11 and 12 observations while the central groups hold 1,290 each. Right, cut at rolling quantiles: every group holds 635" src="figures/signal-distribution-light.png">
</picture>

Ranking the **whole history** into equal groups is worse: whether today counts as "high" would
depend on next year's extremes — clean-looking and pure look-ahead. **Correct: at each `t`, rank
only against history strictly before `t`** — a **rolling quantile**, expanding or fixed-window.
Better balanced than fixed intervals, though it discards some magnitude information.

No single view suffices; produce all three:

| View                     | Shows                           | Hides                                   |
| ------------------------ | ------------------------------- | --------------------------------------- |
| Raw-value buckets        | The signal at its natural scale | Not comparable across regimes or assets |
| Standardized buckets     | Regime-neutral comparison       | Sparse, unreliable tails                |
| Rolling-quantile buckets | No look-ahead, balanced groups  | Magnitude information                   |

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

Tune the **half-life** $H$ — the lag at which a return's weight has decayed to half the weight given
to the newest one. Candidates are fractions of the lookback (1/2, 1/3, 1/5, 1/8). Grid-search them.

MACD's 9-day signal line is an **empirical solution** — a value that fit historical data, nothing
more. Every parameter here has that status, which is [06](06-overfitting-and-robustness.md)'s
subject rather than something to accept on authority.

## 10. MACD, stated precisely

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

**Proof.** Each EMA is a weighted average of past prices whose weights sum to one, so their
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

**Note (What actually differs).** The kernel. A 21-day momentum weights the last 21 returns
equally and everything older at zero; MACD's weights rise from a small value at lag 0, peak around
lag 8, and decay without ever reaching zero. It therefore discounts *yesterday* relative to last
week — deliberately, since the newest return is the noisiest — and never fully forgets.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/signal-kernels-dark.png">
  <img alt="Weight given to each past daily return, against lag in trading days, for two signals normalised to the same total. A 21-day momentum is a flat box: equal weight for the last 21 days and zero beyond. MACD with spans 12 and 26 is a hump that starts low at lag zero, peaks around lag 8, then decays slowly and never reaches zero within sixty days" src="figures/signal-kernels-light.png">
</picture>

Three common rules, in increasing order of information kept. All
three still have to pass § 4's bucket test before they earn a backtest.

| Rule         | Go long when                            | Costs                                                            |
| ------------ | --------------------------------------- | ---------------------------------------------------------------- |
| Zero-line    | MACD is above zero                      | a slow trend filter, late                                        |
| Crossover    | the histogram is above zero             | earlier, noisier — the churn is § 11's subject                 |
| Proportional | always, sized by the standardized value | none of the magnitude, but see[03](03-from-signal-to-position.md) |

## 11. Volatility clustering, and smoothing the fast leg

Volatility arrives in clusters, and a fast signal is exposed: short-lived noise flips it
long/short, and the churn eats the return in transaction costs before any edge is realized. Fix:
**smooth the fast signal** to filter the shortest cycles.

**Constraint:** the smoothing window must be **shorter than the signal's own period**. Smooth with a
long one and you have not denoised the signal — you have built another slow one and lost the
timeliness the fast leg existed for.

## 12. Information availability

Everything above assumes the signal at `t` uses only data knowable at `t`. Look-ahead bias is born
here; the execution offsets in [04](04-understanding-backtesting.md) are the second line of defense
and cannot rescue a signal contaminated at construction. The rolling-quantile rule (§7) and the
train/validation/test split ([06](06-overfitting-and-robustness.md)) are the same discipline.

## Background

### If momentum averages returns, where is the magnitude — isn't the signal still ±1?

No. The two definitions in § 1 differ by one operation: binary momentum wraps the return in
`sign()`, plain momentum does not. An average of returns is an ordinary decimal — `Avg` spelled out
is a sum over the window, the lag $i$ counting backwards from yesterday:

$$
MOM_{s,t} = \frac{1}{N}\sum_{i=1}^{N} r_{s,t-i}
$$

At $N = 21$ that is last month's average daily move. Over a five-day lookback:

| Asset | Last five returns            | Avg → the signal | After`sign()` |
| ----- | ---------------------------- | ----------------- | --------------- |
| A     | +3%, +2%, +4%, +1%, +2%      | **+0.024**  | +1              |
| B     | +1%, −0.5%, +1%, 0%, +0.5%  | **+0.004**  | +1              |
| C     | −2%, −3%, −1%, −2%, −2% | **−0.020** | −1             |

The right column is binary momentum, and it cannot tell A from B. In the left column A is **six
times** B — that ratio *is* the magnitude, and since the signal is proportional to the weight, A is
held six times larger. Nothing is lost: the sign still carries direction, the absolute value adds
strength on top.

One caveat, which is § 6's subject: 0.024 means nothing on its own. 2.4% for SHY and 2.4% for UNG
are not the same trend, and neither are 2021's and 2023's. Only *relative* sizes are ever used.

## Appendix · Notation

Throughout, $s$ indexes the asset and $t$ the date; both are dropped where a formula concerns one
asset on one day.

| Symbol                                          | Means                                                                                                                         | First used |
| ----------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- | ---------- |
| $s$, $t$                                    | the asset, and the date in periods (days here)                                                                                | § 1       |
| $r_{s,t}$, $MOM_{s,t}$, $w_{s,t}$         | that asset's return in that period, the momentum signal it produces, and the position size that signal earns                  | § 1       |
| $N$, $i$                                    | lookback length, and the lag inside it running 1 to N                                                                         | § 1       |
| $x$, $y$, $\beta$, $\epsilon$           | one observation's signal value and forward return, the slope between them, and the part of the return the signal cannot reach | § 2       |
| $\rho$, $R^2$                               | their correlation, and its square — the share of the return's variance the signal explains                                   | § 2       |
| $\sigma_x$, $\sigma_y$, $\sigma_\epsilon$ | standard deviation of the signal, of the return, and of the unreachable part                                                  | § 2       |
| $m$                                           | observations sharing a bucket                                                                                                 | § 2       |
| G1 … G5                                        | the buckets, lowest to highest signal value                                                                                   | § 4       |
| $\sigma_{s,t}$                                | one asset's volatility, estimated on data before that date                                                                    | § 6       |
| $H$                                           | EWMA half-life, in periods                                                                                                    | § 9       |
| $P_t$, $\Delta_{t-j}$                       | price on that date, and the one-period change at that lag                                                                     | § 10      |
| $n_f$, $n_s$                                | fast and slow EMA spans, conventionally 12 and 26                                                                             | § 10      |
| $\alpha_f$, $\alpha_s$                      | their smoothing constants, two over span plus one                                                                             | § 10      |
| $c_i$, $k_j$                                | MACD's net weight on the price at that lag, and its kernel weight on the price change                                         | § 10      |

**Note (Collisions to watch).** Three quantities wear a $\sigma$ and they are not interchangeable:
$\sigma_y$ is the spread of forward return across the pooled cloud (§ 2), $\sigma_\epsilon$ the
part of it the signal cannot reach (§ 2), and $\sigma_{s,t}$ one asset's trailing volatility on one
date (§ 6). Likewise $w_{s,t}$ is a position and $k_j$ a kernel weight, which is why the latter is
not written $w$. And § 3.1's `alpha` is a plotting keyword, not $\alpha$ the smoothing constant
and not a regression intercept — code font against maths is the tell. Chapter
[01](01-what-is-cta.md) uses $s$ for a signed share count; here it is always the asset.

---

## Next → [03 · From Signal to Position](03-from-signal-to-position.md)

Before moving on, **build the 21-day momentum signal and plot its bucket chart three ways** — raw
values, standardized, and rolling quantile — then compare them. Chapter 03 assumes you have a signal
you already believe in.

You should be able to explain:

- [ ] Why a scatter plot proves nothing at a realistic 10–15% correlation
- [ ] Why the bottom bucket lifts, and how you would measure the right skip
- [ ] Why fixed-interval buckets starve the tails and full-history ranking leaks the future
- [ ] Why MACD is momentum with a hump-shaped kernel rather than a separate indicator

[← 01](01-what-is-cta.md) · [Index](00-index.md) · reference: [07 · Toolbox](07-toolbox-pandas.md)
