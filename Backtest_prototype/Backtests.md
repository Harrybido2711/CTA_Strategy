# Backtester 中各列（labels）的含义

这个回测器将外部给定的目标美元仓位 `dollar` 转换为目标股数，模拟交易产生的现金流，最后计算组合价值。

## 各列的含义

| 列名 | 含义 | 计算方式 |
|---|---|---|
| `ts_event` | 当前这行行情对应的日期或时间 | 来自行情数据 `data` |
| `open` | 当期开盘价 | 来自行情数据 |
| `high` | 当期最高价 | 来自行情数据 |
| `low` | 当期最低价 | 来自行情数据 |
| `close` | 当期收盘价 | 来自行情数据 |
| `volume` | 当期成交量 | 来自行情数据 |
| `symbol` | 交易标的，例如 SPY | 来自行情数据 |
| `dollar` | 策略希望持有的目标美元敞口；正数代表做多，负数代表做空，0 代表空仓 | 来自外部仓位信号表 |
| `target_shrs` | 按当前收盘价换算出的目标股数 | `dollar / close` |
| `curr_shrs` | 代码认定的当前实际持仓股数 | 上一行的 `target_shrs` |
| `traded_shrs` | 当前需要买入或卖出的股数；正数为买入，负数为卖出 | 当前 `curr_shrs - 上一期 curr_shrs` |
| `TWAP` | 代码假定的成交价格。这里并不是真正的 TWAP，只是开盘价和收盘价的平均值 | `(open + close) / 2` |
| `cash_spend` | 本期交易花费的现金；正数表示买入支出，负数表示卖出收入 | `traded_shrs * TWAP` |
| `net_cash` | 截至当前累计剩余的净现金流 | `-cash_spend.cumsum()` |
| `asset_value` | 当前持仓按照收盘价计算的市值 | `curr_shrs * close` |
| `portfolio` | 组合价值，即现金加持仓市值 | `net_cash + asset_value` |

`rtype`、`publisher_id` 和 `instrument_id` 是行情数据供应商提供的元数据，不是回测计算出来的指标：

- `rtype`：数据记录类型的编码。
- `publisher_id`：行情发布者或数据源的编号。
- `instrument_id`：该金融工具在数据源中的内部编号。

## 为什么这些列在时间上是错开的？

错开来自两个不同的操作。

### 第一次错开：`delay`

```python
dollar['ts_event'] = dollar['ts_event'] + timedelta(days=1)
```

原始 `dollar` 表中，第一条信号是 2020-01-02 的 `dollar = 1`。加一天后，这条信号的时间变成 2020-01-03。因此合并后的结果是：

| 行情日期 | 合并后的 `dollar` |
|---|---:|
| 2020-01-02 | `NaN` |
| 2020-01-03 | 1 |

`merge_asof(..., direction='backward')` 只会使用当前时点或之前已经出现的信号，因此 1 月 2 日不能提前看到被移到 1 月 3 日的信号。

### 第二次错开：`shift()`

```python
df['curr_shrs'] = df['target_shrs'].shift()
```

这使 `curr_shrs` 使用上一行的 `target_shrs`。由于数据是交易日数据，“上一行/下一行”并不总是相差一个自然日。例如 1 月 3 日的下一行是 1 月 6 日，中间是周末。

实际结果如下：

| 日期 | `dollar` | `target_shrs` | `curr_shrs` | `traded_shrs` |
|---|---:|---:|---:|---:|
| 2020-01-02 | `NaN` | `NaN` | `NaN` | `NaN` |
| 2020-01-03 | 1 | 0.003099 | `NaN` | `NaN` |
| 2020-01-06 | 1 | 0.003093 | 0.003099 | 0.003099 |
| 2020-01-07 | 1 | 0.003130 | 0.003093 | -0.000006 |

因此时间链是：

```text
1 月 2 日生成 dollar 信号
        ↓ delay=1 个自然日
1 月 3 日出现 dollar，并计算 target_shrs
        ↓ shift=1 行（下一个交易日）
1 月 6 日成为 curr_shrs，并产生 traded_shrs
```

`traded_shrs` 自身没有再次滞后。`diff()` 只是计算当前持仓和上一期持仓之间的差：

```python
traded_shrs[t] = curr_shrs[t] - curr_shrs[t-1]
```

第一笔 `traded_shrs` 在 1 月 6 日才出现，是因为它依赖的 `curr_shrs` 已经被 `shift()` 推迟到这一行。

## 当前写法需要注意的问题

`delay` 和 `shift()` 一起使用，相当于先把信号推迟一个自然日，再把持仓推迟一个数据行。这可能是有意设置的执行时间，也可能是重复延迟。

此外，虽然 `dollar` 一直等于 1，但 `target_shrs = 1 / close` 会随着每日收盘价变化，所以代码每天都会进行很小的再平衡交易。例如价格上涨后，维持 1 美元敞口所需要的股数减少，于是 `traded_shrs` 为负数。

如果定义是“延迟后的信号在当天直接成交并成为持仓”，可以不再对目标股数执行 `shift()`：

```python
df['curr_shrs'] = df['target_shrs']
df['traded_shrs'] = df['curr_shrs'].diff().combine_first(df['curr_shrs'])
```

但是否应该删除 `shift()`，最终取决于信号在什么时间产生、使用什么信息，以及计划在什么时间成交。必须先把信号时间、成交时间和持仓生效时间定义清楚，才能避免前视偏差。
