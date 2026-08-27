# Market 101 — Structure, Volatility, and Short Selling

> - **Source:** lecture transcript `GMT20260816-005926_Recording.cc.vtt`, 2026-08-16.
> - **What it is:** the foundations of how a market works — asset classes, why people
>   trade, price discovery, buy side vs sell side, liquidity, market-maker economics —
>   then the precise definition of volatility and short-selling mechanics. The same
>   session's probability review lives in its own note.
> - **Provenance:** content is from the lecture unless a passage says otherwise. A block
>   opening with *Added* was worked out afterwards and was **not** said in class.
> - **Filed under:** market knowledge — general finance that holds regardless of any
>   particular strategy.
> - **See also:** [Probability and Statistics for Quant Interviews](probability-and-statistics.md)
>   for the rest of the session · [Leverage, Deleveraging, and the Time-Horizon Lesson](leverage-deleveraging-and-horizons.md).

---

## 1. Asset classes

The names are everywhere — **equities, fixed income, FX, commodities, real estate,
derivatives**. Naming them is not separating them. What makes two instruments different
*classes* rather than two tickers?

### 1.1 What separates them

*Added, apart from the gold-versus-equities contrast below. The lecture said the classes
behave differently and gave that one example; the three-layer frame, the state grid and
the boundary cases are worked out here.*

Textbooks hand you the list and skip the logic. The logic is this:

> Classes differ in the **nature of the claim**, which puts their returns at the mercy of
> **different macro risks**, which makes them behave **systematically differently across
> economic states**.

Three layers, each one causing the next.

**Layer 1 — Claim structure.** *What right do you hold?* Equity is a **residual** claim —
what is left after everyone else is paid, so unbounded upside and a floor at zero. A bond
is **contractual** — cash flows fixed in advance, so upside locked and the risk is
default. A commodity has **no cash-flow claim at all**: you own the thing, and return can
only come from price.

**Layer 2 — Return driver.** Those structures put returns at the mercy of different
economic variables — growth and earnings for equities, rates and credit for bonds,
supply-demand and inflation for commodities. **This is why correlations are low:** not the
labels, the macro variables behind them.

**Layer 3 — Risk factor exposure.** The deepest view: **the class is packaging; the
primitive is the risk factor** — surprises in growth, surprises in inflation, rates,
credit, liquidity. Each class is one *mix* of them, which is why they sort by economic
state:

| | Inflation rising | Inflation falling |
| --- | --- | --- |
| **Growth rising** | Commodities, inflation-linked bonds | **Equities** |
| **Growth falling** | Gold, inflation-linked bonds | **Nominal bonds** |

**Every long-run return is a risk premium** — you are not buying an asset, you are selling
insurance against one of these states and collecting the premium. So what you diversify is
**not names but risk exposures**: two labels with the same factor mix diversify nothing.

**The test.** Name a shock that moves A up and B down — if you can, different classes; if
you cannot, one class with two tickers. Gold rises on inflation and on war; equities fall
on both. The same test settles the real arguments:

| Case | Verdict |
| --- | --- |
| **High-yield credit** | Behaves like equity — credit risk *is* equity risk in another wrapper |
| **Gold** | Commodity by settlement, currency by behaviour — classify by whichever dominates its P&L |
| **Crypto** | A new class only if its return driver is independent of the existing ones — an open empirical question, not a marketing one |

**Note.** Settlement (deliver the oil, versus book entry at the Depository Trust) and
venue (§ 5) matter operationally, but neither is a risk factor and neither defines a class.

### 1.2 The roster

*Added. The lecture named only commodities, stocks, derivatives and real estate, and did
not separate the wrapper from the class.*

One row per class, read across the three layers. **The factor column is a signed
exposure, not a verdict** — *long X* gains when X surprises upward, *short X* loses. Every
"short" in it is a source of premium, not a defect: you are paid for holding the thing
that hurts in the state people most fear.

| Class | Claim (L1) | Return driver (L2) | Factor mix (L3) | Carry |
| --- | --- | --- | --- | --- |
| **Equities** 股票 | Residual — profit after debt | Growth, earnings, risk appetite | Long growth, short inflation | Dividend yield |
| **Fixed income** 固定收益 (FI) | Contractual — coupons and principal | Policy rates, inflation | Short growth, short inflation | Coupon, plus roll-down |
| **Credit** 信用 | Contractual, minus default risk | Default probability, risk appetite | Long growth (equity-like) | Credit spread |
| **FX** 外汇 | None — a *ratio* of two currencies | Rate differentials, central-bank policy | No standalone factor — a *relative* bet; carry is short crash risk | The rate **differential** |
| **Commodities** 大宗商品 | None — the physical good | Supply shocks, inflation | Long inflation | **Convenience yield** minus storage |
| **Real estate** 房地产 | Rent stream, plus land scarcity | Rates, local supply and demand | Rent bond-like, appreciation equity-like | Net rental yield |
| **Cash** 现金 | Pure time value — the unit of account | The policy rate | Short inflation, flat to growth — the numeraire | The risk-free rate |

**Derivatives are a column of this table, not a row.** An option, a future, a swap is a
payoff *derived* from something else, so it cuts across every row — class and contract
form are orthogonal axes, and the question about a derivative is always *on what?* The one
exception: options carry a factor the underlying lacks, **volatility**, since a
delta-hedged option has zero price exposure and still earns or loses on realized versus
implied vol. By Layer 3 that makes *volatility* a class, not *derivatives*. A wrapper is also in
**zero net supply**, which is the arithmetic behind § 7.

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

**Is trading zero-sum?** Three answers, and they do not conflict.

**Trading, yes** — strictly negative-sum once exchange fees are counted. Every dollar you
make exchanging an asset that already exists is a dollar the counterparty did not make.

**Holding, it depends on net supply** — does the thing exist when nobody trades it?
*(Added: the lecture asserted the zero-sum answer without this argument.)*

| | Positive net supply | Zero net supply |
| --- | --- | --- |
| **Which** | Equities, FI, credit, commodities, real estate | FX positions, and **every derivative** |
| **Why** | Shares, bonds and barrels exist regardless; someone must hold all of them | Every long has an offsetting short — long EURUSD *is* short USD |
| **So** | The aggregate holder bears risk and is paid for it: a **risk premium** available to everyone at once | Aggregate P&L is **exactly zero** before costs; any premium is a *transfer*, not a payment from the asset |

A positive-net-supply class is paid from **outside** the market — corporate profits,
coupons, rent — so all its holders can be paid at once. A zero-net-supply one has no
outside payer, so it is zero-sum by construction. This is also why a fund can be short
crude without anyone burning less oil: the contract is a zero-net-supply **wrapper** on a
positive-net-supply good.

**In utility, no:**

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

*Added. The lecture stated that log returns are additive; the base mismatch, the
multiplication recombination, the telescoping identity and the understatement note are
worked out here.*

Simple returns do not add up — each day's return is measured against a **different
base**. Take a stock going \$100 → \$101 → \$102:

| | Day 1 → 2 | Day 2 → 3 | Sum | Actual total |
| --- | --- | --- | --- | --- |
| **Simple** | 1% | 0.99009% | 1.99009% | 2% ✗ |
| **Log** | $\ln(101/100)$ | $\ln(102/101)$ | $\ln(102/100)$ | $\ln(102/100)$ ✓ |

Day 1's 1% is 1% of \$100; day 2's 0.99009% is 0.99009% of \$101. Different bases, so
the sum means nothing. The only correct way to recombine simple returns is to multiply:
$(1 + 0.01)(1 + 0.0099009) - 1 = 0.02$ — the 2% the stock actually earned.

Log returns turn that multiplication into addition. Since $\ln(ab) = \ln a + \ln b$, the
two-day log return telescopes:

$$\ln\frac{P_2}{P_0} = \ln\frac{P_2}{P_1} + \ln\frac{P_1}{P_0}$$

so the multi-period return **is** the sum of the daily returns — no base to track, no
compounding term to carry. Numerically $\ln(101/100) \approx 0.00995$ and
$\ln(102/101) \approx 0.00985$, summing to $\approx 0.01980 = \ln(102/100)$.

**Note (Additivity costs a second-order understatement).** The true two-day return is 2%,
the log return 1.9803%. The gap is second-order: for small $r$, $\ln(1+r) \approx r$.
The cost is negligible for daily returns, and the payoff is that § 9.5's annualization
becomes one multiplication.

### 9.4 Why log-normal, and where the model breaks

*Added. The lecture gave the log-normal fix and the fat-tail objection; the
equivalence chain, the empirical-rule numbers and the model comparison are worked
out here.*

A naive model says the **price** is normally distributed. A normal distribution ranges
over $(-\infty, \infty)$, so it assigns positive probability to a **negative price** —
impossible. The fix is to model the **log price** as normal instead. Since
$P = e^{\ln P}$ and the exponential is always positive, the price stays positive by
construction. A random variable whose log is normal is called **log-normal**.

This move is exactly equivalent to saying the **return** is normal: the log return
$r_t = \ln P_t - \ln P_{t-1}$ is the difference of two normal log prices, hence normal
itself — and conversely, normal returns make log price a normal random walk. One
assumption, seen from two sides.

**Then that model is wrong too.** Under a normal return the empirical rule promises:

| Range | Probability |
| --- | --- |
| within 1σ | 68% |
| within 2σ | 95% |
| within 3σ | 99.7% |

so a move **beyond three standard deviations** arrives under half a percent of the time
(0.3% in total, split across both tails). In markets, three-sigma moves happen far more
often than that — every time a politician says something. Real returns are
**fat-tailed**: there is more mass in the extremes than a normal predicts, and the
normal **heavily underestimates** how often the extremes arrive. A heavier-tailed model
is needed:

| Model | What it adds | What it is for |
| --- | --- | --- |
| **Student's t** | one extra parameter, the degrees of freedom ν | the whole return distribution — small ν means fat tails |
| **Generalised Pareto (GPD)** | a shape parameter fitted to excesses over a threshold | only the tail, per extreme-value theory |

**Note (The two remedies answer different questions).** Student's t replaces the normal
for the **entire** distribution and is the practical workhorse. GPD deliberately throws
away the middle and models only **how far a return exceeds a threshold** — the right
tool when the size of the tail is all that matters, as in margin or drawdown design.

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
