"""W1 acceptance: the adjusted data has no corporate-action jumps and every fix is where DATA.md says."""
import numpy as np
import pandas as pd
import pytest

import config as C
import rr_data as D


@pytest.fixture(scope="module")
def etfs():
    return D.load_etfs()


def test_calendar(etfs):
    cal = D.calendar(etfs)
    assert len(cal) == 1630
    assert (cal.weekday < 5).all()
    assert cal.min() == pd.Timestamp(C.SAMPLE_START) and cal.max() == pd.Timestamp(C.SAMPLE_END)


def test_no_split_sized_jumps(etfs):
    for t, d in etfs.items():
        assert (d["close"].pct_change().dropna().abs() <= 0.4).all(), t


def test_split_is_continuous(etfs):
    for t in C.SPLIT_TICKERS:
        c = etfs[t]["close"]
        ratio = c.loc["2025-12-05"] / c.loc["2025-12-04"]
        assert 0.98 < ratio < 1.02, (t, ratio)


def test_split_day_bar_repaired(etfs):
    for t in C.SPLIT_TICKERS:
        bar = etfs[t].loc["2025-12-05"]
        assert bar["bar_fixed"] == 1
        assert bar["low"] <= bar["open"] <= bar["high"] and bar["low"] <= bar["close"] <= bar["high"]


def test_unadjusted_tickers_untouched(etfs):
    raw = D._read_ohlcv(f"{C.CTA_DATA}/SPY_ohlcv_1d.csv")
    pd.testing.assert_series_equal(etfs["SPY"]["close"], raw["close"].loc[etfs["SPY"].index], check_names=False)


def test_vix_matches_cboe(etfs):
    cal = D.calendar(etfs)
    vix, _ = D.load_index("VIX", cal)
    cboe = D.load_cboe_vix().reindex(cal)
    m = pd.concat([vix, cboe], axis=1).dropna()
    assert (np.abs(m.iloc[:, 0] - m.iloc[:, 1]) < 0.005).all()


def test_indices_cover_calendar(etfs):
    cal = D.calendar(etfs)
    for name in ("VIX", "MOVE"):
        s, _ = D.load_index(name, cal)
        assert s.notna().all(), name


def test_total_return_identity(etfs):
    cal = D.calendar(etfs)
    close = D.panel(etfs, "close", cal)
    open_ = D.panel(etfs, "open", cal)
    dist = D.load_distributions(cal, close.columns)
    _, tr = D.total_return_prices(open_, close, dist)
    t = "HYG"
    ex = dist.index[dist[t] > 0][5]
    i = cal.get_loc(ex)
    lhs = tr[t].iloc[i] / tr[t].iloc[i - 1]
    rhs = (close[t].iloc[i] + dist[t].iloc[i]) / close[t].iloc[i - 1]
    assert abs(lhs - rhs) < 1e-12
