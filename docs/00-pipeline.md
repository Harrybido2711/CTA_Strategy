# 00 · How a Strategy Is Built

> - **Answers:** what *prediction*, *signal*, *position*, *strategy* and *backtest* each mean, how they chain, and where a model enters.
> - **Prerequisites:** [01 · What Is a CTA Strategy](01-what-is-cta.md).
> - **Read it when:** before [02](02-building-signals.md), and again whenever you lose track of which stage a problem belongs to.

**Orientation, not a step in the sequence.** The numbered chapters each go deep on one stage; this
maps them onto one another so you can see what is being built and why in that order.

---

## 1. The Chain, End to End

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/strategy-pipeline-dark.png">
  <img alt="Market data and features feed two alternative paths. On the left a rule such as momentum or MACD produces a signal directly by sign or threshold. On the right a machine-learning model produces a prediction — future return, probability of a rise, or volatility — which a trading rule then converts into the same signal. Both paths converge on one signal node of long, short or flat, which feeds position sizing and risk limits, then the backtest with costs, delay and turnover, and finally return, Sharpe, drawdown and turnover. A bracket marks everything down to position as the strategy, and the backtest and metrics as validation" src="figures/strategy-pipeline-light.png">
</picture>

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

## 2. Where a Model Enters, and Where It Does Not

**Definition (Prediction).** A *prediction* is a model's estimate of a future quantity — next
period's return, the probability of a rise, expected volatility. It is a number about the world,
carrying no instruction.

**Definition (Signal).** A *signal* is a decision: long, short, or flat. Converting a prediction
into one requires a **trading rule** — a threshold, a sign, a ranking.

```python
prediction = model.predict(features)

if   prediction >  0.01: signal =  1     # long
elif prediction < -0.01: signal = -1     # short
else:                    signal =  0     # flat
```

**Note (Why keep them apart).** The threshold is a choice, not a model output, and it is where
transaction costs enter the decision: widening the dead band trades hit rate for turnover without
retraining anything. Collapse prediction and signal into one step and that dial disappears.

**Note (Even when a model outputs a direction).** Some models classify rather than regress, and
appear to emit a signal directly. The layers still exist and are still worth separating:

```text
P(up) = 70%          prediction   — what the model believes
long                 signal       — the direction that belief implies
30% of capital       position     — how much that belief is worth betting
+0.4% after fees     result       — what the market paid for it
```

**Claim.** A model replaces the rule, not the backtest.

Momentum, MACD and a gradient-boosted tree are alternative ways of producing the same object — a
signal. They sit at the same point in the chain and are judged the same way. What follows the
signal (sizing, costs, execution, metrics) is unchanged, which is precisely what makes a rule and a
model comparable at all. If adopting a model required a different backtester, any performance
difference would be uninterpretable.

**Note.** So the constraint from the rule-based case survives intact: the backtester must not know
where the signal came from. In this project it holds — the multi-asset backtester is a loop over
the single-asset one and contains no strategy logic. See
[Backtest Prototype — Implementation Notes](../Backtest_prototype/Backtests.md).

## 3. Four Levels of Validation

Each layer is tested on its own terms, and passing one says nothing about the next.

| Level                | Question                               | Typical measure                      | Where                                                                   |
| -------------------- | -------------------------------------- | ------------------------------------ | ----------------------------------------------------------------------- |
| **Model**      | does the prediction track the outcome? | test IC, MSE, accuracy               | out-of-sample only                                                      |
| **Signal**     | is the direction right, and tradeable? | bucket monotonicity, turnover        | [02 § 4](02-building-signals.md)                                        |
| **Strategy**   | does it survive real constraints?      | Sharpe, drawdown, return after costs | [04](04-understanding-backtesting.md), [05](05-evaluating-performance.md) |
| **Robustness** | does it persist?                       | across years, markets, parameters    | [06](06-overfitting-and-robustness.md)                                   |

**Note (Each arrow loses candidates).** High test accuracy is not economic value; economic value is
not profit after costs; profit after costs is not stability out of sample. A model can predict
direction 55% of the time and still lose money, because the 45% it gets wrong are the larger moves,
or because acting on it every day costs more than the edge.

## 4. The Build Order

| # | Stage                                          | What happens                                                                  | Chapter                               |
| - | ---------------------------------------------- | ----------------------------------------------------------------------------- | ------------------------------------- |
| 0 | **Validate the data**                    | Confirm prices are continuous and corporate actions are adjusted              | [100](100-dataset.md)                  |
| 1 | **State a hypothesis, compute a signal** | Turn an intuition into a number, then test that it carries information        | [02](02-building-signals.md)           |
| 2 | **Size the positions**                   | Signal → weights → dollars → shares                                        | [03](03-from-signal-to-position.md)    |
| 3 | **Simulate**                             | Apply the positions to history with realistic timing                          | [04](04-understanding-backtesting.md)  |
| 4 | **Evaluate**                             | Reduce the PnL series to numbers you can judge                                | [05](05-evaluating-performance.md)     |
| 5 | **Attack the result**                    | Ask how much of it is signal and how much is search                           | [06](06-overfitting-and-robustness.md) |
| 6 | **Try a model**                          | Ask whether a learned prediction beats the rule — same sizing, same backtest | —                                    |

**Note (Stage 0 is not optional).** Every later stage inherits whatever is wrong with the data. An
unadjusted split is the largest move in the sample by construction, so a trend follower reads it as
the strongest signal it has ever seen — and the equity curve will look *better*, not worse.

**Note (Test the signal before you backtest it).** Stage 1 ends with a check — sort assets into
buckets by signal value and look at the mean forward return per bucket. It is cheaper than a
backtest, and a monotone staircase is much harder to fool yourself with than a rising equity curve.
A signal that fails here will not be rescued by anything downstream.

**Note (Stage 6 comes last for a reason).** A model is only worth testing once the rule-based
version, its costs and its failure modes are understood — otherwise there is no baseline to beat
and no way to tell whether the model added value or merely added parameters.

## 5. Where Each Stage Fails

The stages fail in different ways, and the symptoms are easy to misattribute — the most common
mistake is reading a data defect as a code bug.

| Stage      | Failure                     | What you see                        | Where it is treated                   |
| ---------- | --------------------------- | ----------------------------------- | ------------------------------------- |
| Data       | Unadjusted corporate action | A vertical step in the equity curve | [100 § 1.1](100-dataset.md)           |
| Signal     | No information              | Flat or non-monotone buckets        | [02 § 4](02-building-signals.md)      |
| Sizing     | Exposure not what you think | Gross or net drifts from target     | [03](03-from-signal-to-position.md)    |
| Simulation | Look-ahead bias             | Implausibly smooth, high Sharpe     | [04](04-understanding-backtesting.md)  |
| Evaluation | One number hides the path   | Good Sharpe, unlivable drawdown     | [05](05-evaluating-performance.md)     |
| Robustness | Parameters were searched    | Result vanishes out of sample       | [06](06-overfitting-and-robustness.md) |
| Model      | Fitted to the sample        | Good IC in train, none in test      | out-of-sample split                   |

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
assets, which is what the standardization in [02 § 6](02-building-signals.md) is for.

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

- The same discipline as the rolling-quantile rule in [02 § 7](02-building-signals.md): rank and
  fit using only what was knowable at the time.
- Formal treatment of splits and why a backtest overstates: [06](06-overfitting-and-robustness.md).

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

**Judging the model itself** uses rank correlation per date, not accuracy:

```python
ic = pred.corrwith(fwd_return, axis=1, method="spearman")
ic.mean(), ic.mean() / ic.std()          # average IC, and its stability
```

| Measure | Plausible on daily data | Almost certainly a bug |
| --- | --- | --- |
| Mean daily IC | 0.02 – 0.05 is already good | above 0.15 |
| R² | 0.001 – 0.01 | above 0.1 |

An R² of 0.3 on daily returns is not a discovery; it is a look-ahead bug. Check the `shift(-h)`
alignment first — it is the cheapest sanity check in the whole pipeline.

[← Index](00-index.md)
