# Leverage, Deleveraging, and the Time-Horizon Lesson

> - **Source:** lecture / class discussion, transcribed 2026-08-23; the position mechanics
>   of § 1.2, the liquidation of § 1.3 and the "was it a hunt" question of § 1.5 were added
>   from lecture 5 (`docs/recording_script/lecture_5.vtt`), transcribed 2026-08-31.
> - **What it is:** two passages from one session — a market narrative about a leveraged
>   AI fund blowing up (used to motivate the class), then a review of when a momentum /
>   MACD signal works and fails.
> - **Provenance:** the narrative is as told in class and is **not** audited against any
>   fund's filings. A block opening with *Added* was worked out afterwards and was not said
>   in class.
> - **Filed under:** market knowledge and insights — commentary on market behaviour, not
>   a formal chapter of the course spine.
> - **See also:** [Market 101 — Structure, Volatility, and Short Selling](market-101-foundations.md)
>   for the underlying market structure — leverage, margin calls, and forced covering ·
>   [Cross-Asset Drivers](cross-asset-drivers.md) for what the other sleeves were doing the
>   same week.

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

### 1.2 The position: levered long the AI complex, short one name as the hedge

As described in the later session:

| Leg | What was in it |
| --- | --- |
| **Long** | the AI complex, concentrated — memory and storage (transcribed as **SanDisk**), compute and data-centre names, **Nvidia**, **Microsoft** |
| **Short** | a **single** name, **Adobe**, carried as the hedge |
| **Leverage** | roughly **four times** |

- The long side is one bet written several ways: every name in it answers to the same
  question of whether AI capital expenditure keeps growing.
- The AI complex had in fact topped roughly **two months earlier** — around the time of the
  SK Hynix US listing and, on the same stretch, the SpaceX listing — and had been grinding
  lower since. The blow-up came at the end of that slide, not at the start of it.

*Added.* The hedge is the part worth studying, because it did not hedge. A single-name short
against a concentrated levered basket removes almost none of the basket's risk: the two share
little beyond the market factor, so when the basket fell the short did not rise nearly enough
to offset it. At four times leverage there is very little room for a hedge to be approximately
right — the margin binds long before the offset arrives. Being *short something* is not the
same as being hedged, and the size of the mismatch is what the leverage multiplies.

### 1.3 The unwind: small levered funds flee first

- Because they bought late, the small funds sat on thin gains when the first small dip
  arrived. They were also **small in size** and **leveraged many times over**.
- At the first sign of weakness they sold — fast. That cascade is the **deleveraging
  (去杠杆)** behind the sharp, "crazy" drop in AI names.
- The selling pressure pushed the big fund itself past its leverage limit → it **blew
  up (爆仓)**.
- **How it was closed:** not sold into the market over days but handed over in a **block
  trade (大宗交易)** — the whole position taken down by one or a few buyers at a large
  discount. That is the only way to move a position of that size at once, and the discount
  is the price of immediacy ([Market 101 § 5](market-101-foundations.md)).
- **The next session those names ripped.** Microsoft rose about **10% in a day** — an
  extraordinary move for a company that size, which is what a discounted block being marked
  back up looks like from outside.

### 1.4 The market's inference: it must be a bottom

- If a fund this big blew up, no *bigger* fund can be behind it still holding. If
  leverage is already that extreme, another fund stacking the same leverage would mean
  the whole market is frantically margin-buying one stock — "like the Korean market."
- So the reasoning goes: the biggest levered players in AI have now been flushed out,
  and the original holders have stopped selling. The sellers are exhausted → **this is
  a low**.

### 1.5 "Was it a hunt?" — and why that story does not survive the arithmetic

The story going around afterwards was that Wall Street's old money had deliberately hunted a
young manager. It is a good story and a bad explanation:

- **The cost is on the wrong side.** Breaking one fund means erasing trillions of market
  capitalisation across the whole complex. Whoever did it holds far more of that damage than
  they could collect from the target.
- **Anyone visibly doing it invites the same treatment.** 螳螂捕蝉，黄雀在后 — turn the market
  over to catch one player and you are exposed to somebody larger doing it to you.
- **Nothing needs explaining.** Ordinary deleveraging plus a block sold at a discount and
  marked back up accounts for the whole sequence, drop and rebound alike, with no intent
  required.

The general form: when a mechanical explanation and an intentional one both fit, the
mechanical one is almost always the right read of a market this size.

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
- This is why the rule " **never short America**" (Buffett) exists: the same stock looks
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
- **The course's own answer came a session later**, and it is not a better lookback: identify
  the regime with a forward-looking volatility index and condition the signal on it — see
  [04 · Volatility Regimes](../docs/04-volatility-regimes.md).

---

## Key terms (EN ↔ ZH)

| English | 中文 | Meaning here |
| --- | --- | --- |
| deleveraging | 去杠杆 | levered funds selling to unwind margin |
| block trade | 大宗交易 | an entire position handed to one buyer at once, at a discount |
| hedge | 对冲 | an offsetting position — only a hedge if it actually shares the risk |
| leverage | 杠杆 | position size as a multiple of capital; here about 4× |
| blow up | 爆仓 | position forced to liquidate past its leverage limit |
| go long / bullish | 做多 | betting the price rises |
| slow grind (slow rise/fall) | 慢涨慢跌 | the trend regime where MACD works |
| violent burst (fast rise/fall) | 快涨快跌 | the spike regime where MACD fails |
