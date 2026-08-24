# Leverage, Deleveraging, and the Time-Horizon Lesson

> - **Source:** lecture / class discussion, transcribed 2026-08-23.
> - **What it is:** two passages from one session — a market narrative about a leveraged
>   AI fund blowing up (used to motivate the class), then a review of when a momentum /
>   MACD signal works and fails.
> - **Filed under:** market knowledge and insights — commentary on market behaviour, not
>   a formal chapter of the course spine.
> - **See also:** [Market 101 — Structure, Volatility, and Short Selling](market-101-foundations.md)
>   for the underlying market structure — leverage, margin calls, and forced covering.

---

## 1. The episode: a leveraged AI fund blows up

The instructor tells a recent market story. It is a narrative — names and mechanics are
as told in class, not audited against a specific fund's filings.

### 1.1 The setup: public holdings, lagging copy-cats

- A large fund — transcribed as **"Leo Paulo"** — ran a **heavily leveraged** position
  in AI stocks and **published its holdings**. Publishing was not the mistake.
- The real problem was the copy-cats behind it. Small funds saw the disclosure with a
  **lag**: the big fund had already bought near the bottom; the small funds entered
  later, chasing.

### 1.2 The unwind: small levered funds flee first

- Because they bought late, the small funds sat on thin gains when the first small dip
  arrived. They were also **small in size** and **leveraged many times over**.
- At the first sign of weakness they sold — fast. That cascade is the **deleveraging
  (去杠杆)** behind the sharp, "crazy" drop in AI names.
- The selling pressure pushed the big fund itself past its leverage limit → it **blew
  up (爆仓)**.

### 1.3 The market's inference: it must be a bottom

- If a fund this big blew up, no *bigger* fund can be behind it still holding. If
  leverage is already that extreme, another fund stacking the same leverage would mean
  the whole market is frantically margin-buying one stock — "like the Korean market."
- So the reasoning goes: the biggest levered players in AI have now been flushed out,
  and the original holders have stopped selling. The sellers are exhausted → **this is
  a low**.

---

## 2. Two readings of the same event

| | Quant view | Fundamental view |
| --- | --- | --- |
| **Question asked** | Is the selling exhausted? Is the signal turning? | **Who actually owns the stock?** |
| **Answer found** | Levered funds are gone → sellers exhausted → good entry | The marginal holders *were* levered funds → their exit is a serious structural blow |
| **Forecast** | Price ticks up → more levered funds return → they keep buying | Those buyers may never return, or only far more conservatively; reclaiming the old high is hard |
| **Horizon** | Days to a couple of months; at most ~a quarter | Longer; built from their own analysis, updated slowly |
| **Exit speed** | Machines catch a regime / signal reversal instantly | Few observations to read; moves late, more conservatively |

### 2.1 Why the quant view is not "wrong" for being short-term

- Quants do not look far — a week, a month, or two at most; even large quant asset
  managers rarely hold beyond a quarter.
- They do not need a long horizon because they read the market through **machine
  signals**: the moment the regime shifts and the signal flips, they can be out quickly.
- Fundamental investors have far fewer observations and build their view from their own
  analysis, so they move later and more cautiously.
- Neither side is "right" and the other "wrong" — the different conclusions follow from
  the **holding period and strategy**, not from who is smarter. Short term, most of the
  money is made by quant; long term is a different game.

### 2.2 The horizon lesson

- Do not act on someone else's "it's high / it's low": **their horizon is not yours**.
- Decide your own holding period and what you can actually forecast, then act.
- This is why the rule "**never short America**" (Buffett) exists: the same stock looks
  different through a one-week lens and a twenty-year lens. Long-term strategies are a
  different strategy, not a contradiction of the short-term one.

---

## 3. Into the lesson: when momentum / MACD works

The market discussion closes into the actual class topic — when a momentum or MACD
signal is usable.

### 3.1 The regime where it works: slow, grinding trends

- MACD is useful on **relatively long, slow trends** (慢涨慢跌): the short-term signal
  rides along, and the long-term signal follows — a little slower, but in the same
  direction.
- Both legs agree, so the crossovers give a clean long / short read.

### 3.2 The regime where it fails: a calm tape, then a violent burst

- The failure case is the opposite tape: a **flat, stable** market that suddenly turns
  into a short stretch of **fast up / fast down** (快涨快跌).
- The short-term signal cannot capture the burst, and the long-term signal cannot either
  — the move is over before it reacts. Neither leg helps.

### 3.3 What it asks of a quant (open question)

- A market that is *mostly* slow-trending but occasionally spikes is the hard case: the
  signal is right most of the time and blind exactly when the damage happens. The
  lecture poses the question and leaves it open.
- Natural next step with this repo's tools: test fast/slow MACD spans and EWMA
  half-lives (chapter 03) on the 37-ticker sample against a fast up/down window, and see
  what the lookback choices do to the losses in the spike regime.

---

## Key terms (EN ↔ ZH)

| English | 中文 | Meaning here |
| --- | --- | --- |
| deleveraging | 去杠杆 | levered funds selling to unwind margin |
| blow up | 爆仓 | position forced to liquidate past its leverage limit |
| go long / bullish | 做多 | betting the price rises |
| slow grind (slow rise/fall) | 慢涨慢跌 | the trend regime where MACD works |
| violent burst (fast rise/fall) | 快涨快跌 | the spike regime where MACD fails |
