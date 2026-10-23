"""Round 2: time-series momentum (Moskowitz, Ooi and Pedersen 2012) with volatility targeting.

    T0  w_s = sign(past k-month excess return) x (40% / sigma_s) / S, rebalanced monthly
    T1  T0 x L_t, L_t = 10% / ex-ante book volatility (EWMA covariance), gross <= 3
    T2  T1 x m in the high-VIX tercile, plus a deadband on rebalance trades

Every parameter is config.ROUND2, frozen before any Round 2 number was computed. Positions are
decided at a month's last close and traded at the next close; between rebalances the engine holds
shares (an infinite deadband), so the book drifts with prices as a monthly holder's would.
"""
import numpy as np
import pandas as pd

import config as C

P = C.ROUND2


def excess_returns(close, rf):
    """Daily total-return excess over the bill rate; a missing bar carries the last close."""
    r = close.ffill().pct_change(fill_method=None)
    return r.sub(rf.reindex(r.index).fillna(0.0), axis=0)


def ewma_vol(xr, com=P["ewma_com_days"], ann=P["annualise"]):
    """Paper eq. (1): EWMA of squared demeaned daily returns, centre of mass 60 days, annualised; known by t-1."""
    return (xr.ewm(com=com, adjust=False).var(bias=True) * ann).pow(0.5).shift(1)


def month_ends(cal, start=None):
    s = pd.Series(cal, index=cal)
    me = s.groupby(cal.to_period("M")).max()
    me = pd.DatetimeIndex(me.values)
    return me[me >= pd.Timestamp(start)] if start is not None else me


def tsmom_signal(xr, k_months, md=P["month_days"]):
    """Sign of the past k-month cumulative excess return, through t."""
    n = k_months * md
    cum = np.log1p(xr).rolling(n, min_periods=n).sum()
    return np.sign(cum)


def caps(w, asset_cap=P["asset_weight_cap"], gross_cap=P["gross_cap"]):
    w = w.clip(-asset_cap, asset_cap)
    g = w.abs().sum(axis=1)
    scale = (gross_cap / g).where(g > gross_cap, 1.0)
    return w.mul(scale, axis=0)


def t0_targets(xr, sig_vol, dates, k_months=P["lookback_months"]):
    """Month-end targets of the paper's TSMOM: sign x 40% / sigma, averaged over the S assets with a signal."""
    s = tsmom_signal(xr, k_months).loc[dates]
    v = sig_vol.loc[dates]
    raw = s * (P["asset_vol_target"] / v)
    n = raw.notna().sum(axis=1).replace(0, np.nan)
    return caps(raw.div(n, axis=0).fillna(0.0))


def book_vol(w_me, xr, com=P["book_cov_com_days"], ann=P["annualise"]):
    """Ex-ante annualised volatility of each month-end book from an EWMA covariance known by t-1."""
    cov = xr.ewm(com=com, adjust=False).cov(bias=True)
    out = pd.Series(np.nan, index=w_me.index)
    rows = xr.index
    for d in w_me.index:
        i = rows.get_loc(d)
        if i == 0:
            continue
        S = cov.loc[rows[i - 1]].reindex(index=w_me.columns, columns=w_me.columns).fillna(0.0).to_numpy()
        w = w_me.loc[d].to_numpy()
        out.loc[d] = float(np.sqrt(max(w @ S @ w, 0.0) * ann))
    return out


def t1_targets(w0, xr, target=P["book_vol_target"]):
    """T0 levered to the book volatility target; returns (targets, leverage applied before the caps)."""
    bv = book_vol(w0, xr)
    lev = (target / bv).replace([np.inf, -np.inf], np.nan).fillna(1.0)
    return caps(w0.mul(lev, axis=0)), lev


def t2_targets(w1, regime_high, m):
    """T1 with its leverage multiplied by m on month-ends in the high-VIX tercile."""
    mult = pd.Series(np.where(regime_high.reindex(w1.index).fillna(False), m, 1.0), index=w1.index)
    return caps(w1.mul(mult, axis=0))


def daily_weights(w_me, cal):
    """Month-end targets carried to every day until the next month-end; zero before the first."""
    return w_me.reindex(cal).ffill().fillna(0.0)


def rebalance_deadband(w_me, cal, lag=C.LAG, trade_deadband=0.0):
    """Infinite deadband (hold shares) except on each month-end's fill row, which gets trade_deadband."""
    db = pd.Series(np.inf, index=cal)
    pos = cal.get_indexer(w_me.index) + lag
    pos = pos[(pos >= 0) & (pos < len(cal))]
    db.iloc[pos] = trade_deadband
    return db


def overlap_months(w_me, h):
    """Holding h months as h overlapping monthly tranches (Jegadeesh-Titman), as the paper does."""
    return w_me.rolling(h, min_periods=1).mean() if h > 1 else w_me


def t3_targets(w0_me, xr, cal, high_daily, m, start, end, target=P["book_vol_target"]):
    """T3: T0's monthly directions and per-asset sizing, with the book leverage and the high-VIX
    multiplier re-set every day from information known at that close.

    Added after the pre-Test regime analysis (ROUND2.md, amendment 1): the high-VIX losses were
    contemporaneous, so a month-end leverage decision reacts too late.
    """
    w0d = daily_weights(w0_me, cal)
    days = cal[(cal >= pd.Timestamp(start)) & (cal <= pd.Timestamp(end))]
    bv = book_vol(w0d.loc[days], xr)
    lev = (target / bv).replace([np.inf, -np.inf], np.nan).fillna(1.0)
    w = caps(w0d.loc[days].mul(lev, axis=0))
    mult = pd.Series(np.where(high_daily.reindex(days).fillna(False), m, 1.0), index=days)
    w = caps(w.mul(mult, axis=0))
    out = pd.DataFrame(0.0, index=cal, columns=w0d.columns)
    out.loc[days] = w
    return out, lev
