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


# ----------------------------------------------------------------------------- Part B
def _book(n=500, k=6, seed=5):
    cal, xr = _toy(n, k, seed)
    close = (1 + xr).cumprod() * 100
    me = T.month_ends(cal)
    rng = np.random.default_rng(seed)
    w = pd.DataFrame(rng.uniform(-0.3, 0.3, (len(me), k)), index=me, columns=xr.columns)
    return cal, xr, close, me, w


def test_label_is_known_at_the_next_month_end():
    cal, xr = _toy()
    me = T.month_ends(cal)
    lab = R3.label_return(xr, cal, me, d=1)
    pos = cal.get_indexer(me)
    expect = np.prod(1 + xr.iloc[pos[2] + 2: pos[3] + 1].to_numpy(), axis=0) - 1
    assert np.allclose(lab.iloc[2].to_numpy(), expect)
    xr2 = xr.copy(); xr2.iloc[pos[3] + 1:] *= 9
    assert np.allclose(R3.label_return(xr2, cal, me, 1).iloc[2].to_numpy(), expect)


def test_sliced_engine_matches_the_full_run_after_the_start_fill():
    from rr_engine import simulate
    cal, xr, close, me, w = _book()
    run = lambda c, o, ww, cc: simulate(o, c, T.daily_weights(ww, cc), lag=1, deadband=T.rebalance_deadband(ww, cc, lag=1),
                                        cost_bp=5, slip_bp=2)
    full = run(close, close, w, cal)
    s = cal.get_loc(me[8]); e = cal.get_loc(me[12])
    sl = run(close.iloc[s:e + 1], close.iloc[s:e + 1], w.loc[me[8]:me[11]], cal[s:e + 1])
    after = cal[s + 2:e + 1]
    assert np.allclose(full["pnl_net"].loc[after].to_numpy(), sl["pnl_net"].loc[after].to_numpy(), atol=1e-12)


def test_drifted_weights_match_the_engine():
    from rr_engine import simulate
    cal, xr, close, me, w = _book()
    res = simulate(close, close, T.daily_weights(w, cal), lag=1, deadband=T.rebalance_deadband(w, cal, lag=1))
    i_fill, i_now = cal.get_loc(me[5]) + 1, cal.get_loc(me[6])
    got = R3.drifted(w.loc[me[5]].to_numpy(), close, i_fill, i_now)
    assert np.allclose(got, res["w_held"].iloc[i_now].to_numpy())


def test_choose_drops_deep_drawdowns_then_takes_the_highest_cumulative():
    idx = pd.bdate_range("2024-01-01", periods=60)
    rng = np.random.default_rng(0)
    base = rng.normal(0, 0.001, 60)
    s = {"deep": pd.Series(np.r_[np.full(30, 0.004), np.full(10, -0.01), np.full(20, 0.004)], index=idx),
         "steady": pd.Series(base + 0.001, index=idx), "flat": pd.Series(np.zeros(60), index=idx),
         "weak": pd.Series(base, index=idx)}
    pick, tab = R3.choose(s)
    assert not tab.loc["deep", "kept"] and pick == "steady"
