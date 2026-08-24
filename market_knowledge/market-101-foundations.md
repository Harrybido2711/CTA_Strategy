# Market 101 — Structure, Volatility, and Short Selling

> - **Source:** lecture transcript `GMT20260816-005926_Recording.cc.vtt`, 2026-08-16.
> - **What it is:** the foundations of how a market works — asset classes, why people
>   trade, price discovery, buy side vs sell side, liquidity, market-maker economics —
>   then the precise definition of volatility, short-selling mechanics, and a
>   probability review closing on three interview problems.
> - **Filed under:** market knowledge — general finance that holds regardless of any
>   particular strategy.
> - **See also:** [Leverage, Deleveraging, and the Time-Horizon Lesson](leverage-deleveraging-and-horizons.md).

---

## 1. Asset classes

### 1.1 What actually separates them

The naive answer is "different real-life uses" — commodities are goods needed in the
physical economy (crude, wheat, cattle, gas, gold, silver), stocks are ownership,
derivatives are functions of an underlying, real estate is real estate.

That answer is not wrong, but it is not the one finance cares about. **The classes are
separated by how they behave in the market**, and the real-life differences are mostly
upstream of that.

### 1.2 The concrete difference: delivery

| | Commodity | Stock |
| --- | --- | --- |
| **On settlement** | You must actually deliver the oil — unless you sell the contract first | Ownership transfers electronically |
| **Historically** | Physical goods, physical logistics | A paper certificate of ownership |
| **Today** | Still physical at the end of the chain | The Depository Trust moves a record — "it's yours now, in a computer" |

This delivery requirement is what makes a commodity intrinsically a different instrument,
not merely a different ticker.

### 1.3 The difference that matters: risk characteristics

The first thing a standard finance class teaches is that asset classes carry **different
risk profiles** — they respond to the same shock in opposite directions.

| Shock | Gold | Stocks |
| --- | --- | --- |
| Inflation | up — the classic hedge | down |
| War / crisis | up | down |

Real estate is the odd one: barely correlated with anything else, but **illiquid**, which
is a separate problem entirely (§ 5). A \$65 million penthouse may take two years to sell
at \$65 million; an Nvidia share sells on Robinhood in a second.

---

## 2. Why anyone buys or sells

### 2.1 The four motives

| Motive | Buy side of it | Sell side of it |
| --- | --- | --- |
| **Speculation** | Bet the price rises | Bet the price falls |
| **Cash need** | Have spare cash to invest — an IRA contribution | Need cash for something real — a car |
| **Ownership** | Own a piece of a company you believe in; collect **dividends** | Believe the business has turned bad |
| **Switching** | Rotate into a better idea | Fund that rotation — money is finite |

**Speculation is what people picture, and it is not the bulk of the flow.** The classic
buy-and-hold style — Buffett's — is owning a piece of a company and taking dividends.
Coca-Cola pays a steady dividend every quarter precisely because it has nothing left to
invest in: everyone on Earth who could have a Coke already has one, so absent colonising
Mars there is no market left to expand into, and the profit goes to shareholders.

Pension funds and mutual funds buy for this reason, not for the speculative one. What
they want is **capital preservation** — first, do not lose the money.

Selling to switch is likelier than it looks: buying Tesla may mean selling Apple, and
that says nothing about Apple.

### 2.2 Flow that has nothing to do with the company

This is the part worth carrying into signal work.

SPY is an ETF run by State Street holding the S&P 500 constituents at index weights. When
a company drops out of the index:

- State Street **must** liquidate its entire position in that name — not because anyone
  judged it, but because the index says so.
- It **must** buy the replacement, at size.
- Every other fund tracking a similar basket does the same thing, on the same day.

The result is an enormous buying or selling flow **unrelated to the balance sheet or the
cash-flow statement**. These are huge capital movements, and they are what people mean by
"institutional clients control the flow of the market."

→ The same lesson from the other direction — forced flow from levered funds unwinding:
[Leverage, Deleveraging, and the Time-Horizon Lesson](leverage-deleveraging-and-horizons.md).

---

## 3. Price discovery

### 3.1 Finding a counterparty

If A wants to buy and B wants to sell and neither knows the other exists, they need a
**platform** — Amazon, Etsy, Craigslist for a pen; an exchange for a stock. That part is
easy. Agreeing a price is the hard part.

### 3.2 Which price is "the" price

Four candidates, none of them canonical:

| Candidate | Definition | Weakness |
| --- | --- | --- |
| **Last traded price** | What the last identical item actually traded at | Depends entirely on *when* — one second ago is a good proxy, one year ago is not |
| **Mid price** | (highest bid + lowest ask) / 2 | Needs a live two-sided book |
| **Fundamental price** | What the thing is worth — manufacturing cost for a pen; a DCF or multiples valuation for a stock | Is a judgement, not an observation |
| **Bid or ask** | One side's standing quote | Not fair by construction — it is one side only |

A negotiated trade can land anywhere in between: a \$7 bid against a \$10 ask may settle
at \$8 or \$9, and nothing forces the midpoint.

### 3.3 The mystery box

Change the pen to a **mystery box** and the fundamental price disappears. The only way to
learn the price is **to trade** — that is what *price discovery* means.

- Some participants are **informed** (they know the box is worth \$10), others **naive**
  (they think it is worth \$5).
- In the classic model the informed keep buying at \$5, more buyers push the price up,
  and it converges to \$10, where they stop.
- The informed traders are the mechanism by which the price becomes right.

### 3.4 Why a market maker exists

Negotiating every trade is slow, even once the platform solves discovery. It is far
better if **someone is always standing there** with a price already written on the board
— you either take it or you don't. That standing willingness to buy and sell is the
service; § 8 is why it gets paid for.

---

## 4. Buy side and sell side

### 4.1 The split

| | Buy side | Sell side |
| --- | --- | --- |
| **In one line** | People with money | People providing services |
| **Capital at risk** | Their own | The client's |
| **Revenue** | Investment returns | Commissions and fees |
| **Who** | Hedge funds, mutual funds, pension funds, prop shops / HFT, **retail investors** | Bank sales & trading, investment banking, research, brokers, investment advisers |

**Retail is on the buy side** — the point people forget. If you have ever bought a stock
on Robinhood with your own cash, that is the buy side.

### 4.2 Hedge fund vs mutual fund

| | Hedge fund | Mutual fund |
| --- | --- | --- |
| **Management** | Actively managed — someone decides the weight on every asset | Tends toward passive; buy and hold |
| **Original purpose** | *Hedge* the risk — deliver a return **uncorrelated** with the market, so it earns whether the market rises or falls | Track or hold; deliver market exposure |
| **Disclosure** | Secretive; exempt from mutual-fund disclosure because only accredited / high-net-worth investors may buy | Open to the public, so heavily regulated |
| **Liquidity** | Illiquid — all-or-nothing withdrawals, penalties for withdrawing early, and the fund can force capital back to you | Liquid — must create and redeem shares on demand |
| **Fees** | High | Low |

Pension funds sit further along the same axis: even more risk-averse, saving for
retirement over decades.

Prop shops and HFT firms trade **their own capital**, usually structured as partnerships.

### 4.3 Broker vs dealer — agent and principal capacity

A market maker sits in the middle of the buy/sell split because which side it is on
depends on the **capacity** it is acting in:

| | Broker (agent capacity) | Dealer (principal capacity) |
| --- | --- | --- |
| **What happens** | Finds a counterparty for the client and charges a commission | Is the counterparty — sells the client the shares itself |
| **Whose risk** | The client's | **Its own book** |
| **Which side** | Sell side | Buy side |

Modern market makers do both, which is why they are called **broker-dealers**. Most banks
likewise run prop divisions trading their own money — so a firm labelled sell side has
buy-side desks inside it.

---

## 5. Liquidity

### 5.1 Two conditions, not one

**An asset is liquid when you can execute quickly *and* at a good price.** People
remember the first half and drop the second, and the definition collapses without it:

- A \$65m house that takes two years to sell at \$65m fails the speed test.
- The same house sells **immediately** at \$40m — it passes speed and fails price.

"Good price" means relative to a fair price — the last traded price, the mid, or the
fundamental value. A bid or an ask alone is not fair; it is one-sided.

### 5.2 Size is part of the definition

Liquidity is stated **at a size**. Anything is liquid for one dollar of it; \$10 million
of the same thing is a different question. Comparisons only mean something at matched
size.

| Liquid | Illiquid |
| --- | --- |
| Anything exchange-listed (NYSE names) | Houses and real estate |
| Mutual funds — redeemable near any time | Hedge fund stakes |
| Commodity contracts; physical gold, via a gold shop | OTC stocks — anything not exchange-traded |

---

## 6. Market plumbing

**Primary vs secondary market.** Primary is the first issuance of the stock — where
investment bankers work. Secondary is every change of ownership after that — where sales
& trading and prop desks work.

**Exchanges** (NYSE, NASDAQ) provide the venue and do the unglamorous work: matching,
settlement, delivery, bookkeeping, and policing good faith. Alongside them sit
depository trusts and the regulators (SEC, FINRA).

**Why a quant might care.** Exchange mechanics are the market's **microstructure** — how
orders are processed, how the matching engine works — and they bound how efficient an
algorithm can be. In HFT every nanosecond matters. Outside HFT this is largely
irrelevant, including for interviews.

---

## 7. Motivations, and whether trading is zero-sum

| Participant | Horizon | Objective |
| --- | --- | --- |
| HFT | Seconds and below | Capture mispricing; short-term profit |
| Prop / hedge funds | Days to a quarter | Return on own capital |
| Retail | Long — mostly buy and hold, despite the headlines | Wealth over decades |
| Mutual and pension funds | Ten years | Retirement funding; capital preservation |

**Is trading zero-sum?** In dollars, yes — strictly negative-sum once exchange fees are
counted. In **utility**, no:

> You are an HFT firm and I am a long-term investor. You are happy because you captured
> two cents of edge. I am happy because in ten years my wealth doubles. Are you happy?
> Yes. Am I happy? Yes. Is it zero-sum? Yes.

The resolution is that zero-sum only bites **if both sides liquidate at the same moment**
— and they don't. You liquidate next nanosecond, I liquidate next decade. Different
objectives mean a trade need not have a winner and a loser.

→ The same point in the setting of a real market event:
[Leverage, Deleveraging, and the Time-Horizon Lesson § 2](leverage-deleveraging-and-horizons.md).

---

## 8. Why a market maker deserves the spread

The challenge: if this is a no-brainer, competition should drive the price of the service
to zero and the spread would vanish. It does not. Why?

**The stated answer is that liquidity is a service** — always being there to buy and sell
is valuable, like guaranteeing a fair game. But *why* it is valuable is that it carries
real risks that must be compensated:

| Risk | What it is |
| --- | --- |
| **Inventory risk** | You are never buying exactly at the right tick. Positions accumulate; the price moves against you; you may be forced to hold overnight |
| **One-sided flow** | Everyone wants to buy and nobody wants to sell — you cannot stay flat |
| **Adverse selection** | The mystery-box problem: your counterparty knows the box is worth \$10 and you don't. You get picked off by the informed, so you must **earn back, on average, from the naive** |
| **Capital requirement** | A genuine barrier to entry — you need the balance sheet to stand there at all |

Adverse selection is the load-bearing one: the spread is priced to cover the expected
cost of being on the wrong side of an informed trade.

---

## 9. Volatility, defined correctly

Everyone believes they know this one, so it is worth stating exactly. The common answer —
"the sample standard deviation of the asset price" — is **wrong on both counts that
matter**.

### 9.1 The formula

Given a sample of prices $P_t$, first compute the **log return**, then take the *sample*
standard deviation of the returns:

$$r_t = \ln \frac{P_t}{P_{t-1}}, \qquad \sigma = \text{sd}\left( \{ r_t \} \right)$$

where $P_t$ is the price at $t$ and $r_t$ the log return over one period. Sample, not
population — in Excel, `STDEV.S`.

### 9.2 Why returns and not prices

Take a stock priced near \$1 and one priced near \$1,000. Measured on prices the
\$1,000 stock will *always* have the larger standard deviation, but it is not more
**wobbly** — and wobbliness is what volatility is meant to capture. Split it into a
thousand shares and nothing about the stock changed.

Returns put every asset on the same scale: **comparing apples to apples**. You can then
state a stock's volatility without knowing what it costs.

### 9.3 Why *log* returns

Simple returns do not add up. Take a stock going \$100 → \$101 → \$102:

| | Day 1 → 2 | Day 2 → 3 | Sum | Actual total |
| --- | --- | --- | --- | --- |
| **Simple** | 1% | 0.99009% | 1.99009% | 2% ✗ |
| **Log** | $\ln(101/100)$ | $\ln(102/101)$ | $\ln(102/100)$ | $\ln(102/100)$ ✓ |

Log returns are **additive** — the two-day return is the sum of the daily returns, with
no change-of-base arithmetic. That additivity is the whole reason, and § 9.5 depends on
it.

### 9.4 Why log-normal, and where the model breaks

A naive model says the **price** is normally distributed — which permits a negative price.
The fix is to model the price as **log-normal**, which cannot go negative, and that is
exactly equivalent to saying the **return** is normal.

**Then that model is wrong too.** Under a normal distribution the empirical rule
(68 / 95 / 99.7) puts under half a percent beyond three standard deviations. In markets,
three-sigma moves happen far more often than that — every time a politician says
something. The normal distribution **heavily underestimates the tails**, so a
heavier-tailed model is needed: Student's t, or a generalised Pareto (GPD).

### 9.5 Annualizing

Volatility is quoted annualized unless stated otherwise, and the sample frequency has to
be scaled up. Treat each day as a random variable $X_i$ and **assume IID**:

$$\text{Var}\left( \sum X_i \right) = n \text{Var}(X_i) \quad \Longrightarrow \quad \sigma_{\text{annual}} = n^{1/2} \sigma_{\text{daily}}$$

where $n$ is the number of periods per year. The step from the sum to $n$ times the
variance is exactly the independence assumption — and it is only legitimate because log
returns are additive (§ 9.3).

- $n \approx 252$ trading days.
- **Mental shortcut:** use $256$ instead, since $256^{1/2} = 16$. So annual vol is
  roughly **16 times** daily vol.

**The IID assumption is questionable** — which is precisely why the number is called
*annualized* rather than *yearly*. It is a convention for putting things on one scale, not
a claim about the year.

---

## 10. Short selling

**Definition.** Speculating on a stock without owning it — the way to profit from a fall
rather than merely avoid a loss.

### 10.1 The mechanics, step by step

Label the short seller **A**, the lender **B**, the buyer **C**.

| # | Step | Detail |
| --- | --- | --- |
| 1 | A **borrows** the stock from B | Routed by the prime broker (Robinhood, IBKR), which *locates* the shares. B is typically enrolled in a share-lending / yield programme, often without thinking about it |
| 2 | A **pays interest** to B | No free lunch. A few percent, or 20–30% for a name in heavy demand — **hard to borrow** |
| 3 | A **sells** the stock on the market to C | This is the short sale |
| 4 | The proceeds go into a **margin account** | A cannot spend them — the position is owed to someone else. They earn a small interest, smaller than what A pays in step 2 |
| 5 | The stock falls; A **buys it back** | Sold at \$10, bought back at \$9 |
| 6 | A **returns** the stock to B | Profit \$1, less the borrow cost |

If the stock **rises** instead, A must buy back at \$11 or \$12 — and the loss has no
upper bound, because a price can rise forever.

### 10.2 Who owns the stock mid-short?

Between steps 3 and 5, **C owns it** — defining the owner as whoever receives the
dividend. C bought it on the open market and is the holder of record.

But B's brokerage statement still shows one share, and B has no idea it was lent out. So
the position looks like **dual ownership** of a single share.

### 10.3 The dividend, and why it is a wash

Only one share exists, so the company pays only one dividend — to C. B, who wants the
dividend and did nothing wrong, does not get it.

**The resolution: A pays B the dividend out of pocket.** And this costs A nothing, because
the price drops by the dividend when it is paid:

| | Without dividend | With a \$1 dividend |
| --- | --- | --- |
| A sells at | \$10 | \$10 (dividend already in the price) |
| A buys back at | \$10 | **\$9** — the stock dropped by the dividend |
| A gains on the trade | \$0 | **+\$1** |
| A pays B | — | **−\$1** |
| **Net** | \$0 | **\$0** |

The mechanism exists so that neither party is harmed or enriched by a dividend falling
inside a loan: the short seller would otherwise get a free \$1 from the price drop, and
the lender would otherwise lose the \$1 for having lent.

### 10.4 Short squeeze

The feedback loop, and why it runs away:

```text
stock rises
   → margin no longer looks safe to the broker
   → margin call: post more cash, or be liquidated
   → short seller forced to BUY the stock back to cover
   → buying pushes the price UP
   → back to the top, for the next short seller
```

Each short who covers pushes the price into the next short's margin call. **GME in 2021**
is the case: retail buying started the rise, then forced covering did the rest.

**Why it can exceed 100% of the float.** Person C, now the legal owner, can lend the same
share again — to person D, who shorts it again. One real share, shorted twice.

> If 1,000 shares of GME exist but 2,000 shares are short, then covering requires buying
> **2,000** shares that do not exist in circulation. Shares are created out of the void.

That gap between shares owed and shares available is the upward pressure.

### 10.5 Why short selling matters

- It lets people profit from a fall, rather than merely step aside.
- It **aids price discovery** — if only holders can express a view, the price is less
  efficient. Negative information reaches the price through shorts.
- It adds **liquidity** and enables **hedging**.

---

## 11. Probability and statistics review

Covered rapidly as a level-set. Only the points the instructor flagged as commonly
misunderstood are recorded here; the rest is standard.

| Topic | The trap flagged |
| --- | --- |
| **Counting principle** | Counting outcomes only works when the outcomes are **equally likely**. Textbook problems always are; interview problems often look like they are and are not — see § 12.1 |
| **Independence of events** | $P(A \cap B) = P(A) P(B)$ is the definition |
| **Independence of random variables** | $E[XY] = E[X] E[Y]$ is **necessary, not sufficient**. True independence needs $E[g(X) h(Y)] = E[g(X)] E[h(Y)]$ for *all* bounded continuous $g, h$ |
| **Continuous random variables** | A continuous variable has probability **zero** of taking any particular value. A variable need be neither discrete nor continuous |
| **CDF vs PDF** | The CDF always exists, for any random variable. The PDF only exists where the CDF is differentiable |
| **Linearity of expectation** | Holds with **no** assumption about dependence or structure — the reason it is so powerful, and underrated |
| **Iterated expectation** | $E[X] = E[E[X \mid Y]]$. Often the conditional is far easier — but the $Y$ is usually **not given in the problem**; inventing the right one is the difficulty |
| **Conditional probability** | Tested heavily in interviews because trading *is* conditional: as information arrives, the distribution changes |
| **Order statistics** | The CDF is in every textbook, hard to memorise, easy to re-derive on the spot — don't bother memorising |

---

## 12. The interview problems

### 12.1 Grid paths, and the counting trap

A 4 by 4 grid. Walk from corner A to corner B, one step per second, **right or up only**.

**Part A — how many paths?** Every path is exactly 8 steps: 4 right and 4 up. Choosing
which 4 of the 8 are "up" fixes the path.

$$\text{paths} = \left( \frac{8!}{4! 4!} \right) = 70$$

**Part B — two walkers.** A second walker starts at B and moves **left or down only**.
Each walker picks between its available moves with probability one half, and has no choice
when only one move is legal. What is the probability they meet?

- They move in lockstep, so they can only meet after **4 steps each** — on the
  anti-diagonal. Any other square is the wrong number of moves away.
- When they meet, their two half-paths **join into one complete A-to-B path**. So the
  number of meeting configurations is exactly Part A's answer, 70.
- Within its first 4 moves neither walker can be forced: forcing only begins once a
  walker reaches an edge, which takes 4 moves, so the constraint bites on move 5 and
  never arrives. Every one of the 8 moves is a genuine coin flip.

$$P(\text{meet}) = \frac{70}{2^8} = \frac{70}{256} = \frac{35}{128}$$

**The trap.** Having computed 70 in Part A, it is tempting to treat those 70 complete
paths as equally likely under the random walk. **They are not.** A path that reaches an
edge early spends its remaining moves on forced steps, which cost no probability — so a
boundary-hugging path is *more* likely than an interior one. The counting argument
survives here only because the meeting happens at step 4, before any forcing can occur.

This is the concrete case of the § 11 warning: you may only count outcomes when the
outcomes are equally likely.

### 12.2 Rolling until a six

**Roll a die until a 6 appears. What is the probability the sum of all rolls, including
the 6, is even?**

Let $p$ be that probability, and condition on the first roll:

| First roll | Probability | Effect |
| --- | --- | --- |
| 6 | 1/6 | Stop. Sum is 6 — even. Success |
| 2 or 4 | 2/6 | Even; parity unchanged; continue needing even → contributes $p$ |
| 1, 3, or 5 | 3/6 | Odd; parity flips; continue needing **odd** → contributes $1 - p$ |

$$p = \frac{1}{6} + \frac{2}{6} p + \frac{3}{6} \left( 1 - p \right) \quad \Longrightarrow \quad \frac{7}{6} p = \frac{2}{3} \quad \Longrightarrow \quad p = \frac{4}{7}$$

### 12.3 Minimum spacing of 101 uniform points

**Sample 101 points independently from Uniform(0, 1). (a) What is the probability the
minimum distance between any two points does not exceed 1/1000? (b) What is the expected
shortest distance?**

*Posed in class and left unanswered — the derivation below is added here, not from the
lecture.*

Let $M$ be the smallest gap between adjacent order statistics. For $n$ uniform points the
standard spacings result gives, for $0 \leq d \leq 1 / (n-1)$:

$$P(M > d) = \left( 1 - (n-1) d \right)^n$$

**(a)** With $n = 101$ and $d = 1/1000$:

$$P(M > 0.001) = \left( 1 - 0.1 \right)^{101} = 0.9^{101} \approx 0.0000239$$

$$P(M \leq 0.001) \approx 0.99998$$

Nearly certain — with 101 points the average gap is only about 1/100, so gaps an order of
magnitude tighter are commonplace.

**(b)** Integrating the survival function over $0 \leq d \leq 1/100$:

$$E[M] = \frac{1}{(100)(102)} = \frac{1}{10200} \approx 0.000098$$

---

## Key terms (EN ↔ ZH)

| English | 中文 | Meaning here |
| --- | --- | --- |
| asset class | 资产类别 | A group of instruments sharing market behaviour and risk characteristics |
| delivery | 交割 | Physical settlement obligation — what separates a commodity from a stock |
| liquidity | 流动性 | Executable **quickly** *and* at a **good price**, at a stated size |
| price discovery | 价格发现 | Learning the right price through trading, driven by informed participants |
| bid / ask / mid | 买价 / 卖价 / 中间价 | Best buy quote, best sell quote, their average |
| buy side / sell side | 买方 / 卖方 | People with capital vs people providing services |
| broker / dealer | 经纪商 / 自营商 | Agent capacity (client's risk) vs principal capacity (own book) |
| adverse selection | 逆向选择 | Being picked off by a better-informed counterparty |
| inventory risk | 存货风险 | A market maker's unwanted position moving against it |
| primary / secondary market | 一级 / 二级市场 | First issuance vs subsequent ownership changes |
| microstructure | 微观结构 | Exchange mechanics — matching, routing, settlement |
| log return | 对数收益率 | $\ln (P_t / P_{t-1})$ — additive across periods |
| annualized volatility | 年化波动率 | Daily vol scaled by $n^{1/2}$; roughly 16 times daily |
| fat tails | 肥尾 | Extreme moves far more frequent than a normal distribution implies |
| short selling | 卖空 / 做空 | Borrow, sell, buy back, return |
| hard to borrow | 难以借入 | High borrow interest — heavy short demand |
| margin call | 追加保证金通知 | Post more collateral or be liquidated |
| short squeeze | 轧空 | Forced covering drives the price up, forcing more covering |
| dividend | 股息 | Profit paid to shareholders; the short seller reimburses the lender |
