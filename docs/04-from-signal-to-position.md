# 04 · From Signal to Position

> **This chapter answers:** how a signal (say 21-day momentum) becomes "how many dollars, and then how many shares, of each asset."
> **Prerequisites:** [03 · Building Your Own Signal](03-building-signals.md).
> **After reading you can:** trace the weight → dollar → shares chain, and explain how a holding period is implemented through weights.

---

## How Momentum and the Backtest Relate

They are **upstream / downstream**. Momentum decides *what to hold and how
much*; the backtester assumes you actually traded that and computes the PnL.
The two are fully decoupled — swap the signal without touching the backtester,
or change the trading assumptions without touching the signal.

```text
close prices
   │  ① signal          momentum(21-day mean of daily returns)   谁在涨/跌
   ▼
momentum signal
   │  ② target weights  Portfolio 1 / Portfolio 2                做多/做空谁、各多少%
   ▼
target weights
   │  ③ 5-day overlap   overlap_weights = target.rolling(5).mean()
   ▼
held weights
   │  ④ weight × capital → dollar exposure                      权重 → 美元敞口
   ▼
multi_asset_backtester (loop over 37 assets)
   │  ⑤ dollar ÷ close → shares → simulate → PnL
   ▼
per-asset PnL → summed → equity curve + Sharpe / drawdown
```

**The bridge is weight → dollar → shares** (one-directional):

| Quantity | Meaning | Formula | Unit |
| --- | --- | --- | --- |
| `weight` | how much of the book to allocate | from the momentum signal | fraction (%) |
| `dollar` | that allocation in money | `weight × capital` | USD |
| `shares` | shares that money buys | `dollar / close` | shares |

Weight is the **cause**; dollar and shares are the **effect**. Because
`shares = dollar / close`, the share count drifts every day even when the
target dollar exposure is unchanged — that is why the book makes small daily
rebalancing trades. 用权重而不是股数，是因为 37 只 ETF 价格差别很大，只有百分比敞口才可比。

Everything downstream of ⑤ — fills, cash, valuation — is covered in [05 · Understanding Backtesting](05-understanding-backtesting.md).

## Momentum Signal / 动量信号

Signal = trailing **21 trading days (~1 month)** mean of daily returns, per
asset: `close.pct_change().rolling(21).mean()`. Positive = recent uptrend,
negative = recent downtrend.

Designing and validating the signal itself belongs to [Chapter 03](03-building-signals.md); here it is taken as a given input.

## Holding Period: Why Weights Change / 5 天持仓下权重如何变化

Holding period is **5 trading days (~1 week)**, implemented as **overlapping
portfolios** (Jegadeesh–Titman style), not a hard rebalance every 5th day.
Each day commits 1/5 of the book to that day's fresh signal and holds it 5
days, so the weight actually held is the average of the last 5 daily targets:

```text
held_weight[t] = mean(target[t], target[t-1], ..., target[t-4])
```

Code: `overlap_weights = target.rolling(5).mean()`. Weights therefore **evolve
smoothly** as old signals roll off and new ones roll on (lower turnover). A
side effect: **gross exposure falls below the single-day target** when longs
and shorts from different days offset (e.g. Portfolio 1 gross ≈ 1.83, not 2.0).
这就是作业里"想一想 weights 怎么变化"的答案 —— 不是每 5 天跳一次，而是滚动平滑。

### Why overlap rather than a fixed rebalance day

The mechanical description above says *what* the overlap does. Two reasons explain *why* it is
the right design.

**It stops throwing signals away.** Rebalancing only on Mondays means Tuesday through Friday
each produce a fresh signal that is computed and then discarded. Committing 1/5 of the book each
trading day uses all of them.

**It neutralizes the weekday effect.** Under weak-form efficiency, day-of-week effects persist:
many funds close positions on Friday and re-establish them on Monday to avoid weekend gap risk,
which systematically lifts Monday returns and depresses Friday's. A strategy that always trades
on one weekday inherits that bias wholesale — and you cannot tell it apart from your signal's
edge. Spreading entry across all five weekdays averages it out.

So the tranche structure is a bias-control decision, not just a turnover-smoothing trick:

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/overlap-tranches-dark.png">
  <img alt="Gantt chart of five tranches, each 20% of the book, each held five trading days and each starting one day after the previous — so entry is spread across every weekday and all five are simultaneously live" src="figures/overlap-tranches-light.png">
</picture>

## The Two Portfolios / 两个组合

| | Portfolio 1 | Portfolio 2 |
| --- | --- | --- |
| Long/short rule | **absolute** MOM (>0 long / <0 short) | **relative** MOM (vs peers) |
| Weights | long leg 150% equal-weight, short leg 50% equal-weight | equal magnitude, sign by relative rank |
| Net exposure | +100% (long-biased) | ≈ 0 (market-neutral) |
| Gross exposure | 200% (before overlap) | ~200% (before overlap) |

**Portfolio 1 — Long 150% / Short 50%.** Long every positive-MOM asset
(equal weight, totaling 150%), short every negative-MOM asset (equal weight,
totaling 50%). With `n_pos` longs and `n_neg` shorts: each long = `1.5/n_pos`,
each short = `−0.5/n_neg`. Net = +1.5 − 0.5 = **+1.0**.

### Weights Are Money, Not Shares or Price / 权重是"钱"，不是股数或价格

A frequent confusion: *"SPY, GLD, XLK have different prices — how can they each
be +50% and still sum to 150%?"* The point is that a weight is a **fraction of
capital (money)**, not a share count and not tied to price. "Equal weight" means
**equal dollars**, and the long legs sum to 150% **by construction** — you are
simply slicing a fixed 150% budget into `n_pos` equal money slices, so the sum
is an identity (`1.5/n_pos × n_pos = 1.5`), never a coincidence. 等权 = 等金额，
加总必然是 150%，因为那 150% 本来就是你平均切成 n 份的。

Prices do **not** need to be equal and never enter the weight formula. Price
only enters **later**, when the dollar allocation is converted to shares
(`shares = dollar / close`): the same $ buys **fewer** shares of an expensive
asset and **more** of a cheap one.

| Long asset | Weight (money) | $ on 1000 capital | Price | Shares bought |
| --- | --- | --- | --- | --- |
| SPY | +50% | $500 | $600 | 0.833 |
| GLD | +50% | $500 | $200 | 2.500 |
| XLK | +50% | $500 | $150 | 3.333 |
| **Sum** | **150%** | **$1500** | — | (all different) |

Same **dollars** per name, wildly different **share counts** — exactly as
intended. This is also why the weight formula `1.5 / n_pos` correctly contains
no price term: allocating money does not require knowing the per-share price;
price is consumed earlier (in the momentum signal, which picked the members) and
later (in the share conversion), just not in the money split itself.
分钱不需要知道单价，价格在"选股"和"换算股数"两步才用到。

**Portfolio 2 — Relative MOM (market-neutral).** Equal-magnitude weights whose
**sign** comes from momentum *relative to the cross-section*, not from its
absolute sign. An asset is long if its MOM is **at or above the cross-sectional
median** that day, else short — so an asset can be shorted even with positive
MOM. This reproduces the brief's example (MOM 10% / 5% / 1% → +66% / +66% /
−66%): the median is 5%, so the two assets ≥ median go long and the weakest one
goes short. The **median** is used deliberately — the mean (5.33%) would give
+ / − / −, which does not match the example. Each leg has magnitude `2/N`, so
gross ≈ 2.0 and net ≈ 0. 关键在"相对"：即使都在涨，最弱的也做空，赚的是强弱差价，与大盘涨跌无关。

## From a Continuous Signal to Weights

Both portfolios above throw away information: they reduce the signal to a **sign** and then
equal-weight within each leg. An asset with overwhelming momentum gets exactly the same weight as
one that barely cleared the threshold.

The generalization is to map the normalized signal straight onto position size, so a stronger
signal earns a larger position. Two steps:

**1. Demean.** Subtract the cross-sectional mean so the signal is centred on zero — positive
values become the long side, negative the short side.

**2. Scale to the exposure constraint.** Multiply by whatever factor makes the legs sum to the
target book:

```text
long leg   150%          net exposure  = +100%
short leg   50%          gross exposure = 200%
```

```python
s = signal.sub(signal.mean(axis=1), axis=0)       # demean cross-sectionally
w = s.div(s.abs().sum(axis=1), axis=0) * 2.0      # scale to 200% gross
w = w + (1.0 - w.sum(axis=1).values[:, None]) / w.shape[1]   # shift net to +100%
```

The resulting weights feed the backtester exactly as before — `dollar = weight × capital`, then
`shares = dollar / close`. Nothing downstream changes; only the allocation rule does.

Which version is better is an empirical question, not a theoretical one. Sign-based weighting is
robust to a noisy signal because it only needs the ranking to be right; proportional weighting
extracts more when the signal's *magnitude* is informative and is punished harder when it is not.
Test both against the bucket chart in [03 § 4](03-building-signals.md).

---

## Common pitfalls

- **"A 5-day hold means rebalancing every 5th day."** It does not. Overlapping portfolios rebalance a little every day; the weight held is the mean of the last 5 daily targets, so weights evolve smoothly.
- **"Gross should come out to exactly 200%."** It will not. Since `|mean| ≤ mean|·|`, gross drops below 200% (≈183% in practice) whenever an asset flips sign inside the 5-day window. That drift is the honest footprint of smooth rebalancing, not a bug to be "fixed." Net, by contrast, *is* invariant: because `Σ mean = mean Σ`, net exposure stays exactly +100%.
- **"Weights should account for price."** They should not. A weight allocates money; price enters only at `shares = dollar / close`.
- **Using the mean instead of the median for relative MOM.** The mean gives 1 long / 2 short, which does not match the brief's +66/+66/−66 example. The median is the correct reading.
- **"Positive MOM means go long."** True only under Portfolio 1's absolute rule. Portfolio 2 is relative — the weakest asset is shorted even if it is rising.

## Open questions

*(to be filled in from the Zoom scripts, following the professor's framing)*

- Where does the 150/50 split come from — a risk-budgeting result, or industry convention?
- Would inverse-volatility weighting (risk parity) be more defensible than equal weight here? Volatility across these assets varies enormously (UNG vs SHY).
- How sensitive are the results to sweeping the 5-day hold and 21-day lookback together? That question belongs to [07 · Overfitting & Robustness](07-overfitting-and-robustness.md).
