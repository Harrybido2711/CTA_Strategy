"""Shared access to CTA_data/ for the figures that plot measurements.

Most figures in docs/ are schematics and should stay that way — the shape is
the point, and inventing the numbers keeps it legible. This module exists for
the minority whose claim *is* about this dataset, so that every one of them
loads the same panel, repaired the same way.

Change a default here and every measured figure moves together, exactly as
_style.py does for colour.
"""

import glob
import os

import numpy as np
import pandas as pd

from _style import DATA

# The five sector SPDRs carry an unadjusted 2-for-1 split (docs/chapters/100_dataset/).
# Halving every pre-split close makes the series continuous; without it those
# tickers print a -69% "return" on the day and poison every pooled statistic.
SPLIT_DATE = pd.Timestamp("2025-12-05", tz="UTC")
SPLIT_TICKERS = ("XLB", "XLE", "XLK", "XLU", "XLY")


def load_returns():
    """Daily log returns for the 37 ETFs, split-repaired.

    One column per ticker, indexed by date. Close-to-close, not
    dividend-adjusted — see docs/chapters/100_dataset/ for what that costs.
    """
    closes = {}
    for path in sorted(glob.glob(str(DATA / "*_ohlcv_1d.csv"))):
        ticker = os.path.basename(path).split("_")[0]
        frame = pd.read_csv(path, usecols=["ts_event", "close"], parse_dates=["ts_event"])
        closes[ticker] = frame.set_index("ts_event")["close"]

    px = pd.DataFrame(closes).sort_index()
    for ticker in SPLIT_TICKERS:
        px.loc[px.index < SPLIT_DATE, ticker] /= 2.0
    return np.log(px).diff()


def momentum_panel(lookback=21, vol_window=63, gap=0):
    """The chapter's running signal, and the return it is scored on.

    Risk-adjusted momentum: the mean of the ``lookback`` returns ending at t-1,
    divided by a trailing ``vol_window`` volatility also ending at t-1, so
    nothing in the signal is unknowable at t. It is paired with the return
    ``gap`` days later — gap 0 being the next session.
    """
    rets = load_returns()
    mom = rets.rolling(lookback).mean().shift(1)
    vol = rets.rolling(vol_window).std().shift(1)
    return mom / vol, rets.shift(-gap)


def pooled(signal, forward, n_buckets=5):
    """Stack a (signal, forward) panel into aligned x, y and bucket arrays.

    Each date is ranked against **that asset's own history**, which is the
    scoring rule of 02 § 4 and keeps every bucket a set of dates rather than a
    set of assets. y is returned in basis points.
    """
    rank = signal.rank(pct=True)
    bucket = np.ceil(rank * n_buckets).clip(1, n_buckets)

    x, y, g = signal.stack(), forward.stack(), bucket.stack()
    idx = x.index.intersection(y.index).intersection(g.index)
    x, y, g = x.loc[idx], y.loc[idx], g.loc[idx]

    keep = np.isfinite(x) & np.isfinite(y) & np.isfinite(g)
    return x[keep].to_numpy(), y[keep].to_numpy() * 1e4, g[keep].to_numpy().astype(int)


def bucket_stats(y, g, n_buckets=5):
    """Mean, standard error and count for each bucket, lowest signal first."""
    means, errs, counts = [], [], []
    for k in range(1, n_buckets + 1):
        vals = y[g == k]
        means.append(vals.mean())
        errs.append(vals.std(ddof=1) / len(vals) ** 0.5)
        counts.append(len(vals))
    return np.array(means), np.array(errs), np.array(counts)
