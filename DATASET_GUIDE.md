# CTA Dataset Assignment / CTA 数据作业

## 1. Files and fields / 文件与字段

Each `TICKER_ohlcv_1d.csv` file contains daily OHLCV bars for one ETF. The suffix `1d` means that each row represents one daily bar.  
每个 `TICKER_ohlcv_1d.csv` 文件都包含一个 ETF 的日频 OHLCV 数据。后缀 `1d` 表示每一行代表一个日线 bar。

- `ts_event`: The timestamp of the daily bar. The timestamps in this dataset use UTC.  
  `ts_event`：日线 bar 的时间戳。本数据集使用 UTC 时间。

- `open`: The price of the first eligible trade in the bar.  
  `open`：该 bar 内第一笔被纳入统计的成交价格，即开盘价。

- `high`: The highest eligible trade price during the bar.  
  `high`：该 bar 内被纳入统计的最高成交价格，即最高价。

- `low`: The lowest eligible trade price during the bar.  
  `low`：该 bar 内被纳入统计的最低成交价格，即最低价。

- `close`: The price of the last eligible trade in the bar.  
  `close`：该 bar 内最后一笔被纳入统计的成交价格，即收盘价。

- `volume`: The total quantity of the instrument traded during the bar. Because these instruments are ETFs, the unit is ETF shares, not dollars. Actual dollar turnover is the sum of trade price multiplied by trade size for every trade. With daily data only, `close × volume` is merely an approximation of dollar turnover.  
  `volume`：该 bar 内标的的总成交数量。由于这里的标的是 ETF，所以单位是 ETF 份额（shares），不是美元成交金额。准确成交金额应为每笔成交价格乘以成交数量后求和；只有日线数据时，`close × volume` 只能近似表示成交金额。

- `symbol`: The ETF ticker symbol.  
  `symbol`：ETF 的 ticker 代码。

- `rtype`, `publisher_id`, and `instrument_id`: The data vendor's record type, publisher identifier, and internal instrument identifier. They can be ignored for this assignment.  
  `rtype`、`publisher_id` 和 `instrument_id`：数据供应商使用的记录类型、发布源编号和内部标的编号。本作业可以忽略这些字段。

Databento's `ohlcv-1d` data is aggregated by UTC date. Its electronic-session definition may differ from official exchange settlement or volume statistics. The prices in these CSV files appear to be unadjusted; dividends, splits, and reverse splits can therefore affect cross-day comparisons.  
Databento 的 `ohlcv-1d` 数据按 UTC 日期聚合。其电子交易时段口径可能不同于交易所官方结算价或成交量统计口径。这些 CSV 中的价格看起来是未复权价格，因此分红、拆股和反向拆股都可能影响跨日比较。

## 2. Meaning of the 37 datasets / 37 个数据集的含义

| Category / 类别 | Ticker | Exposure / 主要敞口 |
|---|---|---|
| U.S. broad equity / 美国宽基股票 | SPY | S&P 500 Index / 标普 500 指数 |
|  | QQQ | Nasdaq-100 Index / 纳斯达克 100 指数 |
|  | IWM | Russell 2000 small-cap stocks / Russell 2000 美国小盘股 |
|  | DIA | Dow Jones Industrial Average / 道琼斯工业平均指数 |
|  | MDY | S&P MidCap 400 stocks / 标普 400 中盘股 |
| U.S. equity sectors / 美国行业股票 | XLK | Technology / 科技 |
|  | XLF | Financials / 金融 |
|  | XLE | Energy / 能源 |
|  | XLV | Health care / 医疗保健 |
|  | XLI | Industrials / 工业 |
|  | XLY | Consumer discretionary / 非必需消费品 |
|  | XLP | Consumer staples / 必需消费品 |
|  | XLU | Utilities / 公用事业 |
|  | XLB | Materials / 原材料 |
|  | XLRE | Real estate / 房地产 |
|  | XLC | Communication services / 通信服务 |
| International equity / 国际股票 | EFA | Developed markets excluding the U.S. and Canada / 美国、加拿大以外的发达市场 |
|  | EEM | Emerging markets / 新兴市场 |
|  | VGK | European equities / 欧洲股票 |
|  | EWJ | Japanese equities / 日本股票 |
|  | FXI | Large-cap Chinese equities / 中国大型股 |
| Fixed income / 固定收益 | TLT | U.S. Treasury bonds with maturities above 20 years / 20 年以上美国国债 |
|  | IEF | 7–10 year U.S. Treasury bonds / 7–10 年美国国债 |
|  | SHY | 1–3 year U.S. Treasury bonds / 1–3 年美国国债 |
|  | AGG | Broad U.S. investment-grade bond market / 美国投资级综合债券市场 |
|  | LQD | U.S. dollar investment-grade corporate bonds / 美元投资级公司债 |
|  | HYG | U.S. dollar high-yield corporate bonds / 美元高收益公司债 |
|  | TIP | U.S. Treasury Inflation-Protected Securities / 美国通胀保值国债（TIPS） |
| Commodities / 商品 | GLD | Gold / 黄金 |
|  | SLV | Silver / 白银 |
|  | DBC | Diversified commodity futures / 多元商品期货组合 |
|  | USO | Crude-oil futures exposure, not spot oil / 原油期货敞口，并非原油现货价格 |
|  | UNG | Natural-gas futures exposure, not spot gas / 天然气期货敞口，并非天然气现货价格 |
|  | DBA | Agricultural commodity futures / 农产品期货组合 |
| Alternatives / 其他或另类资产 | VNQ | U.S. real estate investment trusts (REITs) / 美国房地产投资信托（REITs） |
|  | GDX | Global gold-mining company equities / 全球金矿公司股票 |
|  | UUP | Long U.S. dollar exposure against a currency basket / 美元相对一篮子货币走强的敞口 |

## 3. Overnight versus intraday movement / 隔夜与日内变动比较

The script calculates the two movements requested in the assignment:  
脚本按照作业要求计算以下两种变动：

- Absolute overnight movement / 隔夜绝对变动：`abs(Open[t] - Close[t-1])`
- Absolute intraday movement / 日内绝对变动：`abs(Close[t] - Open[t])`

Both dollar and percentage movements are reported. Percentage movements are more appropriate when comparing ETFs with different price levels. Average absolute movement is not the same concept as cumulative return contribution. To test whether most returns are realized overnight, we should additionally compare signed overnight and intraday returns while correctly handling dividends, splits, and adjusted prices.  
结果同时报告美元变动和百分比变动。比较价格水平不同的 ETF 时，百分比变动更加合理。平均绝对变动并不等同于累计收益贡献。若要检验大部分收益是否在隔夜实现，还应该比较有符号的隔夜收益与日内收益，并正确处理分红、拆股和复权价格。

### Results for this dataset / 本批数据的实测结果

- All 37 files loaded successfully and passed checks for required fields, numeric types, missing values, duplicate timestamps, chronological order, OHLC consistency, and manifest row counts.  
  37 个文件全部成功载入，并通过必需字段、数值类型、缺失值、重复时间戳、时间排序、OHLC 关系和 manifest 行数检查。

- Under both the dollar and percentage definitions, only **FXI (1 out of 37 ETFs)** has a larger average absolute overnight movement than average absolute intraday movement. The other 36 ETFs have larger average intraday movements.  
  无论使用美元还是百分比口径，只有 **FXI（37 个 ETF 中的 1 个）** 的平均隔夜绝对变动大于平均日内绝对变动；其余 36 个 ETF 的平均日内变动更大。

- Therefore, for this dataset covering January 2, 2020 through June 29, 2026, the absolute-movement test does not support the claim that overnight movements are usually larger. The statement that returns are mostly realized overnight may instead refer to signed cumulative return contribution, which is a different hypothesis.  
  因此，对于覆盖 2020 年 1 月 2 日至 2026 年 6 月 29 日的本数据集，绝对变动检验并不支持“隔夜变动通常更大”的说法。“收益主要在隔夜实现”可能指有符号的累计收益贡献，这是另一个不同的假设。

- For example, SPY's mean signed returns in this sample are approximately `0.0133%` per day overnight and `0.0453%` per day intraday. Thus, even the signed mean return for SPY is not overnight-dominated in this particular sample. Results can depend on the sample period, session definition, corporate actions, and adjustment method.  
  例如，本样本中 SPY 的平均有符号收益约为：隔夜每天 `0.0133%`，日内每天 `0.0453%`。所以在这一特定样本里，即便比较有符号平均收益，SPY 也不是由隔夜收益主导。结果可能受到样本区间、交易时段定义、公司行动及复权方法的影响。

## 4. How to run the analysis / 如何运行分析

Python 3.9 or newer is recommended. The required packages are `pandas` and `matplotlib`.  
建议使用 Python 3.9 或更高版本。所需第三方包为 `pandas` 和 `matplotlib`。

```bash
python analyze_cta_data.py
```

The script produces the following files:  
脚本会生成以下文件：

- `output/validation_and_gap_summary.csv`: Loading status, quality checks, and the overnight-versus-intraday comparison for every ticker.  
  `output/validation_and_gap_summary.csv`：每个 ticker 的载入状态、质量检查及隔夜—日内比较结果。

- `output/selected_price_trends.png`: Closing-price charts for SPY, TLT, GLD, EEM, and DBC.  
  `output/selected_price_trends.png`：SPY、TLT、GLD、EEM 和 DBC 的收盘价走势图。
