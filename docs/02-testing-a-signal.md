# 02 · Testing a Signal

> - **Answers:** why one correlation is the only number deciding whether a strategy makes money, and how to measure it long before a backtest.
> - **Prerequisites:** [01 · What Is a CTA Strategy](01-what-is-cta.md); the data it runs on is [100 · The Dataset](100-dataset.md).
> - **After reading:** state a signal as a hypothesis, measure whether it carries information with a bar plot, test whether the gap that plot shows is real, and say what the plot cannot tell you.

---

## 1. A signal is a hypothesis, not a formula

### 1.0 The three objects

Everything in this chapter is built from three numbers, one of each per asset per date.

| Object                   | Symbol                                                                                                      | What it is                                                        | Known at$t$ ?                     |
| ------------------------ | ----------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- | ----------------------------------- |
| **Weight**         | $w_{s,t}$   | the share of capital held in asset$s$ on date $t$, signed — negative is a short        | **yes**, you choose it                                      |                                     |
| **Signal**         | $MOM_{s,t}$ | a number computed from data available at$t$, meant to say something about what comes next | **yes**, you compute it                                     |                                     |
| **Forward return** | $r_{s,t}$                                                                                                 | what the asset then goes on to deliver while the position is held | **no** — this is the unknown |

**Note (Scope).** This chapter describes **one asset at a time**: a single series of dates, each
carrying that asset's own signal and its own forward return. That restriction is not a
simplification — assets have different volatilities, so their raw signals are not on one scale and
cannot be compared until § 4 puts them there. Combining several assets into one book comes after
that, in [the position-construction chapter](04-from-signal-to-position.md).

**Definition (Binary momentum).** The simplest member of the family — the sign of last period's
return, and nothing else:

$$
MOM_{s,t}  =  \text{sign}\left( r_{s,t-1} \right)
$$

where $s$ indexes the asset and $t$ the date, $r_{s,t-1}$ is that asset's return over the period
just ended, and $MOM_{s,t}$ is either +1 (long) or −1 (short), with nothing in between.

#### Why the sign alone is not enough

A window in which the asset rose 20% and one in which it rose 10% produce the *same* signal, so a
strategy built on it takes the same size in both. Trend **direction** survives; trend **strength**
is thrown away.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/binary-momentum-dark.png">
  <img alt="Left panel: one asset's price over two lookback windows, rebased to 100, the darker one climbing to 120 and the lighter one to 110. Right panel: the momentum signal each path produces, two bars of identical height at plus one, joined by an arrow labelled identical" src="figures/binary-momentum-light.png">
</picture>

**Definition (Momentum).** Averaging over $N$ periods rather than one, and keeping the value rather
than its sign:

$$
MOM_{s,t}  =  \text{Avg}\left(r_{s,t-i}\right),\qquad i = 1 \ldots N
$$

with $N$ the lookback length and $i$ the lag inside it — the average runs over the $N$ returns
ending yesterday. Spelled out, `Avg` is an ordinary sum over the window:

$$
MOM_{s,t} = \frac{1}{N}\sum_{i=1}^{N} r_{s,t-i}
$$

At $N = 21$ that is last month's average daily move. The two definitions differ by exactly one
operation — binary momentum wraps the return in `sign()`, plain momentum does not — and that one
operation is the whole of what magnitude costs.

**Example.** Three assets over a five-day lookback, and what each definition makes of them:

| Asset | Last five returns            | Avg → the signal | After `sign()` |
| ----- | ---------------------------- | ----------------- | --------------- |
| A     | +3%, +2%, +4%, +1%, +2%      | **+0.024**  | +1              |
| B     | +1%, −0.5%, +1%, 0%, +0.5%  | **+0.004**  | +1              |
| C     | −2%, −3%, −1%, −2%, −2% | **−0.020** | −1             |

The right column is binary momentum, and it cannot tell A from B. In the left column A is **six
times** B — that ratio *is* the magnitude, and since § 1.1 sets each weight proportional to its
signal, A is held six times larger. Nothing is lost: the sign still carries direction, the absolute
value adds strength on top.

**Note (The level is not yet meaningful).** 0.024 means nothing on its own. 2.4% earned in a calm
year and 2.4% earned in a violent one are not the same trend, so only *relative* sizes are ever
used — § 4 is what puts them on one scale.

### 1.1 Why studying the signal is the same as studying the portfolio

A signal is not a strategy: it earns nothing and cannot be held. The reason to spend a chapter on
one runs backwards, from what you are actually paid on.

**Start from the portfolio, because that is what you optimize.**

$$
R_t  =  \sum_s w_{s,t} r_{s,t}
$$

$R_t$ is the portfolio's return on date $t$, summed over every asset in the universe. Of the two
factors in each term only one is yours — $r_{s,t}$ is the market's answer, and it arrives after the
weight is already set. **So the whole of portfolio construction is the choice of $w_{s,t}$.**

**But the weights are not free.** Two sums over the book are fixed before any signal is consulted:

$$
\textbf{net:}\quad \sum_s w_{s,t} = 1
\qquad\qquad
\textbf{gross:}\quad \sum_s |w_{s,t}| = G
$$

| Sum                                                                                                                                                                                                | What it fixes                                                                    | Typical value                |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- | ---------------------------- |
| **Net**, $\sum_s w_{s,t}$                 | how much*market* the book carries — the directional bet, since longs and shorts cancel here | 100% long-biased,$\approx 0$ market-neutral |                                                                                  |                              |
| **Gross**, the same sum over absolute weights                                                                                                                                                | how much*leverage* is deployed, longs and shorts adding rather than cancelling | 200% (a 150/50 book) or 300% |

$G$ is the gross target, and the net holds at 1 only to within a tolerance $\delta$ since
rebalancing is discrete. The two are independent: one asset at 100% and a book long 200% / short
100% carry the same net and three times the position, which is why both have to be stated and why
gross is never free ([01](01-what-is-cta.md)).

**The weights are where the signal enters.** You want weight where the forward return is about to be
high, and that is precisely the number you do not have. The signal is the stand-in you put in its
place, which means setting $w_{s,t} \propto MOM_{s,t}$.

**Claim.** Under that rule the portfolio's expected return is proportional to the correlation
between the signal and the forward return, and to nothing else that can change its sign.

<details>
<summary><b>Proof.</b> expected portfolio return factorises into a leverage scale, two volatilities, and the signal-return correlation — and only the last can be negative</summary>

Take the signal and the return as centred. With $w_{s,t} \propto MOM_{s,t}$,

$$
E[R_t]  \propto  \sum_s E[MOM_{s,t} r_{s,t}]  =  \sum_s \rho_s \sigma_{MOM,s} \sigma_{r,s}
$$

using $E[xy] = \rho \sigma_x \sigma_y$ for centred $x$ and $y$, where $\rho_s$ is the correlation
between asset $s$'s signal and its forward return and $\sigma_{MOM,s}$, $\sigma_{r,s}$ their standard
deviations. The dropped constant is a leverage choice and the volatilities are measurable properties
of the asset — all three positive whatever the signal does. **Only $\rho_s$ can carry a sign, so only
$\rho_s$ decides whether the portfolio makes money or loses it.**

</details>

**Note (The constraints do not disturb this).** Reaching a legal weight vector means **shifting**
the signal until the net lands right and **scaling** until the gross does — both affine with a
positive scale, under which correlation is unchanged: $\rho(a + bx, y) = \rho(x, y)$ for $b > 0$. The
$\rho$ measured on the raw signal is therefore the $\rho$ governing the constrained portfolio, which
is what lets the rest of the chapter ignore weights altogether; [the position-construction
chapter](04-from-signal-to-position.md) carries out both operations.

Everything collapses to that one number, and it is a number about the signal alone:

$$
\textbf{hypothesis:}\quad MOM \uparrow  \Longrightarrow  \text{return} \uparrow
\qquad\qquad
\textbf{that is:}\quad \rho > 0
$$

Three things follow, and between them they set the shape of the rest of the chapter.

| Consequence                                                                                                                                                                                                    | Dealt with in |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------- |
| **The portfolio never has to be built to test the signal.** Measure $\rho$ between the signal and the forward return directly, and you have measured the strategy                                      | § 2, § 3    |
| **Magnitude reaches the position, not just direction.** $w \propto MOM$ means a signal twice as large takes a position twice as large — which is what binary momentum throws away                     | § 1.0        |
| **At equal $\rho$ a volatile asset contributes more than a quiet one**, since each term carries $\sigma_{MOM,s} \sigma_{r,s}$ alongside $\rho_s$. Ranking raw signals therefore ranks volatilities | § 4          |

**Write the hypothesis before the code.** It names what would falsify the signal, and one you
cannot falsify is a plot you will rationalize either way.

### 1.2 Which return the signal is scored on

§ 1.1 measures $\rho$ between the signal and *the forward return*, and that phrase is not yet
precise enough to compute. Three spans sit on the timeline, in this order:

| Span                    | What it holds                                                                       | Typical size          |
| ----------------------- | ----------------------------------------------------------------------------------- | --------------------- |
| **Lookback**      | the $N$ returns the signal averages, ending at $t-1$                             | 20–250 periods       |
| **Gap**           | $g$ periods thrown away — neither averaged into the signal nor scored against it | 0, a week, or a month |
| **Paired return** | $r_{s,t+g}$, the one period the signal is judged on                               | one period            |

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/signal-return-alignment-dark.png">
  <img alt="Two panels of cells laid on a timeline, one cell per period. The top panel is one observation: eight filled cells bracketed as the lookback the signal averages, then three dashed empty cells bracketed as the discarded gap, then a single filled cell bracketed as the one the signal is scored on, with a dotted vertical line marking that the signal is computed from the cells to its left only. The lower panel repeats the same pattern for dates t, t plus one and t plus two, each shifted one cell right, so the lookbacks overlap in all but one cell while the three scored cells form a descending diagonal, annotated one return per date and no two dates share one" src="figures/signal-return-alignment-light.png">
</picture>

The gap is the only free choice of the three. The `-1` in **12-1 momentum** is exactly this gap: a
twelve-month window stopping one month short of today.

**Why leave one at all.** Not executability — § 1.0's window already ends at $t-1$, so $g = 0$ is
knowable in time and anything tighter is look-ahead (§ 5). Executability fixes the floor at zero;
**reversal** decides everything above it. A trend that has just formed hands a little of it back,
and at daily frequency that rebate is large enough to cancel the edge outright — which is how a
real signal arrives at the bar plot looking flat, or upside down. Which mechanisms produce it, and
which of them competition can remove, is this chapter's Background.

**Reversal strengthens as the sampling gets finer**, which is what actually sets $g$. The bid–ask
bounce is a roughly fixed number of ticks per trade while the trend grows with the horizon, so at
one day the bounce dominates and at one month it is rounding error.

**What the gap costs.** It removes the opening of the trend along with the rebate, so a longer $g$
is a staler signal. That makes $g$ a **hyperparameter**, and running it at a day, a week and a month
and keeping whichever bar plot looks best is what [07](07-overfitting-and-robustness.md) warns
about. Set it from your trading frequency and a prior on how long the rebate lasts.

**Note (Neighbouring observations are near-copies).** Step one date forward and the lookback keeps
all but one of its cells, as the figure's lower panel shows. Consecutive signals are therefore not
independent draws, which is where § 3.2.2's caveat on the effective sample size comes from.

## 2. What you hoped for, and what you get

### The plot everyone draws first

§ 1's hypothesis says forward return rises with the signal, so the first move is to plot one against
the other. The picture you had in mind is the leftmost panel below. What comes back — for well over
99% of the scatters you will ever draw — is the rightmost.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/scatter-ladder-dark.png">
  <img alt="Four scatter panels of forward return against a signal, both axes in standard deviations. The first three are drawn at correlations of 80, 45 and 30 percent from 1,500 synthetic points: the 80 percent panel, labelled what you pictured, is a clear diagonal band, and by 30 percent, labelled the eye's floor, the tilt is barely arguable. The fourth is underlined and labelled measured, CTA_data at minus 1.9 percent — a formless round cloud with a denser core than the drawn panels, being real returns with fatter tails" src="figures/scatter-ladder-light.png">
</picture>

### Why the real one is a cloud

**Claim.** The scatter can neither confirm nor refute a signal, because the correlation a working
signal carries sits far below the threshold at which the eye resolves a trend.

**Proof.** Both numbers are readable off the panels above: the eye stops resolving a tilt somewhere
around 30%, and the fourth panel — 21-day risk-adjusted momentum against the next session's return,
measured over the 37 ETFs of [100 · The Dataset](100-dataset.md) — comes in at **−1.9%**. Since
1.9% < 30%, a signal that works and a signal that does not produce the same picture — **the absence
of a visible trend is not evidence of anything.**

So why is the correlation so small? Because the quantity being plotted is mostly not the signal.

**Claim.** Split the forward return into the part the signal reaches and the part it does not,
$y = \beta x + \epsilon$. If $\epsilon$ is uncorrelated with $x$, the signal owns exactly
$\rho^2$ of the return's variance, where $\rho$ is their correlation.

<details>
<summary><b>Proof.</b> uncorrelated parts add their variances, so the explained share is exactly the squared correlation — 0.035% of it here</summary>

Uncorrelated components add their variances,

$$
\text{Var}(y) = \beta^2 \text{Var}(x) + \text{Var}(\epsilon)
$$

and on one regressor with an intercept the explained share is $R^2 = \rho^2$. At
$\rho = -0.019$, $R^2 = 0.00035$ — which does not mean "right 0.035% of the time", but: of the
variation in forward return from one observation to the next, **0.035% is linear in the signal and
99.965% is not.**

</details>

<details>
<summary><b>Example.</b> one asset-date's return split into the 2.8 bp the signal moves and the 149 bp it does not</summary>

Everything below is **one asset-date's** forward return, never a portfolio's, and every number is
measured over the 57,649 asset-dates of the sample. The daily return standard deviation is
$\sigma_y = 0.0149$ — 149 bp, a **basis point** being 0.01%:

| Component             | Size                            | At$\rho = -1.9\%$ |
| --------------------- | ------------------------------- | ------------------- |
| Total return          | $\sigma_y$                    | 149 bp              |
| What the signal moves | $\rho \sigma_y$               | **2.8 bp**    |
| What it does not      | $\sigma_y (1 - \rho^2)^{1/2}$ | **149 bp**    |

The third row is not a rounding slip: at this correlation the signal removes so little that the
unreachable part is the whole of it to three figures. Across an x-axis running from $-2\sigma_x$ to
$+2\sigma_x$ the trend line moves about 11 bp end to end, while at every $x$ the points scatter over
roughly 596 bp. **A 0.11% slope inside a 6% cloud** — that ratio *is* the picture.

</details>

**Note (Where a larger correlation would come from, and where it would not).** A predictor
correlating 50% with next period's return would be arbitraged away long before you found it in
anything liquid, so single digits is a competitive market's ceiling rather than a shortfall in
craft. Two things do legitimately raise it and neither is on offer here: a **longer horizon**, since
the signal's edge accumulates while the noise grows only as the square root of time, and
**combining many signals**, since a composite reaches correlations no ingredient has on its own.
Quoted numbers near 10% are almost always one of those two. A single signal against a single
session is the hardest case in the family, and this chapter is deliberately standing in it.

## 3. Two ways out of the cloud

The scatter is unreadable, but the signal may still be in it. There are two things to try, and only
the second one works.

### 3.1 Turn down `alpha`

`alpha` is a marker's opacity. Turn it far enough down — `alpha=0.05` on a few thousand points,
lower still on more — and a single point becomes nearly invisible, so only *overlap* renders and the
chart is a density map rather than a mass of ink.

**Note (Not the other alphas).** matplotlib's opacity keyword: not a regression intercept, not the
excess return a manager is paid for, not [03](03-shaping-the-lookback.md)'s smoothing constant
$\alpha$. Code font is the tell.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/alpha-opacity-dark.png">
  <img alt="Two scatter panels of forward return against a signal, both plotting the same 6,000 asset-dates measured on CTA_data with both axes standardized. Left, at full opacity, they render as one solid disc with no internal structure. Right, the identical points at an opacity of 0.01: a smooth round density, denser in the core, with no thin region, no empty corner and no visible tilt anywhere" src="figures/alpha-opacity-light.png">
</picture>

Sometimes it is enough. A corner bitten out of the cloud — high signal never followed by a bad
loss — would be a finding, because a signal that only rules something *out* is still tradeable.
This data has no such corner, and that is the ordinary outcome.

**Why it usually fails.** Two reasons that compound:

- **The density comes back smooth.** Tens of thousands of asset-date cells average into a clean
  bivariate blob, and opacity renders that faithfully — a smooth density has no feature, and § 2's
  band is fifty times taller than the tilt hiding in it.
- **It treats the symptom.** The scatter spends its resolution on individual noisy points when the
  claim is about their **average**; no rendering choice changes what is being rendered.

**Note (Look first anyway).** Always draw it. On the rare occasion something *is* readable — a
curve, an empty corner — it beats every statistic, because it gives the *shape*. The mistake is
concluding anything **from** a cloud.

### 3.2 Beta Method

Stop asking each point what it did, and ask each *group* of points what they did on average. The
answer comes back as a **bar plot**, and the rest of § 3 is about reading that one chart.

#### 3.2.1 What a bar plot is

**Definition (Bar plot).** Five bars. The horizontal axis is the **signal**, coarsened into five
ordered slots G1 … G5; the vertical axis is the **mean forward return** of the observations filed
into each slot. Every observation lands in exactly one bar, and the error bar on it is the standard
error of that mean.

**Note (A bucket holds dates, not assets).** G5 is not a set of assets. It holds the **dates** on
which this one asset's signal stood in the top fifth of its own history, and G1 the dates on which
it stood in the bottom fifth. One asset passes through every bucket as the years go by, and the
whole chart describes that asset alone.

Five steps build it:

1. **Fix one asset.** Its history gives one signal $MOM_{s,t}$ and one forward return $r_{s,t}$ per
   date.
2. **Rank the dates by signal value**, highest to lowest.
3. **File each date** into one of five slots by that rank: the highest fifth into G5, down to G1.
4. **Record** under each slot the forward return that date went on to deliver.
5. **Average** the returns filed under each slot.

**Note (Step 2 is where this chapter's one defect lives).** Ranked on *what*, exactly? Take the raw
momentum value and everything above still runs — but the asset's own volatility changes over the
years, so +2% is a strong month in a calm tape and a quiet one in a violent tape, and step 3 files
them into the same slot as if they were the same event. § 4 is the correction, and until it lands
the plot below should be read as machinery rather than as a result.

The figure runs those five left to right, so five dates drawn at random contribute one observation
per slot — the population, each draw sitting at the slots its five dates fell into, and the average
of many with the error on it.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/bucket-construction-dark.png">
  <img alt="Six panels in two rows. The upper row is invented and the lower is measured on CTA_data. Left column, the population of dates with fifteen randomly drawn ones marked in the same colour: on a perfect relationship they sit along a line, on the measured cloud they sit anywhere. Middle column, six draws of five dates plotted against rank slots G1 to G5: on the line every draw rises monotonically, on the cloud the six lines cross and tangle. Right column, the answer with plus or minus two standard errors: a clean rising staircase on the invented row, and on the measured row the real bucket chart over all 57,649 asset-dates — G1 at plus 11 basis points standing well clear of its error bar, G2 to G5 all within a few basis points of zero, so the staircase descends" src="figures/bucket-construction-light.png">
</picture>

**Note (What makes 57,649 dates from 37 assets one pool).** The measured row does not rank raw
momentum across assets. Every signal entering it is already divided by that asset's own trailing
volatility and ranked against that asset's own history before it lands in a bucket — the route § 4
works out in full, with a worked two-asset example. G1 … G5 are therefore **percentile** slots,
comparable across a Treasury ETF and a semiconductor ETF for the same reason they are comparable
across 2021 and 2023: nothing but rank survives the trip, so pooling assets costs no more than
pooling dates already did.

**The sort key is the signal, never the return.** Step 2 orders by $MOM_{s,t}$, which is known at
$t$; step 3 only *records* what followed. G1 therefore holds the lowest-**signal** observations, not
the worst performers.

<details>
<summary><b>Example.</b> five dates filed by signal and by return, and why sorting on the return would make any signal look perfect</summary>

Five dates from one asset's history, invented, filed both ways:

| Date    | Signal | Forward return | Slot by signal | Slot by return |
| ------- | ------ | -------------- | -------------- | -------------- |
| $t_1$ | +2.1%  | −0.4%         | G4             | G2             |
| $t_2$ | −1.8% | +0.9%          | G1             | G4             |
| $t_3$ | +0.6%  | +1.3%          | G3             | G5             |
| $t_4$ | +3.4%  | +0.2%          | G5             | G3             |
| $t_5$ | −0.9% | −1.1%         | G2             | G1             |

Read down *slot by signal* and the returns come out unordered — which is exactly what five dates
look like at a correlation this small. Read down *slot by return* and the ordering is perfect, and would be perfect
for **any** signal including one straight out of a random number generator, because each bar is then
reporting the sort key back to you. **The staircase is evidence only because the thing sorted on and
the thing measured are different, and the second was not knowable when the first was computed.**

One bar therefore carries three pieces of information: which fifth of the signal's range it stands
for, the average return that fifth went on to earn, and how much of that average is sampling noise.

</details>

#### 3.2.2 How the bar plot shows a trend

**The trend is the ordering, not the heights.** § 1's hypothesis was *higher signal, higher forward
return*; on a bar plot that is precisely the statement G1 < G2 < G3 < G4 < G5. A single bar's level
moves with where the boundaries are cut (§ 4) — the ordering is what does not.

Two further readings carry information, and nothing else on the chart does:

| Read                                                | What it establishes                                                                                                                                                         |
| --------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **G5 − G1, measured against the error bars** | the size of the edge next to what noise alone would draw. A rise that fits inside one error bar is not evidence of anything, and § 3.2.3 turns that comparison into a test |
| **The direction of the slope**                | a*descending* staircase is not a dead signal — it is the same edge carrying the opposite sign                                                                            |

A scrambled middle does not disqualify a signal: clean tails around a muddled G2–G4 is a common
shape and a perfectly tradeable one, since the tails are where the positions go.

On direction, adopt a convention and keep it: **leave the signal's sign alone and let the chart come
out upside down.** Flipping a signal the moment its staircase descends is cheap, and a dozen signals
later you will not remember which ones you flipped. Read a descending staircase as *this works,
traded short*, and carry the sign in the strategy rather than in the signal definition.

**Claim.** The ordering surfaces at all only because of step 4 — averaging shrinks the noise and
leaves the signal untouched.

<details>
<summary><b>Proof.</b> averaging leaves the signal where it was and divides the noise by the square root of m, turning 1 : 14 into 7 : 1</summary>

Take $m$ observations sharing a similar signal value. Their mean return still has expectation
$\beta$ times their mean signal — they were chosen for having nearly the same signal, so averaging
them changes it barely at all — while the noise around it falls to $\sigma_\epsilon / m^{1/2}$.
Measured, with the edge taken as the G5 − G1 gap the chart is trying to resolve:

|        | One observation | Mean of 11,522                       |
| ------ | --------------- | ------------------------------------ |
| Signal | 10.4 bp         | 10.4 bp                              |
| Noise  | 149 bp          | $149 / 11522^{1/2} \approx 1.4$ bp |
| Ratio  | 1 : 14          | **7 : 1**                      |

The left column is the scatter of § 2 and the right column is one bar of the chart. Nothing was
added — only the noise was taken away. It takes eleven thousand observations to do here what the
table's old arithmetic did with three hundred, and that is the honest price of a 1.9% correlation.

</details>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/noise-shrinks-dark.png">
  <img alt="Four bucket charts of the same measured population, mean forward return in basis points against signal bucket, each drawn from 30, 300, 3,000 and all 11,522 observations per bucket. At m equals 30 the bars swing between minus 20 and plus 27 basis points with error bars over fifty points wide and no ordering; by m equals 3,000 the error bars have shrunk to about five points and G1 is visibly the tallest bar; at m equals 11,522 the error bars are a few basis points and G1, at plus 11, stands clear of its own error while G2 to G5 sit near zero" src="figures/noise-shrinks-light.png">
</picture>

The quantity being estimated is identical in all four panels — the real bucket means, +11 bp at G1
and roughly zero at G5. Only the error moves, and at $m = 30$ it is five times the whole staircase.
**Sample size is not a detail of the recipe; it is the reason the recipe works.**

**Note (Where that overstates it).** The $m^{1/2}$ assumes independence, and one asset's history
violates it twice over: overlapping lookback windows share most of their inputs, and returns
cluster in time, so consecutive observations are near-copies rather than independent draws. Both
push the effective count well below $m$, and the noise does not really reach 7 bp. The logic
survives: averaging cancels noise and leaves systematic signal.

#### 3.2.3 Is the staircase real?

§ 3.2.2 read the rise against the error bars by eye. That comparison is a hypothesis test, and it is
worth writing down, because the eyeball version and the arithmetic version do not agree.

**Definition (Standard error of a bucket).** For bucket $g$ holding $m_g$ observations whose
forward returns have sample standard deviation $\sigma_g$,

$$
\text{SE}_g = \frac{\sigma_g}{m_g^{1/2}}
$$

the spread of that bucket's **mean**, not of the observations inside it — which is why it shrinks
with $m_g$ while $\sigma_g$ does not. Bars here are drawn at $\pm 2 \text{SE}_g$.

**The hypothesis on trial is § 1's, narrowed to the two buckets that carry the positions.** A long
book buys G5 and sells G1, so what has to be non-zero is the difference between those two means:

$$
H_0: \mu_{G5} = \mu_{G1}
$$

against the alternative that they differ, where $\mu_g$ is bucket $g$'s true mean forward return.
The statistic is the observed difference in units of its own noise:

$$
z = \frac{\mu_{G5} - \mu_{G1}}{\left( \text{SE}_{G5}^2 + \text{SE}_{G1}^2 \right)^{1/2}}
$$

the denominator adding **variances** rather than standard errors, because the two bucket means are
computed from disjoint sets of dates.

**Note (Why it is a $t$ and gets called a $z$).** Both $\mu_g$ and $\sigma_g$ are estimated from the
same sample, so the exact null distribution is Student's $t$, not the normal. It stops mattering
fast: at bucket sizes in the thousands the two are indistinguishable and the number is quoted as a
**z-score**. Derive it as a $t$, report it as a $z$, and at $m_g$ in the tens use the $t$ and mean it.

**Claim.** $|z| \geq 2$ rejects $H_0$ at the 5 percent level.

**Proof.** Under $H_0$ the statistic is standard normal in the large-sample limit, and a standard
normal places 0.0455 of its mass outside $\pm 2$ — less than $\alpha = 0.05$, so the observation
lies inside the two-sided rejection region.

<details>
<summary><b>Example.</b> the measured buckets, tested — a z of −4.9, and bars that clear each other</summary>

The whole sample, five buckets, 11,522 dates in the smallest:

| Bucket | $\mu_g$           | $\sigma_g$ | $m_g$ | $\text{SE}_g$ |
| ------ | ------------------- | ------------ | ------- | --------------- |
| G1     | **+10.72 bp** | 173 bp       | 11,522  | 1.62 bp         |
| G2     | +1.05 bp            | 144 bp       | 11,523  | 1.34 bp         |
| G3     | +3.48 bp            | 136 bp       | 11,525  | 1.27 bp         |
| G4     | +2.83 bp            | 140 bp       | 11,523  | 1.30 bp         |
| G5     | **+0.31 bp**  | 149 bp       | 11,556  | 1.39 bp         |

$$
z = \frac{0.31 - 10.72}{\left( 1.39^2 + 1.62^2 \right)^{1/2}} = \frac{-10.41}{2.13} \approx -4.9
$$

Well past 2 in absolute value, and the bars — G1 spanning +7.5 to +14.0 bp, G5 spanning −2.5 to
+3.1 — clear each other with room to spare.

</details>

**Note (Non-overlap is sufficient, not necessary).** The two readings differ, and in the direction
that costs you signals. Bars of half-width $2\text{SE}$ fail to touch when the difference exceeds
$2 \left( \text{SE}_{G5} + \text{SE}_{G1} \right)$, while the test rejects when it exceeds
$2 \left( \text{SE}_{G5}^2 + \text{SE}_{G1}^2 \right)^{1/2}$ — and a sum is never smaller than the
root of the sum of squares. On the measured numbers the eye demands 6.0 bp and the test demands
4.3 bp, so a difference between those two is one the picture calls inconclusive and the arithmetic
calls significant. **Bars that clear each other are always significant; bars that touch may still
be.** Use the chart to accept and compute $z$ before rejecting.

**The sign is negative, and that is a result rather than a failure.** $z = -4.9$ says the two
means differ, decisively; it says nothing about which way round they should be. What was measured is
that **a high 21-day momentum is followed by a slightly worse next session than a low one** — the
descending staircase § 3.2.2 told you to expect and to keep. It is not a broken signal, it is
**reversal**, and the Background section explains where it comes from and what removes it: put a gap
between the signal's window and the return it is scored on, and the sign comes back.

**Note (What the test does not license).** Two things sit outside it. The $m_g^{1/2}$ in every
standard error assumes independent observations, and § 3.2.2's closing Note explains why one asset's
overlapping windows are nothing of the kind — the effective count is well below $m_g$, so every $z$
here is optimistic. And a threshold of 5 percent means one signal in twenty passes on noise, which
is a fact about *one* test: running twenty variants and reporting the one that cleared 2 is not a
test at all, and is [07](07-overfitting-and-robustness.md)'s subject.

**Failing to reject is a verdict on the measurement, not on the signal.** $|z| < 2$ says the data
did not separate the two means. Whether that is because they are equal, or because the error bars
were too wide to tell them apart, is a question about $m_g$ — and the two readings are not
interchangeable. The smallest gap the test could have caught, at the four sample sizes of the figure
above and a common $\sigma_g$ of 149 bp:

| $m_g$ | $\text{SE}_g$ | Smallest detectable G5 − G1 | What a null result there rules out                                                    |
| ------- | --------------- | ---------------------------- | ------------------------------------------------------------------------------------- |
| 30      | 27 bp           | 77 bp                        | Almost nothing. An edge large enough to build a career on is still consistent with it |
| 300     | 8.6 bp          | 24 bp                        | Only edges several times larger than anything this chapter measures                   |
| 3,000   | 2.7 bp          | 7.7 bp                       | Most of the range that matters, but not the part costs decide                         |
| 11,522  | 1.4 bp          | 3.9 bp                       | The effect, down to a gap too small to survive execution anyway                       |

Only the bottom row turns a null result into a finding. In the top row the gate has not been failed
so much as attempted — **the honest report is "not measured yet", and the fix is more observations,
not a different signal.**

#### 3.2.4 What the bar plot cannot show

Every date contributes one observation — its signal's score, and the return that followed. Step 5
flattens all of them onto one picture, five slots wide.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/bucket-time-collapse-dark.png">
  <img alt="Two panels. Left, one asset's dates strung along a time axis, each dot drawn at the slot its signal scored into, so all five rows are populated throughout and a violent stretch at the right is shaded. Right, the same observations with the date discarded: five bars of mean forward return rising from G1 to G5, with error bars. An arrow between them is labelled average down each column" src="figures/bucket-time-collapse-light.png">
</picture>

Step 5 integrates over $t$, and an integral hands back an area, never the shape of the function
underneath it. A staircase that is monotone over twenty years is equally consistent with an edge
that held throughout and with one that worked for five years and was flat for fifteen.

| Not on the chart                                                  | Where to look instead                                     |
| ----------------------------------------------------------------- | --------------------------------------------------------- |
| **When** the edge happened                                  | the equity curve of[05](05-understanding-backtesting.md)   |
| **Who** is inside a bucket — which dates, which regime     | the dates behind each bar, tabulated rather than averaged |
| **The spread** of returns behind a bar, as against its mean | the distribution within a bucket, not its mean            |
| **How independent** the observations are                    | overlapping windows, per the Note above                   |

## 4. Step 2, corrected — risk-adjusted momentum

**This section repairs § 3.2, it does not extend it.** Every piece of machinery there survives: the
sort key is knowable at $t$, the returns are recorded honestly, and the averaging shrinks noise
exactly as the proof says. What § 3.2 never settled is *what step 2 ranks*, and ranking the raw
momentum value produces a chart about something other than the signal.

Raw momentum is not comparable **across time**, and § 3.2 compares nothing else: its five slots sort
one asset's own dates against one another. 2% in the calm 2021 tape and 2% in the 2023 rate-hike
drawdown are different events, and filing them into the same slot says they are the same.

The identical failure reappears one step later, **across assets**, the moment you want more than one
name in a book — and there it is an assumption you have to state rather than a fact. A universe of
five hundred large-cap equities might plausibly sit on one scale already. A CTA universe does not:
50 bp in a session is an ordinary day for an equity index and, for a Treasury future, an event that
would lead the news. 2% monthly momentum in a Treasury ETF is a large move; the same 2% in a
semiconductor ETF is a quiet month. Rank the two against each other on raw momentum and the
semiconductor wins every time — not because its trend is stronger but because everything about it is
larger.

Divide by volatility:

$$
MOM^{\text{risk-adj}}_{s,t}  =  \text{Avg}\left(\frac{r_{s,t-i}}{\sigma_{s,t}}\right),\qquad i = 1 \ldots N
$$

where $\sigma_{s,t}$ is that asset's volatility, estimated on data strictly before $t$ — a
denominator that peeks at the future contaminates the signal as surely as a numerator would (§ 6).

Every date, and later every asset, now lands on one scale, so § 3.2's slots compare like with
like — two students both scoring 80 on different exams against different cohorts have not achieved
the same thing.

**Note (A second route to the same plane).** Dividing by $\sigma_{s,t}$ is not the only way. You can
also replace the value outright by **its percentile against that asset's own past**, which lands
every date on $[0, 1]$ by construction and needs no volatility estimate at all. Either route hands
step 2 something it can legitimately rank.

<details>
<summary><b>Example.</b> two assets whose raw signals cannot be compared, and the percentiles that can</summary>

Two assets, each with five past signal values and one for today:

| Asset | Its own past signals      | Today          | Beats        | Percentile   |
| ----- | ------------------------- | -------------- | ------------ | ------------ |
| A     | −10, 8, 4, 0, −5        | **+7**   | four of five | **80** |
| B     | −100, −80, 90, −60, 20 | **−70** | two of five  | **40** |

Raw, `+7` against `−70` is not a comparison anybody should make. As percentiles, 80 against 40 is —
and it says A is the stronger trend *relative to its own history*, which is the only sense in which
the question has an answer. The cost is the one every rank charges: the magnitudes are gone.

</details>

**Note (Which cut to use once it is scored).** The percentile route hands back a uniform score, so
cutting at the quintiles gives five equal groups for free. The volatility route does not: a
standardized signal is roughly normal, so cutting it at fixed intervals such as ±1 and ±2 leaves
almost everything in the middle and starves the two tails you would actually trade. Cut it at its
quintiles instead.

**The rule this section leaves behind.** Every signal is **standardized** or **scored against its
own past** before it is compared to anything — otherwise the bar plot reports volatility while
wearing the signal's name. The measured chart back in § 3.2 already followed this rule before this
section stated it: the percentile route is what let 37 assets share one pool of buckets.

## 5. What to report — and why it is not a Sharpe ratio

Every chart in § 3 reports one quantity: **the mean forward return of a bucket, with its standard
error.** The instinct at this point is to reach for something that sounds more like a result, and
the one everybody reaches for is the wrong tool for this stage.

**Definition (Sharpe ratio).** A portfolio's average return in excess of what financing it costs,
per unit of the volatility it ran:

$$
\text{SR} = \frac{E[R_p] - r_f}{\sigma_p}
$$

with $R_p$ the portfolio's return over a period, $r_f$ the risk-free rate charged on the capital it
used, and $\sigma_p$ the standard deviation of $R_p$. It is the right measurement for a finished
portfolio and the wrong one here, for four separate reasons.

**There is no portfolio yet.** § 1.1's argument is precisely that the signal can be judged *without*
building one, and nothing in § 3 has chosen a weight. A Sharpe ratio scores the output of a
construction step that has not happened; computing one on a bucket's returns scores a portfolio
nobody would run — equal weight on every date that fell into one fifth of the sample.

**The financing rate is not zero here, and it is not constant.** The numerator subtracts $r_f$, and
which rate that is depends on the book's **net exposure** (§ 1.1):

| Book                                                   | Net exposure  | Correct$r_f$                                                                              |
| ------------------------------------------------------ | ------------- | ------------------------------------------------------------------------------------------- |
| Dollar-neutral long/short —\$1 long against \$1 short | $\approx 0$ | **zero.** The short leg's proceeds fund the long leg, so no capital is being borrowed |
| A 150/50 CTA book                                      | 100%          | **the actual financing rate**, on the capital the net exposure represents             |

Statistical-arbitrage books are the first row, which is where the habit of setting $r_f = 0$ comes
from and where it is correct. A CTA book is the second row, and the rate belonging in it is a
**time series**, not a constant: the policy rate this sample spans moved from near zero to above
five percent. Carrying over "we always used 2 percent" from a book that was dollar-neutral puts an
invented series into the numerator of every number reported.

**It folds three estimates into one number.** Mean, volatility and financing rate, each with its
own error. A Sharpe that falls because the edge died and a Sharpe that falls because the tape got
noisier are the same number — the exact opposite of § 3.2's method, where one chart carries one
quantity so a change has one cause.

**A Sharpe means nothing without the market it was earned in.** Two books, and the smaller number is
the better strategy:

| The tape           | Market's own Sharpe | The book's Sharpe | Reading                                                                                                                            |
| ------------------ | ------------------- | ----------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Violent throughout | 0.4                 | **0.8**     | held together through amplitude that should have wrecked it, at twice the market's own risk-adjusted return — an excellent result |
| Calm and rising    | 0.8                 | **0.9**     | barely beat holding the index. The extra 0.1 is within what one lucky bet would produce                                            |

**The mean return is the quantity you can actually trade.** It is what the book delivers, it is what
§ 1.1's algebra is written in, and it is denominated in the same basis points as the costs that will
be subtracted from it later. A Sharpe ratio is a score attached afterwards, useful for comparing
**finished** portfolios against each other — which is [06](06-evaluating-performance.md)'s subject,
after an optimization step has given it something to measure.

## 6. Information availability

Everything above assumes the signal at `t` uses only data knowable at `t`. Look-ahead bias is born
here; the execution offsets in [05](05-understanding-backtesting.md) are the second line of defense
and cannot rescue a signal contaminated at construction. The rolling-quantile rule (§ 4) and the
train/validation/test split ([07](07-overfitting-and-robustness.md)) are the same discipline.

## Background

### Why does a trend hand part of itself back, and can that be competed away?

**Reversal is not an anomaly, it is the normal state of the tape.** A trend that has just formed
hands a little of it back, and at daily frequency that rebate is large enough to cancel the edge
outright — which is why § 1.2 leaves a gap $g$ between the signal's window and the return it is
scored on. Three mechanisms produce it, and they are not equally fragile:

| Mechanism                      | What happens                                                                                                                    | Competed away?                                       |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| **Bid–ask bounce**      | Closes print alternately at the bid and the ask, oscillating around the true mid — negative serial correlation by construction | **No.** A measurement artefact; no price moved |
| **Paying for liquidity** | An order that must fill now pushes price past fair value, and whoever takes the other side is repaid when it returns            | **No.** A fee for a service actually rendered  |
| **Overreaction**         | News is over-extrapolated, then partly corrected                                                                                | **Yes** — the only part that decays           |

Two of the three are not mistakes, which is why reversal survives competition instead of being
arbitraged into nothing — only the overreaction row decays as more people trade against it.

## Appendix · Notation

Throughout, $s$ indexes the asset and $t$ the date. The signal is computed per asset, so $s$ is
dropped wherever a formula never leaves one asset; it carries weight everywhere the assets are
ranked against each other.

| Symbol                                                                                                                                                                          | Means                                                                                                                         | First used |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- | ---------- |
| $s$, $t$                                                                                                                                                                    | the asset, and the date in periods (days here)                                                                                | § 1       |
| $r_{s,t}$, $MOM_{s,t}$, $w_{s,t}$                                                                                                                                         | that asset's return in that period, the momentum signal it produces, and the share of capital that signal earns it            | § 1.0     |
| $R_t$                                          | the portfolio's return on that date,$\sum_s w_{s,t} r_{s,t}$                                                               | § 1.1                                                                                                                        |            |
| $G$, $\delta$                                                                                                                                                               | the gross-exposure target the weights must sum in absolute value to, and the tolerance allowed on the net                     | § 1.1     |
| $\rho_s$, $\sigma_{MOM,s}$, $\sigma_{r,s}$                                                                                                                                | one asset's signal-return correlation, and the standard deviations of its signal and its forward return                       | § 1.1     |
| $N$, $i$                                                                                                                                                                    | lookback length, and the lag inside it running 1 to N                                                                         | § 1.0     |
| $x$, $y$, $\beta$, $\epsilon$                                                                                                                                           | one observation's signal value and forward return, the slope between them, and the part of the return the signal cannot reach | § 2       |
| $\rho$, $R^2$                                                                                                                                                               | their correlation, and its square — the share of the return's variance the signal explains                                   | § 2       |
| $\sigma_x$, $\sigma_y$, $\sigma_\epsilon$                                                                                                                                 | standard deviation of the signal, of the return, and of the unreachable part                                                  | § 2       |
| $m$, $m_g$                                                                                                    | observations sharing a bucket, and the count in bucket$g$ | § 3.2                                                                                                                        |            |
| $\mu_g$, $\sigma_g$, $\text{SE}_g$                                                                                                                                        | one bucket's true mean forward return, the sample standard deviation of the returns in it, and the standard error of its mean | § 3.2.3   |
| $H_0$, $z$, $\alpha$                                                                                                                                                      | the null that two buckets share a mean, the standardized G5 − G1 difference testing it, and the level it is tested at        | § 3.2.3   |
| G1 … G5                                                                                                                                                                        | the buckets, lowest to highest signal**within a date**                                                                  | § 3.2     |
| $\sigma_{s,t}$                                                                                                                                                                | one asset's volatility, estimated on data before that date                                                                    | § 4       |
| $R_p$, $r_f$, $\sigma_p$                                                                                                                                                  | a portfolio's return over a period, the financing rate subtracted from it, and its return volatility                          | § 5       |
| $g$                                                                                                                                                                           | gap length — periods between the end of the signal's window and the return it is scored on                                   | § 1.2     |
