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

The names are everywhere — **equities, fixed income, FX, commodities, real estate,
derivatives**. Naming them is not separating them. What makes two instruments belong to
different *classes* rather than being two tickers?

### 1.1 What separates them: three layers

Textbooks hand you the list and skip the logic. The separation works on three levels,
each one **causing** the next.

**Layer 1 — Claim structure.** *What right do you actually hold?* Equity is a **residual**
claim — what is left after everyone else is paid, so unbounded upside and a floor at zero.
A bond is a **contractual** claim — cash flows agreed in advance, so upside locked and the
risk is default. A commodity carries **no cash-flow claim at all**: you own the thing, and
return can only come from price. Cash is pure time value.

**Layer 2 — Return driver.** Those structures put returns at the mercy of different
economic variables — growth and earnings for equities, rates and credit for bonds,
supply-demand and inflation for commodities. **This is why correlations are low:** not
because the labels differ, but because the macro variables behind them do.

**Layer 3 — Risk factor exposure.** The deepest view: **the class is packaging; the
primitive is the risk factor** — surprises in growth, surprises in inflation, rates,
credit, liquidity. Each class is one *mix* of them, which is why they sort by economic
state:

| | Inflation rising | Inflation falling |
| --- | --- | --- |
| **Growth rising** | Commodities, inflation-linked bonds | **Equities** |
| **Growth falling** | Gold, inflation-linked bonds | **Nominal bonds** |

**Every long-run return is a risk premium.** You are not buying an asset — you are selling
insurance against one of these states and collecting the premium.

**In one sentence.**

> Classes differ in the **nature of the claim**, which puts their returns at the mercy of
> **different macro risks**, which makes them behave **systematically differently across
> economic states**.

So **what you diversify is not names, it is risk exposures** — two labels with the same
factor mix diversify nothing.

**The test.** Name a shock that moves A up and B down: if you can, different classes; if
you cannot, one class with two tickers. Gold rises on inflation and on war, equities fall
on both. The same test settles the real arguments:

| Case | Verdict |
| --- | --- |
| **High-yield credit** | Behaves like equity — credit risk *is* equity risk in another wrapper |
| **Gold** | Commodity by settlement, currency by behaviour — classify by whichever dominates its P&L |
| **Crypto** | A new class only if its return driver is independent of the existing ones — an open empirical question, not a marketing one |

**Note.** Two mechanical differences are *not* about risk: **settlement** (deliver the oil,
versus book entry at the Depository Trust) and **venue** (where it trades bounds how fast
the factor reprices — § 5). Both matter operationally; neither defines the class.

### 1.2 The roster

One row per class, read across the three layers:

| Class | Claim (L1) | Return driver (L2) | Factor mix (L3) | Carry |
| --- | --- | --- | --- | --- |
| **Equities** 股票 | Residual — profit after debt | Growth, earnings, risk appetite | Long growth, short inflation | Dividend yield |
| **Fixed income** 固定收益 (FI) | Contractual — coupons and principal | Policy rates, inflation | Short growth, short inflation | Coupon, plus roll-down |
| **Credit** 信用 | Contractual, minus default risk | Default probability, risk appetite | Long growth (equity-like) | Credit spread |
| **FX** 外汇 | None — a *ratio* of two currencies | Rate differentials, central-bank policy | Relative rates and policy | The rate **differential** |
| **Commodities** 大宗商品 | None — the physical good | Supply shocks, inflation | Long inflation | **Convenience yield** minus storage |
| **Real estate** 房地产 | Rent stream, plus land scarcity | Rates, local supply and demand | Rent bond-like, appreciation equity-like | Net rental yield |
| **Cash** 现金 | Pure time value — the unit of account | The policy rate | Short everything; the numeraire | The risk-free rate |

**Derivatives are a column of this table, not a row.** An option, a future, a swap is a
payoff *derived* from something else, so it cuts across every row. Class and contract form
are orthogonal axes, and the right question about a derivative is always *on what?*

**The one exception.** Options carry a factor the underlying lacks: **volatility**. A
delta-hedged option has zero price exposure and still earns or loses on realized versus
implied vol — but by Layer 3 that makes *volatility* a class, not *derivatives*.

### 1.3 Can the class pay anyone?

The risk factor says what *moves* a class. **Net supply** says whether it can pay its
holders anything in aggregate — does the thing exist when nobody trades it?

| | Positive net supply | Zero net supply |
| --- | --- | --- |
| **Which** | Equities, FI, credit, commodities, real estate | FX positions, and **every derivative** |
| **Why** | Shares, bonds and barrels exist regardless; someone must hold all of them | Every long has an offsetting short — long EURUSD *is* short USD |
| **So** | The aggregate holder bears risk and is paid for it: a **risk premium** available to everyone at once | Aggregate P&L is **exactly zero** before costs; any premium is a *transfer*, not a payment from the asset |

Which is why a fund can be short crude without anyone burning less oil: the contract is a
zero-net-supply **wrapper** on a positive-net-supply good, and the two need not agree in
size.

→ The same zero-sum arithmetic, and why it does not mean a trade has a loser: § 7.

---

## 2. Why trades happen

A trade is two parties on **opposite sides** — one buys, one sells — and their motives
need not match: a speculator buys from a switcher, a dividend buyer from someone needing
cash. That asymmetry is what keeps a market clearing.

### 2.1 The four motives

| Motive | Buy side of it | Sell side of it |
| --- | --- | --- |
| **Speculation** | Bet the price rises | Bet the price falls |
| **Cash need** | Have spare cash to invest — an IRA contribution | Need cash for something real — a car |
| **Ownership** | Own a piece of a company you believe in; collect **dividends** | Believe the business has turned bad |
| **Switching** | Rotate into a better idea | Fund that rotation — money is finite |

**Speculation is not the bulk of the flow.** Most buying is ownership — hold a company
and collect dividends (Buffett), or pension and mutual funds preserving capital. Selling
to switch is common too: buying Tesla may mean selling Apple, and that says nothing about
Apple.

### 2.2 When a trade needs no opinion at all

A trade can also happen with **no opinion** — rules force it. When a name leaves the S&P
500, every index-tracking fund (led by SPY) must dump the whole position and buy the
replacement on the same day: enormous flow unrelated to any balance sheet.

→ The same lesson from the other direction — forced flow from levered funds unwinding:
[Leverage, Deleveraging, and the Time-Horizon Lesson](leverage-deleveraging-and-horizons.md).

---

## 3. How a trade happens

§ 2 said why someone *wants* to trade. Wanting to is not enough. A and B still have to
**find each other**, then **agree a price** — and because agreeing a price one negotiation
at a time is unworkable at scale, in practice **someone has to be standing there
already**. Three beats, and the third exists because the second is slow.

### 3.1 Finding each other — the platform

A venue lists everyone in one place: Amazon or Craigslist for a pen, an exchange for a
stock. **This is the easy half** — matching *who*. Agreeing *at what price* is the hard
half.

### 3.2 Agreeing a price

No canonical answer — four candidates, each with a defect:

| Candidate | Definition | Weakness |
| --- | --- | --- |
| **Last traded price** | What the last identical item actually traded at | Depends entirely on *when* — one second ago is a good proxy, one year ago is not |
| **Mid price** | (highest bid + lowest ask) / 2 | Needs a live two-sided book to exist at all |
| **Fundamental price** | What the thing is worth — manufacturing cost for a pen, a DCF or multiples for a stock | A judgement, not an observation |
| **Bid or ask** | One side's standing quote | Not fair by construction — it is one side only |

So the price is **negotiated**, and can land anywhere in the gap: a \$7 bid against a
\$10 ask may settle at \$8 or \$9, and nothing forces the midpoint.

### 3.3 When there is no price to agree on

Replace the pen with a **mystery box** and the fundamental price vanishes. The only way to
learn the price is **to trade** — that is *price discovery*. The **informed** know the box
is worth \$10, the **naive** think \$5; the informed keep buying at \$5, buying pushes the
price up, and it converges to \$10, where they stop. **Price discovery is not a poll — it
is the informed being paid to correct the naive.**

### 3.4 Why it takes a market maker

Negotiating every single trade is far too slow. It is enormously better if **someone is
always standing there** with a price already on the board — take it or leave it, one step
instead of a haggle. That standing willingness to buy **and** sell is the service, and
§ 8 is what it is being paid for.

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

Pension funds sit further along the same axis — more risk-averse still, saving over
decades. Prop shops and HFT firms trade **their own capital**, usually as partnerships.

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
| fixed income | 固定收益 | A contractual stream of coupons and principal — FI |
| foreign exchange | 外汇 | FX — the relative price of two currencies, not a claim on anything |
| credit | 信用 | The default-risk component carved out of a bond |
| derivative | 衍生品 | A payoff derived from an underlying — a wrapper across classes, not a class |
| carry | 持有收益 | What the position earns if the price never moves |
| convenience yield | 便利收益 | The benefit of holding the physical good rather than a claim on it |
| net supply | 净供给 | Positive if the asset exists untraded; zero if every long has a matching short |
| residual claim | 剩余求偿权 | Equity — paid last, so unbounded upside and a floor at zero |
| contractual claim | 合同求偿权 | Fixed income — cash flows agreed in advance, capped upside, default risk |
| risk factor | 风险因子 | Growth surprise, inflation surprise, rates, credit, liquidity — the primitives a class is built from |
| risk premium | 风险溢价 | Compensation for bearing risk nobody can diversify away |
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
