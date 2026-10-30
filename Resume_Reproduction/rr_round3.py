"""Round 3 (ROUND3.md): regime measures under the dynamic cut D, and the learning-path pipeline.

Part A pieces live here: the D percentile and tercile, the per-asset and market measures of A1,
the exact holding-month return of a month-end position, and A8's turnover decomposition.
Everything a label at date t uses is known at the close of t (indices, correlation) or of t - 1
(per-asset volume and volatility, as rr_regimes defines them).
"""
import numpy as np
import pandas as pd

import config as C
import rr_data as D
import rr_regimes as R
import rr_tsmom as T

P3 = C.ROUND3
P2 = C.ROUND2
LABELS = R.LABELS
BONDS = [t for t, c in C.UNIVERSE_CATEGORY.items() if c == "bonds"]


# ----------------------------------------------------------------------------- the cut
def d_pct(x, n=P3["rank_window"], minp=P3["rank_min_periods"]):
    """D: percentile of today's value among the trailing n days, today included."""
    return x.rolling(n, min_periods=minp).rank(pct=True)


def d_tercile(pct):
    """0 / 1 / 2 = low / mid / high at the 1/3 and 2/3 percentiles; NaN where pct is NaN."""
    lab = np.where(pct <= 1 / 3, 0, np.where(pct <= 2 / 3, 1, 2))
    if isinstance(pct, pd.DataFrame):
        return pd.DataFrame(lab, index=pct.index, columns=pct.columns).where(pct.notna())
    return pd.Series(lab, index=pct.index).where(pct.notna())


# ----------------------------------------------------------------------------- A1 measures
def avg_pairwise_corr(xr, n=P3["corr_window"]):
    """Mean off-diagonal correlation of daily excess returns over the trailing n days, through t."""
    a = xr.to_numpy()
    out = np.full(len(a), np.nan)
    for i in range(n - 1, len(a)):
        blk = a[i - n + 1:i + 1]
        keep = np.isfinite(blk).sum(axis=0) >= n - 5
        if keep.sum() < 10:
            continue
        c = pd.DataFrame(blk[:, keep]).corr().to_numpy()
        k = c.shape[0]
        out[i] = (np.nansum(c) - k) / (k * (k - 1))
    return pd.Series(out, index=xr.index, name="avg_corr")


def ewma_sigma(xr, com):
    """Annualised EWMA volatility through t - 1 (the paper's estimator at another centre of mass)."""
    return T.ewma_vol(xr, com=com)


def measures(wd, xr):
    """A1, as daily frames: per-asset percentiles and terciles, and the market-wide series."""
    vol = D.panel(wd.etfs, "volume", wd.cal)
    v_pct = d_pct(R.volume_measure(vol, P3["measure_window"]))
    s_pct = d_pct(R.sigma_measure(wd.close, P3["measure_window"]))
    vix, _ = D.load_index("VIX", wd.cal)
    move, _ = D.load_index("MOVE", wd.cal)
    vix_pct, move_pct = d_pct(vix), d_pct(move)
    idx_pct = pd.DataFrame({t: (move_pct if t in BONDS else vix_pct) for t in wd.close.columns})
    mkt_vol_pct = d_pct(v_pct.mean(axis=1))
    corr = avg_pairwise_corr(xr)
    corr_pct = d_pct(corr)
    fast, slow = ewma_sigma(xr, P3["sigma_fast_com"]), ewma_sigma(xr, P3["sigma_slow_com"])
    return {
        "V_pct": v_pct, "sigma_pct": s_pct, "index_pct": idx_pct,
        "V_lab": d_tercile(v_pct), "sigma_lab": d_tercile(s_pct), "index_lab": d_tercile(idx_pct),
        "VIX": vix, "MOVE": move, "VIX_pct": vix_pct, "MOVE_pct": move_pct,
        "VIX_lab": d_tercile(vix_pct), "MOVE_lab": d_tercile(move_pct),
        "mkt_volume_pct": mkt_vol_pct, "mkt_volume_lab": d_tercile(mkt_vol_pct),
        "corr": corr, "corr_pct": corr_pct, "corr_lab": d_tercile(corr_pct),
        "sigma_fast": fast, "sigma_slow": slow,
    }


def trend_z(xr, sig_vol, k_months, md=P2["month_days"]):
    """k-month cumulative excess log return over sigma x sqrt(k / 12), through t (sigma through t - 1)."""
    n = k_months * md
    cum = np.log1p(xr).rolling(n, min_periods=n).sum()
    return cum / (sig_vol * np.sqrt(k_months / 12.0))


# ----------------------------------------------------------------------------- holding months
def holding_rows(cal, me, lag=C.LAG):
    """For each month-end F, the calendar rows whose daily return the position formed at F earns.

    The fill is at close F + lag; the position is held until the fill after the next month-end.
    Daily return at row j is close_j / close_{j-1} - 1, so the rows are pos(F)+lag+1 .. pos(F')+lag.
    The last month-end has no F' and gets no rows.
    """
    pos = cal.get_indexer(me)
    out = {}
    for i, f in enumerate(me[:-1]):
        a, b = pos[i] + lag + 1, pos[i + 1] + lag
        if b < len(cal):
            out[f] = np.arange(a, b + 1)
    return out


def holding_return(xr, cal, me, lag=C.LAG):
    """Compounded daily excess return of every asset over each month-end's holding month."""
    rows = holding_rows(cal, me, lag)
    a = xr.to_numpy()
    out = pd.DataFrame(np.nan, index=me, columns=xr.columns)
    for f, r in rows.items():
        blk = a[r]
        g = np.prod(1.0 + np.nan_to_num(blk), axis=0) - 1.0
        g[np.isnan(blk).all(axis=0)] = np.nan
        out.loc[f] = g
    return out


def book_holding_return(x_daily, cal, me, lag=C.LAG):
    """Sum of a book's daily excess PnL over each month-end's holding month ($1 of capital, additive)."""
    rows = holding_rows(cal, me, lag)
    v = x_daily.reindex(cal).to_numpy()
    return pd.Series({f: float(np.nansum(v[r])) for f, r in rows.items()})


# ----------------------------------------------------------------------------- A8 turnover sources
def turnover_sources_t0(sign, a, w0):
    """Split T0's month-end weight changes into flips, entries/exits, sizing, 1/S and the caps.

    w0 = caps(sign x a / S). The path from one month-end to the next changes, in order, the sign,
    the size a = 40%/sigma, the count S, then the caps; the parts sum exactly to w0_t - w0_{t-1}.
    Returns one row per month-end with the L1 norm of each part and of the actual change.
    """
    valid = sign.notna() & a.notna()                           # T0's S counts exactly these
    s = sign.where(valid).fillna(0.0)
    aa = a.where(valid).fillna(0.0)
    n = valid.sum(axis=1).astype(float).replace(0, np.nan).ffill().bfill()
    rows = []
    for i in range(1, len(w0)):
        s0, s1 = s.iloc[i - 1], s.iloc[i]
        a0, a1 = aa.iloc[i - 1], aa.iloc[i]
        n0, n1 = n.iloc[i - 1], n.iloc[i]
        flip = (s0 != 0) & (s1 != 0) & (s0 != s1)
        entry = (s0 == 0) != (s1 == 0)
        a_ref = a0.where(s0 != 0, a1)                           # an entry is sized at its new size
        d_sign = (s1 - s0) * a_ref / n0
        d_size = s1 * (a1 - a_ref) / n0
        d_count = s1 * a1 / n1 - s1 * a1 / n0
        uc0, uc1 = s0 * a0 / n0, s1 * a1 / n1
        d_cap = (w0.iloc[i] - uc1) - (w0.iloc[i - 1] - uc0)
        actual = w0.iloc[i] - w0.iloc[i - 1]
        rows.append({"date": w0.index[i],
                     "sign_flip": float(d_sign[flip].abs().sum()), "entry_exit": float(d_sign[entry].abs().sum()),
                     "sizing": float(d_size.abs().sum()), "count_1_over_S": float(d_count.abs().sum()),
                     "caps": float(d_cap.abs().sum()), "actual": float(actual.abs().sum()),
                     "check": float((d_sign + d_size + d_count + d_cap - actual).abs().max())})
    return pd.DataFrame(rows).set_index("date")


def turnover_sources_t1(w0, lev, w1):
    """T1 = caps(L x T0). Split its change into T0's own change at the old leverage, the leverage
    change, and T1's caps; the parts sum exactly to w1_t - w1_{t-1}."""
    rows = []
    for i in range(1, len(w1)):
        l0, l1 = lev.iloc[i - 1], lev.iloc[i]
        d_book = l0 * (w0.iloc[i] - w0.iloc[i - 1])
        d_lev = (l1 - l0) * w0.iloc[i]
        d_cap = (w1.iloc[i] - l1 * w0.iloc[i]) - (w1.iloc[i - 1] - l0 * w0.iloc[i - 1])
        actual = w1.iloc[i] - w1.iloc[i - 1]
        rows.append({"date": w1.index[i], "T0_change_at_old_leverage": float(d_book.abs().sum()),
                     "leverage": float(d_lev.abs().sum()), "caps": float(d_cap.abs().sum()),
                     "actual": float(actual.abs().sum()),
                     "check": float((d_book + d_lev + d_cap - actual).abs().max())})
    return pd.DataFrame(rows).set_index("date")


# ----------------------------------------------------------------------------- inference
def month_mean_se(panel_y, mask=None, nw_lag=1):
    """Equal-weight each month: cross-sectional mean per month, then mean and NW SE across months."""
    import rr_metrics as M
    y = panel_y if mask is None else panel_y.where(mask)
    d = y.mean(axis=1).dropna()
    se = M.newey_west_se(d, nw_lag) if len(d) > 2 else np.nan
    return d, (float(d.mean()) if len(d) else np.nan), se


def block_bootstrap_ci(d, blocks=(1, 3, 6), n_draws=4000, level=0.90):
    """Stationary-bootstrap CI of a monthly series' mean at several mean block lengths; the widest."""
    import rr_metrics as M
    x = np.asarray(d, dtype=float)
    out = {}
    for bl in blocks:
        idx = M.stationary_bootstrap_indices(len(x), bl, n_draws, seed=bl)
        m = x[idx].mean(axis=1)
        out[bl] = (float(np.quantile(m, (1 - level) / 2)), float(np.quantile(m, 1 - (1 - level) / 2)))
    lo = min(v[0] for v in out.values()); hi = max(v[1] for v in out.values())
    return lo, hi, out
