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

| Layer | What it does | Output | Example |
| --- | --- | --- | --- |
| **Features** | describe the market | prices, volume, volatility | 21-day realised vol |
| **Rule** *or* **model** | encode or learn a regularity | a number | MACD; ridge regression |
| **Prediction** | state a judgement about the future | expected return, P(up), expected vol | `+0.8%` next week |
| **Signal** | turn that judgement into a direction | `+1` / `−1` / `0` | long if prediction > 1% |
| **Position** | decide how much to bet | a weight, after risk limits | 30% of capital, long |
| **Backtest** | apply it all to history under real constraints | a PnL series | after costs and delay |
| **Metrics** | judge the PnL | Sharpe, drawdown, turnover, hit rate | Sharpe 0.4, −18% |

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

| Level | Question | Typical measure | Where |
| --- | --- | --- | --- |
| **Model** | does the prediction track the outcome? | test IC, MSE, accuracy | out-of-sample only |
| **Signal** | is the direction right, and tradeable? | bucket monotonicity, turnover | [02 § 4](02-building-signals.md) |
| **Strategy** | does it survive real constraints? | Sharpe, drawdown, return after costs | [04](04-understanding-backtesting.md), [05](05-evaluating-performance.md) |
| **Robustness** | does it persist? | across years, markets, parameters | [06](06-overfitting-and-robustness.md) |

**Note (Each arrow loses candidates).** High test accuracy is not economic value; economic value is
not profit after costs; profit after costs is not stability out of sample. A model can predict
direction 55% of the time and still lose money, because the 45% it gets wrong are the larger moves,
or because acting on it every day costs more than the edge.

## 4. The Build Order

| # | Stage | What happens | Chapter |
| --- | --- | --- | --- |
| 0 | **Validate the data** | Confirm prices are continuous and corporate actions are adjusted | [100](100-dataset.md) |
| 1 | **State a hypothesis, compute a signal** | Turn an intuition into a number, then test that it carries information | [02](02-building-signals.md) |
| 2 | **Size the positions** | Signal → weights → dollars → shares | [03](03-from-signal-to-position.md) |
| 3 | **Simulate** | Apply the positions to history with realistic timing | [04](04-understanding-backtesting.md) |
| 4 | **Evaluate** | Reduce the PnL series to numbers you can judge | [05](05-evaluating-performance.md) |
| 5 | **Attack the result** | Ask how much of it is signal and how much is search | [06](06-overfitting-and-robustness.md) |
| 6 | **Try a model** | Ask whether a learned prediction beats the rule — same sizing, same backtest | — |

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

| Stage | Failure | What you see | Where it is treated |
| --- | --- | --- | --- |
| Data | Unadjusted corporate action | A vertical step in the equity curve | [100 § 1.1](100-dataset.md) |
| Signal | No information | Flat or non-monotone buckets | [02 § 4](02-building-signals.md) |
| Sizing | Exposure not what you think | Gross or net drifts from target | [03](03-from-signal-to-position.md) |
| Simulation | Look-ahead bias | Implausibly smooth, high Sharpe | [04](04-understanding-backtesting.md) |
| Evaluation | One number hides the path | Good Sharpe, unlivable drawdown | [05](05-evaluating-performance.md) |
| Robustness | Parameters were searched | Result vanishes out of sample | [06](06-overfitting-and-robustness.md) |
| Model | Fitted to the sample | Good IC in train, none in test | out-of-sample split |

**Note.** The order is forced in one direction — you cannot evaluate before simulating, or simulate
before sizing. The one shortcut is that stage 1 can be validated *without* stages 2–4, and it
should be.

---

## Common pitfalls

| Belief | Correction |
| --- | --- |
| "Momentum is a strategy." | It is a hypothesis, so a family of signals. A strategy also needs a sizing rule. |
| "ML validates the signal." | ML *produces* signals. The backtest validates the whole strategy. |
| "A prediction is a signal." | A prediction is a number about the future; a signal is a decision. A trading rule sits between them. |
| "High accuracy means it makes money." | Not after costs, not if the errors are the big moves, not necessarily next year. |
| "The backtest is part of the strategy." | It is the instrument that measures one. Changing it changes your ruler, not your idea. |
| "A signal is good if the backtest looks good." | Test the signal on its own first; an equity curve is far easier to rationalize. |
| "Bad data makes results look bad." | An unadjusted split usually makes them look *better*. |

## Next → [02 · Building Your Own Signal](02-building-signals.md)

Before moving on, write down — in one sentence each — the hypothesis you want to test, the number
that would express it, and the observation that would prove it wrong. Chapter 02 starts from
exactly that.

You should be able to explain:

- [ ] Why prediction, signal and position are three different objects
- [ ] Why a model replaces the rule but not the backtest
- [ ] Why a high test accuracy is not yet a reason to trade
- [ ] Which stage a vertical jump in the equity curve belongs to

[← Index](00-index.md)
