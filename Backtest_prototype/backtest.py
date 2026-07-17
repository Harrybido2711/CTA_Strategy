"""
Multi-asset momentum backtester.

Pipeline
--------
1. Single-asset backtester (`backtester`): turns a time-varying target *dollar*
   exposure into shares, simulates trading at an approximate TWAP, and returns
   the cumulative PnL contribution of that one asset.
2. Multi-asset backtester (`multi_asset_backtester`): the simplest possible
   extension -- just LOOP the single-asset backtester over every asset, each
   with its own dollar series, and sum the per-asset PnL contributions.
3. Momentum signal: past ~1 month (21 trading days) average daily return.
4. Two long/short portfolios rebalanced with a 5-trading-day holding period,
   implemented as *overlapping* portfolios (see `overlap_weights`).

Run:  python backtest.py
"""

import os
import glob
from datetime import timedelta

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Repo root = one level above this file (Backtest_prototype/).
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "CTA_data")

# Strategy parameters.
LOOKBACK = 21   # trading days used for the momentum signal (~1 month)
HOLD = 5        # holding period in trading days (~1 week)
CAPITAL = 1.0   # 1 unit of capital; all PnL is expressed per unit of capital


# --------------------------------------------------------------------------- #
# 1. Single-asset backtester  (unchanged logic from backtester.ipynb)
# --------------------------------------------------------------------------- #
def backtester(data, dollar, delay=timedelta(days=1)):
    """Simulate one asset given a target dollar exposure over time.

    Parameters
    ----------
    data   : DataFrame with columns ts_event, open, high, low, close, ...
    dollar : DataFrame with columns ts_event, dollar (desired $ exposure;
             +long / -short / 0 flat). Signed dollar exposure per date.
    delay  : execution delay applied to the signal (default one calendar day).

    Returns a DataFrame; the `portfolio` column is this asset's cumulative
    PnL contribution (it starts near 0, because buying spends cash equal to
    the position value).
    """
    dollar = dollar.copy()
    data = data.copy()

    # A signal dated t only becomes tradable after `delay`.
    dollar["ts_event"] = dollar["ts_event"] + delay
    df = pd.merge_asof(left=data, right=dollar, on="ts_event", direction="backward")

    df["target_shrs"] = df["dollar"] / df["close"]   # shares the strategy wants
    df["curr_shrs"] = df["target_shrs"].shift()       # held after 1-row exec lag
    df["traded_shrs"] = df["curr_shrs"].diff().combine_first(df["curr_shrs"])
    df["TWAP"] = df["open"] / 2 + df["close"] / 2      # approx execution price
    df["cash_spend"] = df["traded_shrs"] * df["TWAP"]
    df["net_cash"] = df["cash_spend"].cumsum() * (-1)
    df["asset_value"] = df["curr_shrs"] * df["close"]
    df["portfolio"] = df["net_cash"] + df["asset_value"]
    return df


# --------------------------------------------------------------------------- #
# 2. Data loading
# --------------------------------------------------------------------------- #

# a dictionary of the ticker is returned key: name of the ticker; value: <DataFrame>
def load_assets(data_dir=DATA_DIR):
    """Load every *_ohlcv_1d.csv into a dict {ticker: OHLCV DataFrame}."""
    files = sorted(glob.glob(os.path.join(data_dir, "*_ohlcv_1d.csv")))
    asset_data = {}
    for f in files:
        ticker = os.path.basename(f).split("_")[0]
        d = pd.read_csv(f)
        d["ts_event"] = pd.to_datetime(d["ts_event"])
        asset_data[ticker] = d[["ts_event", "open", "high", "low", "close",
                                 "volume", "symbol"]].sort_values("ts_event")
    return asset_data 
    


def close_matrix(asset_data):
    """Wide DataFrame of close prices, index=date, columns=tickers.

    Assets with missing dates simply carry NaN there; downstream rolling and
    weight logic handle NaN so mismatched calendars are fine.
    """
    close = pd.DataFrame({tk: d.set_index("ts_event")["close"]
                          for tk, d in asset_data.items()})
    return close.sort_index()


# --------------------------------------------------------------------------- #
# 3. Momentum signal
# --------------------------------------------------------------------------- #
def momentum(close, lookback=LOOKBACK):
    """Signal = trailing `lookback`-day mean of daily returns, per asset."""
    daily_ret = close.pct_change()
    return daily_ret.rolling(lookback).mean()


# --------------------------------------------------------------------------- #
# 4. Portfolio construction (target weights BEFORE the holding-period overlap)
# --------------------------------------------------------------------------- #
def target_weights_p1(mom):
    """Portfolio 1: Long 150% of the positive-MOM assets (equal weight),
    short 50% of the negative-MOM assets (equal weight).

    Each day: net exposure = +1.5 - 0.5 = +1.0, gross = 2.0.
    """
    pos = mom > 0
    neg = mom < 0
    n_pos = pos.sum(axis=1).replace(0, np.nan)   # avoid divide-by-zero
    n_neg = neg.sum(axis=1).replace(0, np.nan)

    long_w = pos.astype(float).div(n_pos, axis=0) * 1.5
    short_w = neg.astype(float).div(n_neg, axis=0) * (-0.5)
    return long_w.add(short_w, fill_value=0.0).fillna(0.0)


def target_weights_p2(mom):
    """Portfolio 2: equal-magnitude weights whose SIGN comes from each asset's
    momentum *relative to the cross-section*.

    An asset is held long if its MOM is at/above the cross-sectional MEDIAN that
    day, otherwise short -- so an asset can be shorted even with positive MOM,
    exactly as in the brief (MOM 10% / 5% / 1% -> +66% / +66% / -66%). Median is
    used because it reproduces that 2-long / 1-short example; the mean would give
    1-long / 2-short. Each leg gets magnitude 2/N, so gross ~= 2.0 and the book
    is roughly market-neutral.
    """
    valid = mom.notna()
    n = valid.sum(axis=1)                       # assets with a signal that day
    med = mom.median(axis=1)
    rel = mom.sub(med, axis=0)                  # momentum relative to the median
    sign = rel.ge(0).astype(float) * 2 - 1      # +1 if >= median else -1
    w = sign.mul(2.0).div(n, axis=0)            # equal magnitude 2/N
    return w.where(valid, 0.0)


def overlap_weights(target, hold=HOLD):
    """Convert daily target weights into actually-held weights for a `hold`-day
    holding period, using OVERLAPPING portfolios (Jegadeesh-Titman style).

    Each day we commit 1/hold of the book to that day's fresh target and hold it
    for `hold` days. So the weight actually held on day t is the average of the
    last `hold` daily targets:

        held_weight[t] = mean(target[t], target[t-1], ..., target[t-hold+1])

    This is the answer to "how do the weights change under a 5-day hold": they
    do NOT jump every 5th day; they evolve smoothly as old signals roll off and
    new ones roll on, which also cuts turnover. Note gross exposure can fall
    below the single-day target when longs/shorts from different days offset.
    """
    return target.rolling(hold).mean()


# --------------------------------------------------------------------------- #
# 5. Multi-asset backtester  (the LOOP)
# --------------------------------------------------------------------------- #
def multi_asset_backtester(asset_data, weights, capital=CAPITAL,
                           delay=timedelta(days=1)):
    """Loop the single-asset backtester over every column of `weights`.

    `weights` is a wide DataFrame (index=date, columns=tickers) of held weights.
    Returns (total_pnl, contributions) where total_pnl is the summed per-asset
    PnL and contributions is the per-asset PnL DataFrame.
    """
    contributions = {}
    for ticker in weights.columns:
        dollar = pd.DataFrame({"ts_event": weights.index,
                               "dollar": weights[ticker].values * capital})
        res = backtester(asset_data[ticker], dollar, delay=delay)
        contributions[ticker] = res.set_index("ts_event")["portfolio"]

    contributions = pd.DataFrame(contributions)
    total_pnl = contributions.sum(axis=1)
    return total_pnl, contributions


# --------------------------------------------------------------------------- #
# 6. Performance reporting
# --------------------------------------------------------------------------- #
def perf_stats(pnl):
    """Summary stats for a cumulative-PnL series (per unit capital)."""
    r = pnl.diff().dropna()
    ann_ret = r.mean() * 252
    ann_vol = r.std() * np.sqrt(252)
    sharpe = ann_ret / ann_vol if ann_vol > 0 else np.nan
    max_dd = (pnl - pnl.cummax()).min()
    return pd.Series({"final_PnL": pnl.dropna().iloc[-1],
                      "ann_return": ann_ret,
                      "ann_vol": ann_vol,
                      "sharpe": sharpe,
                      "max_drawdown": max_dd})


def main():
    asset_data = load_assets()
    close = close_matrix(asset_data)
    print(f"Loaded {close.shape[1]} assets, {close.shape[0]} dates "
          f"({close.index.min().date()} -> {close.index.max().date()})")

    mom = momentum(close)

    # Target weights, then apply the 5-day overlapping hold.
    w1 = overlap_weights(target_weights_p1(mom))
    w2 = overlap_weights(target_weights_p2(mom))

    # Sanity check on exposures (last row).
    print(f"P1 gross~{w1.abs().sum(1).dropna().iloc[-1]:.2f} "
          f"net~{w1.sum(1).dropna().iloc[-1]:.2f} | "
          f"P2 gross~{w2.abs().sum(1).dropna().iloc[-1]:.2f} "
          f"net~{w2.sum(1).dropna().iloc[-1]:.2f}")

    port1, _ = multi_asset_backtester(asset_data, w1)
    port2, _ = multi_asset_backtester(asset_data, w2)

    summary = pd.DataFrame({"Portfolio 1 (150/50)": perf_stats(port1),
                            "Portfolio 2 (relative MOM)": perf_stats(port2)})
    print("\n" + summary.round(4).to_string())

    # SPY buy & hold benchmark.
    spy = asset_data["SPY"].set_index("ts_event")["close"]
    spy_bh = spy / spy.iloc[0] - 1

    _, ax = plt.subplots(figsize=(11, 5))
    ax.plot(port1.index, port1.values, label="Portfolio 1: Long 150% / Short 50%")
    ax.plot(port2.index, port2.values, label="Portfolio 2: Relative MOM (neutral)")
    ax.plot(spy_bh.index, spy_bh.values, label="SPY buy & hold", alpha=0.5, ls="--")
    ax.axhline(0, color="k", lw=0.5)
    ax.set_title("Multi-Asset Momentum Backtest (21d signal, 5d overlapping hold)")
    ax.set_ylabel("Cumulative PnL per unit capital")
    ax.legend()
    plt.tight_layout()

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "momentum_backtest.png")
    plt.savefig(out, dpi=120)
    print(f"\nSaved plot -> {out}")


if __name__ == "__main__":
    main()
