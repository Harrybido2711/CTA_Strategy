# 01 · What Is a CTA Strategy

> **Answers:** what a CTA is, why it might make money, how long/short works, and who else is trading.
> **Prerequisites:** none — first chapter.
> **After reading:** explain what a CTA does, and why a short sale is not selling out of thin air.

---

**Definition (CTA strategy).** A *CTA (Commodity Trading Advisor) strategy* is a rule-based
strategy that trades **futures** systematically across asset classes — equities, fixed income,
commodities, currencies — targeting **absolute return**, independent of market direction.

**Note.** The name is a historical artifact. Modern CTAs are not commodity-only; typical markets
are equity-index futures (S&P 500, Nasdaq), Treasury futures, FX futures, energy, metals, and
agriculture.

## 1. Instruments: Index, ETF, Future

"S&P 500" names three different objects. Only two of them can be traded.

| Layer | Example | What it is | Tradeable |
| --- | --- | --- | --- |
| **Index** | SPX, NDX | A published number computed from its constituents | No |
| **ETF** | SPY, VOO, QQQ | A fund holding the constituents; its own shares trade | Yes |
| **Future** | ES, NQ | A contract to settle at a future date; holds nothing | Yes |

**Definition (Index).** A published real-valued process

```text
I_t  =  ( Σ_i  P_it · N_it )  /  D_t
```

where `P_it` is the price of constituent `i`, `N_it` its float-adjusted share count, and `D_t > 0`
the *divisor*.

- **Cap-weighted, not averaged.** The largest few names dominate `I_t`. Contrast the Dow
  (price-weighted) and RSP (equal-weighted — the actual arithmetic average). The "500" is a
  constituent count, not a denominator.
- **The level carries no information; only returns do.** `D_t` exists solely to keep `I_t`
  continuous when constituents change. The S&P 500 base period is 1941–43 = 10, so the level is a
  growth factor off an arbitrary scale, with no tendency to revert to it.

**Claim.** A CTA trades futures, not ETFs.

| Reason | Futures | ETFs |
| --- | --- | --- |
| **Symmetry** | Shorting costs nothing extra | Shorting needs borrowed shares, a fee, availability |
| **Coverage** | Deep markets in all four asset classes | Poor in commodities and FX |
| **Capital efficiency** | Margin ≈ 5–10% of notional; spare cash earns **collateral yield** | Full notional tied up |

Symmetry is the decisive one: a strategy that must go short as freely as long cannot tolerate that
asymmetry.

**Note (The cost).** Futures expire, so no natural continuous ES series exists — contracts must be
stitched together. See [02](02-data-and-corporate-actions.md).

## 2. Why CTA/Momentum Strategies Work

Two candidate explanations. Neither is settled; momentum has nonetheless been durably profitable.

- **Information diffusion.** Unglamorous news with real macro effects spreads gradually, creating
  sustained pressure. Possibly weakened since 2008 — faster computing prices news more quickly.
- **Selective momentum capture.** Recent winners keep winning, recent losers keep losing. Three
  mechanisms are usually offered:
  - Large positions take time to build and unwind, so institutional flow persists.
  - Investors chase winners and abandon losers, self-reinforcing while it lasts.
  - Major economic events do not resolve in one day; their impact is spread out.

## 3. Long/Short Mechanics

**Definition (Long).** Buy first, sell later. Profit = sell price − buy price.

**Definition (Short).** Borrow and sell first, buy back and return later. Profit = sell price −
buy-back price.

- Running both deploys capital fully — 150/50 or 200/100 rather than leaving cash idle.
- Empirically longs contribute more P&L than same-size shorts, possibly a carry or
  risk-free-rate effect.

Turning a long/short stance into per-asset weights is [04](04-from-signal-to-position.md).

### How short selling works

A short sale is not selling out of thin air — **you borrow the shares first**, exactly like
borrowing money, except the thing borrowed is stock.

```text
1. Borrow    — borrow N shares from a lender (broker / long-term holder)
2. Sell      — sell them now, receive cash
3. Buy back  — later buy N shares back from the market
4. Return    — return the N shares, closing the position
```

**Note (Fungibility).** You never create shares. Returning "N shares of SPY" — not specific
certificates — settles the debt.

**Note (Why lenders lend).** Long-term holders (Vanguard, BlackRock, pension funds) earn a
**lending fee** on stock they were going to sit on anyway. The broker matches the two sides and
holds margin. The market for this is **securities lending**.

**Claim.** A long has bounded loss; a short does not.

A long can lose at most 100%, since price is floored at zero. A short owes the market price of the
borrowed shares, which can rise without limit, so the liability is **theoretically unbounded**.
Hence margin requirements and forced buy-ins. This is also why a 150/50 book — 200% gross — is
**2× leverage**, not free money.

### In this backtest

No borrowing, fees, or margin are modelled. A **negative share count** (`curr_shrs < 0`) is valued
at `asset_value = curr_shrs × close`, so a short is a negative position value — a liability — that
gains when price falls.

**Note (Sign convention).** The negative sign encodes *direction*, a debt owed, not a loss. Shares
are assumed always borrowable at zero cost: fine for teaching, not for trading. Accounting detail:
[05](05-understanding-backtesting.md).

## 4. Market Participants by Holding Period

| Participant | Examples | Typical hold |
| --- | --- | --- |
| Index / passive funds | Vanguard, BlackRock | Years to decades |
| Active managers | Fidelity, PIMCO | Monthly to quarterly |
| Hedge funds | — | Intraday to several days |
| Market makers | Optiver, Citadel Securities, IMC, SIG | Seconds to minutes |
| Noise traders | Retail, uninformed flow | No consistent horizon |

Pension funds favour bonds for predictable cash flows. Hedge funds charge management plus
performance fees behind lockups. Market makers provide liquidity and carry minimal overnight
exposure. Noise-trader flow has no informational content.

---

## Common pitfalls

| Belief | Correction |
| --- | --- |
| "CTA means commodities only." | Historical artifact; main exposures are equity-index, rate, and FX futures. |
| "You can buy the S&P 500." | You buy an ETF or a future *tracking* it. The index is a number. |
| "The index is at 5000, so the market is expensive." | The base scale is arbitrary (1941–43 = 10). Only returns are interpretable. |
| "A negative position means I lost money." | The sign encodes direction — a debt — not P&L. |
| "150/50 is free extra return." | 200% gross is 2× leverage; risk scales with it. |
| "Momentum works because information diffuses slowly." | One candidate explanation, possibly weakened after 2008. Nothing is settled. |

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
- [ ] The difference between an index, an ETF, and a future — and why CTAs use futures
- [ ] Why a negative share count is a direction, not a loss
- [ ] Why a 150/50 book is 2× leverage rather than free return

[← Index](00-index.md)
