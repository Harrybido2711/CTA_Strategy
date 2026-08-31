# 00 · How a Strategy Is Built

This series is the record of one project: an execution-aware trend-following CTA, built from
momentum and MACD signals over 37 daily ETF series, and then rebuilt once it became clear what the
first version had been measuring. §1 tells that as a story — what was built, what execution took
away, what the diagnosis was, and what the rebuild bought. §2 onward states the same journey as
machinery: the layers, the stages, and the question each one has to answer before the next is worth
starting.

## 1. The Story

The project ran in four acts. Each was provoked by the failure of the one before it, which is why
the order matters more than any single result in it.

| Act | What was done | What came back |
| --- | --- | --- |
| **I · Build it** | Momentum and MACD on 37 ETFs, sized long/short, held five days, backtested | A curve that looked like an edge |
| **II · Cost it** | Transaction costs, slippage, one-day execution delay, turnover | Over a quarter of the return, gone |
| **III · Diagnose it** | Rolling volume and volatility, cut into regimes, the signal re-tested inside each | The edge lived in liquid, calm markets |
| **IV · Rebuild it** | Regime-aware features, volatility scaling, turnover control | Out-of-sample Sharpe +8 percent, annual turnover −14 percent |

### 1.1 The question the project was built to answer

Not *can I find a signal* — cross-sectional momentum has been in the public literature for thirty
years, and finding it again proves nothing. The question was narrower and harder:

**Does a documented edge survive the part of trading that no paper reports?**

A published result is measured on returns. A traded result is measured on returns *minus* what it
cost to obtain them — the commission, the spread, the price that moved between the decision and the
fill, and the fact that a decision made at today's close cannot be acted on until tomorrow. None of
that is exotic; all of it is left out of a first backtest, and the size of what it removes is the
whole subject.

### 1.2 Act I — a trend follower that looked like it worked

**Definition (The naïve backtest).** A simulation that applies the signal to history with no
friction: it trades at the same close that produced the signal, pays no commission and no spread,
and assumes its own order moved no price.

The strategy underneath it is ordinary, and deliberately so:

| Piece | Choice |
| --- | --- |
| Signal | Trailing 21-day mean daily return, and a MACD fast-minus-slow leg → [03](03-shaping-the-lookback.md) |
| Universe | 37 daily ETF series standing in for futures → [100](100-dataset.md) |
| Sizing | Cross-sectional long/short, 150 percent long against 50 percent short → [04](04-from-signal-to-position.md) |
| Holding period | Five days, implemented as five overlapping daily tranches |

Run that way, the equity curve rises. It is the curve every naïve backtest produces, and nobody can
trade.

**Note.** A naïve backtest is not a lie; it is a question badly posed. It measures the *signal* —
does a higher signal precede a higher return — and answers it honestly. It says nothing about the
*strategy*, because a strategy is a signal plus the cost of acting on it, and the second term has
been set to zero.

### 1.3 Act II — execution took over a quarter of it

Three assumptions were added, each modelling one way reality charges for a trade.

| Assumption | What it models | Where it bites hardest |
| --- | --- | --- |
| **Transaction cost** | Commission plus half the bid-ask spread, per dollar traded | Anything that trades often |
| **Slippage** | The gap between the price on the screen and the price on the fill | Thin, fast-moving markets |
| **Execution delay** | A signal known at the close of `t` cannot trade before `t+1` | Signals whose edge decays within days |

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/execution-haircut-dark.png">
  <img alt="A waterfall chart. The naïve backtest's cumulative return is indexed to 100; transaction costs remove 11, slippage 7 and execution delay 8, leaving 74 as traded. A bracket spans the gap between the first and last bars, marking that over a quarter of the naïve return disappears before any judgement about the market is involved" src="figures/execution-haircut-light.png">
</picture>

The measured total was **over 25 percent of the naïve return**. The split between the three is
illustrative; the total is not.

**Claim.** The drag is not a fixed haircut on the result — it is proportional to how much the book
trades, so the faster the signal, the more of its own edge it spends.

**Proof.** Write the strategy's turnover over the sample as the total absolute weight change,

$$\text{TO} = \sum_t \sum_s | w_{s,t} - w_{s,t-1} |$$

where $s$ indexes the asset, $t$ the date, and $w_{s,t}$ is the target weight of asset $s$ on date
$t$ as a fraction of capital. If each dollar traded costs $\gamma$ — commission, spread and
slippage combined — then

$$\text{PnL}_{\text{net}} = \text{PnL}_{\text{gross}} - \gamma \text{TO}$$

$\text{PnL}_{\text{gross}}$ is a property of the signal alone; $\gamma \text{TO}$ is a property of
how the signal is traded. Two strategies with the same gross return and different turnover keep
different amounts of it, and nothing about the signal's quality enters the second term.

**Note (Delay is a different mechanism from cost).** Cost subtracts a known quantity. Delay does
not subtract anything — it *changes which trade happens*, replacing the return from `t` with the
return from `t+1`. For a signal whose edge decays over weeks the difference is small; for one that
decays over days it can remove most of it. That is why the delay is written into the simulation as
an explicit parameter rather than assumed away.

### 1.4 Act III — the edge has an address

The obvious response to Act II is to trade less. The better response is to find out *where* the
surviving return came from, because a strategy that earns in one kind of market and bleeds in
another has a single average return that describes neither.

Two rolling measures were computed per asset and cut into terciles: 21-day mean volume $V_{s,t}$,
standing for liquidity, and 21-day realized volatility $\sigma_{s,t}$, standing for how violent the
tape is. That gives nine regime cells, and the signal was re-tested inside each.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/regime-map-dark.png">
  <img alt="A three-by-three grid of regime cells: rolling volume in terciles across, rolling realized volatility in terciles up. Each cell holds the top-minus-bottom bucket spread the momentum signal delivered inside that regime, in basis points. The values rise from plus 2 in the high-volatility, low-volume cell to plus 38 in the low-volatility, high-volume cell, which is ringed and annotated as where the signal kept working" src="figures/regime-map-light.png">
</picture>

The result was monotone in both directions: the edge concentrated in **high-volume, low-volatility**
cells and was close to nothing in the opposite corner. Two mechanisms explain it, and they are the
same fact seen from two sides:

- **Trend needs persistence.** A trend signal earns when a drift continues. High realized volatility
  is the regime where price direction reverses inside the holding period, so the signal flips, and
  every flip is a round trip paid for at $\gamma$ per dollar.
- **Thin markets charge more.** Slippage and spread are widest exactly where volume is lowest, so
  the low-volume cells carry the largest $\gamma$ *and* the least reliable drift.

Act II and Act III are therefore one finding: the naïve backtest was being paid, on paper, for
holding risk in conditions where the strategy could not actually have collected.

**Note (A conditional finding is a hypothesis, not a licence).** Two axes at three buckets each is
nine cells, and the best of nine is the one most likely to be luck. The conditional result has to
survive the same attack as the unconditional one — out of sample, across sub-periods, and with the
Sharpe deflated for the number of cells that were looked at. → [07](07-overfitting-and-robustness.md)

### 1.5 Act IV — rebuild against the diagnosis

Each change answers one line of the diagnosis. None of them is a new signal; all of them are ways
of spending the existing signal where it works and not where it does not.

| Change | The line of the diagnosis it answers | Mechanism |
| --- | --- | --- |
| **Regime-aware features** | The edge is concentrated in liquid, calm cells | Let the regime enter the signal — scale or condition on $V_{s,t}$ and $\sigma_{s,t}$ — rather than deleting the other days |
| **Volatility scaling** | One weight means different risk on different days | Size on $w_{s,t} \propto \frac{x_{s,t}}{\sigma_{s,t}}$, where $x_{s,t}$ is the raw signal, so each position contributes comparable risk |
| **Turnover control** | The drag is $\gamma \text{TO}$, and it was the turnover doing the damage | Rebalance only when the target weight has moved by at least a deadband $\eta$; a drift smaller than that cannot pay for its own round trip |

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/rebuild-scorecard-dark.png">
  <img alt="Two panels comparing the baseline strategy with the rebuilt one. Left: out-of-sample Sharpe ratio, higher after the rebuild, marked plus 8 percent. Right: annual turnover as a multiple of book value, lower after the rebuild, marked minus 14 percent" src="figures/rebuild-scorecard-light.png">
</picture>

The rebuild raised out-of-sample Sharpe by **8 percent** and cut annual turnover by **14 percent**
against the same baseline.

**Note (Why a small number is the credible one).** An 8 percent Sharpe improvement is modest, and it
should be. The changes did not find new information — they stopped paying for the information
already there in the regimes where it was not worth the cost. A rebuild of that kind buys a few
percent. A rebuild that doubles the Sharpe has almost always found a leak instead, and the turnover
number is what makes the claim checkable: the strategy trades *less* and earns *slightly more*,
which is the signature of removing cost rather than adding fit.

### 1.6 What the story claims, and what it does not

- **The percentages are this project's, measured on this sample.** They are not a property of trend
  following. The chapters teach the method that produced them; they do not promise the number.
- **The prototype in the repository is deliberately behind the story.** It runs a plain five-day
  cross-sectional momentum and posts a near-zero Sharpe, because its job is the mechanics of the
  chain, not the result. Measured output and its caveats live with the code, in
  [Implementation Notes](../Backtest_prototype/Backtests.md).
- **Five tickers still carry an unadjusted split.** Any conclusion spanning 2025-12-05 is suspect
  until they are fixed. → [100](100-dataset.md)

## 2. The Chain, End to End

The story above used *signal*, *prediction*, *position* and *strategy* as though they were near
enough the same thing. They are not, and the rest of the series depends on keeping them apart.

In one line: **a model finds the pattern, a prediction states the judgement, a signal picks the
direction, a position sizes the bet, and the backtest asks whether any of it survives.**

| Layer | What it does | Output | Example |
| --- | --- | --- | --- |
| **Features** | Describe the market | Prices, volume, volatility | 21-day realized volatility |
| **Rule** *or* **model** | Encode or learn a regularity | A number | MACD; ridge regression |
| **Prediction** | State a judgement about the future | Expected return, P(up), expected vol | `+0.8%` next week |
| **Signal** | Turn that judgement into a direction | `+1` / `−1` / `0` | Long if the prediction is in the top quintile |
| **Position** | Decide how much to bet | A weight, after risk limits and volatility scaling | 30 percent of capital, long |
| **Backtest** | Apply it all to history under real constraints | A PnL series | After costs, slippage and delay |
| **Metrics** | Judge the PnL | Sharpe, drawdown, turnover, hit rate | Sharpe 0.4, −18 percent |

**Note.** Act II is entirely a statement about the *backtest* row: nothing about the prediction
changed, and a quarter of the return went. Act IV is mostly a statement about the *position* row —
volatility scaling and turnover control are sizing decisions, and only the regime-aware features
reach back into the signal. That so much can be lost, and some of it won back, while the prediction
stands almost still is the reason these layers are worth separating at all.

## 3. The Build Order, Step by Step

Each stage does one thing, asks one question, and hands one object to the next. Read a row as: do
the work, answer the question, and only then pass the handoff on — the question is the gate, and a
stage that fails it is not repaired by anything downstream.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/build-order-dark.png">
  <img alt="Eight build stages in a vertical chain, each a labelled card carrying the question it must answer, with the object it hands to the next stage named on the arrow between them — trusted data, edge confirmed, sized book, honest PnL, verdict, a diagnosis, a better signal. Stages 0 and 2 are blue as building the strategy, stages 3 to 5 green as measuring it, stages 1 and 6 violet as the signal and the rebuild, stage 7 a lighter blue as an optional extension. A violet return path runs from stage 6 back into stage 1, labelled as the second lap: regime-aware features, volatility scaling, turnover control. A right-hand column names what judges each stage" src="figures/build-order-light.png">
</picture>

| # | Stage | Act | The question it asks |
| - | --- | --- | --- |
| 0 | **Validate the data** | I | Can I trust a single number in this dataset? |
| 1 | **Compute a signal** | I | Is a higher signal followed by a higher forward return? |
| 2 | **Size the positions** | I | How much do I bet, and is the exposure what I think it is? |
| 3 | **Simulate under execution** | II | How much of it survives costs, slippage and delay? |
| 4 | **Evaluate** | II | Is it any good, and where exactly does it fail? |
| 5 | **Attack the result** | III | How much is edge, and how much is search? |
| 6 | **Rebuild against the diagnosis** | IV | Does the edge improve where the diagnosis said it would? |
| 7 | **Try a model** | — | Does a learned prediction beat the rule? |

Stage 6 is not the end of the chain but a return to its start: the diagnosis re-enters at stage 1 as
a better signal and at stage 2 as a better-sized one, and stages 3 to 5 then run again untouched.
That is what makes the comparison in §1.5 meaningful — what was measured moved, the measurement did
not.

### 3.1 Stage 0 — Validate the data

**What it does.** Check that the price series are continuous and corporate actions are adjusted,
and that the forward-return target is aligned with the signal that labels it — verify a handful of
rows by hand before trusting anything downstream. Five sector SPDRs (XLB, XLE, XLK, XLU, XLY) still
carry an unadjusted 2-for-1 split effective 2025-12-05, so any result spanning that date is suspect
until the split is adjusted.

**What judges it.** Continuity — no gaps, zeros or negative prices — split-adjusted consistency, and
a hand-checked alignment between the signal at `t` and the return it labels.

**What it hands on.** A record every downstream statistic can be read against. An unadjusted split
is the largest move in the sample by construction, so a trend follower reads it as its strongest
signal ever — and the equity curve looks *better*, not worse.

→ [100 · The Dataset](100-dataset.md)

### 3.2 Stage 1 — Compute a signal

**What it does.** Turn the intuition into a number — a momentum signal is the trailing 21-day mean
of daily returns, a MACD signal is a fast average minus a slow one — then ask whether that number
carries information. The test is the bucket plot: rank dates by signal, file them into five ordered
buckets G1 … G5, and plot the mean forward return each bucket went on to deliver, with the standard
error of that mean as the error bar.

**What judges it.** Bucket monotonicity (G1 < G2 < … < G5), the G5 − G1 spread measured against the
error bars, and a two-sample t-score on the head against the tail — past ±2 the separation is
significant at the 5 percent level. Turnover matters here too, before any cost has been modelled: a
signal you cannot act on cheaply costs more than it earns.

**What it hands on.** Permission to size positions. This is the cheapest test in the chain, and a
signal that fails here is rescued by nothing downstream. It is also the one place Sharpe must not
appear: Sharpe folds the mean, the volatility and the risk-free rate into a single number you cannot
decompose.

→ [02 § 3.2](02-testing-a-signal.md) for the test, [03](03-shaping-the-lookback.md) for the lookback

### 3.3 Stage 2 — Size the positions

**What it does.** Convert the signal into target weights, weights into dollar exposure, dollars into
shares, and apply risk limits — carrying the position as a signed quantity, long or short. The two
portfolios here size differently: Portfolio 1 longs 150 percent of the positive-momentum assets
(equal weight) and shorts 50 percent of the negative ones; Portfolio 2 sizes by whether momentum is
above or below the cross-sectional median, so an asset can be shorted even with positive momentum. A
five-day holding period is implemented as overlapping portfolios, so the weights evolve smoothly as
old signals roll off rather than jumping every fifth day.

**What judges it.** Gross exposure (about 2.0), net exposure (Portfolio 1 about +1.0, Portfolio 2
about 0), and turnover — the $\text{TO}$ that stage 3 will charge for.

**What it hands on.** A PnL path with a real gross and net exposure and a real cost of acting. It is
here, at a 150/50 book, that the risk-free-rate question becomes concrete — a question the signal
stage never had to answer.

→ [04 · From Signal to Position](04-from-signal-to-position.md)

### 3.4 Stage 3 — Simulate under execution

**What it does.** Apply the sized positions to history under the constraints a real book faces: an
execution delay (a signal dated `t` trades a day later), an approximate execution price, transaction
costs, slippage, and the turnover the rebalancing implies. This is Act II, and it is the stage that
separates a signal from a strategy.

**What judges it.** Honesty, not goodness: check for look-ahead bias — its single entry point is the
alignment of the forward return with the signal — and measure the drag each assumption puts on the
raw result, separately, so you can say which one did the damage.

**What it hands on.** A PnL series that can be reduced to metrics. This is the first stage at which
a Sharpe is even meaningful, and the first at which a leak announces itself: as an implausibly
smooth, high-Sharpe curve.

→ [05 · Understanding Backtesting](05-understanding-backtesting.md)

### 3.5 Stage 4 — Evaluate

**What it does.** Reduce the PnL series to the numbers a practitioner quotes — annualized return,
Sharpe, maximum drawdown, hit rate, turnover — and read them beside the equity curve, not instead of
it, so a number is never separated from the path that produced it.

**What judges it.** The headline statistics and the drawdowns they hide: a Sharpe of 0.2 could be
steady earnings or one great quarter followed by five years of bleeding. One number hides the time
dimension, so the curve and its worst drawdowns are part of the judgement.

**What it hands on.** A verdict that the strategy *might* work, and — more useful — a list of the
periods where it did not. That list is what stage 5 conditions on.

→ [06 · Evaluating Performance](06-evaluating-performance.md)

### 3.6 Stage 5 — Attack the result

**What it does.** Ask how much of the result survives once you stop believing it: across years,
across markets, across the parameters you searched, and — this is Act III — across regimes. Cut the
sample by rolling volume and rolling volatility and re-run the stage 1 test inside each cell. Split
the sample out of sample, with a purge and sometimes an embargo so the target of the last training
rows cannot leak into validation, and deflate the Sharpe for the number of variants tried.

**What judges it.** Out-of-sample performance, the deflated Sharpe, parameter sensitivity — a broad
plateau of neighbouring good parameters is more believable than a single bright cell — and whether
the regime split is monotone rather than one lucky corner.

**What it hands on.** Two things, and the second is the point: a baseline that has survived attack,
and a *diagnosis* naming the conditions under which the edge exists.

→ [07 · Overfitting &amp; Robustness](07-overfitting-and-robustness.md),
[04 · Volatility Regimes](04-volatility-regimes.md)

### 3.7 Stage 6 — Rebuild against the diagnosis

**What it does.** Spend the diagnosis. Feed the regime measures into the signal, scale positions by
the inverse of forecast volatility, and add a deadband so a small change in the target does not
trigger a trade that cannot pay for itself. Then run stages 2 through 5 again with nothing else
altered.

**What judges it.** Out-of-sample Sharpe and annual turnover, measured against the *same* baseline
on the *same* split. Any comparison against a re-tuned baseline is not a comparison.

**What it hands on.** A strategy whose improvement can be attributed to a named cause. If the Sharpe
rises and the turnover does not fall, the diagnosis was probably not what fixed it.

**Note.** The temptation at this stage is to re-open stage 1 and search for a better signal while
the regime work is still fresh. Every parameter tried here is a parameter stage 5 must deflate for.
Change one thing per lap.

→ [04 § 5](04-volatility-regimes.md)

### 3.8 Stage 7 — Try a model

**What it does.** Replace the rule with a learned prediction — a regression on the same features —
and run it through the *same* sizing, the *same* backtest, the *same* metrics. Keep prediction and
signal apart: a **prediction** is the model's estimate of a future quantity, a **signal** is the
long/short/flat decision made from it, and the conversion needs a trading rule — a threshold, a
sign, a ranking. A model replaces the rule, not the chain.

**What judges it.** The test IC — rank correlation between prediction and forward return, per date —
its mean, and its stability, the mean divided by its own standard deviation. Expect predictions far
narrower than reality: at tiny $R^2$ a 2.5 percent spread of returns yields predictions inside ±0.5
percent, so an absolute threshold never fires. Threshold on the prediction's own quantiles instead.

**What it hands on.** Closure: the model is judged exactly as the rule was, which is why the whole
chain had to be built rule-first.

→ [09 · IC and R²](09-ic-and-r-squared.md)

## 4. Four Levels of Validation

Each layer is tested on its own terms, and passing one says nothing about the next.

| Level | Question | Typical measure | Where |
| --- | --- | --- | --- |
| **Model** | Does the prediction track the outcome? | Test IC, MSE, accuracy | Out of sample only |
| **Signal** | Is the direction right, and tradeable? | Bucket monotonicity, turnover | [02 § 3.2](02-testing-a-signal.md) |
| **Strategy** | Does it survive real constraints? | Sharpe, drawdown, return after costs | [05](05-understanding-backtesting.md), [06](06-evaluating-performance.md) |
| **Robustness** | Does it persist? | Across years, markets, regimes, parameters | [07](07-overfitting-and-robustness.md), [04](04-volatility-regimes.md) |

**Note (Each arrow loses candidates).** High test accuracy is not economic value; economic value is
not profit after costs; profit after costs is not stability out of sample. A model can predict
direction 55 percent of the time and still lose money, because the 45 percent it gets wrong are the
larger moves, or because acting on it every day costs more than the edge — which is Act II stated as
a general fact rather than a measurement.

## 5. Where Each Stage Fails

The stages fail in different ways, and the symptoms are easy to misattribute — the most common
mistake is reading a data defect as a code bug.

| Stage | Failure | What you see | Where it is treated |
| --- | --- | --- | --- |
| Data | Unadjusted corporate action | A vertical step in the equity curve | [100 § 1.1](100-dataset.md) |
| Signal | No information | Flat or non-monotone buckets | [02 § 3.2](02-testing-a-signal.md) |
| Sizing | Exposure not what you think | Gross or net drifts from target | [04](04-from-signal-to-position.md) |
| Simulation | Look-ahead bias | Implausibly smooth, high Sharpe | [05](05-understanding-backtesting.md) |
| Evaluation | One number hides the path | Good Sharpe, unlivable drawdown | [06](06-evaluating-performance.md) |
| Robustness | Parameters were searched | Result vanishes out of sample | [07](07-overfitting-and-robustness.md) |
| Rebuild | The fix was fitted to the diagnosis | Sharpe rises but turnover does not fall | [07](07-overfitting-and-robustness.md) |
| Model | Fitted to the sample | Good IC in train, none in test | Out-of-sample split |

**Note.** The order is forced in one direction — you cannot evaluate before simulating, or simulate
before sizing. There are two shortcuts. Stage 1 can be validated *without* stages 2–4, and should
be, because it is the cheapest test in the chain. And stage 6 re-enters at stage 1 rather than
continuing forward, which is why the second lap costs a fraction of the first.

## Appendix · Notation

| Symbol | Meaning | First used |
| --- | --- | --- |
| $s$, $t$ | The asset, and the date — as in [02](02-testing-a-signal.md) | § 1.3 |
| $w_{s,t}$ | Target weight of asset $s$ on date $t$, as a fraction of capital | § 1.3 |
| $x_{s,t}$ | The raw signal value for that asset on that date | § 1.5 |
| $\text{TO}$ | Turnover — total absolute weight change over the sample | § 1.3 |
| $\gamma$ | Round-trip cost per dollar traded: commission, spread and slippage | § 1.3 |
| $V_{s,t}$ | Rolling 21-day mean volume, standing for liquidity | § 1.4 |
| $\sigma_{s,t}$ | Rolling 21-day realized volatility for that asset | § 1.4 |
| $\eta$ | Deadband — the weight change below which no trade is placed | § 1.5 |
| $R^2$ | Fraction of return variance a model explains | § 3.8 |

**Note (Collisions avoided).** Three symbols are deliberately not the obvious ones.
[04](04-volatility-regimes.md) already spends $\tau$ on an option's time to expiry and $c$ on its
regime multiplier, so turnover is written $\text{TO}$ and the cost rate $\gamma$; and
[02 § 1.1](02-testing-a-signal.md)'s $\delta$ is the tolerance on *net exposure*, a different
tolerance from this chapter's deadband, which is therefore $\eta$. Uppercase $V_{s,t}$ is one
asset's volume; [04 § 4.1](04-volatility-regimes.md)'s lowercase $v_t$ is a market-wide volatility
index. $\sigma_{s,t}$ is reused from [02 § 4](02-testing-a-signal.md) on purpose — it is the same
object, one asset's trailing volatility — and is not 04's market-wide $\sigma^{\text{real}}_t$.

[← Index](00-index.md)
