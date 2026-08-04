# 02 · Data & Corporate Actions

> **This chapter answers:** what is actually in these CSV files, what the 37 tickers represent, and how a corporate action can silently destroy a backtest.
> **Prerequisites:** [01 · What Is a CTA Strategy](01-what-is-cta.md).
> **After reading you can:** validate a price dataset before trusting it, and detect an unadjusted split from the data alone.

---

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

Databento's `ohlcv-1d` data is aggregated by UTC date. Its electronic-session definition may differ from official exchange settlement or volume statistics. The prices in these CSV files are **not dividend-adjusted**, so distributions still affect cross-day comparisons.  

### 1.1 Corporate actions in this sample / 本样本中的公司行为

A split changes the price basis but not the value of the position. If pre-split rows are left at the old basis, the split date carries a **phantom return** — a jump of several hundred percent, or a clean −50% — that is an accounting artifact, not a market move. Momentum, volatility, and correlation estimates that span such a date are all corrupted by it, and a trend follower will read the artifact as the strongest signal in the sample.

**Detection.** Scan every ticker for `|close.pct_change()| > 0.4`. A genuine one-day move of that size is rare and shows up in correlated names at once; a split shows up in one ticker (or one fund family) while its peers stay flat, and the new price level persists on the following days.

#### Adjusted (fixed)

| Ticker | Action | Effective | Adjustment applied |
|---|---|---|---|
| `UNG` | 1-for-4 reverse split | 2024-01-24 | pre-split OHLC × 4, volume ÷ 4 |
| `USO` | 1-for-8 reverse split | 2020-04-29 | pre-split OHLC × 8, volume ÷ 8 |

Without this, UNG showed a phantom +300% and USO a phantom +700% on those dates. After adjustment the close series is continuous and the largest remaining one-day moves are +25.7% (UNG) and +27.4% (USO, 2020-04-21 — the real WTI-negative-price crash, which should be kept). The original unadjusted vendor files are preserved in `CTA_data/_unadjusted_raw/`; that subdirectory is deliberately **not** matched by the `*_ohlcv_1d.csv` glob used by the loaders, so it cannot be picked up by accident.

#### ⚠️ Not yet adjusted

`XLB`, `XLE`, `XLK`, `XLU`, `XLY` — all five had a **2-for-1 forward split effective 2025-12-05** and still sit at the pre-split basis. Evidence:

| Ticker | Dec 4 close | Dec 5 close | ratio |
|---|---|---|---|
| XLK | 290.98 | 146.68 | **0.5041** |
| XLE | 92.30 | 46.21 | **0.5007** |
| XLB | 88.40 | 44.10 | **0.4989** |
| XLU | 87.38 | 43.39 | **0.4966** |
| XLY | 238.39 | 119.84 | **0.5027** |
| XLF, XLV, XLI, XLP, XLRE, XLC, SPY (control) | — | — | 0.994 – 1.009 |

The five ratios sit within ±0.7% of exactly one half while the other six sector SPDRs and SPY move by less than 1% on the same day, and the halved level persists into Dec 8 — conclusive for a split rather than a sell-off. Volume is *not* a reliable tell here (XLK 0.88×, XLY 0.51× versus the prior day); use the close ratio and the persistence of the new level instead.

**Fix required:** for rows before 2025-12-05, divide OHLC by 2 and multiply volume by 2.

**Second, separate defect — the 2025-12-05 bar itself is corrupt.** On the split date the `open` and `high` were not adjusted along with `low` and `close`:

```
XLK  2025-12-05:  O=174.74  H=174.74  L=145.49  C=146.68
                  174.74 / 290.98 (prev close) = 0.60
```

That is neither the pre-split nor the post-split level — early prints at the old basis leaked into the daily aggregate. On a clean 2-for-1 split every field should land near 0.50 of the prior close; instead:

| Ticker | open / prev close | high / prev close | low, close |
|---|---|---|---|
| XLK | 0.6005 ✗ | 0.6005 ✗ | post-split ✓ |
| XLE | 0.5092 ✓ | 0.6005 ✗ | post-split ✓ |
| XLB | 0.5355 ✗ | 0.5355 ✗ | post-split ✓ |
| XLU | 0.5352 ✗ | 0.5352 ✗ | post-split ✓ |
| XLY | 0.5873 ✗ | 0.5873 ✗ | post-split ✓ |

The `high` is inflated in all five; the `open` is inflated in four (XLE's open is roughly correct, so the bad field is not identical across tickers and a single blanket rule will not cover them). Rescaling the pre-split history therefore does **not** repair this bar: it leaves XLK with a fabricated −16.1% intraday range on that day. Any signal that reads `high` or `low` — ATR, Donchian / breakout channels, intraday-range volatility — will be contaminated even after the split adjustment. Options are to clamp `open`/`high` into the range implied by `low`/`close`, or to mark that single bar `NaN` for the five tickers and let the backtest skip it (more conservative, costs one day per ticker).

The other 30 tickers show no split-sized jumps in this sample window.  

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
Run from the repository root:

```bash
python analyze_cta_data.py
```

Source: [`analyze_cta_data.py`](../analyze_cta_data.py).

The script produces the following files:  

- `output/validation_and_gap_summary.csv`: Loading status, quality checks, and the overnight-versus-intraday comparison for every ticker.  

- `output/selected_price_trends.png`: Closing-price charts for SPY, TLT, GLD, EEM, and DBC.  
