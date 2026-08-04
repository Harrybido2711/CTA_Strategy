# 06 · Evaluating Performance

> **This chapter answers:** once the backtest produces an equity curve, how do you judge whether it is any good?
> **Prerequisites:** [05 · Understanding Backtesting](05-understanding-backtesting.md).
> **After reading you can:** report a strategy's performance in the terms a practitioner expects, and know what each number hides.

> 🟡 **Partly written.** § 1 is complete; §§ 2–5 are outline only.

---

## 1. A single number throws away the time dimension

Every headline statistic — Sharpe, mean return, hit rate — is an average over the whole sample.
Averaging across time is exactly what destroys the information you most need: **which market
regime the strategy was working in.** A Sharpe of 0.2 could be a strategy that earns steadily, or
one that made everything in a single quarter and bled for five years. The number cannot tell you.

So before quoting any statistic, **plot the performance curve and look at where it fails.** Then
tie each failure to what the market was doing at the time — a liquidity shock, a volatility spike,
a regime break. The question to answer is *why* the strategy broke there, because that is what
tells you whether the failure is a fixable flaw or an inherent exposure.

**What not to do: drop the asset that caused the damage.** It is tempting to find the single
ticker responsible for the worst drawdown and exclude it, after which every statistic improves.
That is not analysis, it is fitting to the sample. And it does not transfer to practice: a real
asset-management product cannot arbitrarily drop holdings from its stated universe. If an asset is
in the mandate, its bad periods are part of the strategy's honest performance.

The legitimate response to a bad period is to understand its cause and, if the cause is a genuine
risk exposure, to hedge or size against it — not to delete the evidence.

## 2. Return and risk

*(outline — to be written)*

- Arithmetic vs geometric return; why compounding matters for a leveraged book.
- Volatility, and why annualizing by `√252` assumes something that is usually false.

## 3. Sharpe ratio

*(outline — to be written)*

- Definition, the risk-free-rate term, and the annualization convention.
- What Sharpe cannot see: skew, fat tails, path dependence, and the fact that both portfolios
  in this project land near zero.

## 4. Drawdown, turnover, capacity

*(outline — to be written)*

- Maximum drawdown, drawdown duration, and why duration is often the binding constraint in practice.
- Turnover implied by daily rebalancing (see [04](04-from-signal-to-position.md) on why it is
  never zero), and what it costs.
- Where the strategy stops scaling.

## 5. Attribution and benchmarking

*(outline — to be written)*

- Per-asset and per-sleeve PnL: which of the 37 assets actually produced the result — as
  diagnosis, not as a licence to drop the loser (see § 1).
- Long leg vs short leg.
- Against what benchmark? Buy-and-hold SPY, an equal-weight basket, or a random-sign portfolio.
  Net vs gross exposure makes the comparison non-obvious for a 150/50 book.

---

## Common pitfalls

- **Quoting a Sharpe without looking at the curve.** The average hides whether the return was steady or a single lucky quarter.
- **Excluding the worst-performing asset to improve the statistics.** That is in-sample fitting, and a real product cannot drop holdings from its mandate anyway.
- **Explaining a drawdown by its size instead of its cause.** "−18% in March" is a fact; "the strategy is short volatility and March was a vol spike" is a finding.

## Open questions

*(to be written)*
