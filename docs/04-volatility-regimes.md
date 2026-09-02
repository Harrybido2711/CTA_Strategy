# 04 · Volatility Regimes

> - **Answers:** why MACD earns its edge in a quiet tape and hands it back in a violent one, what "violent" means as a number rather than a mood, and how to fold that number into the book without paying twice for information the signals already carry.
> - **Prerequisites:** [03 · Shaping the Lookback](03-shaping-the-lookback.md) § 3.2 for MACD's kernel, which § 1.2 takes apart, and § 4 for volatility clustering; [02 · Testing a Signal](02-testing-a-signal.md) § 3.2, whose bar plot is still the only gauge.
> - **After reading:** state high volatility as a ratio, derive why a fast/slow rule's edge scales with drift over amplitude, say why a trailing volatility estimate arrives too late to correct with, read an implied-volatility index as a forecast, cut one into regime labels, and test whether the label carries anything your trend signals do not already own.

---

## 1. Why MACD hands its edge back in a violent tape

[03](03-shaping-the-lookback.md) built MACD out of two exponential averages and then, in its § 4,
walked it into a wall: a market that suddenly gets loud breaks the rule regardless of how the two
spans are tuned, because the failure belongs to the market rather than to the parameters. This
chapter starts at that wall. § 1 says precisely what "loud" is and how much of the edge it costs;
§§ 2–6 build the correction.

### 1.1 What "high volatility" means

**Definition (High volatility).** A state of the market, not a direction of it. Date $t$ sits in a
high-volatility state when $\sigma$, the standard deviation of the period's move without regard to
its sign, is large relative to the same market's own ordinary level $\sigma_{\text{calm}}$. It is
therefore a **ratio**, $\sigma / \sigma_{\text{calm}}$, and never an absolute level: 1.2 percent a
day is unremarkable for a single technology name and a crisis for a two-year note.

Three things it is routinely confused with, and is not:

| A high-volatility state is not | It is |
| --- | --- |
| a fall in price | a widening of the day's range, in **either** direction |
| a trend | the spread around whatever trend there is |
| one large day | a stretch of dates that stays wide — days to months |

**Example (Reading the ratio off an index).** An implied-volatility index quotes an annualized
percentage, so the daily move it implies is roughly $v_t / (252)^{1/2} \approx v_t / 15.9$.

| Index level $v_t$ | Implied daily move | Reads as |
| --- | --- | --- |
| 12 | 0.75 percent | the ordinary tape |
| 20 | 1.3 percent | busy |
| 40 | 2.5 percent | a crisis |

A move from 12 to 40 is not "a bad week". It is the same market with its daily range widened by a
factor of **three**, and § 1.2 is what that factor does to a trend signal.

The state is worth naming at all only because it persists. [03 § 4](03-shaping-the-lookback.md)
established that amplitude is autocorrelated while direction is not — large moves follow large
moves regardless of sign — so a market that was loud yesterday is likely to be loud today. A
property that flickered day to day could not be labelled, conditioned on, or corrected for.

**Definition (Volatility regime).** A stretch of dates over which $\sigma$ is roughly constant and
materially different from the stretch on either side. A **regime shift** is the boundary between two
such stretches.

**Note (Regimes are entered abruptly and left slowly).** The two boundaries are not symmetric. News
prints and the market's view of $\sigma$ steps up within the session; it then decays over weeks and
settles somewhere **above** where it started, because the thing the news was about has not been
resolved. The consequence matters for what follows: the damage a burst does to a trend rule is not
one bad day but the entire decay, over which the rule keeps trading at a degraded ratio. § 2's
figure draws that shape.

### 1.2 Why the edge falls with it

**Claim.** A fast/slow rule's ability to identify the direction of the trend scales with
$\mu / \sigma$ — the drift per period against the amplitude around it — and with nothing else that
the market can move. Tripling $\sigma$ while the drift is unchanged cuts it to a third.

**Proof.** [03 § 3.2](03-shaping-the-lookback.md) showed MACD is a **fixed** weighted sum of
one-period price changes,

$$
\text{MACD}_t = \sum_j k_j \Delta_{t-j} , \qquad
k_j = (1-\alpha_s)^{j+1} - (1-\alpha_f)^{j+1} \geq 0
$$

where $\Delta_{t-j}$ is the price change at lag $j$ and $k_j$ the kernel weight the two spans give
it. Write each change as a drift plus a shock,

$$
\Delta_{t-j} = \mu + \sigma u_{t-j}
$$

with $\mu$ the mean change per period, $\sigma$ its standard deviation, and $u_{t-j}$ a shock of
mean zero and unit variance, uncorrelated across lags. Take the mean and the variance term by term:

$$
E\left[ \text{MACD}_t \right] = \mu \sum_j k_j , \qquad
\text{SD}\left[ \text{MACD}_t \right] = \sigma \left( \sum_j k_j^2 \right)^{1/2}
$$

so their ratio splits cleanly into a market part and a kernel part:

$$
\frac{E\left[ \text{MACD}_t \right]}{\text{SD}\left[ \text{MACD}_t \right]}
= \frac{\mu}{\sigma} \cdot \frac{\sum_j k_j}{\left( \sum_j k_j^2 \right)^{1/2}}
$$

The second factor is fixed by $n_f$ and $n_s$ alone; no state of the market touches it. Every effect
the tape has on the ratio therefore runs through $\mu / \sigma$, and a burst that leaves the trend
where it was while tripling $\sigma$ divides the whole ratio by three.

**Example (What the two factors are worth at 12/26).** With $\alpha = 2/(n+1)$ the kernel part is
available in closed form — $\sum_j k_j = (n_s - 1)/2 - (n_f - 1)/2 = 7$ and
$\left( \sum_j k_j^2 \right)^{1/2} \approx 1.14$ — so the kernel contributes about **6.1**. Take a
trend worth an annualized Sharpe near 0.5, which is $\mu / \sigma \approx 0.03$ per day:

| Tape | $\mu / \sigma$ | ratio | $\text{P}\left( \text{sign of MACD} = \text{sign of } \mu \right)$ | edge over a coin |
| --- | --- | --- | --- | --- |
| calm | 0.030 | 0.185 | 0.573 | 7.3 points |
| three times as loud | 0.010 | 0.062 | 0.525 | 2.5 points |

reading the probability as $\Phi$ of the ratio, which holds when the shocks are roughly normal.
Because $\Phi$ is close to linear near zero, **the edge over a coin falls in almost exact proportion
to $\sigma$**: 7.3 points becomes 2.5, not 6.

**Note (The drift does not rise with the noise, and that is the whole point).**
[03 § 4](03-shaping-the-lookback.md)'s clustering is a statement about $|r|$ and explicitly not
about $r$ — amplitude persists, direction does not. A burst therefore multiplies the denominator and
leaves the numerator where it was. If $\mu$ scaled with $\sigma$ the ratio would be invariant, the
signal would work equally everywhere, and this chapter would have nothing to correct.

**Note (Risk-adjusting the signal does not repair the ratio).** [02 § 4](02-testing-a-signal.md)
divides a signal by the asset's trailing volatility before ranking, and that is worth doing — it
makes values comparable across assets and stops the loudest asset dominating the book. It does not
touch what is measured above. Dividing $\text{MACD}_t$ by $\sigma$ divides its mean and its standard
deviation alike, leaving the ratio and the sign exactly where they were. Standardizing fixes the
**size** of the position; it cannot improve the **quality** of the sign.

**Note (On log prices the shock is a return).** [03 § 3.1](03-shaping-the-lookback.md) writes the
two EMAs on the price, so $\Delta$ is a price change and $\mu, \sigma$ carry its units. Run the same
pair on the log price — the usual implementation — and $\Delta$ is the one-period return outright,
with $\sigma$ the return volatility of § 1.1. The proof is unchanged either way: it uses only that
the kernel is fixed and that one number scales every shock.

### 1.3 And the bill rises while the edge falls

The ratio is one blade. The second is that the same burst raises what the rule pays to stay in the
market, through three further channels — and the table below sets all four side by side.

| What a burst changes | Direction | Why |
| --- | --- | --- |
| the edge on each date | **falls**, like $\sigma_{\text{calm}} / \sigma$ | § 1.2 |
| the number of round trips | **rises** — the two legs touch whenever noise carries one across the other, and how often that happens is set by the amplitude, not by the rule ([03 § 3.3](03-shaping-the-lookback.md)) | [03 § 4](03-shaping-the-lookback.md) |
| the cost of each round trip | **rises** — spreads are widest and depth thinnest in exactly the state that produces the extra trades ([00](00-pipeline.md)) | market structure |
| the sign of each round trip | **wrong on average** — the downward spike flips the book short at the bottom and the snap-back flips it long at the top | [03 § 4](03-shaping-the-lookback.md) |

The fourth row is the one that makes the arithmetic ugly. Whipsaw is not scatter around the right
answer; it is the opposite of the right answer, repeated on a schedule the noise sets.

**Claim.** Past some multiple of the calm-state amplitude, a fast/slow rule's net edge is not merely
smaller — it is negative, and the rule pays to trade.

Two quantities are moving in opposite directions: a gross edge falling roughly like $1/\sigma$
against a cost rising faster than $\sigma$, because both the trade count and the price of each trade
climb together. A falling curve and a rising one cross, and past the crossing the difference has a
sign. Where it crosses is an empirical number that differs by market and by rule — § 5.1 is how it
is measured rather than assumed.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/edge-vs-volatility-dark.png">
  <img alt="Two stacked panels sharing a horizontal axis of volatility relative to calm, running from one to three and a half times. The upper panel plots the probability that MACD's sign matches the drift's sign: it starts at 0.573 in a calm tape and decays toward a dashed line at 0.5 labelled a coin, passing 0.525 at three times the calm amplitude. The lower panel plots two curves in basis points per year: a gross edge falling from four hundred like one over sigma, and a cost rising from one hundred faster than sigma because there are more round trips and each one is dearer. They cross a little below 1.8 times, and the region past the crossing, where cost exceeds gross edge, is shaded violet and the crossing itself is marked net turns negative" src="figures/edge-vs-volatility-light.png">
</picture>

Read the two panels as one argument. The upper one is § 1.2 — the rule's sign decaying toward a coin
flip as the tape widens. The lower one is the table above: the gross edge that decay leaves behind,
against a bill that grows while it shrinks. The crossing is where a signal stops being weak and
starts being harmful.

### 1.4 Why nothing that reads only the signal can repair this

[03 § 4](03-shaping-the-lookback.md) closed on the two local fixes — a **smoother** on the computed
signal, and a **deadband** requiring a crossing to clear a margin before the position flips. Both
work on the churn, and neither can do what § 1.3 asks, for one reason: **neither of them knows the
tape is violent.** Each damps every date alike, so each pays on the quiet days to protect the loud
ones, and neither can tell the difference between a crossing worth 7.3 points and a crossing worth
2.5. That is the ceiling on anything reading only the signal.

The measurement has the same blind spot. [02 § 3.2.4](02-testing-a-signal.md) already stated it in
general form: the bar plot's step 5 averages over $t$, and an integral hands back an area rather
than the shape of the function under it. A signal earning +26 bp in G5 across the whole sample is
equally consistent with +30 bp every year and with +40 bp in calm markets against −20 bp in violent
ones. Those are not the same strategy — the second is one you would size differently or switch off —
and the one-dimensional plot cannot say which you have, because it has already added them together.

Clearing the ceiling means promoting the state of the market to a **variable**: measured, named, and
carried alongside the signal rather than filtered out of it. A variable you can observe is a
variable you can condition on.

### 1.5 The correction, end to end

Six questions, in the order they have to be answered. The rest of the chapter is one per step.

| # | The question | Answered in |
| --- | --- | --- |
| 1 | How wide is the tape **today** — not how wide has it been? | § 2 rules out the trailing estimate; § 3 buys a forecast instead |
| 2 | Whose fear labels *this* sleeve? | § 3.4 |
| 3 | How does a continuous level become a small set of named states? | § 4 |
| 4 | Does the edge actually differ across those states? | § 5.1 |
| 5 | Is the state new information, or a restatement of what the book already runs? | § 5.2 |
| 6 | Where does the answer get spent? | § 6 |

**Note (Steps 4 and 5 are different questions).** It is possible — common, in fact — for the answer
to step 4 to be yes and to step 5 to be no: the edge genuinely differs by regime, and the regime
still adds nothing to a return forecast, because the signals already in the book move with it. That
combination is not a failure. § 6.2 is where such an answer is spent.

## 2. The obvious meter, and why it is too late

Step 1 of § 1.5, first attempt. The obvious way to measure how wide the tape is, is to measure how
wide it has just been.

**Definition (Realized volatility).** The standard deviation of the last $L$ returns, annualized.
Taking the returns as centred,

$$
\sigma^{\text{real}}_t = \left( \frac{1}{L} \sum_{i=0}^{L-1} r_{t-i}^2 \right)^{1/2}
$$

where $L$ is the window length in periods and $r_{t-i}$ the return at lag $i$. It is free, needs no
instrument beyond the price series, and it does not work for this purpose.

**Claim.** A trailing estimate over $L$ periods reaches only half of its eventual level about $L/2$
periods after a shift, and its full level only after $L$ — so with a monthly window it reports a
burst that has already ended.

**Proof.** Square the definition and it is a flat average of the last $L$ squared returns — the
boxcar kernel of [03 § 1.1](03-shaping-the-lookback.md), which weights every lag alike. Suppose the
tape jumps from $\sigma_{\text{calm}}$ to $\sigma_{\text{high}}$ at date 0 and stays there. At date
$t < L$ exactly $t+1$ of the $L$ terms are drawn from the new regime and the rest from the old, so

$$
E\left[ \left(\sigma^{\text{real}}_t\right)^2 \right] = \frac{t+1}{L} \sigma_{\text{high}}^2 + \frac{L-t-1}{L} \sigma_{\text{calm}}^2
$$

The estimate therefore climbs **linearly** from the old level to the new one, reaching half the rise
at $t \approx L/2$ and the whole of it only at $t = L-1$. At $L = 21$ that is ten sessions to half
and twenty-one to full.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/regime-lag-dark.png">
  <img alt="Two stacked panels sharing an axis of trading days since a news event, from minus forty to plus sixty. The upper panel plots the absolute daily return as vertical bars: quiet either side, with a burst of three to four percent moves in the eight sessions after day zero. The lower panel plots annualized volatility. The implied line jumps from about eleven percent to forty-three on the day the news prints and decays smoothly back toward thirteen. The realized twenty-one-day line barely moves on the day, climbs steadily, and does not peak until session twenty-one, an interval marked by a double-headed arrow labelled twenty-one sessions late — by which time the burst in the upper panel has been over for two weeks" src="figures/regime-lag-light.png">
</picture>

The upper panel is the event and the lower panel is the two answers to it. It is also § 1.1's
asymmetry drawn: the implied line steps up inside a session and takes weeks to come back down. By
the time the trailing line peaks, the burst it is describing has been over for a fortnight, and a
position sized off it would be de-risking into the recovery.

**Note (Shortening the window does not rescue it).** The lag falls with $L$ and the noise rises with
it: the relative standard error of a variance estimate from $L$ observations runs about
$\left( 2/L \right)^{1/2}$, so $L = 5$ buys a two-session lag at the price of a 63 percent error on
the level. Every $L$ is either late or unreliable, and an EWMA ([03 § 1.2](03-shaping-the-lookback.md))
only re-shapes the same trade-off — a short half-life reacts sooner and jitters more. The problem is
not the window. **It is that a backward-looking estimator has no term for news that has just
arrived.**

## 3. What the option market already knows

Step 1, second attempt: stop estimating the state and buy somebody's forecast of it.

### 3.1 Implied volatility

Somebody does have a term for news that has just arrived. An option's value depends on how far the
underlying might travel before it expires, so anyone quoting one is quoting a volatility forecast
whether they name it or not.

**Definition (Implied volatility).** The value of $\sigma$ that makes a pricing model reproduce an
option's traded price. It is a forecast for the life of the contract, read out of a price rather
than estimated from history.

**Claim.** An option's price is strictly increasing in $\sigma$, so that inversion is well defined —
one price, one implied volatility.

**Proof.** A call pays $\text{max}(S_T - K, 0)$ at expiry, which is a convex function of $S_T$.
Raising $\sigma$ spreads the distribution of $S_T$ while leaving its forward mean where it was, and
the expectation of a convex function rises under a mean-preserving spread. So the price is
monotone in $\sigma$, and a monotone map is invertible.

**Note (What the forecast is worth is a separate question).** Implied volatility is what the market
charges, not what will happen, and the two differ systematically — insurance is sold at a premium to
its expected cost. That gap is a strategy in its own right and not this chapter's subject. Here the
index is used only as a **state label**, for which being a live consensus is enough.

### 3.2 VIX, stated precisely

**Definition (VIX).** A constant-30-day implied volatility for the S&P 500, built from the prices of
the whole strip of out-of-the-money options at two expiries that bracket 30 calendar days.

Four steps produce it:

1. **Pick two expiries** with $\tau$, the time to expiry, between **23 and 37 days** — one below 30
   and one above.
2. **From each expiry's whole strip of strikes**, compute that expiry's implied variance. Using the
   strip rather than a single at-the-money option is what makes the number a property of the market
   rather than of one contract.
3. **Interpolate the two linearly in $\tau$** to land on exactly 30 days.
4. **Annualize**, take the square root, and quote it as a percentage.

**Why the 23-to-37 window.** Listed expiries do not fall on a 30-day schedule, so on most dates
there is no contract with exactly 30 days left. The band is wide enough that two expiries always
bracket the target and narrow enough that the interpolation is over a short distance: 28 days and 35
days bracket 30, and the answer is five-sevenths of the way from the first to the second.

### 3.3 Variance or volatility

$$
\text{VIX}_t = 100 \left( \sigma^2_{30,t} \right)^{1/2}
$$

where $\sigma^2_{30,t}$ is the annualized 30-day implied **variance** the strip formula produces.
Step 2 computes a variance; step 4 takes its square root. **The published level is therefore already
a volatility, in percentage points** — a VIX of 20 means an annualized 20 percent — and squaring it
recovers the variance underneath.

**Note (Decide which one your formula wants).** This is not bookkeeping. Variance is what is
additive — across time, and across independent sources of risk — and volatility is not. Anything
that rescales a horizon or adds contributions together needs $\sigma^2$, so what goes into such a
formula is $\left( \text{VIX}_t / 100 \right)^2$; anything compared against a return in the same
units needs $\sigma$. Reaching for the index level because it is the number on the screen is how a
factor of a square root goes missing, and the error is invisible: the result is still a
plausible-looking positive number.

### 3.4 One index for equities, another for rates

**Claim.** One equity index's implied volatility is a usable regime label for most sleeves, even
though it is computed from one market.

The reason is what a panic does to correlations. In calm markets the sleeves answer to different
things and move mostly apart; when a large enough shock arrives, the same levered participants are
selling all of them at once to raise cash, and the cross-asset correlations run toward one. So the
states in which the label matters most are exactly the states in which one market's fear is every
market's fear. It is an empirical regularity rather than a theorem, and it holds better for the
extremes than for the middle.

**Note (Rates are the genuine exception).** The Treasury market's volatility is close to unrelated
to the equity market's, because the two are frightened by different things: equity volatility is
about growth and earnings, rate volatility about policy, inflation prints and auctions. A rate
sleeve labelled by VIX will be labelled wrongly, and the instrument built for it is **MOVE**, the
same construction run on Treasury options.

| Sleeve | Regime index | What its spikes are about |
| --- | --- | --- |
| Equities, credit, most commodities | **VIX** | growth and earnings shocks, and forced deleveraging |
| Rates, and anything priced off the curve | **MOVE** | policy surprises, inflation prints, auction stress |

**Note (Neither is in this repo's sample).** `CTA_data/` holds 37 price series and no volatility
index ([100](100-dataset.md)), so both have to be fetched before any of § 5 can be run.

## 4. From an index level to a regime label

Step 3. §§ 2–3 produce a number per date; § 5 needs a **label** — a small set of named states —
because a continuous variable cannot be a row of a table.

### 4.1 Why the level will not bucket

Write $v_t$ for the index level on date $t$. Its distribution is the obstacle.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/vix-bucketing-dark.png">
  <img alt="Two histograms of the same illustrative sample of volatility index levels. On the left, plotted against the raw level from 8 to 90, the mass piles into a narrow spike between 12 and 20 and trails off into sixty points of near-empty tail, annotated half the sample inside a 6-point band. On the right, plotted against the natural logarithm of the same values, the distribution is close to symmetric, and two dashed vertical lines at 3 and 4 — labelled e cubed approximately 20 and e to the fourth approximately 55 — divide it into three regions labelled calm, stressed and crisis" src="figures/vix-bucketing-light.png">
</picture>

The level spends most of its life in a band a few points wide and occasionally reaches four times
that. Cut it into equal-width bins and the first bin holds nearly everything while the top bins hold
a handful of days each — which is the opposite of what a bucket chart needs, since
[02 § 3.2.2](02-testing-a-signal.md)'s whole argument runs on having enough observations inside each
bucket for the averaging to bite.

**Note (Is the level something you can model at all?).** [Market 101 § 9.2](../market_knowledge/market-101-foundations.md)
gives the reason returns are modelled and prices are not: a price wanders without a level to come
back to, and two unrelated prices will show a high correlation for that reason alone. A volatility
index is better behaved — it cannot grow without bound, it has a floor, and it visibly reverts,
spending long stretches near its lows and returning there after each spike. Treat it as
mean-reverting rather than as stationary in any strict sense, and prefer constructions that depend
on **where the level sits relative to its own history** over ones that depend on the level's
absolute value.

### 4.2 The log-ceiling cut

**Definition (Log-ceiling bucket).** Take the natural log of the level and round up to the next
integer:

$$
g_t = \text{ceil}\left( \ln v_t \right)
$$

where $g_t$ is the regime label on date $t$ and `ceil` is the smallest integer at or above its
argument. Because $\ln$ compresses the sparse upper tail and stretches the crowded lower band, the
integer cuts land at levels that are multiplicatively rather than additively spaced:

| Label $g_t$ | Level range | Reads as |
| --- | --- | --- |
| 3 | $v_t \in (7.4, 20.1]$ | calm — the ordinary tape |
| 4 | $v_t \in (20.1, 54.6]$ | stressed |
| 5 | $v_t \in (54.6, 148.4]$ | crisis |

The boundaries are $e^3$ and $e^4$, and they are close to where a practitioner would have drawn the
lines by hand. That is the construction's real virtue: **the cuts are fixed, so a date's label means
the same thing in 2015 and in 2020**, and the labels are legible without a lookup table.

**Note (Tuning the granularity).** Three buckets over the whole range is coarse. A multiplier
recovers as many as wanted,

$$
g_t = \text{ceil}\left( c \ln v_t \right)
$$

with the boundaries at $e^{k/c}$ for integer $k$: at $c = 2$ they fall near 7.4, 12.2, 20.1, 33.1
and 54.6, giving five live buckets over the same range. $c$ is a hyperparameter like any other, and
picking it by which value produces the best-looking grid is what
[07](07-overfitting-and-robustness.md) is about.

### 4.3 The rolling-quantile cut

The alternative is [02 § 3.2.1](02-testing-a-signal.md)'s own machinery, applied to the index
instead of to the signal: rank the dates by $v_t$ and cut at the quintiles.

**The ranking must be rolling, never full-sample.** A quintile computed over the whole history uses
2020's levels to label 2015's dates, which is look-ahead bias of the plainest kind
([02 § 6](02-testing-a-signal.md)) — and it is easy to commit here, because the index feels like
context rather than like data. Rank each date against a trailing or expanding window only.

| | Log-ceiling | Rolling quantile |
| --- | --- | --- |
| **Boundaries** | fixed at $e^{k/c}$, the same in every year | move with the window |
| **Group sizes** | very unequal — the crisis bucket may hold 3 percent of the sample | equal by construction |
| **A label means** | an absolute level of market fear | a rank against the recent past |
| **Comparable across time** | yes | no — the same $v_t$ can be G5 one year and G3 the next |
| **Look-ahead risk** | none, the cuts use no data | real, if the window is not trailing |

Neither dominates. The log cut is the one to reach for when the question is *what happens in a
crisis*, because it holds the definition of "crisis" still; the quantile cut is the one for *how
does the edge vary across the range*, because it guarantees each bucket is populated.

## 5. Correcting the signal with the label

### 5.0 What is on the table now

Each date now carries three numbers rather than two: a signal value, a forward return, and a regime
label $g_t$. Steps 4 and 5 of § 1.5 are the two questions that can be asked of that, and they are
not the same question:

- **Does the edge differ by regime?** — a conditioning question, answered by § 5.1.
- **Does the regime carry information the signal does not already have?** — an incremental question,
  answered by § 5.2.

### 5.1 Conditioning — the two-way sort

Put the signal buckets across and the regime labels up, and report the mean forward return in every
cell. It is [02 § 3.2](02-testing-a-signal.md)'s bar plot run once per regime, laid side by side so
the rows can be compared — equivalently, a **conditional model**: sort first on the state, then on
the signal within it.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/regime-signal-grid-dark.png">
  <img alt="A three-by-five grid of mean forward returns in basis points, signal buckets G1 to G5 across and volatility regime up: calm, stressed, crisis. The calm row, holding 75 percent of the sample, rises monotonically from minus 24 to plus 26 basis points. The stressed row, 22 percent of the sample, rises about half as steeply from minus 14 to plus 15. The crisis row, 3 percent of the sample, has no ordering at all — plus 4, minus 3, plus 2, minus 5, plus 3 — and its shading is flat across the row" src="figures/regime-signal-grid-light.png">
</picture>

Read it by rows, and the reading is the finding. A staircase in the calm row that flattens through
the stressed row and disappears in the crisis row is § 1.2 measured rather than derived: the same
rule, the same parameters, a third of the ratio. It also says the signal is a **calm-market
signal** — and the one-dimensional plot of [02](02-testing-a-signal.md), which is the
sample-weighted average of the three rows, reports the calm row lightly diluted and never mentions
that the other two exist.

The grid is the correction, not yet the fix. What it licenses is a *shape* for the fix — exposure
that falls as the row flattens, and something other than a trend rule in the row that has no
staircase left — and where that shape is imposed is § 6.2.

**Note (What a second axis costs).** The cells partition the same sample, so the count in each falls
by the number of regime rows and the error bars of [02 § 3.2.3](02-testing-a-signal.md)
widen by its square root. A one-way plot puts $N/5$ dates in a bar; three rows put $N/15$ in a cell, so every error bar is
$3^{1/2} \approx 1.7$ times wider, and at five rows it is $5^{1/2} \approx 2.2$. **Keep the regime
axis coarse** — three labels, not five — because the axis being added is the one with less to say
per level.

**Note (And the row you most want is the worst measured).** The crisis row is 3 percent of the
sample, so its cells hold roughly $N/167$ dates against a one-way bar's $N/5$: error bars about
$\left( 167/5 \right)^{1/2} \approx 5.8$ times wider. A flat crisis row is therefore *not yet*
evidence that the edge dies in a crisis — it is equally consistent with an edge nobody has enough
crisis days to measure. Report the count in every cell next to the mean, and treat a row you cannot
measure as unknown rather than as zero.

### 5.2 Residualizing — is any of it new?

The second question is whether the regime tells you anything the signals already in the book do not.
Regress the candidate on the incumbents and keep what is left:

$$
x_t = \beta_0 + \sum_j \beta_j x_{j,t} + \epsilon_t
$$

where $x_t$ is the candidate signal on date $t$, $x_{j,t}$ the signals already in the book — momentum
and MACD, here — $\beta_j$ their fitted coefficients, and $\epsilon_t$ the residual. Then run
[02 § 3.2](02-testing-a-signal.md)'s bar plot on $\epsilon_t$ in place of $x_t$.

**Claim.** If the staircase survives on $\epsilon_t$, the candidate carries an edge the existing
signals do not already own.

**Proof.** Least squares picks $\beta$ by setting the derivative of the summed squared error to
zero, which yields one normal equation per regressor,

$$
\sum_t \epsilon_t x_{j,t} = 0 \quad \text{for every } j, \qquad \sum_t \epsilon_t = 0
$$

the second from the intercept. A centred variable with zero sum of products has zero sample
covariance, so $\rho(\epsilon, x_j) = 0$ for every incumbent signal. By
[02 § 1.1](02-testing-a-signal.md) a portfolio's expected return runs entirely through the
correlation between what sets the weights and the forward return; a weight vector built on
$\epsilon_t$ is therefore uncorrelated with every weight vector the book already runs, and whatever
it earns is earned somewhere the book is not standing.

**Note (Orthogonal is not independent).** Zero *linear* correlation is the whole of what least
squares buys. A residual that is large exactly when MACD is large **in absolute value** is a
function of MACD that the regression cannot see and did not remove, and its bar plot would report
the incumbent's information back as new. Where that is a live worry, add the transform you suspect
— the absolute value, the square — as an extra regressor and residualize against that too. This is
not a corner case here: § 1.2's whole mechanism is about $\sigma$, and $|\text{MACD}|$ carries
$\sigma$ ([03 § 4](03-shaping-the-lookback.md)), so a volatility candidate is precisely the kind
that can come back looking new while restating the incumbent's amplitude.

### 5.3 What to do when there are fifty signals

Two incumbents make § 5.2 easy. Fifty do not: fitting a candidate against fifty regressors on
overlapping daily data will fit noise long before it exhausts the information, and running the
pairwise version instead is fifty regressions whose answers do not compose.

**Regress against the model's output, not against its inputs.** The book already produces one number
per asset per date — its combined prediction. Use that single series as the regressor:

$$
x_t = \beta_0 + \beta_1 p_t + \epsilon_t
$$

with $p_t$ the current model's combined prediction. One regressor, one residual, and the question
it answers is the one actually being asked — *does this add anything to what I already run* — rather
than the fifty separate questions of whether it overlaps each ingredient.

## 6. One increment at a time

### 6.1 The record, and the test it has to pass

Everything above is one instance of a discipline that outlives it: **add one dimension per
experiment, and record what that dimension bought.**

Three things belong in that record, and only the first is the obvious one:

- **What the step adds on its own** — the bar plot for the new variable.
- **Whether it overlaps what is already there** — § 5.2's residual. A variable that looks strong
  alone and flat after residualizing is a re-description of the book, not an addition to it.
- **Which direction it is useful in.** A variable can predict *return* poorly and *volatility* well,
  and that is a perfectly good result: it earns a place in the risk model and a small weight, if
  any, in the return model. Recording only "it worked" throws that distinction away.

**The test the record has to pass is interpretability, in an operational sense.** Move an input and
you should be able to say, in advance and roughly, what the output does: this signal going from 3.0
to 3.2 should add on the order of 10 bp to the return forecast and 2 bp to the risk estimate.
Measuring 8 bp afterwards is fine — the intermediate steps are approximations and the estimate was
never exact. **"It moved and I do not know by how much" is not fine**, and it is what adding several
things at once guarantees, because when the book starts losing money there is no way back to which
piece is doing it.

### 6.2 Where this chapter's answer goes

**Often not into the return model at all.** The natural home for § 5.1's grid is the
**optimizer** — as a penalty that rises with the regime, an exposure cap that binds in the crisis
row, a volatility target that scales the whole book — which is why the grid earns its place even
when § 5.2's residual comes back flat. That is
[06](06-evaluating-performance.md)'s subject, not this chapter's.

**And the measurement stays a mean return.** Every chart in § 5 reports mean forward return with an
error bar, for the reasons [02 § 5](02-testing-a-signal.md) sets out. A Sharpe ratio here would fold
the regime axis back into a single number and hide the thing the axis was added to expose.

**Note (The scorecard is regime-dependent too).** The reason runs deeper than tidiness. A Sharpe
ratio has the tape's volatility in its own denominator, so the same number means different things in
different rows of the grid: 0.8 earned in a year when the index itself ran at 0.4 is a far harder
result than 0.9 earned in a year when buying the index and doing nothing paid 0.8. Collapsing the
regime axis into one ratio destroys exactly the context needed to read the ratio — which is why the
regime work comes before the scorecard, not after it.

## Background

### What is an option, and what does the buyer actually get?

A contract fixing a price today for a trade that may happen later — and the buyer chooses whether it
happens. That choice is the whole instrument; it is what *option* names.

Two of them, defined by which side the choice sits on:

| | **Call** | **Put** |
| --- | --- | --- |
| The holder may | **buy** the underlying at $K$ | **sell** the underlying at $K$ |
| Worth exercising when | $S_T > K$ | $S_T < K$ |
| Payoff at expiry | $\text{max}(S_T - K, 0)$ | $\text{max}(K - S_T, 0)$ |
| Bought by someone who | wants upside without owning it | wants a floor under something they own |

with $K$ the **strike** — the fixed price — $S_T$ the underlying's price at expiry, and the expiry
itself the date the choice must be made.

Worked through: you hold a call struck at \$100.

- The stock ends at \$150. Exercise — buy at 100, worth 150, so the contract is worth \$50.
- The stock ends at \$90. Do not exercise. Buying at 100 what the market sells at 90 would be a
  choice to lose \$10, and nothing compels it. The contract expires worth nothing.

So the payoff is **flat at zero up to the strike, then rises one-for-one** — a kinked line rather
than a straight one. That kink is the reason the next question has an answer.

### Why is an option the instrument a volatility forecast comes from?

- **Its value depends on the range, not the direction.** A forward contract's value moves with where
  the underlying ends up. An option's moves with how far it might get — the flat half of the payoff
  truncates the losses, so a wider distribution of outcomes is worth strictly more.
- **That makes it the most volatility-sensitive thing quoted.** A stock's price barely responds to a
  change in the volatility forecast; an option's responds directly, which is what makes the
  inversion of § 3.1 stable enough to be worth doing.
- **Out-of-the-money contracts are close to pure volatility bets.** A contract struck far above the
  price is worth something only if the underlying travels an unusual distance, so its price is
  almost entirely a statement about the tails. That is why VIX reads the whole strip of strikes
  rather than the at-the-money contract alone (§ 3.2).
- **The forecast has a fixed horizon attached.** Every contract has an expiry, so an implied
  volatility is always *volatility over the next $\tau$ days* — which is what allows step 3 of § 3.2
  to interpolate two of them onto a constant 30-day horizon.

## Appendix · Notation

Throughout, $t$ is the date. The regime index is a property of the market rather than of one asset,
so it carries no asset subscript $s$.

| Symbol | Means | First used |
| --- | --- | --- |
| $\sigma$, $\sigma_{\text{calm}}$, $\sigma_{\text{high}}$ | the amplitude of the period's move, and its levels either side of a regime shift | § 1.1 |
| $\mu$ | the drift — the mean one-period price change, or return on log prices | § 1.2 |
| $u_{t-j}$ | the standardized shock at lag $j$: mean zero, unit variance, uncorrelated across lags | § 1.2 |
| $k_j$, $\alpha_f$, $\alpha_s$, $n_f$, $n_s$ | MACD's kernel weight at lag $j$, the two smoothing constants and the two spans that fix it, all from [03 § 3](03-shaping-the-lookback.md) | § 1.2 |
| $\Phi$ | the standard normal cumulative distribution function | § 1.2 |
| $\sigma^{\text{real}}_t$, $L$ | realized volatility on that date, and the trailing window in periods it is computed over | § 2 |
| $K$, $S_T$, $\tau$ | an option's strike, the underlying's price at expiry, and the time to expiry in days | § 3 |
| $\sigma^2_{30,t}$ | the annualized 30-day implied variance the option strip produces | § 3.3 |
| $v_t$ | the volatility index level on that date — VIX for equities, MOVE for rates | § 4.1 |
| $g_t$, $c$ | the regime label, and the multiplier setting how fine the log cuts are | § 4.2 |
| $x_t$, $x_{j,t}$ | the candidate signal on that date, and the signals already in the book | § 5.2 |
| $\beta_j$, $\epsilon_t$ | the fitted coefficient on incumbent signal $j$, and the residual left after removing all of them | § 5.2 |
| $p_t$ | the current model's combined prediction, used as the single regressor of § 5.3 | § 5.3 |
| $N$ | the number of dates in the sample | § 5.1 |

**Note (Collisions to watch).** $\sigma$ carries a market-wide meaning throughout this chapter — the
amplitude of the tape — where [02 § 4](02-testing-a-signal.md)'s $\sigma_{s,t}$ is one asset's
trailing volatility used to standardize its signal. $\mu$ here is a per-period drift; [02 § 3.2.3](02-testing-a-signal.md)'s
$\mu_g$ is a bucket's mean forward return. $u_{t-j}$ is the standardized shock of § 1.2 and is
deliberately not written $z$, which [02 § 3.2.3](02-testing-a-signal.md) reserves for its test
statistic. Lowercase $g_t$ is a regime label on the vertical axis; the uppercase G1 … G5 of
[02 § 3.2](02-testing-a-signal.md) are signal buckets on the horizontal one, and § 5.1's grid has
both at once. $\epsilon_t$ here is the residual of a signal regressed on other **signals**;
[02 § 2](02-testing-a-signal.md)'s $\epsilon$ is the part of the forward **return** no signal
reaches — same construction, different regression, and § 5.2 would be wrong if they were the same
object. The trailing window of § 2 is written $L$ rather than $k$ precisely because $k_j$ is already
MACD's kernel weight in § 1.2. Uppercase $S_T$ is a price at expiry and lowercase $s$ is
[02](02-testing-a-signal.md)'s asset index; $N$ is a sample size here and a lookback length there.

---

## Next → [05 · Understanding Backtesting](05-understanding-backtesting.md)

Before moving on, **build the log-ceiling regime label on VIX and on MOVE, then draw § 5.1's grid
twice** — your 21-day risk-adjusted momentum against VIX on the equity ETFs, and against MOVE on the
bond ETFs. Print the observation count in every cell beside the mean, and say for each row whether
you have measured it or merely populated it.

Then check § 1.2 against your own grid: the calm row's G5 − G1 spread divided by the stressed row's
should come out near the ratio of the two rows' volatilities. If it comes out far from that, either
the drift moved with the noise or the rows are too thin to compare — and § 5.1's second note says
which to suspect first.

You should be able to explain:

- [ ] Why "high volatility" is a ratio rather than a level, and what a move from VIX 12 to VIX 40 does to the day's range
- [ ] Why MACD's ratio of mean to standard deviation splits into a market factor and a kernel factor, and which of them the tape can move
- [ ] Why risk-adjusting the signal does not restore the edge that a burst takes away
- [ ] Why a burst makes the rule trade more often, more expensively, and in the wrong direction, all at once
- [ ] Why a 21-day realized volatility peaks after the burst it is measuring, and why a shorter window does not fix it
- [ ] Why an option price can be inverted for a volatility forecast at all
- [ ] Why VIX is quoted as a volatility though the strip formula computes a variance, and when the difference bites
- [ ] Why the equity index labels most sleeves but not the rates sleeve
- [ ] Why the log of the level buckets and the level itself does not
- [ ] Why a flat crisis row may mean no edge or may mean no data, and what to print to tell them apart
- [ ] Why a residual bar plot answers a different question from a conditional grid

[← 03](03-shaping-the-lookback.md) · [Index](00-index.md) · reference: [08 · Toolbox](08-toolbox-pandas.md)
