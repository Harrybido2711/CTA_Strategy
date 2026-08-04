# 01 · CTA 是什么 / What Is a CTA Strategy

> **Answers:** what a CTA is, why it might make money, how long/short works, and who else is trading.
> **Prerequisites:** none — first chapter.
> **After reading:** explain what a CTA does, and why a short sale is not selling out of thin air.

---

## What Is a CTA Strategy?

A **CTA (Commodity Trading Advisor) strategy** systematically trades **futures** across asset
classes — equities, fixed income, commodities, currencies.

Despite the name, modern CTAs are **not limited to commodities**. Typical markets: equity-index
futures (S&P 500, Nasdaq), Treasury futures, currency futures, energy (oil, natural gas), precious
metals, agriculture.

The objective is **absolute return**, regardless of market direction.

## 1. Why CTA/Momentum Strategies Work

- **Information diffusion.** Unglamorous news with real long-term macro effects spreads gradually,
  creating sustained pressure. This explanation may have weakened since 2008 — faster computing and
  data distribution let markets price news much more quickly.
- **Selective momentum capture.** Assets that performed well over recent months tend to keep doing
  so, and weak performers tend to keep declining.
  - 大资金完成买卖需要时间。
  - 投资者存在"追涨杀跌"的心理。
  - 重大经济事件的影响通常不会在一天内结束。

Neither explanation is conclusive, but momentum has been durably profitable historically.

## 2. Long/Short Mechanics

- **Long:** buy low, sell higher.
- **Short:** borrow and sell, buy back lower.
- Combining both deploys capital fully — 150/50 or 200/100 structures rather than leaving cash idle.
- Empirically, longs contribute more P&L than same-size shorts, possibly a carry or risk-free-rate
  effect.

Turning a long/short stance into per-asset weights is [04](04-from-signal-to-position.md).

## 3. How Short Selling Works / 做空的原理

*How can you sell shares you don't own?* A short sale is not selling out of thin air — **you borrow
the shares first**, exactly like borrowing money, except the thing borrowed is stock.
你不是凭空卖，而是"先借来再卖"。

### The four steps / 四个步骤

```text
1. Borrow  借入   — borrow N shares from a lender (broker / long-term holder)
2. Sell    卖出   — sell those borrowed shares now, receive cash
3. Buy back 买回  — later buy N shares back from the market
4. Return  归还   — return the N shares to the lender (close the position)
```

You never create shares; you use someone else's temporarily and return an **equal quantity of the
same stock**. Shares are fungible — returning "N shares of SPY", not specific certificates, settles
the debt. 股票同质可替代，还等量同种即可。

### A cola analogy / 一个类比

```text
Today : borrow 1 case (worth $100), sell it immediately  → receive $100
Later : cola drops, buy 1 case back for $80
        return the case to the lender                     → you keep $20
```

Profit = **sell price − buy-back price**. A short is a bet the price **falls**.
做空就是"赌它跌"：跌了→还债更便宜→赚；涨了→还债更贵→亏。

### Why lenders lend / 出借方图什么

Long-term holders (Vanguard, BlackRock, pension funds) earn a **lending fee** on stock they were
going to sit on anyway. The broker matches borrowers with lenders and holds margin. This mature
market is **securities lending 证券借贷**.

### Why shorting is riskier / 为什么做空更危险

- **Long:** most you can lose is 100%. Bounded.
- **Short:** price can rise without limit, so what you owe can become arbitrarily expensive —
  **loss is theoretically unbounded**. Brokers require **margin** and may force a **buy-in** to
  protect the lender. This is also why a 150/50 = 200% gross book is **2× leverage**, not free money.

### In this backtest / 在本回测中

The code models no borrowing, fees, or margin. It allows a **negative share count**
(`curr_shrs < 0`) valued at `asset_value = curr_shrs × close`, so a short is a **negative position
value (a liability)** that gains when price falls. This assumes shares are always borrowable at zero
cost — fine for teaching, not for real trading.
负号代表"这是做空方向、是要还的债"，不是"亏损"。

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
- **"A negative position means I lost money."** The sign encodes *direction* — a debt — not P&L.
- **"150/50 is free extra return."** 200% gross is 2× leverage; risk scales with it.
- **"Momentum works because information diffuses slowly."** One candidate explanation, possibly weakened after 2008. Nothing is settled.

## Open questions

- Longs out-contribute same-size shorts — carry / risk-free-rate effect, or just equities' long-run positive drift?
- If information diffusion weakened after 2008, what keeps momentum alive since?

---

## Next → [02 · Data & Corporate Actions](02-data-and-corporate-actions.md)

Before moving on, **open `CTA_data/_manifest.csv`** and look at the 37 tickers you will be working
with — note which are equity, rate, commodity, and FX exposures. Chapter 02 is about trusting that
data before building anything on it.

You should be able to explain:

- [ ] What a CTA actually trades, and why the name is misleading
- [ ] Why a negative share count is a direction, not a loss
- [ ] Why a 150/50 book is 2× leverage rather than free return

[← Index](00-index.md)
