"""Metrics, each defined once (OUTLINE.md 4.1).

Book-level numbers take the engine's daily PnL per $1 of constant notional, which is the daily
return: additive, not compounded. Signal-level numbers take a score panel and a forward-return
panel on the same calendar, averaged per date first and then across dates, with Newey-West
standard errors because neighbouring dates share most of their forward window.
"""
import numpy as np
import pandas as pd

ANN = 252


# ----------------------------------------------------------------------------- statistics
def newey_west_se(x, lag):
    """Standard error of the mean of x with a Bartlett-kernel Newey-West correction."""
    x = pd.Series(x).dropna().to_numpy(float)
    n = len(x)
    if n < 2:
        return np.nan
    e = x - x.mean()
    s = e @ e / n
    for k in range(1, min(lag, n - 1) + 1):
        s += 2.0 * (1.0 - k / (lag + 1.0)) * (e[k:] @ e[:-k]) / n
    return float(np.sqrt(max(s, 0.0) / n))


# ----------------------------------------------------------------------------- book level
def excess_returns(r, rf=None, net=None):
    """Daily return minus the bill rate on the net exposure (DATA.md 5).

    Capital not deployed earns the bill rate and capital borrowed pays it, so the excess over the
    bill rate is r - rf * net. For a net-zero book the term vanishes, which is why r_f = 0 is exact.
    """
    r = pd.Series(r).astype(float)
    if rf is None:
        return r
    net = pd.Series(1.0, index=r.index) if net is None else pd.Series(net).reindex(r.index).fillna(0.0)
    return r - pd.Series(rf).reindex(r.index).fillna(0.0) * net


def sharpe(r, rf=None, net=None):
    x = excess_returns(r, rf, net).dropna()
    sd = x.std()
    return float(x.mean() / sd * np.sqrt(ANN)) if sd > 0 else np.nan


def sharpe_se_iid(sr, n_days):
    """Lo's iid approximation for the standard error of an annualised Sharpe ratio."""
    return float(np.sqrt((1.0 + sr ** 2 / (2 * ANN)) * ANN / n_days))


def max_drawdown(r):
    """(largest fall of cumulative PnL from its peak, in units of initial capital, as % of peak equity)."""
    cum = pd.Series(r).fillna(0.0).cumsum()
    dd_units = float((cum - cum.cummax()).min())
    eq = 1.0 + cum
    dd_pct = float(((eq - eq.cummax()) / eq.cummax()).min())
    return dd_units, dd_pct


def annual_turnover(turnover, gross=None):
    """Mean daily traded dollars per $1 x 252; per unit mean gross when gross is given."""
    to = float(pd.Series(turnover).mean() * ANN)
    if gross is None:
        return to
    g = float(pd.Series(gross).mean())
    return to / g if g > 0 else np.nan


def book_summary(res, rf=None, mask=None):
    """One row of numbers for one engine run, optionally restricted to a date mask."""
    keys = ["pnl_net", "pnl_gross", "cost", "slip", "borrow", "turnover_exec", "turnover_signal", "gross", "net"]
    s = {k: res[k] if mask is None else res[k][mask] for k in keys}
    r = s["pnl_net"]
    sr = sharpe(r, rf, s["net"]) if rf is not None else sharpe(r)
    dd_u, dd_p = max_drawdown(r)
    return pd.Series({
        "days": int(r.notna().sum()),
        "cum_pnl": float(r.sum()),
        "cum_pnl_gross": float(s["pnl_gross"].sum()),
        "ann_return": float(r.mean() * ANN),
        "ann_vol": float(r.std() * np.sqrt(ANN)),
        "sharpe": sr,
        "sharpe_se_iid": sharpe_se_iid(sr, int(r.notna().sum())) if np.isfinite(sr) else np.nan,
        "rf": "DTB3 x net" if rf is not None else "0",
        "max_dd_units": dd_u,
        "max_dd_pct_peak": dd_p,
        "hit_rate": float((r > 0).mean()),
        "turnover_ann": annual_turnover(s["turnover_exec"]),
        "turnover_ann_per_gross": annual_turnover(s["turnover_exec"], s["gross"]),
        "turnover_signal_ann": annual_turnover(s["turnover_signal"]),
        "cost_ann_bp": float(s["cost"].mean() * ANN * 1e4),
        "slip_ann_bp": float(s["slip"].mean() * ANN * 1e4),
        "gross_mean": float(s["gross"].mean()),
        "net_mean": float(s["net"].mean()),
        "net_abs_max": float(s["net"].abs().max()),
    })


def concentration(res, categories, mask=None):
    """Largest weight, mean Herfindahl of |w|/gross, and the share of PnL from each category."""
    w = res["w_held"] if mask is None else res["w_held"][mask]
    pa = res["pnl_asset"] if mask is None else res["pnl_asset"][mask]
    aw = w.abs()
    g = aw.sum(axis=1).replace(0, np.nan)
    herf = ((aw.div(g, axis=0)) ** 2).sum(axis=1)
    by_cat = pa.sum().groupby(pd.Series(categories)).sum()
    total = pa.sum().sum()
    out = {"max_abs_weight": float(aw.max().max()), "herfindahl_mean": float(herf.mean())}
    for c, v in by_cat.items():
        out[f"pnl_share_{c}"] = float(v / total) if total != 0 else np.nan
    return pd.Series(out)


# ----------------------------------------------------------------------------- signal level
def bucket_test(score, fwd, n_buckets=5, nw_lag=4):
    """Mean forward return per bucket of a centred percentile score, per date then across dates.

    score is in [-0.5, 0.5] (a trailing percentile minus one half); buckets are fixed 0.2-wide
    cuts of the percentile, so they use no data. Returns one row per bucket plus the G5 - G1
    spread, each with its Newey-West SE and the number of dates and observations behind it.
    """
    s, f = score.align(fwd, join="inner")
    pct = s + 0.5
    b = np.floor(pct * n_buckets).clip(0, n_buckets - 1)
    b = b.where(s.notna() & f.notna())
    rows, per_date = [], {}
    for k in range(n_buckets):
        m = f.where(b == k)
        d = m.mean(axis=1)                  # per date: mean over the assets in bucket k
        per_date[k] = d
        rows.append({"bucket": f"G{k + 1}", "mean": float(d.mean()), "se_nw": newey_west_se(d, nw_lag),
                     "dates": int(d.notna().sum()), "obs": int(m.notna().sum().sum())})
    spread = per_date[n_buckets - 1] - per_date[0]
    rows.append({"bucket": f"G{n_buckets}-G1", "mean": float(spread.mean()), "se_nw": newey_west_se(spread, nw_lag),
                 "dates": int(spread.notna().sum()), "obs": int(spread.notna().sum())})
    out = pd.DataFrame(rows).set_index("bucket")
    out["t"] = out["mean"] / out["se_nw"]
    return out


def ic_series(score, fwd, min_assets=10):
    """Per-date Spearman rank correlation across assets between score and forward return."""
    s, f = score.align(fwd, join="inner")
    rs = s.rank(axis=1)
    rf_ = f.where(s.notna()).rank(axis=1)
    rs = rs.where(f.notna())
    ok = rs.notna().sum(axis=1) >= min_assets
    a = rs.sub(rs.mean(axis=1), axis=0)
    b = rf_.sub(rf_.mean(axis=1), axis=0)
    num = (a * b).sum(axis=1)
    den = np.sqrt((a ** 2).sum(axis=1) * (b ** 2).sum(axis=1))
    return (num / den).where(ok)


def ic_summary(score, fwd, horizon=5):
    ic = ic_series(score, fwd).dropna()
    mu, sd = ic.mean(), ic.std()
    icir = mu / sd if sd > 0 else np.nan
    return pd.Series({"mean_ic": float(mu), "ic_sd": float(sd), "icir": float(icir),
                      "t_deflated": float(icir * np.sqrt(len(ic) / horizon)), "dates": int(len(ic))})


def win_rate(score, fwd, dead=0.1):
    """Signal win rate: share of (asset, date) whose score sign matches the forward-return sign.

    Pairs with |score| <= dead are excluded as sign noise; computed per date, then across dates.
    Two readings:
      raw       sign(score) vs sign(return), beside the pooled base rate max(P(up), P(down)) over
                the whole sample (a per-date majority would be an oracle that knows each day's market)
      relative  sign(score) vs sign(return minus that date's cross-sectional mean), base rate 0.5;
                this is the reading that matches a dollar-neutral book
    """
    s, f = score.align(fwd, join="inner")
    keep = s.notna() & f.notna() & (s.abs() > dead) & (f != 0)
    hit = (np.sign(s) == np.sign(f)).where(keep)
    up = float((f > 0)[keep].sum().sum() / keep.sum().sum())
    rel = f.sub(f.where(f.notna() & s.notna()).mean(axis=1), axis=0)
    hit_rel = (np.sign(s) == np.sign(rel)).where(keep & (rel != 0))
    win = float(hit.mean(axis=1).mean())
    win_rel = float(hit_rel.mean(axis=1).mean())
    return pd.Series({"win_rate": win, "base_rate": max(up, 1 - up), "excess": win - max(up, 1 - up),
                      "win_rate_relative": win_rel, "excess_relative": win_rel - 0.5,
                      "share_excluded": float(1 - keep.sum().sum() / (s.notna() & f.notna()).sum().sum()),
                      "dates": int(hit.mean(axis=1).notna().sum())})


# ----------------------------------------------------------------------------- robustness
def stationary_bootstrap_indices(n, mean_block, n_draws=2000, seed=0):
    """Politis-Romano stationary bootstrap: blocks of geometric length with mean `mean_block`."""
    rng = np.random.default_rng(seed)
    p = 1.0 / mean_block
    idx = np.empty((n_draws, n), dtype=np.int64)
    idx[:, 0] = rng.integers(0, n, size=n_draws)
    jump = rng.random((n_draws, n)) < p
    fresh = rng.integers(0, n, size=(n_draws, n))
    for t in range(1, n):
        idx[:, t] = np.where(jump[:, t], fresh[:, t], (idx[:, t - 1] + 1) % n)
    return idx


def sharpe_rows(x):
    """Annualised Sharpe of every row of a 2-D array."""
    sd = x.std(axis=1, ddof=1)
    return np.where(sd > 0, x.mean(axis=1) / sd * np.sqrt(ANN), np.nan)


def deflated_sharpe(r, trial_sharpes_daily, n_trials):
    """Bailey & Lopez de Prado's deflated Sharpe ratio for a daily return series r.

    SR0 is the expected maximum Sharpe of n_trials unskilled strategies whose Sharpes vary as the
    trials did; DSR is the probability that the true Sharpe exceeds it, given skew and kurtosis.
    """
    from scipy.stats import kurtosis, norm, skew
    x = pd.Series(r).dropna().to_numpy()
    T = len(x)
    sr = x.mean() / x.std(ddof=1)
    v = float(np.var(trial_sharpes_daily, ddof=1))
    e = 0.5772156649
    n = max(int(n_trials), 2)
    sr0 = np.sqrt(v) * ((1 - e) * norm.ppf(1 - 1 / n) + e * norm.ppf(1 - 1 / (n * np.e)))
    g3, g4 = skew(x), kurtosis(x, fisher=False)
    z = (sr - sr0) * np.sqrt(T - 1) / np.sqrt(1 - g3 * sr + (g4 - 1) / 4 * sr ** 2)
    return {"sharpe_daily": float(sr), "sr0_daily": float(sr0), "dsr": float(norm.cdf(z)), "n_trials": n, "days": T}


def effective_trials(series, cutoff):
    """Greedy clustering: a trial joins the first cluster whose representative it correlates with above cutoff."""
    reps = []
    for s in series:
        if not any(np.corrcoef(s, r)[0, 1] > cutoff for r in reps):
            reps.append(s)
    return len(reps)
