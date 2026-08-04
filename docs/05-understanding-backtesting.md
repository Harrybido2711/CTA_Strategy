# 05 · Understanding Backtesting

> - **Answers:** what a backtester computes, why decision and fill must be offset in time, and how large that offset should be.
> - **Prerequisites:** [04 · From Signal to Position](04-from-signal-to-position.md).
> - **After reading:** read every column of the output, and say whether your backtest has look-ahead bias.

A backtester does one thing: **convert a target dollar exposure into shares, simulate the trade,
compute the portfolio value.** Implementation: [`backtest.py`](../Backtest_prototype/backtest.py).

---

## Column Definitions

| Column | Meaning | Calculation |
| --- | --- | --- |
| `ts_event` | Date or time of the market record | From market data |
| `open`, `high`, `low`, `close` | Market prices for the period | From market data |
| `volume` | Trading volume | From market data |
| `symbol` | Instrument ticker | From market data |
| `dollar` | Desired dollar exposure: + long, − short, 0 flat | From the strategy |
| `target_shrs` | Shares the strategy wants to hold | `dollar / close` |
| `curr_shrs` | Shares currently held in the simulation | Previous row's `target_shrs` |
| `traded_shrs` | Shares bought (+) or sold (−) | Change in `curr_shrs` |
| `TWAP` | Assumed execution price — an approximation, not a true TWAP | `(open + close) / 2` |
| `cash_spend` | Cash used to trade; + purchase, − sale | `traded_shrs * TWAP` |
| `net_cash` | Cumulative net cash from trading | `-cash_spend.cumsum()` |
| `asset_value` | Market value of the position | `curr_shrs * close` |
| `portfolio` | Total portfolio value | `net_cash + asset_value` |

`rtype`, `publisher_id`, `instrument_id` are vendor metadata, not backtest results.

## Target, Traded, Current, and Total

Four stages of managing a position:

- **Target shares** — what the strategy wants.
- **Traded shares** — the order that moves the old position toward the target.
- **Current shares** — what is actually held after execution.
- **Total value** — the whole account, called `portfolio` here.

Holding 6, targeting 10: `traded = 10 − 6 = +4`, `new current = 6 + 4 = 10`.

## Why Are the Values Offset?

Decision and execution are separate events:

```text
information available → calculate target → submit and fill → update position and value
```

The offset exists because a signal may depend on end-of-period information, orders take time to
fill, the fill price differs from the price used to compute the target, and large orders may fill
only partially. A target computed from today's close cannot be traded at today's earlier open.

The offset need not be one full day: a pre-market signal may trade at that day's open, an intraday
signal seconds later. Correct timing depends on when information arrives and when execution is
possible.

## Timing in This Backtester

Two offsets. First the signal date is delayed:

```python
dollar['ts_event'] = dollar['ts_event'] + delay     # Jan 2 signal → available Jan 3
```

Then the target position is shifted one row:

```python
df['curr_shrs'] = df['target_shrs'].shift()         # Jan 3 target → held Jan 6
```

| Date | `dollar` | `target_shrs` | `curr_shrs` | `traded_shrs` |
| --- | ---: | ---: | ---: | ---: |
| Jan 2 | `NaN` | `NaN` | `NaN` | `NaN` |
| Jan 3 | 1 | 0.003099 | `NaN` | `NaN` |
| Jan 6 | 1 | 0.003093 | 0.003099 | 0.003099 |
| Jan 7 | 1 | 0.003130 | 0.003093 | -0.000006 |

`diff()` adds no delay — it only computes `traded_shrs[t] = curr_shrs[t] − curr_shrs[t−1]`.

Because `delay` and `shift()` both offset, **the current code may delay execution twice**. Whether
both are needed depends on the intended signal-and-execution timeline.

Note also that `target_shrs = dollar / close` moves whenever the close moves, even at constant
`dollar` — hence small daily rebalancing trades.

The economic order is always: **target decision → execution → current position → valuation.**

## Daily Lifecycle After Each Close

```text
day t close arrives
   │
   ├─ signal side:   close → daily return → 21d momentum → target weights → dollar
   │                 ("the position I want", not yet executed)
   │
   ├─ execution side (delay ~1 day): dollar → target_shrs
   │                 → next bar becomes curr_shrs → traded_shrs (shares to trade today)
   │
   └─ accounting side: fill at TWAP=(open+close)/2 → update net_cash, asset_value
                       → portfolio = net_cash + asset_value = cumulative PnL
```

Multi-asset runs this loop for all 37 assets and sums each `portfolio` into the equity curve.

---

## Common pitfalls

- **Counting `diff()` as another delay.** It computes a difference, not an offset. Only `delay` and `.shift()` shift time.
- **Assuming more offset is safer.** This code may delay twice; over-delaying understates returns — as wrong as look-ahead, in the opposite direction.
- **"Unchanged `dollar` means nothing to trade."** `shares = dollar / close` moves with price. Turnover is never zero.
- **Reading an equity-curve jump as a code bug.** Check the data first — see [02](02-data-and-corporate-actions.md).
- **Treating TWAP as a real fill.** `(open+close)/2` has no slippage, commissions, or liquidity constraint.

## Open questions

- Keep `delay` or `.shift()` — which? Write down when the signal is knowable and when a fill is possible, then decide.
- How much does `(open+close)/2` change the conclusions? Test against close-fill and open-fill.
- With commissions and slippage, does daily rebalancing turnover consume the entire return?

---

## Next → [06 · Evaluating Performance](06-evaluating-performance.md)

Before moving on, **run the backtest and trace one asset by hand** — pick a single ticker and follow
one row from `dollar` through `target_shrs`, `curr_shrs`, `traded_shrs`, `TWAP`, to `portfolio`:

```bash
python ../Backtest_prototype/backtest.py
```

You should be able to explain:

- [ ] What each column means and which are inputs vs computed
- [ ] Exactly where the two time offsets are, and whether your code delays twice
- [ ] Why turnover is never zero even at constant `dollar`

[← 04](04-from-signal-to-position.md) · [Index](00-index.md)
