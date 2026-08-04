# 02 · Data & Corporate Actions

> **Answers:** what is in these CSV files, what the 37 tickers represent, and how a corporate action silently destroys a backtest.
> **Prerequisites:** [01 · What Is a CTA Strategy](01-what-is-cta.md).
> **After reading:** validate a price dataset before trusting it, and detect an unadjusted split from the data alone.

---

## 1. Files and Fields

Each `TICKER_ohlcv_1d.csv` holds daily OHLCV bars for one ETF; `1d` means one row per daily bar.

| Field                                          | Meaning                                                                                                     |
| ---------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| `ts_event`                                   | Timestamp of the bar, in**UTC**                                                                       |
| `open` / `high` / `low` / `close`      | First / highest / lowest / last eligible trade price in the bar                                             |
| `volume`                                     | Quantity traded, in**ETF shares, not dollars**. `close × volume` only approximates dollar turnover |
| `symbol`                                     | Ticker                                                                                                      |
| `rtype`, `publisher_id`, `instrument_id` | Vendor metadata — ignore                                                                                   |

Databento's `ohlcv-1d` is aggregated by UTC date, and its electronic-session definition may differ
from official exchange settlement or volume statistics. Prices are **not dividend-adjusted**, so
distributions still affect cross-day comparisons.

### 1.1 Corporate actions in this sample / 本样本中的公司行为

A split changes the price basis, not the value of the position. Leave pre-split rows at the old
basis and the split date carries a **phantom return** — several hundred percent, or a clean −50% —
that is an accounting artifact. Momentum, volatility, and correlation estimates spanning that date
are corrupted, and a trend follower reads the artifact as the strongest signal in the sample.

**Detection.** Scan every ticker for `|close.pct_change()| > 0.4`. A genuine move that size shows up
in correlated names at once; a split hits one ticker (or one fund family) while peers stay flat, and
the new price level persists. Rule of thumb: past **10%** is worth re-checking, and for a broad ETF
past **50–60%** is almost certainly a corporate action rather than the market.

**Provenance.** The corrected UNG and USO files came from the course's replacement (aggregated,
back-adjusted) data. The two tickers' split factors differ — verify rather than assume.

#### Adjusted (fixed)

| Ticker  | Action                | Effective  | Adjustment applied               |
| ------- | --------------------- | ---------- | -------------------------------- |
| `UNG` | 1-for-4 reverse split | 2024-01-24 | pre-split OHLC × 4, volume ÷ 4 |
| `USO` | 1-for-8 reverse split | 2020-04-29 | pre-split OHLC × 8, volume ÷ 8 |

Unadjusted, UNG showed a phantom +300% and USO +700%. After adjustment the close series is
continuous, and the largest remaining one-day moves are +25.7% (UNG) and +27.4% (USO on 2020-04-21 —
the real WTI-negative-price crash, which should be kept). Originals are preserved in
`CTA_data/_unadjusted_raw/`, deliberately outside the `*_ohlcv_1d.csv` glob so the loaders cannot
pick them up.

#### ⚠️ Not yet adjusted

`XLB`, `XLE`, `XLK`, `XLU`, `XLY` all had a **2-for-1 forward split effective 2025-12-05** and remain
at the pre-split basis:

| Ticker                                       | Dec 4 close | Dec 5 close | ratio            |
| -------------------------------------------- | ----------- | ----------- | ---------------- |
| XLK                                          | 290.98      | 146.68      | **0.5041** |
| XLE                                          | 92.30       | 46.21       | **0.5007** |
| XLB                                          | 88.40       | 44.10       | **0.4989** |
| XLU                                          | 87.38       | 43.39       | **0.4966** |
| XLY                                          | 238.39      | 119.84      | **0.5027** |
| XLF, XLV, XLI, XLP, XLRE, XLC, SPY (control) | —          | —          | 0.994 – 1.009   |

All five sit within ±0.7% of exactly one half while the other six sector SPDRs and SPY move under 1%
that day, and the halved level persists into Dec 8 — conclusive for a split. Volume is *not* a
reliable tell (XLK 0.88×, XLY 0.51×); use the close ratio and the persistence of the new level.

**Fix required:** for rows before 2025-12-05, divide OHLC by 2 and multiply volume by 2.

**Second, separate defect — the 2025-12-05 bar itself is corrupt.** `open` and `high` were not
adjusted along with `low` and `close`:

```
XLK  2025-12-05:  O=174.74  H=174.74  L=145.49  C=146.68
                  174.74 / 290.98 (prev close) = 0.60
```

Neither the pre- nor post-split level — early prints at the old basis leaked into the aggregate. On
a clean 2-for-1 every field should land near 0.50 of the prior close:

| Ticker | open / prev close | high / prev close | low, close    |
| ------ | ----------------- | ----------------- | ------------- |
| XLK    | 0.6005 ✗         | 0.6005 ✗         | post-split ✓ |
| XLE    | 0.5092 ✓         | 0.6005 ✗         | post-split ✓ |
| XLB    | 0.5355 ✗         | 0.5355 ✗         | post-split ✓ |
| XLU    | 0.5352 ✗         | 0.5352 ✗         | post-split ✓ |
| XLY    | 0.5873 ✗         | 0.5873 ✗         | post-split ✓ |

`high` is inflated in all five, `open` in four — so no single blanket rule covers them. Rescaling the
pre-split history does **not** repair this bar; XLK keeps a fabricated −16.1% intraday range. Any
signal reading `high`/`low` — ATR, Donchian channels, intraday-range volatility — stays contaminated.
Either clamp `open`/`high` into the range implied by `low`/`close`, or mark the bar `NaN` for those
five and let the backtest skip it (more conservative, costs one day per ticker).

The other 30 tickers show no split-sized jumps in this window.

## 2. Meaning of the 37 Datasets

| Category / 类别                    | Ticker | Exposure / 主要敞口                                                                |
| ---------------------------------- | ------ | ---------------------------------------------------------------------------------- |
| U.S. broad equity / 美国宽基股票   | SPY    | S&P 500 Index / 标普 500 指数                                                      |
|                                    | QQQ    | Nasdaq-100 Index / 纳斯达克 100 指数                                               |
|                                    | IWM    | Russell 2000 small-cap stocks / Russell 2000 美国小盘股                            |
|                                    | DIA    | Dow Jones Industrial Average / 道琼斯工业平均指数                                  |
|                                    | MDY    | S&P MidCap 400 stocks / 标普 400 中盘股                                            |
| U.S. equity sectors / 美国行业股票 | XLK    | Technology / 科技                                                                  |
|                                    | XLF    | Financials / 金融                                                                  |
|                                    | XLE    | Energy / 能源                                                                      |
|                                    | XLV    | Health care / 医疗保健                                                             |
|                                    | XLI    | Industrials / 工业                                                                 |
|                                    | XLY    | Consumer discretionary / 非必需消费品                                              |
|                                    | XLP    | Consumer staples / 必需消费品                                                      |
|                                    | XLU    | Utilities / 公用事业                                                               |
|                                    | XLB    | Materials / 原材料                                                                 |
|                                    | XLRE   | Real estate / 房地产                                                               |
|                                    | XLC    | Communication services / 通信服务                                                  |
| International equity / 国际股票    | EFA    | Developed markets excluding the U.S. and Canada / 美国、加拿大以外的发达市场       |
|                                    | EEM    | Emerging markets / 新兴市场                                                        |
|                                    | VGK    | European equities / 欧洲股票                                                       |
|                                    | EWJ    | Japanese equities / 日本股票                                                       |
|                                    | FXI    | Large-cap Chinese equities / 中国大型股                                            |
| Fixed income / 固定收益            | TLT    | U.S. Treasury bonds with maturities above 20 years / 20 年以上美国国债             |
|                                    | IEF    | 7–10 year U.S. Treasury bonds / 7–10 年美国国债                                  |
|                                    | SHY    | 1–3 year U.S. Treasury bonds / 1–3 年美国国债                                    |
|                                    | AGG    | Broad U.S. investment-grade bond market / 美国投资级综合债券市场                   |
|                                    | LQD    | U.S. dollar investment-grade corporate bonds / 美元投资级公司债                    |
|                                    | HYG    | U.S. dollar high-yield corporate bonds / 美元高收益公司债                          |
|                                    | TIP    | U.S. Treasury Inflation-Protected Securities / 美国通胀保值国债（TIPS）            |
| Commodities / 商品                 | GLD    | Gold / 黄金                                                                        |
|                                    | SLV    | Silver / 白银                                                                      |
|                                    | DBC    | Diversified commodity futures / 多元商品期货组合                                   |
|                                    | USO    | Crude-oil futures exposure, not spot oil / 原油期货敞口，并非原油现货价格          |
|                                    | UNG    | Natural-gas futures exposure, not spot gas / 天然气期货敞口，并非天然气现货价格    |
|                                    | DBA    | Agricultural commodity futures / 农产品期货组合                                    |
| Alternatives / 其他或另类资产      | VNQ    | U.S. real estate investment trusts (REITs) / 美国房地产投资信托（REITs）           |
|                                    | GDX    | Global gold-mining company equities / 全球金矿公司股票                             |
|                                    | UUP    | Long U.S. dollar exposure against a currency basket / 美元相对一篮子货币走强的敞口 |

## 3. Overnight Versus Intraday Movement

- Absolute overnight movement: `abs(Open[t] - Close[t-1])`
- Absolute intraday movement: `abs(Close[t] - Open[t])`

Both are reported in dollars and percent; percent is the right comparison across ETFs at different
price levels. Note that average absolute movement is **not** cumulative return contribution — testing
whether returns are realized overnight needs *signed* returns, with dividends and splits handled.

### Results for This Dataset

- All 37 files passed checks for required fields, numeric types, missing values, duplicate timestamps, chronological order, OHLC consistency, and manifest row counts.
- Under both definitions only **FXI (1 of 37)** has larger average absolute overnight than intraday movement. The other 36 are intraday-dominated.
- So for 2020-01-02 → 2026-06-29, the absolute-movement test does **not** support the claim that overnight moves are usually larger. The "returns happen overnight" claim may refer to signed cumulative contribution, a different hypothesis.
- SPY's mean signed returns here are ≈ `0.0133%`/day overnight and `0.0453%`/day intraday — not overnight-dominated either. Results depend on sample period, session definition, corporate actions, and adjustment method.

## 4. How to Run the Analysis

Python 3.9+ with `pandas` and `matplotlib`, from the repository root:

```bash
python analyze_cta_data.py
```

Source: [`analyze_cta_data.py`](../analyze_cta_data.py). Outputs:

- `output/validation_and_gap_summary.csv` — load status, quality checks, and the overnight-vs-intraday comparison per ticker.
- `output/selected_price_trends.png` — closing-price charts for SPY, TLT, GLD, EEM, DBC.

---

## Next → [03 · Building Your Own Signal](03-building-signals.md)

Before moving on, **run the validation and find the defects yourself**:

```bash
python ../analyze_cta_data.py
```

Then scan every ticker for `|close.pct_change()| > 0.4` and confirm you land on the five SPDRs that
are still unadjusted. Chapter 03 builds a signal on this data — anything you miss here propagates.

You should be able to explain:

- [ ] Which two tickers were fixed, which five are not, and what a phantom return is
- [ ] Why volume is not a reliable split tell (XLK 0.88×, XLY 0.51×)
- [ ] Why the 2025-12-05 bar stays corrupt even after a split adjustment

[← 01](01-what-is-cta.md) · [Index](00-index.md)
