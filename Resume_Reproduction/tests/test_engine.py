"""Engine mechanics on toy data: timing, vendor gaps, costs, deadband, borrow."""
import numpy as np
import pandas as pd
import pytest

from rr_engine import simulate

IDX = pd.bdate_range("2021-01-04", periods=300)


def one_asset(prices, weights):
    c = pd.DataFrame({"A": prices}, index=IDX[: len(prices)])
    w = pd.DataFrame({"A": weights}, index=c.index)
    return c, c.copy(), w


@pytest.mark.parametrize("lag,expected_jump_pnl", [(0, 0.1), (1, 0.1), (4, 0.1), (5, 0.0)])
def test_signal_trades_only_after_lag(lag, expected_jump_pnl):
    prices = [100.0] * 10 + [110.0] * 10
    weights = [0.0] * 5 + [1.0] * 15            # decided at the close of row 5
    c, o, w = one_asset(prices, weights)
    r = simulate(o, c, w, lag=lag)
    pnl = r["pnl_net"].to_numpy()
    assert np.allclose(pnl[: 5 + lag], 0.0)     # nothing before the fill row
    assert pnl[10] == pytest.approx(expected_jump_pnl)


def test_vendor_gap_does_not_dip():
    c = pd.DataFrame({"A": 100.0, "B": 100.0}, index=IDX[:20])
    c.iloc[7:10, 1] = np.nan                    # B has no bar on three days
    w = pd.DataFrame({"A": 0.5, "B": -0.5}, index=c.index)
    r = simulate(c, c, w, lag=1)
    assert np.allclose(r["pnl_net"].to_numpy(), 0.0)
    assert r["trade_dollars"]["B"].iloc[7:10].abs().sum() == 0.0


def test_costs_and_slippage_round_trip():
    c, o, w = one_asset([100.0] * 10, [1.0] * 5 + [0.0] * 5)
    r = simulate(o, c, w, lag=0, cost_bp=5.0, slip_bp=2.0)
    assert r["cost"].sum() == pytest.approx(2 * 5e-4)
    assert r["slip"].sum() == pytest.approx(2 * 2e-4)
    assert r["pnl_net"].sum() == pytest.approx(-(2 * 5e-4 + 2 * 2e-4))
    assert r["turnover_exec"].sum() == pytest.approx(2.0)


def test_deadband_suppresses_small_rebalances():
    c, o, w = one_asset([100.0] * 20, [0.50, 0.51] * 10)
    r0 = simulate(o, c, w, lag=0)
    r1 = simulate(o, c, w, lag=0, deadband=0.05)
    assert r0["turnover_exec"].sum() > 0.5
    assert r1["turnover_exec"].sum() == pytest.approx(0.50)


def test_borrow_charged_on_short_gross():
    c, o, w = one_asset([100.0] * 253, [-1.0] * 253)
    r = simulate(o, c, w, lag=0, borrow_bp=25.0)
    assert r["borrow"].sum() == pytest.approx(25e-4 * 253 / 252)


def test_constant_dollar_rebalances_with_price():
    prices = [100.0, 110.0, 121.0]
    c, o, w = one_asset(prices, [1.0, 1.0, 1.0])
    r = simulate(o, c, w, lag=0)
    assert r["w_held"]["A"].to_numpy() == pytest.approx([1.0, 1.0, 1.0])
    assert r["pnl_net"].to_numpy() == pytest.approx([0.0, 0.1, 0.1])


def test_deadband_can_change_over_time():
    c, o, w = one_asset([100.0] * 20, [0.50, 0.51] * 10)
    db = pd.Series([0.05] * 10 + [0.0] * 10, index=c.index)
    r = simulate(o, c, w, lag=0, deadband=db)
    assert r["turnover_exec"].iloc[:10].sum() == pytest.approx(0.50)
    assert r["turnover_exec"].iloc[10:].sum() == pytest.approx(9 * 0.01)   # row 10 already sits at 0.50


def test_optimizer_respects_vector_inputs():
    from rr_optimizer import MeanVariance, chol_t
    rng = np.random.default_rng(3)
    n = 6
    A = rng.normal(size=(50, n))
    sigma = np.cov(A.T)
    mu = np.array([0.02, 0.01, 0.0, -0.01, -0.02, 0.03])
    cap = np.array([0.5, 0.5, 0.5, 0.5, 0.5, 0.1])        # the last asset is held to 0.1
    opt = MeanVariance(n, gross=2.0, net=0.0)
    w = opt.solve(mu, chol_t(sigma), np.zeros(n), 0.5, cap, np.zeros(n))
    assert abs(w.sum()) < 1e-6
    assert np.abs(w).sum() <= 2.0 + 1e-6
    assert (np.abs(w) <= cap + 1e-6).all()
    assert w[0] > 0 and w[4] < 0
