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

### What

"S&P 500" names three different objects. Only two of them can be traded.

| Layer | Example | What it is | Tradeable |
| --- | --- | --- | --- |
| **Index** | SPX, NDX | A published number computed from its constituents | No |
| **ETF** | SPY, VOO, QQQ | A fund holding the constituents; its own shares trade | Yes |
| **Future** | ES, NQ | A contract to settle at a future date; holds nothing | Yes |

**Definition (Index).** A published real-valued process

```text
I_t  =  M_t / D_t        where   M_t = Σ_i  N_i · P_it
```

with `P_it` the price of constituent `i`, `N_i` its float-adjusted share count, `M_t` the total
float capitalisation, and `D_t > 0` the *divisor*.

### Why

**Claim.** The index return is the capitalisation-weighted average of constituent returns, and the
divisor never enters it.

**Proof.** Take two dates with no constituent change, so `D` is constant and
`I_{t+1}/I_t = M_{t+1}/M_t`. The numerator moves by

```text
M_{t+1} − M_t  =  Σ_i  N_i (P_i,t+1 − P_it)  =  Σ_i  N_i P_it · r_i
```

where `r_i = (P_i,t+1 − P_it)/P_it`. Dividing by `M_t`,

```text
r_I  =  Σ_i  (N_i P_it / M_t) · r_i  =  Σ_i  w_it · r_i ,      w_it = N_i P_it / M_t
```

and `Σ_i w_it = 1`, so `r_I` is a weighted average with weights equal to capitalisation shares.
`D` cancels.

**Note (Consequence).** Weights are share-of-capitalisation, so with `w ≈ 7%` for the largest
constituent and `w ≈ 0.02%` for the smallest, the largest name carries roughly **350× the index
impact** of the smallest per unit of its own return. The "500" is a constituent count, not a
denominator — this is not an average of 500 prices. Contrast the Dow (price-weighted) and RSP
(equal-weighted, the actual arithmetic average).

**Note (Why the divisor exists).** Since `D` cancels from returns, it does nothing except keep
`I_t` continuous when `M_t` jumps for non-market reasons — a constituent replacement, an issuance.
The S&P 500 base is 1941–43 = 10, so the level is a growth factor off an arbitrary scale, with no
tendency to revert to it. **Levels are not comparable; only returns are.**

**Claim.** A CTA trades futures, not ETFs.

| Reason | Futures | ETFs |
| --- | --- | --- |
| **Symmetry** | Shorting costs nothing extra | Shorting needs borrowed shares, a fee, availability |
| **Coverage** | Deep markets in all four asset classes | Poor in commodities and FX |
| **Capital efficiency** | Margin ≈ 5–10% of notional; spare cash earns **collateral yield** | Full notional tied up |

This one is a judgement, not a derivation: symmetry is decisive because a strategy that must go
short as freely as long cannot tolerate the asymmetry, and § 3 shows why the short leg is the
fragile one.

**Note (The cost).** Futures expire, so no natural continuous ES series exists — contracts must be
stitched together. See [02](02-data-and-corporate-actions.md).

### How

Because levels are not comparable, any cross-asset chart must be **rebased** first — divide each
series by its own first observation:

```python
from backtest import load_assets, close_matrix

close = close_matrix(load_assets())                  # index=date, columns=tickers
first = close.apply(lambda s: s.dropna().iloc[0])    # tickers start on different dates
rebased = close.div(first) * 100                     # every series now starts at 100
```

| Date | SPY | TLT | GLD |
| --- | --- | --- | --- |
| 2020-01-02 | 100.0 | 100.0 | 100.0 |
| 2026-06-29 | **227.9** | **63.7** | **255.9** |

Read directly: SPY +128%, TLT −36%, GLD +156% over the sample. The raw closes on that date —
SPY 740.83, TLT 87.35, GLD 368.49 — support no such comparison, since each price level is set by
share-creation history rather than by performance.

## 2. Why CTA/Momentum Strategies Work

Two candidate explanations. Neither is settled — there is no proof stage here, and that is the
honest state of the field. Momentum has nonetheless been durably profitable.

- **Information diffusion.** Unglamorous news with real macro effects spreads gradually, creating
  sustained pressure. Possibly weakened since 2008 — faster computing prices news more quickly.
- **Selective momentum capture.** Recent winners keep winning, recent losers keep losing. Three
  mechanisms are usually offered:
  - Large positions take time to build and unwind, so institutional flow persists.
  - Investors chase winners and abandon losers, self-reinforcing while it lasts.
  - Major economic events do not resolve in one day; their impact is spread out.

Chapter [03](03-building-signals.md) turns this from a story into something testable.

## 3. Long/Short Mechanics

### What

**Definition (Long).** Buy first, sell later. Profit = sell price − buy price.

**Definition (Short).** Borrow and sell first, buy back and return later. Profit = sell price −
buy-back price.

A short sale is not selling out of thin air — **you borrow the shares first**, exactly like
borrowing money, except the thing borrowed is stock:

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

### Why

**Claim.** For a static position, a long's loss is bounded by its outlay; a short's is not.

**Proof.** Let `s` be the signed share count, opened at `P₀ > 0` and closed at `P_T`. Then

```text
PnL(P_T) = s · (P_T − P₀),        P_T ∈ [0, ∞)
```

the domain being half-open because a price cannot be negative.

*Long, `s > 0`.* `PnL` is increasing in `P_T`, so its infimum over the domain is at the left
endpoint: `PnL ≥ s(0 − P₀) = −s·P₀`, which is exactly the amount paid. The loss is bounded.

*Short, `s < 0`.* `PnL` is decreasing in `P_T`, and the domain has no right endpoint, so
`PnL(P_T) → −∞` as `P_T → ∞`. No bound exists.

The asymmetry is in the **domain**, not the payoff: both are straight lines of slope `|s|`. The
floor exists only because prices are floored at zero.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/payoff-asymmetry-dark.png">
  <img alt="P&L per dollar of exposure against terminal price. The long and short payoffs are straight lines of equal and opposite slope crossing at the entry price; the long's line terminates at minus 100 percent when the price reaches zero, while the short's line continues downward without limit as the price rises" src="figures/payoff-asymmetry-light.png">
</picture>

**Note.** This is why brokers require **margin** and may force a **buy-in**, and why a 150/50 book
— 200% gross — is **2× leverage**, not free money.

### How

The backtester models no borrowing, fees, or margin. It simply allows a **negative share count**.

**Claim.** In [`backtester`](../Backtest_prototype/backtest.py#L40-L69), a position with
`curr_shrs < 0` gains exactly when the close falls — with no branch special-casing shorts.

**Proof.** Open `s` shares on day 0 at execution price `p₀ = TWAP₀` and hold to a close `p₁` with
no further trades. Following the code lines in order:

```text
cash_spend  = s · p₀                              # traded_shrs × TWAP
net_cash    = −cumsum(cash_spend) = −s · p₀
asset_value = s · p₁                              # curr_shrs × close
portfolio   = net_cash + asset_value = s (p₁ − p₀)
```

which is the same `s(P_T − P₀)` as above. For `s < 0`, `portfolio > 0 ⟺ p₁ < p₀`. The sign of the
share count carries the direction, and the accounting needs no other case.

**Note (Sign convention).** A negative `asset_value` is a **liability** — a debt owed — not a
loss. Shares are assumed always borrowable at zero cost: fine for teaching, not for trading.

Shorting \$1 of SPY across the whole sample, where SPY rose from 325.05 to 740.83 (×2.28):

| Position | Final PnL per \$1 | Why |
| --- | --- | --- |
| Static short (share count frozen at entry) | **−1.2791** | The full `s(P_T − P₀)` above |
| Constant −\$1 exposure (what `backtester` does) | **−0.9385** | Exposure is trimmed daily as the price rises |

**Note.** The unboundedness proof assumes a *static* position. Holding constant **dollar**
exposure rebalances the short smaller as it moves against you, which is why the realised loss is
−93.9% rather than −127.9%. The proof is not wrong; the backtester is simply not running the
position it describes. Accounting detail: [05](05-understanding-backtesting.md).

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
| "The index is the average of 500 stocks." | It is a cap-weighted average of 500 *returns*; the top names dominate. |
| "A negative position means I lost money." | The sign encodes direction — a debt — not P&L. |
| "150/50 is free extra return." | 200% gross is 2× leverage; risk scales with it. |
| "Momentum works because information diffuses slowly." | One candidate explanation, possibly weakened after 2008. Nothing is settled. |

## Open questions

- Longs out-contribute same-size shorts — carry / risk-free-rate effect, or just equities' long-run positive drift?
- If information diffusion weakened after 2008, what keeps momentum alive since?
- Constant-dollar exposure quietly caps short losses. Is that a realistic model of a CTA, or a hidden risk control the backtest gets for free?

---

## Next → [02 · Data & Corporate Actions](02-data-and-corporate-actions.md)

Before moving on, **reproduce the rebased table above** for all 37 tickers and find the best and
worst performer over the sample. Then open `CTA_data/_manifest.csv` and note which tickers are
equity, rate, commodity, and FX exposures. Chapter 02 is about trusting that data before building
anything on it.

You should be able to explain:

- [ ] What a CTA actually trades, and why the name is misleading
- [ ] The difference between an index, an ETF, and a future — and why CTAs use futures
- [ ] Why the divisor cancels out of index *returns* but sets the *level*
- [ ] Why a negative share count is a direction, not a loss
- [ ] Where the short's unbounded loss comes from, and why the backtester does not realise it

[← Index](00-index.md)
