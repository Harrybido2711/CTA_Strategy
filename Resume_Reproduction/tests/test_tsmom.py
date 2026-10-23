"""Round 2 mechanics on toy data."""
import numpy as np
import pandas as pd
import pytest

import rr_tsmom as T
from rr_engine import simulate


def test_sign_signal_and_vol_scaling():
    idx = pd.bdate_range("2020-01-01", periods=400)
    rng = np.random.default_rng(0)
    # strong drifts so the 12-month sign is certain; vols large enough that the 0.5 cap does not bind
    xr = pd.DataFrame({"UP": 0.006 + 0.03 * rng.standard_normal(400), "DN": -0.012 + 0.06 * rng.standard_normal(400)}, index=idx)
    vol = T.ewma_vol(xr)
    me = T.month_ends(idx, start=idx[300])
    w = T.t0_targets(xr, vol, me)
    assert (w["UP"] > 0).all() and (w["DN"] < 0).all()
    # the noisier asset gets the smaller weight, about in the ratio of the vols
    assert (w["UP"].abs() > w["DN"].abs()).all()


def test_caps_bind():
    w = pd.DataFrame({"A": [0.9, 0.1], "B": [-0.9, 2.9], "C": [0.0, 2.9]})
    c = T.caps(w, asset_cap=0.5, gross_cap=1.2)
    assert (c.abs() <= 0.5 + 1e-12).all().all()
    assert (c.abs().sum(axis=1) <= 1.2 + 1e-12).all()


def test_monthly_hold_trades_only_on_fill_rows():
    idx = pd.bdate_range("2021-01-01", periods=70)
    close = pd.DataFrame({"A": np.linspace(100, 120, 70)}, index=idx)
    me = T.month_ends(idx)
    w_me = pd.DataFrame({"A": [1.0, -1.0, 1.0, 1.0][: len(me)]}, index=me)
    w = T.daily_weights(w_me, idx)
    db = T.rebalance_deadband(w_me, idx)
    r = simulate(close, close, w, lag=1, deadband=db)
    traded = r["trade_dollars"]["A"].abs() > 0
    assert set(idx[traded]) <= set(idx[np.isfinite(db.to_numpy())])
