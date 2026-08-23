# 00 · How a Strategy Is Built

## 1. The Chain, End to End

In one line: **a model finds the pattern, a prediction states the judgement, a signal picks the
direction, a position sizes the bet, and the backtest asks whether any of it survives.**

| Layer                                 | What it does                                   | Output                               | Example                 |
| ------------------------------------- | ---------------------------------------------- | ------------------------------------ | ----------------------- |
| **Features**                    | describe the market                            | prices, volume, volatility           | 21-day realised vol     |
| **Rule** *or* **model** | encode or learn a regularity                   | a number                             | MACD; ridge regression  |
| **Prediction**                  | state a judgement about the future             | expected return, P(up), expected vol | `+0.8%` next week     |
| **Signal**                      | turn that judgement into a direction           | `+1` / `−1` / `0`             | long if prediction > 1% |
| **Position**                    | decide how much to bet                         | a weight, after risk limits          | 30% of capital, long    |
| **Backtest**                    | apply it all to history under real constraints | a PnL series                         | after costs and delay   |
| **Metrics**                     | judge the PnL                                  | Sharpe, drawdown, turnover, hit rate | Sharpe 0.4, −18%       |

## 2. The Build Order, Step by Step

Each stage does one thing, asks one question, and hands one object to the next. Read a row as: do
the work, answer the question, and only then pass the handoff on — the question is the gate, and a
stage that fails it is not repaired by anything downstream.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/build-order-dark.png">
  <img alt="Seven build stages in a vertical chain: stages 0–2 in blue as the strategy, stages 3–5 in green as validation, and stage 1, the signal, in violet as the crux. Each box carries the question the stage must answer; each arrow is labelled with the object it hands to the next stage — trusted data, edge confirmed, sized book, honest PnL, verdict, surviving baseline. To the right, the signal's two sources — a rule (momentum, MACD) or a learned model feeding a prediction — converge on the signal, and stage 6 loops a learned prediction back to replace the rule" src="figures/build-order-light.png">
</picture>

| # | Step | What you do | The question it asks |
| - | --- | --- | --- |
| 0 | **Validate the data** | Confirm prices are continuous, corporate actions are adjusted, and the target is aligned | Can I trust a single number in this dataset? |
| 1 | **State a hypothesis, compute a signal** | Turn the intuition into a number, then test it with the bucket plot | Is higher signal followed by higher forward return? |
| 2 | **Size the positions** | Signal → weights → dollars → shares, with risk limits | How much should I bet, and is the exposure what I think it is? |
| 3 | **Simulate** | Apply the positions under costs, delay, turnover and realistic timing | Does any of it survive reality? |
| 4 | **Evaluate** | Reduce the PnL to Sharpe, drawdown, turnover, hit rate | Is the strategy any good, and where does it fail? |
| 5 | **Attack the result** | Test across years, markets and parameters; out-of-sample; deflate the Sharpe | How much is real edge, and how much is search? |
| 6 | **Try a model** | Learn a prediction; run the same sizing, backtest and metrics as the rule | Does a learned prediction beat the rule? |

Each row is unpacked below: what the stage actually does, the metrics that judge it, and the object
it hands to the next stage.

### 2.1 Stage 0 — Validate the data

**What it does.** Check that the price series are continuous and corporate actions are adjusted,
and that the forward-return target is aligned with the signal that labels it — verify a handful of
rows by hand before trusting anything downstream. Five sector SPDRs (XLB, XLE, XLK, XLU, XLY)
still carry an unadjusted 2-for-1 split effective 2025-12-05, so any result spanning that date is
suspect until the split is adjusted.

**What judges it.** Continuity (no gaps, zeros or negative prices), split-adjusted consistency, and
a hand-checked alignment between the signal at `t` and the return it labels.

**What it hands on.** A record every downstream statistic can be read against. An unadjusted split
is the largest move in the sample by construction, so a trend follower reads it as its strongest
signal ever — and the equity curve looks *better*, not worse.

→ [100 · The Dataset](100-dataset.md)

### 2.2 Stage 1 — State a hypothesis, compute a signal

**What it does.** Turn the intuition into a number — a momentum signal is the trailing 21-day mean
of daily returns — then ask whether that number carries information. The test is the bucket plot:
rank dates by signal, file them into five ordered buckets G1 … G5, and plot the mean forward return
each bucket went on to deliver, with the standard error of that mean as the error bar.

**What judges it.** Bucket monotonicity (G1 < G2 < … < G5), the G5 − G1 spread measured against the
error bars, and a two-sample t-score on the head against the tail — past ±2 the separation is
significant at the 5% level. Turnover matters too: a signal you cannot act on cheaply costs more
than it earns.

**What it hands on.** Permission to size positions. This is the cheapest test in the chain, and a
signal that fails here is rescued by nothing downstream. It is also the one place Sharpe must not
appear: Sharpe folds the mean, the volatility and the risk-free rate into a single number you
cannot decompose.

→ [02 § 3.2](02-testing-a-signal.md)

### 2.3 Stage 2 — Size the positions

**What it does.** Convert the signal into target weights, weights into dollar exposure, dollars
into shares, and apply risk limits — carrying the position as a signed quantity, long or short.
The two portfolios here size differently: Portfolio 1 longs 150% of the positive-momentum assets
(equal weight) and shorts 50% of the negative ones; Portfolio 2 sizes by whether momentum is above
or below the cross-sectional median, so an asset can be shorted even with positive momentum. A
5-day holding period is implemented as overlapping portfolios, so the weights evolve smoothly as
old signals roll off rather than jumping every fifth day.

**What judges it.** Gross exposure (about 2.0), net exposure (Portfolio 1 about +1.0, Portfolio 2
about 0), and turnover — the cost of acting on the signal each day.

**What it hands on.** A PnL path with a real gross and net exposure and a real cost of acting. It
is here, at a 150/50 book, that the risk-free-rate question becomes concrete — a question the
signal stage never had to answer.

→ [04 · From Signal to Position](04-from-signal-to-position.md)

### 2.4 Stage 3 — Simulate

**What it does.** Apply the sized positions to history under the constraints a real book faces: an
execution delay (a signal dated `t` trades a day later), an approximate execution price,
transaction costs, and the turnover the rebalancing implies.

**What judges it.** Honesty, not goodness: check for look-ahead bias — its single entry point is
the alignment of the forward return with the signal — and measure the drag that costs and delay
put on the raw signal.

**What it hands on.** A PnL series that can be reduced to metrics. This is the first stage at
which a Sharpe is even meaningful: a leak announces itself as an implausibly smooth, high-Sharpe
curve.

→ [05 · Understanding Backtesting](05-understanding-backtesting.md)

### 2.5 Stage 4 — Evaluate

**What it does.** Reduce the PnL series to the numbers a practitioner quotes — annualised return,
Sharpe, maximum drawdown, hit rate, turnover — and read them beside the equity curve, not instead
of it, so a number is never separated from the path that produced it.

**What judges it.** The headline statistics and the drawdowns they hide: a Sharpe of 0.2 could be
steady earnings or one great quarter followed by five years of bleeding. One number hides the time
dimension, so the curve and its worst drawdowns are part of the judgement.

**What it hands on.** A verdict that the strategy *might* work. The verdict stays provisional
until the next stage attacks it.

→ [06 · Evaluating Performance](06-evaluating-performance.md)

### 2.6 Stage 5 — Attack the result

**What it does.** Ask how much of the result survives once you stop believing it: across years,
across markets, across the parameters you searched. Split the sample out-of-sample — with a purge,
and sometimes an embargo, so the target of the last training rows cannot leak into validation —
and deflate the Sharpe for the number of variants you tried.

**What judges it.** Out-of-sample performance, the deflated Sharpe, and parameter sensitivity: a
broad plateau of neighbouring good parameters is more believable than a single bright cell.

**What it hands on.** A baseline that has survived attack — the only thing a model is worth being
compared with.

→ [07 · Overfitting & Robustness](07-overfitting-and-robustness.md)

### 2.7 Stage 6 — Try a model

**What it does.** Replace the rule with a learned prediction — a regression on the same features —
and run it through the *same* sizing, the *same* backtest, the *same* metrics. Keep prediction and
signal apart: a **prediction** is the model's estimate of a future quantity, a **signal** is the
long/short/flat decision you make from it, and the conversion needs a trading rule — a threshold, a
sign, a ranking. A model replaces the rule, not the backtest.

**What judges it.** The test IC — rank correlation between prediction and forward return, per
date — its mean, and its stability (mean divided by its standard deviation). Expect predictions
far narrower than reality: at tiny R² a 2.5% spread of returns yields predictions inside ±0.5%, so
an absolute threshold never fires — threshold on the prediction's own quantiles.

**What it hands on.** Closes the loop: the model is judged exactly as the rule was, which is why
the whole chain had to be built rule-first.

→ [09 · IC and R²](09-ic-and-r-squared.md); the prediction-to-signal conversion is in Background.

## 3. Four Levels of Validation

Each layer is tested on its own terms, and passing one says nothing about the next.

| Level                | Question                               | Typical measure                      | Where          |
| -------------------- | -------------------------------------- | ------------------------------------ | -------------- |
| **Model**      | does the prediction track the outcome? | test IC, MSE, accuracy               | OOS only       |
| **Signal**     | is the direction right, and tradeable? | bucket monotonicity, turnover        | [02 § 3.2](02-testing-a-signal.md) |
| **Strategy**   | does it survive real constraints?      | Sharpe, drawdown, return after costs | [05](05-understanding-backtesting.md), [06](06-evaluating-performance.md) |
| **Robustness** | does it persist?                       | across years, markets, parameters    | [07](07-overfitting-and-robustness.md) |

**Note (Each arrow loses candidates).** High test accuracy is not economic value; economic value is
not profit after costs; profit after costs is not stability out of sample. A model can predict
direction 55% of the time and still lose money, because the 45% it gets wrong are the larger moves,
or because acting on it every day costs more than the edge.

## 4. Where Each Stage Fails

The stages fail in different ways, and the symptoms are easy to misattribute — the most common
mistake is reading a data defect as a code bug.

| Stage      | Failure                     | What you see                        | Where it is treated |
| ---------- | --------------------------- | ----------------------------------- | ------------------- |
| Data       | Unadjusted corporate action | A vertical step in the equity curve | [100 § 1.1](100-dataset.md) |
| Signal     | No information              | Flat or non-monotone buckets        | [02 § 3.2](02-testing-a-signal.md) |
| Sizing     | Exposure not what you think | Gross or net drifts from target     | [04](04-from-signal-to-position.md) |
| Simulation | Look-ahead bias             | Implausibly smooth, high Sharpe     | [05](05-understanding-backtesting.md) |
| Evaluation | One number hides the path   | Good Sharpe, unlivable drawdown     | [06](06-evaluating-performance.md) |
| Robustness | Parameters were searched    | Result vanishes out of sample       | [07](07-overfitting-and-robustness.md) |
| Model      | Fitted to the sample        | Good IC in train, none in test      | OOS split |

**Note.** The order is forced in one direction — you cannot evaluate before simulating, or simulate
before sizing. The one shortcut is that stage 1 can be validated *without* stages 2–4, and it
should be.

---

## Background

General background needed to read this chapter, not part of its argument.

### What are the features and the target?

**Features** are everything knowable at time `t`. The project names three groups, and a regime
indicator built from them:

| Group | Examples |
| --- | --- |
| Price | momentum at several lookbacks, MACD line, MACD histogram |
| Volume | rolling mean volume, volume z-score |
| Volatility | rolling realised volatility |
| Regime | high/low volatility, high/low volume, as quantile dummies |

**The target** is the forward return over a chosen horizon `h`:

```python
y = close.pct_change(h).shift(-h)      # the return from t to t+h, labelled at t
```

- Prefer a **volatility-scaled** target, `y / vol`. Raw returns are heteroscedastic, so a model
  fitted to them spends most of its capacity on high-volatility periods, where the numbers are
  large but not more informative.
- That `shift(-h)` is the single place look-ahead bias enters. Verify the alignment on a handful
  of rows by hand before trusting anything downstream.

**One model or 37?** Pool the assets — stack `(date, ticker)` into rows and fit once. Per-asset
models get ~1,600 rows each and overfit. Pooling requires the features to be comparable across
assets, which is what the standardization in [02 § 4](02-testing-a-signal.md) is for.

**Note the effective sample size.** 37 tickers × ~1,600 days looks like 60,000 observations, but
the assets move together, so the number of genuinely independent observations is closer to the
number of **days**. That is the main reason flexible models overfit on a panel like this.

### Why can a time series not be split randomly?

Because a random fold puts **future rows in the training set and past rows in the test set**. The
model then "predicts" a past it has already seen, and the score is meaningless.

Split by time instead:

```text
|------------ train ------------|-- valid --|-- test --|
2020                          2024        2025      2026
```

There is a second, subtler leak even after splitting by time. If the target is a 5-day forward
return, the last five training rows describe returns that fall inside the validation window. Leave
a gap of `h` observations between the segments — **purging**, sometimes with an extra **embargo**.

- The same discipline as the score-against-your-own-past rule in [02 § 4](02-testing-a-signal.md): rank and
  fit using only what was knowable at the time.
- Formal treatment of splits and why a backtest overstates: [07](07-overfitting-and-robustness.md).

### How does a model's output become a signal?

`predict` returns one number per row. Reshaped, it is a `date × ticker` matrix — **the same shape
as a momentum signal**, which is what lets the two be swapped:

```python
model.fit(X_train, y_train)
pred = model.predict(X_test)
pred = pd.Series(pred, index=X_test.index).unstack()     # date × ticker
```

From there, nothing downstream changes:

```python
signal  = momentum(close)     # rule path
signal  = pred                # model path — same shape, same everything after

weights = overlap_weights(target_weights_p1(signal))
pnl, _  = multi_asset_backtester(asset_data, weights)
```

**Expect the predictions to be far narrower than reality.** A least-squares fit shrinks toward the
mean in proportion to how little it can explain, so at R² = 0.005 a 2.5% spread of returns yields
predictions spread over roughly 0.2%. This is forced rather than a defect, and it has one immediate
consequence for the rule: **an absolute threshold will never fire.** `prediction > 1%` selects
nothing when predictions live inside ±0.5%. Threshold on the prediction's *own* quantiles, or rank
cross-sectionally and take the top and bottom names each day.

**Judging the model itself** uses rank correlation per date, not accuracy:

```python
ic = pred.corrwith(fwd_return, axis=1, method="spearman")
ic.mean(), ic.mean() / ic.std()          # average IC, and its stability
```

→ Why that is the right statistic rather than R², what each one measures, why they can disagree
completely, and how to read the magnitudes: [09 · IC and R²](09-ic-and-r-squared.md).

[← Index](00-index.md)
