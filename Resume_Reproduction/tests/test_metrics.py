"""Metric definitions on data whose answer is known."""
import numpy as np
import pandas as pd
import pytest

import rr_metrics as M


def test_newey_west_lag0_is_iid():
    x = np.random.default_rng(0).normal(size=500)
    assert M.newey_west_se(x, 0) == pytest.approx(np.std(x) / np.sqrt(len(x)))


def test_newey_west_widens_for_overlap():
    e = np.random.default_rng(1).normal(size=2000)
    x = pd.Series(e).rolling(5).sum().dropna()      # five-day overlapping sums
    assert M.newey_west_se(x, 4) > 1.8 * M.newey_west_se(x, 0)


def test_max_drawdown_units_and_pct():
    u, p = M.max_drawdown([0.1, -0.2, 0.05])
    assert u == pytest.approx(-0.2)
    assert p == pytest.approx(-0.2 / 1.1)


def test_excess_returns_vanish_for_net_zero():
    r = pd.Series([0.01, -0.005, 0.002])
    rf = pd.Series([0.0001] * 3)
    assert np.allclose(M.excess_returns(r, rf, pd.Series([0.0] * 3)), r)
    assert np.allclose(M.excess_returns(r, rf, pd.Series([1.0] * 3)), r - 0.0001)


@pytest.fixture
def panels():
    rng = np.random.default_rng(2)
    idx = pd.bdate_range("2021-01-04", periods=400)
    score = pd.DataFrame(rng.uniform(-0.5, 0.5, size=(400, 37)), index=idx)
    return score


def test_bucket_test_is_monotone_for_a_perfect_signal(panels):
    out = M.bucket_test(panels, panels * 0.01)
    means = out.loc[["G1", "G2", "G3", "G4", "G5"], "mean"].to_numpy()
    assert (np.diff(means) > 0).all()
    assert out.loc["G5-G1", "mean"] == pytest.approx(0.008, rel=0.05)


def test_ic_and_win_rate_of_a_perfect_signal(panels):
    assert M.ic_summary(panels, panels)["mean_ic"] == pytest.approx(1.0)
    assert M.win_rate(panels, panels)["win_rate"] == pytest.approx(1.0)
