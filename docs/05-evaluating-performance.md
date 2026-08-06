# 05 · Evaluating Performance

> - **Answers:** given an equity curve, how do you judge whether it is any good?
> - **Prerequisites:** [04 · Understanding Backtesting](04-understanding-backtesting.md).
> - **After reading:** report performance in the terms a practitioner expects, and know what each number hides.

> 🟡 **Partly written.** § 1 complete; §§ 2–5 outline.

---

## 1. A single number throws away the time dimension

Every headline statistic — Sharpe, mean return, hit rate — averages over the whole sample, and
averaging across time destroys what you most need: **which regime the strategy was working in.** A
Sharpe of 0.2 could be steady earnings or one great quarter followed by five years of bleeding. The
number cannot tell you.

So before quoting any statistic, **plot the curve and look at where it fails**, then tie each
failure to what the market was doing — a liquidity shock, a volatility spike, a regime break.
Answering *why* it broke is what separates a fixable flaw from an inherent exposure.

**What not to do: drop the asset that caused the damage.** Excluding the ticker behind the worst
drawdown improves every statistic, but it is fitting to the sample — and it doesn't transfer, since
a real product cannot arbitrarily drop holdings from its stated universe. If an asset is in the
mandate, its bad periods are part of the honest performance. Understand the cause and, if it is a
genuine risk exposure, hedge or size against it.

## 2. Return and risk

*(outline)* — Arithmetic vs geometric return, and why compounding matters for a leveraged book.
Volatility, and why annualizing by `√252` assumes something usually false.

## 3. Sharpe ratio

*(outline)* — Definition, the risk-free term, the annualization convention. What it cannot see:
skew, fat tails, path dependence — and that both portfolios here land near zero.

## 4. Drawdown, turnover, capacity

*(outline)* — Maximum drawdown and drawdown *duration*, often the binding constraint in practice.
Turnover from daily rebalancing (never zero — see [03](03-from-signal-to-position.md)) and its cost.
Where the strategy stops scaling.

## 5. Attribution and benchmarking

*(outline)* — Per-asset and per-sleeve PnL as diagnosis, not a licence to drop the loser (§ 1).
Long leg vs short leg. Against what benchmark — buy-and-hold SPY, an equal-weight basket, or a
random-sign portfolio? Net vs gross exposure makes this non-obvious for a 150/50 book.

---

## Common pitfalls

- **Quoting a Sharpe without looking at the curve.** The average hides steady returns vs one lucky quarter.
- **Excluding the worst asset to improve the statistics.** In-sample fitting, and impossible in a real mandate.
- **Explaining a drawdown by its size instead of its cause.** "−18% in March" is a fact; "short volatility into a vol spike" is a finding.

## Open questions

*(to be written)*

---

## Next → [06 · Overfitting & Robustness](06-overfitting-and-robustness.md)

Before moving on, **plot the equity curve and annotate its three worst drawdowns** with what the
market was doing at the time. Chapter 06 asks how much of the remaining result is real.

You should be able to explain:

- [ ] Why a Sharpe number alone cannot distinguish steady earnings from one lucky quarter
- [ ] Why dropping the worst asset is fitting rather than analysis

[← 04](04-understanding-backtesting.md) · [Index](00-index.md)
