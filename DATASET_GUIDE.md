# CTA Dataset Assignment

## 1. Files and Fields

Each `TICKER_ohlcv_1d.csv` file contains daily OHLCV bars for one ETF. The suffix `1d` means that each row represents one daily bar.  

- `ts_event`: The timestamp of the daily bar. The timestamps in this dataset use UTC.  

- `open`: The price of the first eligible trade in the bar.  

- `high`: The highest eligible trade price during the bar.  

- `low`: The lowest eligible trade price during the bar.  

- `close`: The price of the last eligible trade in the bar.  

- `volume`: The total quantity of the instrument traded during the bar. Because these instruments are ETFs, the unit is ETF shares, not dollars. Actual dollar turnover is the sum of trade price multiplied by trade size for every trade. With daily data only, `close × volume` is merely an approximation of dollar turnover.  

- `symbol`: The ETF ticker symbol.  

- `rtype`, `publisher_id`, and `instrument_id`: The data vendor's record type, publisher identifier, and internal instrument identifier. They can be ignored for this assignment.  

Databento's `ohlcv-1d` data is aggregated by UTC date. Its electronic-session definition may differ from official exchange settlement or volume statistics. The prices in these CSV files appear to be unadjusted; dividends, splits, and reverse splits can therefore affect cross-day comparisons.  

## 2. Meaning of the 37 Datasets

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

## 3. Overnight Versus Intraday Movement

The script calculates the two movements requested in the assignment:  

- Absolute overnight movement: `abs(Open[t] - Close[t-1])`
- Absolute intraday movement: `abs(Close[t] - Open[t])`

Both dollar and percentage movements are reported. Percentage movements are more appropriate when comparing ETFs with different price levels. Average absolute movement is not the same concept as cumulative return contribution. To test whether most returns are realized overnight, we should additionally compare signed overnight and intraday returns while correctly handling dividends, splits, and adjusted prices.  

### Results for This Dataset

- All 37 files loaded successfully and passed checks for required fields, numeric types, missing values, duplicate timestamps, chronological order, OHLC consistency, and manifest row counts.  

- Under both the dollar and percentage definitions, only **FXI (1 out of 37 ETFs)** has a larger average absolute overnight movement than average absolute intraday movement. The other 36 ETFs have larger average intraday movements.  

- Therefore, for this dataset covering January 2, 2020 through June 29, 2026, the absolute-movement test does not support the claim that overnight movements are usually larger. The statement that returns are mostly realized overnight may instead refer to signed cumulative return contribution, which is a different hypothesis.  

- For example, SPY's mean signed returns in this sample are approximately `0.0133%` per day overnight and `0.0453%` per day intraday. Thus, even the signed mean return for SPY is not overnight-dominated in this particular sample. Results can depend on the sample period, session definition, corporate actions, and adjustment method.  

## 4. How to Run the Analysis

Python 3.9 or newer is recommended. The required packages are `pandas` and `matplotlib`.  

```bash
python analyze_cta_data.py
```

The script produces the following files:  

- `output/validation_and_gap_summary.csv`: Loading status, quality checks, and the overnight-versus-intraday comparison for every ticker.  

- `output/selected_price_trends.png`: Closing-price charts for SPY, TLT, GLD, EEM, and DBC.  
