# 01 · What Is a CTA Strategy

> **Answers:** what a CTA is, why it might make money, how long/short works, and who else is trading.
> **Prerequisites:** none — first chapter.
> **After reading:** explain what a CTA does, and why a short sale is not selling out of thin air.

---

## What Is a CTA Strategy?

**Definition (CTA strategy).** A *CTA (Commodity Trading Advisor) strategy* is a rule-based
strategy that trades **futures** systematically across asset classes — equities, fixed income,
commodities, currencies — with the objective of **absolute return**, independent of market
direction.

**Note.** The name is a historical artifact. Modern CTAs are not limited to commodities; typical
markets are equity-index futures (S&P 500, Nasdaq), Treasury futures, currency futures, energy,
precious metals, and agriculture.

### Instruments: Index, ETF, Future

The phrase "S&P 500" names three different objects. Only two of them can be traded.

**Definition (Index).** An *index* is a published real-valued process

```text
I_t  =  ( Σ_i  P_it · N_it )  /  D_t
```

where `P_it` is the price of constituent `i` at time `t`, `N_it` its float-adjusted share count,
and `D_t > 0` the *divisor*. An index is a number, not a claim on anything, and therefore cannot
be bought.

**Definition (ETF).** An *exchange-traded fund* is a fund that holds the constituents of some
index and whose own shares trade on an exchange. Examples: SPY, IVV, VOO track the S&P 500; QQQ
tracks the Nasdaq-100.

**Definition (Futures contract).** A *futures contract* is an agreement to settle a specified
quantity of an underlying at a specified price on a specified future date. No constituent shares
are held. Examples: ES (S&P 500), NQ (Nasdaq-100).

**Note (Weighting).** `I_t` above is **float-adjusted market-capitalisation weighted**, not a
simple average of constituent prices — the largest few names dominate the level. Contrast the Dow
Jones Industrial Average, which is *price*-weighted, and an equal-weight fund such as RSP, which
is the actual arithmetic average. The "500" is the constituent count, not a denominator.

**Note (Level versus return).** `D_t` carries no economic meaning; it exists only to keep `I_t`
continuous when constituents change. The base period of the S&P 500 is 1941–43 = 10, so the level
is a cumulative growth factor from an arbitrary starting scale. Only *changes* in `I_t` are
interpretable — the level itself admits no "high" or "low" reading, and `I_t` has no tendency to
revert to its base.

**Claim.** A CTA trades futures rather than ETFs.

Three reasons, in descending order of importance.

1. **Symmetry.** Shorting a future carries no instrument-specific cost. Shorting an ETF requires
   borrowed shares, a borrow fee, and availability. A strategy that must take short positions as
   freely as long ones cannot tolerate that asymmetry.
2. **Coverage.** Commodities and currencies have deep futures markets and poor ETFs. One
   instrument type spans all four asset classes under one framework.
3. **Capital efficiency.** Margin is roughly 5–10% of notional, so unused cash sits in Treasury
   bills. That interest is a genuine return component, termed **collateral yield**.

**Note (The cost).** Futures expire. There is no natural continuous ES price series, so contracts
must be stitched together — see [02](02-data-and-corporate-actions.md).

## 1. Why CTA/Momentum Strategies Work

Two candidate explanations. Neither is conclusive; momentum has nonetheless been durably
profitable historically.

**Information diffusion.** Unglamorous news with real long-term macro effects spreads gradually,
creating sustained pressure. This explanation may have weakened since 2008 — faster computing and
data distribution let markets price news much more quickly.

**Selective momentum capture.** Assets that performed well over recent months tend to keep doing
so, and weak performers tend to keep declining. Three mechanisms are usually offered:

- Large positions take time to build and unwind, so institutional flow persists.
- Investors chase winners and abandon losers, which is self-reinforcing while it lasts.
- Major economic events do not resolve within a single day; their price impact is spread out.

## 2. Long/Short Mechanics

**Definition (Long).** Buy first, sell later. Profit is the sell price minus the buy price.

**Definition (Short).** Borrow and sell first, buy back and return later. Profit is the sell price
minus the buy-back price.

**Note.** Combining both deploys capital fully — 150/50 or 200/100 structures rather than leaving
cash idle.

**Note.** Empirically, longs contribute more P&L than same-size shorts, possibly a carry or
risk-free-rate effect.

Turning a long/short stance into per-asset weights is [04](04-from-signal-to-position.md).

## 3. How Short Selling Works

*How can you sell shares you don't own?* A short sale is not selling out of thin air — **you
borrow the shares first**, exactly like borrowing money, except the thing borrowed is stock.

### The four steps

```text
1. Borrow    — borrow N shares from a lender (broker / long-term holder)
2. Sell      — sell those borrowed shares now, receive cash
3. Buy back  — later buy N shares back from the market
4. Return    — return the N shares to the lender (close the position)
```

**Note (Fungibility).** You never create shares; you use someone else's temporarily and return an
**equal quantity of the same stock**. Shares are fungible, so returning "N shares of SPY" — not
specific certificates — settles the debt.

**Example.** Today: borrow one case of cola worth \$100 and sell it immediately, receiving \$100.
Later: the price falls, so buy one case back for \$80 and return it to the lender. You keep \$20.
Profit is sell price minus buy-back price, so a short is a bet the price **falls**.

### Why lenders lend

Long-term holders (Vanguard, BlackRock, pension funds) earn a **lending fee** on stock they were
going to sit on anyway. The broker matches borrowers with lenders and holds margin. This mature
market is called **securities lending**.

### Why shorting is riskier

**Claim.** A long position has bounded loss; a short position does not.

A long can lose at most 100% of the amount invested, since the price is floored at zero. A short
owes the market price of the borrowed shares, and that price can rise without limit, so the
liability is **theoretically unbounded**. Brokers therefore require **margin** and may force a
**buy-in** to protect the lender.

**Note.** This is also why a 150/50 book — 200% gross — is **2× leverage**, not free money.

### In this backtest

The code models no borrowing, fees, or margin. It allows a **negative share count**
(`curr_shrs < 0`) valued at `asset_value = curr_shrs × close`, so a short is a **negative position
value**, i.e. a liability, that gains when price falls.

**Note (Sign convention).** A negative number encodes *direction* — a debt owed — not a loss. The
model assumes shares are always borrowable at zero cost: fine for teaching, not for real trading.

Accounting detail: [05](05-understanding-backtesting.md).

## 4. Market Participants by Holding Period

Longest to shortest:

1. **Index and passive funds** — Vanguard, BlackRock; years to decades. Pension funds favour bonds for predictable cash flows.
2. **Active managers** — Fidelity, PIMCO; monthly to quarterly, more discretionary/fundamental.
3. **Hedge funds** — high minimums, lockups, management + performance fees; intraday to several days.
4. **Market makers** — Optiver, Citadel Securities, IMC, Susquehanna; liquidity provision, extremely short holds, minimal overnight exposure.
5. **Noise traders** — retail or uninformed flow, no consistent horizon or informational content.

---

## Common pitfalls

- **"CTA means commodities only."** A historical artifact of the name; main exposures are equity-index, rate, and FX futures.
- **"You can buy the S&P 500."** You buy an ETF or a future *tracking* it. The index is a number.
- **"The index level tells you whether the market is expensive."** The base scale is arbitrary (1941–43 = 10). Only returns are interpretable.
- **"A negative position means I lost money."** The sign encodes *direction* — a debt — not P&L.
- **"150/50 is free extra return."** 200% gross is 2× leverage; risk scales with it.
- **"Momentum works because information diffuses slowly."** One candidate explanation, possibly weakened after 2008. Nothing is settled.

## Open questions

- Longs out-contribute same-size shorts — carry / risk-free-rate effect, or just equities' long-run positive drift?
- If information diffusion weakened after 2008, what keeps momentum alive since?

---

## Next → [02 · Data &amp; Corporate Actions](02-data-and-corporate-actions.md)

Before moving on, **open `CTA_data/_manifest.csv`** and look at the 37 tickers you will be working
with — note which are equity, rate, commodity, and FX exposures. Chapter 02 is about trusting that
data before building anything on it.

You should be able to explain:

- [ ] What a CTA actually trades, and why the name is misleading
- [ ] The difference between an index, an ETF, and a future — and why CTAs use futures
- [ ] Why a negative share count is a direction, not a loss
- [ ] Why a 150/50 book is 2× leverage rather than free return

[← Index](00-index.md)
