# Walk-Forward Modelling, Winsorization, and Standardization

> - **Source:** lecture 6 (`docs/recording_script/lecture_6.vtt`), transcribed 2026-09-02.
> - **What it is:** the step from *signal exploration* to *modelling* — how to split a price
>   history for time-series fitting, which layer of the split chooses what, and the two
>   pre-processing steps (clip, then standardize) a signal must pass before a model sees it.
> - **Provenance:** content is as taught in class. A block opening with *Added* was worked out
>   afterwards and was not said in the lecture. The market narrative in § 8.2 is as told in
>   class and is **not** audited against any fund's filings.
> - **See also:** [02 · Testing a Signal](../docs/02-testing-a-signal.md) for the bucket and
>   beta tests this chapter now feeds into a model · [04 · Volatility Regimes](../docs/04-volatility-regimes.md)
>   for the VIX conditioning it refers back to · [09 · IC and R²](../docs/09-ic-and-r-squared.md)
>   for the R² levels quoted in § 8.1 · [Implementation Notes](../Backtest_prototype/Backtests.md).
> - **Written up as:** [05 · Modelling](../docs/05-modelling.md), which is the course
>   chapter built from §§ 1–6 of this note.

---

Where the course now stands: the signals have been explored one at a time — bucket returns,
quantile portfolios, equity curves, and the *additional* information a new signal adds on top of
an existing one. Momentum works, MACD adds something on top of momentum, VIX adds something on
top of both. **The open question is how to combine them**, and combining means fitting a model.

Everything below is about making that fit honest.

## 1. Why one train/validation/test split is not enough

The textbook split — one contiguous block for training, one for validation, one for test — can be
run on a price history, and it will produce a number. It has three defects, and they compound.

| Defect | What goes wrong |
| --- | --- |
| **It fits once, so it discards time** | A single fit over several years asserts that one set of coefficients describes all of them. It does not. Early in the pandemic the world locked down at once, demand collapsed, and nobody wanted oil; the consensus was that the economy had permanently gone electronic. Coming out of it, the world returned to roughly what it was, and energy prices then flew on war. Data from the first regime has little bearing on the second. |
| **It leaves almost no backtest** | Give validation a year and test a year — generous by data-science standards — and validation is roughly 250 daily observations. A year is also too short for the market to change much, so the split never asks the question that matters: when the regime *does* shift, does the strategy survive it, or does the book blow up? Max drawdown measured over one calm year is not a risk estimate. |
| **The whole dataset is small, and the signal is faint** | A school project with a thousand points and an R² of 0.5–0.8 is normal; in physics 0.9 is normal. In finance and in user-behaviour work, an R² of **0.1–0.2 is already a good result**. Low true correlation plus few points is exactly the regime where a fit lands on noise — pick ten points out of a cloud and a line through them at R² 0.8 is easy to find. |

**The tempting fix is the wrong one.** Duplicating the dataset to manufacture observations — the
classic interview question, *what happens to $\beta$ and to its standard error when you duplicate
every row of a regression* — leaves the fit where it was and shrinks the reported uncertainty. It
is overfitting with extra steps.

## 2. Walk-forward validation

Cut the history into short segments, then slide a train / validation / test frame across them.

### 2.1 Why segments, and how long

**A regime shift takes time, because the participants are people.** The market cannot plausibly
shift within a day — the crowd does not change its mind at once, even if individuals do. Within a
month, after a run of large news, one shift is plausible. Within a year or two there is room for
several. So a segment of roughly **two to three months** is short enough that one segment is
approximately one regime, and long enough to hold a usable sample.

### 2.2 The slide

With segments numbered $1, 2, 3, \ldots$:

| Iteration | Train | Validation | Test |
| --- | --- | --- | --- |
| 1 | 1–3 | 4 | 5 |
| 2 | 2–4 | 5 | 6 |
| 3 | 3–5 | 6 | 7 |

Each step moves the test segment forward by one. **The previous iteration's test becomes the next
iteration's validation** — every segment is eventually scored out of sample, and the number of
out-of-sample observations grows with the length of the history rather than being fixed at one
year.

What it buys, defect by defect: time is no longer ignored, because each fit sees one regime's
worth of data; the backtest sample is now every segment rather than one block; and a regime shift
landing inside a validation segment becomes a *test* of the strategy rather than an accident that
the single split happened to miss.

### 2.3 The gap between fitting and testing, and the refit

Train ends, then a validation segment intervenes, then test. That gap is a month or more of
market the model has never seen, and test performance suffers for it. The repair is the same
move Lasso already forces: **select on one window, refit on the window that ends where the
prediction starts.**

Lasso adds an $L_1$ penalty to the objective, which drives coefficients to zero and so doubles as
feature selection. Used that way it is standard to **refit** the surviving features without the
penalty before predicting — the penalty's job was selection, not estimation. Walk-forward
inherits the same two-step shape:

1. Fit on train, use the validation segment to **select features**.
2. **Refit** on a window shifted forward, then apply to test.

Two house styles exist for step 2 — refit on the shifted training window only, or refit on
training *plus* the validation segment. The sample sizes differ little and either is defensible;
it is a preference, not a correctness issue.

## 3. Two validation layers, and what each one is allowed to choose

There is the small per-fold validation segment inside the slide, and the large held-out validation
block at the end of the history. They do different jobs.

| Layer | Chooses |
| --- | --- |
| **Inner** — the validation segment inside each walk-forward iteration | which **features** survive, then the refit |
| **Outer** — the large held-out validation block | the **model class** (Lasso, Ridge, …), its **hyperparameters** (the $\lambda$ grid: 0.1, 0.5, 0.7, 1), and the **portfolio optimization parameters** |
| **Test** | nothing. It is not supposed to be touched. |

Why features cannot be trusted from training alone: exploration already looked at which signals
worked *in the training period*, so of course the model fits it well. That momentum looked useful
in hindsight over the training block does not mean it was useful going in — the selection may
simply have found what was globally true of that block and nowhere else. The held-out space
exists precisely to answer that, which is why it is left untouched until then.

**Note.** A signal's usefulness is not constant either. When a signal starts to fail, or when
more signals are added, momentum should no longer carry the weight it did — which is another
thing the outer layer has to decide rather than assume.

### 3.1 The optimization parameters

The portfolio step solves, for weights $w$,

$$\max_w \quad E[r_p] - \gamma \cdot \text{Risk}(w)$$

subject to constraints such as

$$\sum_i w_i = 1.0 \qquad \sum_i |w_i| \leq 2.0 \qquad |w_i| \leq 0.20$$

— net exposure 100 percent, gross exposure at most 200 percent, and no single asset above 20
percent — where $E[r_p]$ is the portfolio's expected return, $\text{Risk}(w)$ its risk measure, $\gamma$ the
risk-aversion coefficient, and $w_i$ the weight on asset $i$. (The lecture originally wrote the
coefficient as $\lambda$, then renamed it to $\gamma$ so as not to collide with the Lasso penalty.)

Two of these need tuning, and neither has a value you can reason your way to:

- **$\gamma$, the risk-aversion coefficient.** Nobody can say from first principles whether a risk
  appetite is 0.3, 0.5, or 1 — the number has no interpretable units. It is chosen by trying
  values and reading the result.
- **The per-asset cap.** With only 37 assets, a 20 percent cap may be too tight to let the book
  hold enough of the names that are actually paying. Try 25 percent, try 30 percent. The gross
  and net exposure constraints, by contrast, are set by mandate and are not free parameters.

All of this tuning happens **in the large outer validation block**, not in the small per-fold
validation segments.

## 4. Winsorization: clip the signal, do not delete the point

### 4.1 The problem

The expectation is that a signal is spread evenly across $[0, 1]$ after ranking. The actual
distribution is a **barbell** — heavy at both ends, thin in the middle. Momentum does this
readily: a name rips for a stretch and its signal sits pinned at an extreme.

A regression fitted through that cloud is dragged by the few points far out on the axis. Move one
of them and the fitted line swings; the coefficients are then **volatile for reasons that have
nothing to do with the market**.

### 4.2 Why the textbook fix does not apply

Standard practice is to detect outliers and drop them. Here, both halves of that fail:

- **The sample is already too small.** Every deletion makes the small-sample problem of § 1 worse,
  and in a messy sample it is genuinely unclear which points are outliers at all.
- **The outliers carry information.** What the book does when a signal goes extreme is exactly
  what you want the model to learn. Delete those rows and the model can never learn it.

### 4.3 The fix

Clip rather than delete — industry calls it **winsorization**. Choose a threshold, find the
rolling quantiles, and pull anything outside the band onto the band:

- pick a pair such as 1 % / 99 %, or 2.5 % / 97.5 % — there is no canonical choice
- if the signal exceeds the upper quantile, set it to the upper quantile; below the lower, set it
  to the lower

```python
lo = signal.rolling(60).quantile(0.01)
hi = signal.rolling(60).quantile(0.99)
clipped = signal.clip(lower=lo, upper=hi)   # never write this back over `signal`
```

**Compare raw to raw.** The rolling quantiles for the *next* observation must be computed from the
**unmodified** signal history, not from the clipped series. If yesterday's outlier was replaced by
its cap and that cap is then fed into today's quantile, the band drifts inward and the procedure
eats itself. Keep the raw column intact and produce the clipped one alongside it.

The rolling window also fixes a worry that would be fatal for a fixed threshold: a value that is
an outlier relative to the last three months may be entirely ordinary six months later, once the
market has moved. Because the band is re-estimated each step, that happens automatically — nothing
is permanently pinned at the 99th percentile of an old window.

## 5. Standardization: put the signals on one scale

### 5.1 The problem

Momentum lives in roughly $[-0.05, 0.05]$. VIX lives in $[0, 100]$. Regress returns on both and
the fitted coefficients are forced to compensate: momentum's $\beta$ comes out enormous, VIX's
tiny. Two consequences, in opposite directions:

- a **large $\beta$ amplifies noise** — a small wobble in momentum, which may be pure measurement
  noise, is multiplied into a large change in the prediction;
- a **small $\beta$ suppresses signal** — when VIX genuinely moves, the model barely responds.

### 5.2 Why the wobble is usually noise

Every input is an **estimate**, and every estimate carries error. The true quantity is not
observable; what is observable is a measurement of it, and a return-based momentum measurement is
noisy because it is the residue of players entering and leaving. Even an averaged momentum has
real measurement error in it.

The lecture's analogy is the hypothesis test: with $H_0$ that two means are equal, $H_1$ that they
are not, and $\alpha = 0.05$, rejecting means roughly 95 percent confidence — and roughly a 5
percent chance of a false positive. Models inherit the same property. A jump in $\beta$ is often
not the market shifting; it is noise being fitted.

### 5.3 The fix and what it buys

Standardize every signal **the same way** — z-score it, or divide by its standard deviation, or
divide by its sum; the choice matters less than applying one choice uniformly. Then:

| Benefit | Why |
| --- | --- |
| **Coefficients become comparable** | $\beta$ magnitudes can be read against one another, so you can see which signal the model is actually leaning on. |
| **The coefficient path becomes a regime read** | Plot every $\beta$ over time on one chart: momentum dominating in one stretch and volatility in another *is* the change in market sentiment, made visible. |
| **Errors average down** | With the signals on one scale, their errors are roughly independent and their coefficients of comparable size, so across many signals the errors partly cancel. The model is far less likely to be dragged around by any single one. |

## 6. Which mean and standard deviation you are allowed to use

Standardizing needs a mean and a standard deviation, and choosing them is where look-ahead
usually enters.

The rule follows from **where the model is built**: at the *end* of the training window. At that
moment, every observation inside the training window is known. So standardizing training data with
the mean and standard deviation of the **whole training window** is legitimate — from the point
of view of the individual signal it looks like hindsight, but from the point of view of the model
the whole window is already history, and the full-window estimate is the more accurate one.

| Stage | Point of construction | Statistics you may use |
| --- | --- | --- |
| Initial fit | end of the training window | the whole training window |
| — | — | **never** the validation segment |
| After a refit | end of the refit sample | the whole refit sample, validation segment included |

The lecture returns to this repeatedly for one reason: in time series, **the smallest leak makes
the model look excellent**, and the gap between that result and live performance is enormous.

## 7. The assignment

Write the whole walk-forward pipeline end to end, then drop a **plain Lasso** into it. Parameter
choices — the $\lambda$ grid, the feature-selection rule, the optimizer settings — come after the
pipeline runs.

The standing priority: a complete research pipeline (signals → model → optimization) beats more
signals. Once the pipeline exists, later work is mostly feeding new signals and new models into
it. Anyone behind on the earlier assignments should skip the VIX and MACD extensions and get the
basic pipeline working first — that is also what a new hire is put on first at a firm, precisely
because it teaches the research process and the market at the same time.

## 8. Q&A — a weak result is the correct result

### 8.1 Reading a disappointing signal test

A student reported a signal whose spread was not significant (values around 0.82, −1.13, 0.67) and
whose error bars overlapped. The answers, in order:

- **Do not look at test.** Test is not supposed to be touched.
- **Faintness is expected.** Momentum is traded by a very large number of participants; if a
  momentum signal on public data were strongly significant, everyone would be making money on it.
  An R² of 10 percent is already good; 30–40 percent would imply a portfolio returning 40–50
  percent annually, at which point look-ahead is the likelier explanation than skill.
- **Check which error bar was plotted.** Bars built from the **sample standard deviation** must
  overlap — two return distributions overlap heavily, always. Bars built from the **standard error
  of the mean** need not. The hypothesis being tested is that the two *means* differ, not that the
  two distributions are disjoint. If two full return distributions really did separate, you could
  short the low group and buy the high group and draw a straight line upward — an equity curve
  that neither Buffett nor Soros has ever produced.
- **The payoff comes from repetition.** A quant earns from the law of large numbers: a small edge
  per bet, taken over very many bets. That is also why a portfolio built on a real but small mean
  difference still looks unimpressive on any single stretch.

### 8.2 Why last year was a momentum year

*As told in class; not audited.* Two episodes, both driven by who was in the market rather than by
anything in the price series:

- **April, the tariff shock.** March and April were quiet — institutions had de-risked ahead of the
  announcement and the tape drifted lower. The announcement then surprised everyone with tariffs
  applied across the board; three violent days followed, and institutions were carried out,
  including **AQR**, whose momentum book was blown out at the low. Retail and small funds bought
  that low. What followed was a long, steady unwind of the tariffs — and a long, clean momentum
  leg. A pure momentum strategy would have been short into the crash and long the recovery.
- **August–September, memory and storage.** The market realized capacity was short. **SanDisk**
  (transcribed "smdk") ran roughly eighteen-fold before giving back some 40 percent — another long
  trend to hold.

The dispersion across funds that year makes the point about timing: one fund is quoted at +17–18
percent for the year; another lost 28 percent in the April dip alone and finished around −10
percent despite the two trends that followed. Whoever was not carried out in April had a
20–30 percent year. Momentum has big years and thin years, and which one you get is the market's
choice, not the model's.

### 8.3 What to do with a signal that does not work

Not abandon it. A single simple signal is *supposed* to be weak — if a simple signal were strong,
the only explanation would be data nobody else can obtain, and that is not the situation here.
Even the classic example of proprietary data — satellite imagery, bought and flown privately —
stopped being an edge once vendors formed: one person cannot buy a satellite, but a group can, so
a data vendor now sells the same feed at nearly the same latency.

The productive move is to look **around** the signal rather than at it:

1. Take the dates where the signal fired and made money, and the dates where it fired and lost.
2. Ask what the market was doing *before* each, and what happened *after*.
3. If those two behaviours differ, build a signal that captures the difference — this is exactly
   why the VIX exercise was set: to see how momentum behaves in different volatility states.
4. Combine. Each added signal strengthens the stack a little.

The rough progression given: around **10 signals** to clear transaction costs, **20** to keep pace
with the index, **30** before there is something that genuinely beats it. Getting there is a
matter of generating and testing ideas one at a time.
