# 99 · Glossary

English–Chinese reference for terms used across the series. Each entry links to the chapter
where the concept has its home, per [convention 1](00-index.md#writing-conventions).

> 📝 **Incomplete.** Seeded with terms already used in the written chapters; extend as new
> chapters land.

| Term | 中文 | Meaning | Home |
|---|---|---|---|
| CTA (Commodity Trading Advisor) | 商品交易顾问 | Systematic strategy trading futures across asset classes; not limited to commodities | [01](01-what-is-cta.md) |
| Absolute return | 绝对收益 | Return target independent of market direction | [01](01-what-is-cta.md) |
| Long position | 多头 | Buy low, sell higher | [01](01-what-is-cta.md) |
| Short position | 空头 | Borrow and sell, buy back lower | [01](01-what-is-cta.md) |
| Securities lending | 证券借贷 | The market that supplies borrowable shares to short sellers | [01](01-what-is-cta.md) |
| Buy-in | 强制平仓 | Lender-protective forced close of a short | [01](01-what-is-cta.md) |
| Margin | 保证金 | Collateral posted against a leveraged or short position | [01](01-what-is-cta.md) |
| Information diffusion | 信息扩散 | Candidate explanation for momentum: news spreads gradually | [01](01-what-is-cta.md) |
| Market maker | 做市商 | Liquidity provider with very short holding periods | [01](01-what-is-cta.md) |
| Noise trader | 噪音交易者 | Uninformed order flow | [01](01-what-is-cta.md) |
| OHLCV | 开高低收量 | Open, high, low, close, volume — one daily bar | [02](02-data-and-corporate-actions.md) |
| Corporate action | 公司行为 | Split, reverse split, dividend — anything that changes the price basis | [02](02-data-and-corporate-actions.md) |
| Forward split | 正向拆股 | One share becomes many; price divides | [02](02-data-and-corporate-actions.md) |
| Reverse split | 反向拆股 / 并股 | Many shares become one; price multiplies | [02](02-data-and-corporate-actions.md) |
| Back-adjustment | 复权 | Rescaling pre-event prices so the return series is continuous | [02](02-data-and-corporate-actions.md) |
| Phantom return | 假收益 | Return produced by an unadjusted corporate action, not by the market | [02](02-data-and-corporate-actions.md) |
| Bucketed bar chart | 分组柱状图 | Sort by signal, split into groups, plot mean forward return per group — the core signal test | [03](03-building-signals.md) |
| Reversal | 反转 | Extreme recent moves partially undo themselves; strongest at high frequency | [03](03-building-signals.md) |
| Skip / lag | 跳过期 | Dropping the most recent period from the lookback so reversal does not contaminate momentum | [03](03-building-signals.md) |
| EWMA | 指数加权移动平均 | Moving average weighting recent observations more heavily; tuned by half-life | [03](03-building-signals.md) |
| Half-life | 半衰期 | Periods after which an EWMA observation's weight has decayed by half | [03](03-building-signals.md) |
| Volatility clustering | 波动率聚类 | Volatility arrives in bursts, not evenly — what makes a fast signal churn | [03](03-building-signals.md) |
| Smoothing | 平滑 | Filtering the shortest cycles out of a fast signal; window must be shorter than its period | [03](03-building-signals.md) |
| Grid search | 网格搜索 | Sweeping a parameter pair exhaustively rather than guessing | [07](07-overfitting-and-robustness.md) |
| Heat map | 热力图 | 2-D view of a parameter sweep; a plateau is an edge, a spike is an artifact | [07](07-overfitting-and-robustness.md) |
| Empirical solution | 经验解 | A parameter that fit past data and carries no guarantee about the future (e.g. MACD 26/12/9) | [07](07-overfitting-and-robustness.md) |
| Demean | 去均值 | Centring a cross-sectional signal on zero so it splits into long and short sides | [04](04-from-signal-to-position.md) |
| Risk-adjusted momentum | 风险调整动量 | `Avg(r/σ)` — momentum divided by volatility so values compare across assets and regimes | [03](03-building-signals.md) |
| Rolling-rank bucketing | 滚动历史排序分组 | Rank a signal only against history strictly before `t`, avoiding look-ahead | [03](03-building-signals.md) |
| Error bar | 误差棒 | Uncertainty of a bucket's mean; what distinguishes a real bar from a 2-sample one | [03](03-building-signals.md) |
| Train / validation / test | 训练/验证/测试集 | Three-way split: form the hypothesis, choose among candidates, confirm generalization | [07](07-overfitting-and-robustness.md) |
| Autocorrelation | 自相关 | Overlapping lookback windows make adjacent momentum values non-independent | [07](07-overfitting-and-robustness.md) |
| Weak-form efficiency | 弱式有效性 | Market form under which day-of-week effects can persist | [04](04-from-signal-to-position.md) |
| Weekday effect | 周效应 | Systematic Monday/Friday return bias from funds avoiding weekend gap risk | [04](04-from-signal-to-position.md) |
| Momentum (MOM) | 动量 | Tendency of recent winners to keep winning | [04](04-from-signal-to-position.md) |
| Cross-sectional | 横截面 | Compared against other assets on the same day | [04](04-from-signal-to-position.md) |
| Weight | 权重 | Fraction of capital allocated — money, not shares | [04](04-from-signal-to-position.md) |
| Net exposure | 净敞口 | Long minus short; invariant under overlapping | [04](04-from-signal-to-position.md) |
| Gross exposure | 总敞口 | Long plus short in absolute terms; a proxy for leverage | [04](04-from-signal-to-position.md) |
| Overlapping portfolios | 重叠组合 | Jegadeesh–Titman holding-period scheme: hold 5 daily tranches at once | [04](04-from-signal-to-position.md) |
| Market-neutral | 市场中性 | Net exposure ≈ 0, so market direction is not the source of return | [04](04-from-signal-to-position.md) |
| Rebalancing | 再平衡 | Trading to restore target exposure as prices move | [04](04-from-signal-to-position.md) |
| Look-ahead bias | 前视偏差 | Using information the strategy could not have had at the time | [05](05-understanding-backtesting.md) |
| TWAP | 时间加权平均价 | Time-weighted average price; here approximated as `(open+close)/2` | [05](05-understanding-backtesting.md) |
| Slippage | 滑点 | Difference between assumed and realized fill price | [05](05-understanding-backtesting.md) |
| Turnover | 换手率 | How much of the book is traded per period | [05](05-understanding-backtesting.md) |
| Sharpe ratio | 夏普比率 | Excess return per unit of volatility | [06](06-evaluating-performance.md) |
| Drawdown | 回撤 | Decline from a running peak in the equity curve | [06](06-evaluating-performance.md) |
| Attribution | 归因 | Decomposing PnL by asset, sleeve, or leg | [06](06-evaluating-performance.md) |
| Overfitting | 过拟合 | Fitting the sample's noise rather than its structure | [07](07-overfitting-and-robustness.md) |
| Out-of-sample | 样本外 | Data not used when the strategy was chosen | [07](07-overfitting-and-robustness.md) |
| Multiple testing | 多重检验 | Trying many variants inflates the best one's apparent quality | [07](07-overfitting-and-robustness.md) |
| Survivorship bias | 幸存者偏差 | Studying only the assets that still exist today | [07](07-overfitting-and-robustness.md) |

---

[Index](00-index.md)
