"""Round 3, Part A: the dynamic cut, its timing, the holding month, and the turnover split."""
import numpy as np
import pandas as pd

import rr_round3 as R3
import rr_tsmom as T


def _toy(n=400, k=5, seed=3):
    rng = np.random.default_rng(seed)
    cal = pd.bdate_range("2020-01-01", periods=n)
    xr = pd.DataFrame(rng.normal(0, 0.01, (n, k)), index=cal, columns=[f"A{i}" for i in range(k)])
    return cal, xr


def test_d_pct_is_rank_in_trailing_window_including_today():
    x = pd.Series(np.arange(300, dtype=float))
    p = R3.d_pct(x, n=252, minp=126)
    assert p.iloc[:125].isna().all()
    assert p.iloc[299] == 1.0                       # the largest of its own window
    y = x.copy(); y.iloc[299] = -1.0
    assert R3.d_pct(y, 252, 126).iloc[299] == 1 / 252


def test_d_tercile_cuts():
    p = pd.Series([0.1, 1 / 3, 0.34, 2 / 3, 0.9, np.nan])
    assert R3.d_tercile(p).tolist()[:5] == [0, 0, 1, 1, 2]
    assert np.isnan(R3.d_tercile(p).iloc[5])


def test_measures_do_not_look_ahead():
    cal, xr = _toy(k=12)
    t = 300
    base = R3.avg_pairwise_corr(xr).iloc[t]
    assert np.isfinite(base)
    xr2 = xr.copy(); xr2.iloc[t + 1:] *= 5.0
    assert R3.avg_pairwise_corr(xr2).iloc[t] == base
    s1, s2 = R3.ewma_sigma(xr, 10), R3.ewma_sigma(xr2, 10)
    assert np.array_equal(s1.iloc[: t + 2].to_numpy(), s2.iloc[: t + 2].to_numpy(), equal_nan=True)  # row t+1 sees row t only
    xr3 = xr.copy(); xr3.iloc[t] *= 5.0
    assert np.array_equal(R3.ewma_sigma(xr3, 10).iloc[t].to_numpy(), s1.iloc[t].to_numpy())


def test_holding_rows_match_the_fill_after_each_month_end():
    cal, xr = _toy()
    me = T.month_ends(cal)
    rows = R3.holding_rows(cal, me, lag=1)
    pos = cal.get_indexer(me)
    f = me[3]
    assert rows[f][0] == pos[3] + 2 and rows[f][-1] == pos[4] + 1
    r = R3.holding_return(xr, cal, me, lag=1)
    expect = np.prod(1 + xr.iloc[pos[3] + 2: pos[4] + 2].to_numpy(), axis=0) - 1
    assert np.allclose(r.loc[f].to_numpy(), expect)


def test_turnover_sources_sum_to_the_actual_change():
    cal, xr = _toy(n=700)
    vol = T.ewma_vol(xr)
    me = T.month_ends(cal)[13:]
    sign = T.tsmom_signal(xr, 12).loc[me]
    a = 0.40 / vol.loc[me]
    w0 = T.t0_targets(xr, vol, me, 12)
    src = R3.turnover_sources_t0(sign, a, w0)
    assert src["check"].max() < 1e-12
    w1, lev = T.t1_targets(w0, xr)
    src1 = R3.turnover_sources_t1(w0, lev, w1)
    assert src1["check"].max() < 1e-12
