"""Per-asset regimes (resume bullet 3; OUTLINE 4.4, DATA 6.1).

Two measures per asset, both known by the close before the date they label:
    V     21-day mean share volume through t-1 (one venue feed: only ever ranked against the
          asset's own past, never compared across assets)
    sigma 21-day realised volatility of daily returns through t-1

Each is cut into terciles four ways:
    D   rolling: rank against the asset's own trailing 252 days (min 126)        dynamic
    S2  frozen per rung: the asset's own terciles over that rung's training window  static
    S3  full sample: the asset's own terciles over the whole history (look-ahead)   diagnostic
    S1  data-free: ceil(2 ln sigma_ann%) merged into three; sigma only, demonstration
"""
import numpy as np
import pandas as pd

import config as C
import rr_metrics as M
import rr_signals as S

LABELS = ("low", "mid", "high")


def volume_measure(volume, n=21):
    return volume.rolling(n).mean().shift(1)


def sigma_measure(close, n=21):
    return S.sigma(S.returns(close), n)


def _tercile(x, lo, hi):
    lab = pd.DataFrame(np.where(x <= lo, 0, np.where(x <= hi, 1, 2)), index=x.index, columns=x.columns)
    return lab.where(x.notna())


def cut_rolling(x, n=252, minp=126):
    pct = x.rolling(n, min_periods=minp).rank(pct=True)
    return _tercile(pct, 1 / 3, 2 / 3)


def cut_fullsample(x, end):
    ref = x.loc[:end]
    return _tercile(x, ref.quantile(1 / 3), ref.quantile(2 / 3))


def cut_frozen_per_rung(x, cal, rungs):
    """For each rung, the asset's terciles over the rung's training quarters, applied to its test quarter."""
    out = pd.DataFrame(np.nan, index=x.index, columns=x.columns)
    for r in rungs:
        q = cal.to_period("Q")
        tq = pd.Period(r["test_q"], "Q")
        ref = x[q.isin([tq - 4, tq - 3, tq - 2])]
        d = cal[r["test"]]
        out.loc[d] = _tercile(x.loc[d], ref.quantile(1 / 3), ref.quantile(2 / 3)).to_numpy()
    return out


def cut_datafree_sigma(sig_daily):
    ann_pct = sig_daily * np.sqrt(252) * 100
    g = np.ceil(2 * np.log(ann_pct))
    lab = pd.DataFrame(np.where(g <= 6, 0, np.where(g == 7, 1, 2)), index=g.index, columns=g.columns)
    return lab.where(ann_pct.notna())


def episodes(mask):
    """Number of runs of consecutive True per column, summed."""
    m = mask.fillna(False).astype(int)
    starts = (m.diff().fillna(m) == 1)
    return int(starts.sum().sum())


def regime_grid(score, fwd, vlab, slab, sample, dates_floor=250, obs_floor=1000, ep_floor=10):
    """3 x 3 grid of how well the signal times returns inside each (volume, sigma) cell.

    Primary statistic, the signal-weighted forward return: for every asset-day in the cell,
    (2 x centred score) x forward return, which is the trend follower's own PnL per unit of
    signal; averaged over the cell's assets per date, then across dates with a Newey-West SE.
    A per-date G5 - G1 spread inside a cell is not computable here: a cell holds about four
    assets on a date, so G1 and G5 rarely coexist on one date (W5 run, 2026-10-23). The pooled
    G5 - G1 spread over all of the cell's asset-days is printed beside it, descriptive only.
    """
    rows, per_date = [], {}
    bucket = np.floor((score + 0.5) * 5).clip(0, 4)
    for vi, vn in enumerate(LABELS):
        for si, sn in enumerate(LABELS):
            cell = (vlab == vi) & (slab == si) & sample.to_numpy()[:, None] & score.notna() & fwd.notna()
            sw = (2.0 * score * fwd).where(cell)
            d = sw.mean(axis=1).dropna()
            se = M.newey_west_se(d, C.NW_LAG)
            g1 = fwd.where(cell & (bucket == 0)); g5 = fwd.where(cell & (bucket == 4))
            pooled = float(np.nanmean(g5.to_numpy()) - np.nanmean(g1.to_numpy())) if g1.notna().any().any() and g5.notna().any().any() else np.nan
            n_dates, n_obs, n_ep = int(len(d)), int(cell.sum().sum()), episodes(cell)
            rows.append({"volume": vn, "sigma": sn, "signal_weighted_bp": float(d.mean() * 1e4),
                         "se_bp": float(se * 1e4), "t": float(d.mean() / se) if se > 0 else np.nan,
                         "pooled_g5_g1_bp": pooled * 1e4, "dates": n_dates, "asset_days": n_obs,
                         "episodes": n_ep,
                         "measurable": n_dates >= dates_floor and n_obs >= obs_floor and n_ep >= ep_floor})
            per_date[(vn, sn)] = sw.mean(axis=1)
    return pd.DataFrame(rows).set_index(["volume", "sigma"]), per_date


def corner_difference(per_date, a=("high", "low"), b=("low", "high")):
    d = (per_date[a] - per_date[b]).dropna()
    se = M.newey_west_se(d, C.NW_LAG)
    return {"corner_a": "/".join(a), "corner_b": "/".join(b), "diff_bp": float(d.mean() * 1e4),
            "se_bp": float(se * 1e4), "t": float(d.mean() / se) if se > 0 else np.nan, "dates": int(len(d))}
