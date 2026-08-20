# 02 · Building Your Own Signal

> - **Answers:** how to turn an intuition into a computable signal, and how to tell whether it carries information before backtesting it.
> - **Prerequisites:** [01 · What Is a CTA Strategy](01-what-is-cta.md); the data it runs on is [100 · The Dataset](100-dataset.md).
> - **After reading:** state a signal as a hypothesis, test it with a bar plot, normalize it, and combine horizons without drowning in noise.

---

## 1. A signal is a hypothesis, not a formula

### 1.0 The three objects

Everything in this chapter is built from three numbers, one of each per asset per date.

| Object | Symbol | What it is | Known at $t$ ? |
| --- | --- | --- | --- |
| **Weight** | $w_{s,t}$ | the share of capital held in asset $s$ on date $t$, signed — negative is a short | **yes**, you choose it |
| **Signal** | $MOM_{s,t}$ | a number computed from data available at $t$, meant to say something about what comes next | **yes**, you compute it |
| **Forward return** | $r_{s,t}$ | what the asset then goes on to deliver while the position is held | **no** — this is the unknown |

**Note (Scope).** The signal is *computed* one asset at a time, from that asset's own history;
everything downstream is a **panel** of many assets × many dates. § 3.2 ranks the assets against
each other on each date — the cross-sectional sort a CTA actually trades — and
[03](03-from-signal-to-position.md) turns those ranks into positions.

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
ending yesterday. What it keeps is a magnitude proportional to how strongly the asset trended.

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

$G$ is the gross target; the net holds at 1 only to within a tolerance $\delta$, since rebalancing
is discrete and the book drifts between trades. The two sums are independent:

| Sum | What it fixes | Typical value |
| --- | --- | --- |
| **Net**, $\sum_s w_{s,t}$ | how much *market* the book carries — the directional bet, since longs and shorts cancel here | 100% long-biased, $\approx 0$ market-neutral |
| **Gross**, the same sum over absolute weights | how much *leverage* is deployed, longs and shorts adding rather than cancelling | 200% (a 150/50 book) or 300% |

A book holding one asset at 100% and a book long 200% / short 100% carry the same net and three
times the position — which is why both sums have to be stated, and why gross is never free
([01](01-what-is-cta.md)).

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
is what lets the rest of the chapter ignore weights altogether; [03](03-from-signal-to-position.md)
carries out both operations.

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

<details>
<summary><b>Proof.</b> uncorrelated parts add their variances, so the explained share is exactly the squared correlation — 1.44% of it at 12%</summary>

Uncorrelated components add their variances,

$$
\text{Var}(y) = \beta^2 \text{Var}(x) + \text{Var}(\epsilon)
$$

and on one regressor with an intercept the explained share is $R^2 = \rho^2$. At $\rho = 0.12$,
$R^2 = 0.0144$ — which does not mean "right 1.4% of the time", but: of the variation in forward
return from one observation to the next, 1.44% is linear in the signal and 98.56% is not.

</details>

**Example.** Everything below is **one asset-date's** forward return, never a portfolio's. Take a
daily return standard deviation of $\sigma_y = 0.012$ — 120 bp, typical for a single equity ETF,
a **basis point** being 0.01%:

| Component             | Size                            | At 12% correlation |
| --------------------- | ------------------------------- | ------------------ |
| Total return          | $\sigma_y$                    | 120 bp             |
| What the signal moves | $\rho \sigma_y$               | **14.4 bp**  |
| What it does not      | $\sigma_y (1 - \rho^2)^{1/2}$ | **119 bp**   |

Across an x-axis running from $-2\sigma_x$ to $+2\sigma_x$ the trend line climbs about 58 bp end
to end, while at every $x$ the points scatter over roughly 476 bp. **A 0.6% slope inside a 4.8%
cloud** — that ratio *is* the picture.

**Note (And it is worse than that).** Part of those 119 bp is not the market's doing: pooling a
calm 2021 with a violent 2023 adds spread that standardization (§ 4) removes. Nor is a larger
$\rho$ on offer — a predictor correlating 50% with next month's return would be arbitraged away
long before you found it in anything liquid. 10–15% is a competitive market's ceiling, not a
shortfall in craft.

## 3. Two ways out of the cloud

The scatter is unreadable, but the signal may still be in it. There are two things to try, and only
the second one works.

### 3.1 Turn down `alpha`

`alpha` is a marker's opacity. Turn it far enough down — `alpha=0.05` on a few thousand points,
lower still on more — and a single point becomes nearly invisible, so only *overlap* renders and the
chart is a density map rather than a mass of ink. Below, the left panel is the before and the other
two are both the after.

**Note (Not the other alphas).** matplotlib's opacity keyword: not a regression intercept, not the
excess return a manager is paid for, not § 8's smoothing constant $\alpha$. Code font is the tell.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/alpha-opacity-dark.png">
  <img alt="Three scatter panels of forward return against a signal, drawn from 5,000 pooled asset-date observations. Left, at full opacity, they render as one solid disc with no internal structure. Middle, the same rendering at low opacity on a series where a high signal rules out deep losses: a soft density cloud with the bottom-right corner visibly bitten out, annotated high signal, no deep loss. Right, low opacity on the original points: a smooth round density with no thin region anywhere" src="figures/alpha-opacity-light.png">
</picture>

Sometimes it is enough — the middle panel, where high signal against a badly negative return has
thinned enough to read. A signal that only rules something *out* is still tradeable.

**Why it usually fails.** Three reasons that compound:

- **The density comes back smooth.** Tens of thousands of asset-date cells average into a clean
  bivariate blob, and opacity renders that faithfully. A smooth density has no feature.
- **The tilt is finer than the ink.** § 2's band is eight times taller than the trend line's whole
  rise, so the lean is smaller than the markers drawn over it.
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

**Note (The buckets are cut inside a date).** G5 does not hold the assets whose momentum was
highest *ever*; it holds, for each date, the assets whose momentum was highest **that day**.
Membership therefore changes daily, and over a long sample every asset passes through every bucket.

Five steps build it:

1. **Take a date.** Its cross-section is every asset carrying a signal that day.
2. **Rank** those assets by signal and cut into five groups: highest $MOM_{s,t}$ into G5, down to G1.
3. **Record** the forward return each asset went on to deliver, filed under its bucket.
4. **Repeat** for every date in the sample.
5. **Average** everything filed under each bucket.

**Note (Step 2 presupposes a common scale).** Ranking assets against each other only means something
if their signals are already measured on one scale, and raw momentum is not — § 4. Read step 2 as
ranking a signal that has already been made comparable; § 4 is a precondition for this section, not
a later refinement of it.

The figure runs those five left to right on a five-asset universe, so one date contributes exactly
one observation per bucket — the population, each date sitting at the slots its five assets fell
into, and the average of many with the error on it.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/bucket-construction-dark.png">
  <img alt="Six panels in two rows, each row running the same steps on a different world. Left column, forward return against signal, the population with fifteen asset-date cells marked in the same colour: on a perfect line they sit along it, on the real cloud they sit anywhere. Middle column, six dates' cross-sections of five assets plotted against rank slots G1 to G5: on the line every date rises monotonically, on the cloud the six lines cross and tangle with no order at all. Right column, mean forward return per signal bucket averaged over 400 draws with error bars: a clean staircase on the line, and on the cloud a shorter staircase from a negative G1 to a positive G5 whose error bars are a third of the bar heights" src="figures/bucket-construction-light.png">
</picture>

**The sort key is the signal, never the return.** Step 2 orders by $MOM_{s,t}$, which is known at
$t$; step 3 only *records* what followed. G1 therefore holds the lowest-**signal** observations, not
the worst performers.

**Example.** One date's cross-section of five assets, invented, filed both ways:

|   | Signal$MOM_{s,t}$ | Forward return$r_{s,t}$ | Slot by signal | Slot by return |    |
| - | ----------------------------------------------- | -------------- | -------------- | -- |
| A | +2.1%                                           | −0.4%         | G4             | G2 |
| B | −1.8%                                          | +0.9%          | G1             | G4 |
| C | +0.6%                                           | +1.3%          | G3             | G5 |
| D | +3.4%                                           | +0.2%          | G5             | G3 |
| E | −0.9%                                          | −1.1%         | G2             | G1 |

Read down *slot by signal* and the returns come out unordered — which is exactly what one date
looks like at 12% correlation. Read down *slot by return* and the ordering is perfect, and would be perfect
for **any** signal including one straight out of a random number generator, because each bar is then
reporting the sort key back to you. **The staircase is evidence only because the thing sorted on and
the thing measured are different, and the second was not knowable when the first was computed.**

One bar therefore carries three pieces of information: which fifth of the signal's range it stands
for, the average return that fifth went on to earn, and how much of that average is sampling noise.

#### 3.2.2 How the bar plot shows a trend

**The trend is the ordering, not the heights.** § 1's hypothesis was *higher signal, higher forward
return*; on a bar plot that is precisely the statement G1 < G2 < G3 < G4 < G5. A single bar's level
moves with the bucketing choice (§ 5) — the ordering is what does not.

Two further readings carry information, and nothing else on the chart does:

| Read                                                | What it establishes                                                                                                         |
| --------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| **G5 − G1, measured against the error bars** | the size of the edge next to what noise alone would draw. A rise that fits inside one error bar is not evidence of anything |
| **The direction of the slope**                | a*descending* staircase is not a dead signal — it is the same edge carrying the opposite sign                            |

A scrambled middle does not disqualify a signal: clean tails around a muddled G2–G4 is a common
shape and a perfectly tradeable one, since the tails are where the positions go.

On direction, adopt a convention and keep it: **leave the signal's sign alone and let the chart come
out upside down.** Flipping a signal the moment its staircase descends is cheap, and a dozen signals
later you will not remember which ones you flipped. Read a descending staircase as *this works,
traded short*, and carry the sign in the strategy rather than in the signal definition.

**Claim.** The ordering surfaces at all only because of step 4 — averaging shrinks the noise and
leaves the signal untouched.

<details>
<summary><b>Proof.</b> averaging leaves the signal where it was and divides the noise by the square root of m, turning 1 : 8 into 2 : 1</summary>

Take $m$ observations sharing a similar signal value. Their mean return still has expectation
$\beta$ times their mean signal — they were chosen for having nearly the same signal, so averaging
them changes it barely at all — while the noise around it falls to $\sigma_\epsilon / m^{1/2}$:

|        | One observation | Mean of 300                        |
| ------ | --------------- | ---------------------------------- |
| Signal | 14.4 bp         | 14.4 bp                            |
| Noise  | 119 bp          | $119 / 300^{1/2} \approx 6.9$ bp |
| Ratio  | 1 : 8           | **2 : 1**                    |

The left column is the scatter of § 2 and the right column is one bar of the chart. Nothing was
added — only the noise was taken away.

</details>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/noise-shrinks-dark.png">
  <img alt="Four bucket charts of the same population at 12 percent correlation, mean forward return in basis points against signal bucket, computed from 5, 30, 300 and 3,000 observations each. At m equals 5 the bars swing between minus 80 and plus 93 basis points and are not monotone; by m equals 300 they have settled into a monotone staircase from about minus 20 to plus 20 basis points, and at m equals 3,000 the error bars are barely visible" src="figures/noise-shrinks-light.png">
</picture>

The true bars are identical in all four panels — near −20 bp at G1 and +20 bp at G5. Only the error
moves, and at $m = 5$ it is larger than the whole staircase. **Sample size is not a detail of the
recipe; it is the reason the recipe works.**

**Note (Where that overstates it).** The $m^{1/2}$ assumes independence, and a panel violates it
twice over. Down the time axis, overlapping lookback windows and returns that cluster in time make
consecutive observations near-copies. Across a date, every asset in the bucket shares that day's
market move, so the observations inside one bar are not $m$ independent draws either. Both push the
effective count well below $m$, and the noise does not really reach 7 bp. The logic survives:
averaging cancels noise and leaves systematic signal.

#### 3.2.3 What the bar plot cannot show

Step 2 ranks inside a single date, so every date produces its own little staircase — five buckets
and five average returns, computed from that morning's cross-section alone. Step 5 flattens all of
them onto one picture.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/bucket-time-collapse-dark.png">
  <img alt="A horizontal time axis labelled t with five dates marked on it. Standing on each date is a small slanted panel holding that date's cross-section of five assets, signal slot G1 to G5 across and forward return up, and none of the five panels shows any ordering. An arrow labelled pool every date then average within each slot points down from the axis to a bar plot of mean forward return against signal bucket, five bars with error bars rising monotonically from about minus 20 basis points at G1 to plus 20 at G5, annotated that the ordering is the whole claim and that the chart says nothing about when the edge happened" src="figures/bucket-time-collapse-light.png">
</picture>

Step 5 integrates over $t$, and an integral hands back an area, never the shape of the function
underneath it. A staircase that is monotone over twenty years is equally consistent with an edge
that held throughout and with one that worked for five years and was flat for fifteen.

| Not on the chart                                                  | Where to look instead                                   |
| ----------------------------------------------------------------- | ------------------------------------------------------- |
| **When** the edge happened                                  | the equity curve of[04](04-understanding-backtesting.md) |
| **Who** is inside a bucket — which assets, which regime    | the composition printed under § 5's three cuts         |
| **The spread** of returns behind a bar, as against its mean | the distribution within a bucket, not its mean          |
| **How independent** the observations are                    | overlapping windows, per the Note above                 |

## 4. Risk-adjusted momentum

**Whether two assets' signals may be compared at all is an assumption, and it is yours to make.** A
universe of five hundred large-cap equities might plausibly sit on one scale already. A CTA universe
does not: 50 bp in a session is an ordinary day for an equity index and, for a Treasury future, an
event that would lead the news. So for momentum the answer is settled before any data is consulted —
the assets are **not** on a common scale, and putting them there is a precondition for § 3.2's sort.
State the assumption either way, because everything downstream inherits it.

Raw momentum is not comparable **across assets**, and a cross-sectional sort does nothing but
compare across assets. 2% monthly momentum in a Treasury ETF is a large move; the same 2% in a
semiconductor ETF is a quiet month. Rank the two against each other on raw momentum and the
semiconductor wins every time — not because its trend is stronger but because everything about it is
larger. The same failure repeats across time: 2% in the calm 2021 tape and 2% in the 2023 rate-hike
drawdown are different events.

Divide by volatility:

$$
MOM^{\text{risk-adj}}_{s,t}  =  \text{Avg}\left(\frac{r_{s,t-i}}{\sigma_{s,t}}\right),\qquad i = 1 \ldots N
$$

where $\sigma_{s,t}$ is that asset's volatility, estimated on data strictly before $t$ — a
denominator that peeks at the future contaminates the signal as surely as a numerator would (§ 10).

Every asset and every period now lands on one scale, so the ranking in § 3.2 compares like with
like — two students both scoring 80 on different exams against different cohorts have not achieved
the same thing.

**Note (A second route to the same plane).** Dividing by $\sigma_{s,t}$ is not the only way. You can
also replace the value outright by **its percentile against that asset's own past**, which lands
every asset on $[0, 1]$ by construction and needs no volatility estimate at all.

**Example.** Two assets, each with five past signal values and one for today:

| Asset | Its own past signals | Today | Beats | Percentile |
| --- | --- | --- | --- | --- |
| A | −10, 8, 4, 0, −5 | **+7** | four of five | **80** |
| B | −100, −80, 90, −60, 20 | **−70** | two of five | **40** |

Raw, `+7` against `−70` is not a comparison anybody should make. As percentiles, 80 against 40 is —
and it says A is the stronger trend *relative to its own history*, which is the only sense in which
the question has an answer. The cost is the one § 5 charges for every rank: the magnitudes are
gone.

## 5. We Need Three Graphs

§ 3.2 took the five buckets as given. Where to put the boundaries is a separate choice, and there
are three defensible answers. Below they run on identical data — 20 assets over 1,500 days, the same
cells, the same forward returns, every asset carrying the same risk-adjusted edge and its own
volatility level. Only the cut changes.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/three-bucketings-dark.png">
  <img alt="Three bucket charts side by side, mean forward return in basis points against signal bucket, computed from the same 20-asset panel by three different cuts. All three rise monotonically from G1 to G5 and look equally healthy. Under each bar are two numbers: the observation count and the share of that bucket drawn from the top quartile of volatility, whose base rate is 25 percent. Cutting on raw values gives equal counts of 5,000 but high-volatility shares of 46, 13, 9, 12 and 46 percent, so the tails are nearly all high-volatility assets. Cutting the standardized signal at fixed intervals gives counts of 782, 3,518, 16,416, 3,514 and 770 with shares of 32 and 29 percent in the tails. Cutting at each date's cross-sectional quantiles gives 5,000 in every bucket and shares flat at 24 to 26 percent" src="figures/three-bucketings-light.png">
</picture>

**Read the counts, not the bars.** All three staircases are monotone, and all three would pass
§ 3.2's test unchanged. Everything that separates them is in the two lines printed underneath.

| Cut                                     | What it answers                                                                                                    | What it distorts                                                                                                                                                                                                                       |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Raw values**                    | What the signal looks like at its own natural scale, before any modelling choice is imposed on it                  | **Volatility becomes the sort key.** Both tails are 46% high-volatility observations against a 25% base rate, and the middle is 9% — so the staircase is largely a volatility sort wearing the signal's name                    |
| **Standardized, fixed intervals** | Whether the edge survives once every asset is put on a common scale (§ 4)                                         | **Starved tails.** 782 and 770 observations in the two buckets you would actually trade, against 16,416 in the middle one you would not. Trailing vol also lags an asset's own vol break, so the tails still tilt to 32% and 29% |
| **Cross-sectional quantile**      | Whether the ordering holds using only what was knowable on the day — the only one of the three with no look-ahead | **Magnitude is discarded.** The top-ranked asset ranks identically whether it beat its peers by a nose or by a mile, and that difference carried information                                                                     |

None of the three dominates, so produce all three and read them against each other. A staircase that
survives all three cuts is a different claim from one that appears only in the first.

### Why ranking the pooled panel leaks

The obvious repair for starved tails is to rank every cell in the panel at once and split into equal
fifths. That fixes the counts and breaks something worse. Take one asset's momentum in time order —
`+1%, +2%, −1%, −2%, +4%, +5%, +3%`.

Ranked against the pooled panel — which contains every date, the ones after `t` among them — the
leading 1% sits fifth of seven and lands in a low bucket. But on the day it was observed only 1% and
2% existed, and against what was knowable then 1% was **high**. It reads as unremarkable only
because of the 5% that had not happened yet. Sorting is where look-ahead gets in, and it gets in
silently — the resulting chart looks cleaner, not dirtier.

**Correct: rank inside date `t`'s cross-section, and nothing else.** Every signal in that ranking
was on screen that morning, so no future date can reach it. The same 1% then lands in a high bucket
on a day when its peers are flat and a low one on a day when they are running — which is exactly
right, because it carried different information on those two days.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/signal-distribution-dark.png">
  <img alt="Two standard-normal density curves of the standardized signal. Left, cut at fixed intervals of one sigma: the tail groups hold 11 and 12 observations while the central groups hold 1,290 each. Right, cut at the cross-sectional quantiles: every group holds 635" src="figures/signal-distribution-light.png">
</picture>

**Note (What the cross-sectional cut needs instead).** No burn-in — that day's ranking reads only
that day, so the first date in the sample is as usable as the last. What it does need is a universe
wide enough that five buckets are not two names apiece, and members comparable enough that ranking
them means anything: § 4's standardization is a prerequisite for this cut, not an alternative to it.
The 37 ETFs of [100](100-dataset.md) give about seven per bucket.

### What none of the three shows

The composition that separates these three panels shows up only in the printed counts — which is
§ 3.2.3's point arriving with numbers attached. The bars themselves look equally healthy in all
three.

Nor does any of them say what to do with a rank once you have it. Whether G5 becomes a long and G1
a short, at what size, and whether the split is absolute or relative, is the Portfolio 1 vs
Portfolio 2 question of [03](03-from-signal-to-position.md).

## 6. Combining a slow and a fast horizon

One lookback forces a choice between stable and timely. Instead use a **fast momentum to time the
turns in a slow one** — MACD's structure, where a short EMA crossing a long one marks the entry
earlier.

**Ratio.** Conventionally about **2:1** (MACD's 26/12), but that is a starting point: find the pairing
by **grid search**, read as a **heat map**. A real edge is a contiguous warm region; one hot cell is
an artifact.

**Where it pays.** Best in **commodities** — supply-and-demand cycles drive long, persistent trends.
Equities second. **Bonds** weakest, being the most arbitraged, so deviations close fastest.

## 7. EWMA instead of a simple moving average

An SMA weights a price from 60 days ago exactly as much as yesterday's. To weight recent prices more:

```python
signal = returns.ewm(halflife=H).mean()
```

Tune the **half-life** $H$ — the lag at which a return's weight has decayed to half the weight given
to the newest one. Candidates are fractions of the lookback (1/2, 1/3, 1/5, 1/8). Grid-search them.

MACD's 9-day signal line is an **empirical solution** — a value that fit historical data, nothing
more. Every parameter here has that status, which is [06](06-overfitting-and-robustness.md)'s
subject rather than something to accept on authority.

## 8. MACD, stated precisely

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
three still have to pass § 3.2's bar plot before they earn a backtest.

| Rule         | Go long when                            | Costs                                                            |
| ------------ | --------------------------------------- | ---------------------------------------------------------------- |
| Zero-line    | MACD is above zero                      | a slow trend filter, late                                        |
| Crossover    | the histogram is above zero             | earlier, noisier — the churn is § 9's subject                  |
| Proportional | always, sized by the standardized value | none of the magnitude, but see[03](03-from-signal-to-position.md) |

## 9. Volatility clustering, and smoothing the fast leg

Volatility arrives in clusters, and a fast signal is exposed: short-lived noise flips it
long/short, and the churn eats the return in transaction costs before any edge is realized. Fix:
**smooth the fast signal** to filter the shortest cycles.

**Constraint:** the smoothing window must be **shorter than the signal's own period**. Smooth with a
long one and you have not denoised the signal — you have built another slow one and lost the
timeliness the fast leg existed for.

## 10. Information availability

Everything above assumes the signal at `t` uses only data knowable at `t`. Look-ahead bias is born
here; the execution offsets in [04](04-understanding-backtesting.md) are the second line of defense
and cannot rescue a signal contaminated at construction. The rolling-quantile rule (§5) and the
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

One caveat, which is § 4's subject: 0.024 means nothing on its own. 2.4% earned in a calm year and
2.4% earned in a violent one are not the same trend. Only *relative* sizes are ever used.

### After I compute momentum on day $t$, which return does it get paired with?

Not necessarily the next one. Three spans sit on the timeline, in this order:

| Span                    | What it holds                                                                       | Typical size          |
| ----------------------- | ----------------------------------------------------------------------------------- | --------------------- |
| **Lookback**      | the$N$ returns the signal averages, ending at $t-1$                             | 20–250 periods       |
| **Gap**           | $g$ periods thrown away — neither averaged into the signal nor scored against it | 0, a week, or a month |
| **Paired return** | $r_{s,t+g}$, the one period the signal is judged on                               | one period            |

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/signal-return-alignment-dark.png">
  <img alt="Two panels of cells laid on a timeline, one cell per period. The top panel is one observation: eight filled cells bracketed as the lookback the signal averages, then three dashed empty cells bracketed as the discarded gap, then a single filled cell bracketed as the one the signal is scored on, with a dotted vertical line marking that the signal is computed from the cells to its left only. The lower panel repeats the same pattern for dates t, t plus one and t plus two, each shifted one cell right, so the lookbacks overlap in all but one cell while the three scored cells form a descending diagonal, annotated one return per date and no two dates share one" src="figures/signal-return-alignment-light.png">
</picture>

**Two ways to write the same thing.** Both produce an identical pairing table, so use whichever
reads better in your code:

| Form                       | What it does                                                                                       | Where you meet it                                                        |
| -------------------------- | -------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| Slide the return column    | pairs$MOM_{s,t}$ with $r_{s,t+g}$ rather than $r_{s,t}$                                      | `ret.shift(-g)` before the join                                        |
| Pull the window's end back | builds the signal from$r_{s,t-g-i}$, $i = 1 \ldots N$, then pairs it with $r_{s,t}$ as usual | 12-1 momentum: a twelve-month window that stops one month short of today |

The `-1` in *12-1* **is** the gap.

**Why leave one at all.** Two reasons, and they are not the same kind of reason:

- **Executability** — a hard floor. § 1's window already ends at $t-1$, so at $g = 0$ the signal
  is knowable before the period it is scored on begins. Anything tighter is look-ahead (§ 10), not
  a modelling choice.
- **Reversal** — a judgement call, and the one worth thinking about. A trend that has just formed
  tends to hand a little of it back: the flow that built it is spent, and an over-bought book
  unwinds. Score the signal on that period and you are measuring the trend and its immediate rebate
  netted into one number — which is how a real edge arrives at the bar plot looking flat, or
  upside down.

**What the gap costs.** It does not remove only the rebate; it removes the opening of the trend
too. The longer the gap, the staler the signal and the less of the move you are still present for.
So $g$ trades one against the other — and it is a **hyperparameter**: running $g$ at one day, one
week and one month and keeping whichever bar plot looks best is precisely what
[06](06-overfitting-and-robustness.md) warns about. Set it from execution reality and a prior about
how long the rebate lasts, never from the prettiest staircase.

**One check.** The two forms must agree. If you slide the return column and the $MOM$ values move
as well, the edit reached the signal, which it never should.

The lower panel is also where § 3.2.2's caveat comes from. Step one date forward and the lookback
keeps all but one of its cells, so neighbouring signals are nearly the same number — the reason the
effective sample sits well below $m$.

## Appendix · Notation

Throughout, $s$ indexes the asset and $t$ the date. The signal is computed per asset, so $s$ is
dropped inside constructions that never leave one asset (§§ 7–8); it carries weight everywhere the
assets are ranked against each other.

| Symbol                                                                                                            | Means                                                                                                                         | First used |
| ----------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- | ---------- |
| $s$, $t$                                                                                                      | the asset, and the date in periods (days here)                                                                                | § 1       |
| $r_{s,t}$, $MOM_{s,t}$, $w_{s,t}$                                                                           | that asset's return in that period, the momentum signal it produces, and the share of capital that signal earns it            | § 1.0     |
| $R_t$                                          | the portfolio's return on that date,$\sum_s w_{s,t} r_{s,t}$ | § 1.1                                                                                                                        |            |
| $G$, $\delta$                                                                                                 | the gross-exposure target the weights must sum in absolute value to, and the tolerance allowed on the net                     | § 1.1     |
| $\rho_s$, $\sigma_{MOM,s}$, $\sigma_{r,s}$                                                                  | one asset's signal-return correlation, and the standard deviations of its signal and its forward return                       | § 1.1     |
| $N$, $i$                                                                                                      | lookback length, and the lag inside it running 1 to N                                                                         | § 1.0     |
| $x$, $y$, $\beta$, $\epsilon$                                                                             | one observation's signal value and forward return, the slope between them, and the part of the return the signal cannot reach | § 2       |
| $\rho$, $R^2$                                                                                                 | their correlation, and its square — the share of the return's variance the signal explains                                   | § 2       |
| $\sigma_x$, $\sigma_y$, $\sigma_\epsilon$                                                                   | standard deviation of the signal, of the return, and of the unreachable part                                                  | § 2       |
| $m$                                                                                                             | observations sharing a bucket                                                                                                 | § 3.2     |
| G1 … G5                                                                                                          | the buckets, lowest to highest signal**within a date**                                                                  | § 3.2     |
| $\sigma_{s,t}$                                                                                                  | one asset's volatility, estimated on data before that date                                                                    | § 4       |
| $H$                                                                                                             | EWMA half-life, in periods                                                                                                    | § 7       |
| $P_t$, $\Delta_{t-j}$                                                                                         | price on that date, and the one-period change at that lag                                                                     | § 8       |
| $n_f$, $n_s$                                                                                                  | fast and slow EMA spans, conventionally 12 and 26                                                                             | § 8       |
| $\alpha_f$, $\alpha_s$                                                                                        | their smoothing constants, two over span plus one                                                                             | § 8       |
| $c_i$, $k_j$                                                                                                  | MACD's net weight on the price at that lag, and its kernel weight on the price change                                         | § 8       |
| $g$                                                                                                             | gap length — periods between the end of the signal's window and the return it is scored on                                   | Background |

**Note (Collisions to watch).** $R_t$ is the portfolio's return on a date (§ 1.1); $R^2$ is a share
of variance (§ 2). Lowercase $\delta$ is the tolerance on net exposure (§ 1.1); uppercase
$\Delta_{t-j}$ is a one-period price change (§ 8). They share a letter and nothing else. Three quantities wear a $\sigma$ and they
are not interchangeable:
$\sigma_y$ is the spread of forward return across the pooled cloud (§ 2) — the panel-wide version of
§ 1.1's per-asset $\sigma_{r,s}$ — while $\sigma_\epsilon$ is the part of it the signal cannot reach
(§ 2) and $\sigma_{s,t}$ one asset's trailing volatility on one date (§ 4). Likewise $w_{s,t}$ is a position and $k_j$ a kernel weight, which is why the latter is
not written $w$. And § 3.1's `alpha` is a plotting keyword, not $\alpha$ the smoothing constant
and not a regression intercept — code font against maths is the tell. Lowercase $g$ is the gap, unrelated to the buckets G1 … G5. Chapter
[01](01-what-is-cta.md) uses $s$ for a signed share count; here it is always the asset.

---

## Next → [03 · From Signal to Position](03-from-signal-to-position.md)

Before moving on, **build the 21-day momentum signal across the 37-ETF universe and plot its bucket
chart three ways** — raw values, standardized, and cross-sectional quantile — then compare them. Chapter 03 assumes you have a signal
you already believe in.

You should be able to explain:

- [ ] Why a scatter plot proves nothing at a realistic 10–15% correlation
- [ ] Why the sort key must be the signal and never the forward return
- [ ] Why a gap sits between the signal's window and the return it is scored on, and what that gap costs
- [ ] Why the buckets are cut inside a date, and that the time axis is what pooling costs
- [ ] Why fixed-interval buckets starve the tails and pooled-panel ranking leaks the future
- [ ] Why MACD is momentum with a hump-shaped kernel rather than a separate indicator

[← 01](01-what-is-cta.md) · [Index](00-index.md) · reference: [07 · Toolbox](07-toolbox-pandas.md)
