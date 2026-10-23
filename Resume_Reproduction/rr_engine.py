"""Execution engine: target weights in, honest PnL out (OUTLINE.md 4.2).

The accounting is the prototype's (Backtest_prototype/backtest.py): a target dollar exposure is
turned into shares, the shares are traded at an execution price, cash moves by the traded value,
and the book is marked at the close. What this adds is the execution model the prototype lacks,
each piece a parameter:

    lag          trading rows between the close a weight is decided at and the row it trades on
    exec_price   'close' of the fill row (primary) or 'twap' = (open + close) / 2 (sensitivity)
    size_price   'exec' sizes shares at the fill price; 'prev_close' at the previous close
    cost_bp      bp of traded dollars, per side
    slip_bp      bp of traded dollars: the fill moved against the trade
    borrow_bp    bp per year on the short gross, charged daily
    deadband     no trade in an asset whose current weight is within this of its target

The prototype corresponds to lag=2, exec_price='twap', size_price='prev_close' and no frictions
(tests/test_parity.py). Missing bars (the 2022 vendor gap) are carried: no trade, no cost, the
position marked at its last close, so total PnL does not dip and recover on those days.
"""
import numpy as np
import pandas as pd


def simulate(open_, close, w_target, lag=1, exec_price="close", size_price="exec",
             cost_bp=0.0, slip_bp=0.0, borrow_bp=0.0, deadband=0.0, capital=1.0):
    """Run one book. All panels share one calendar index and one column set.

    w_target[t] is the weight decided with information up to the close of row t; it trades on
    row t + lag. NaN weights mean flat. Returns a dict of Series (book level) and DataFrames
    (per asset).
    """
    cols = list(close.columns)
    idx = close.index
    O = open_.reindex(index=idx, columns=cols).to_numpy(float)
    Cl = close.reindex(columns=cols).to_numpy(float)
    W = w_target.reindex(index=idx, columns=cols).to_numpy(float)
    W = np.nan_to_num(W, nan=0.0)
    T, N = Cl.shape

    avail = ~np.isnan(Cl)
    mark = pd.DataFrame(Cl).ffill().to_numpy()            # last known close, for valuation
    if exec_price == "close":
        P = Cl
    elif exec_price == "twap":
        P = (O + Cl) / 2.0
    else:
        raise ValueError(exec_price)

    shares = np.zeros(N)
    cash = 0.0
    equity_prev = 0.0
    w_fill_prev = np.zeros(N)
    value_prev = np.zeros(N)

    out_pnl = np.zeros(T); out_cost = np.zeros(T); out_slip = np.zeros(T); out_borrow = np.zeros(T)
    out_to_exec = np.zeros(T); out_to_sig = np.zeros(T); out_gross = np.zeros(T); out_net = np.zeros(T)
    out_shares = np.zeros((T, N)); out_wheld = np.zeros((T, N)); out_pnl_asset = np.zeros((T, N))
    out_trade_dollars = np.zeros((T, N))

    c_rate, s_rate, b_rate = cost_bp / 1e4, slip_bp / 1e4, borrow_bp / 1e4 / 252.0
    for t in range(T):
        w_fill = W[t - lag] if t - lag >= 0 else np.zeros(N)
        a = avail[t]
        pf = P[t]
        if size_price == "exec":
            ps = pf
        elif size_price == "prev_close":
            ps = mark[t - 1] if t > 0 else np.full(N, np.nan)
        else:
            raise ValueError(size_price)

        with np.errstate(invalid="ignore", divide="ignore"):
            target_sh = w_fill * capital / ps
            w_cur = shares * pf / capital
        tradable = a & np.isfinite(target_sh) & np.isfinite(pf)
        if deadband > 0:
            tradable &= np.abs(w_fill - np.nan_to_num(w_cur)) >= deadband
        trade = np.where(tradable, target_sh - shares, 0.0)
        traded_dollars = np.where(tradable, np.abs(trade) * pf, 0.0)
        exec_cash = np.where(tradable, trade * pf, 0.0)

        cost_a = traded_dollars * c_rate
        slip_a = traded_dollars * s_rate
        shares = shares + trade
        value = shares * np.nan_to_num(mark[t])
        borrow_a = np.maximum(-value, 0.0) * b_rate

        cash = cash - exec_cash.sum() - cost_a.sum() - slip_a.sum() - borrow_a.sum()
        equity = cash + value.sum()

        out_pnl_asset[t] = value - value_prev - exec_cash - cost_a - slip_a - borrow_a
        out_pnl[t] = equity - equity_prev
        out_cost[t], out_slip[t], out_borrow[t] = cost_a.sum(), slip_a.sum(), borrow_a.sum()
        out_to_exec[t] = traded_dollars.sum() / capital
        out_to_sig[t] = np.abs(w_fill - w_fill_prev).sum()
        out_shares[t] = shares
        out_wheld[t] = value / capital
        out_gross[t] = np.abs(value).sum() / capital
        out_net[t] = value.sum() / capital
        out_trade_dollars[t] = np.where(tradable, trade * pf, 0.0)

        equity_prev, value_prev, w_fill_prev = equity, value, w_fill

    S = lambda x, name: pd.Series(x, index=idx, name=name)     # noqa: E731
    F = lambda x: pd.DataFrame(x, index=idx, columns=cols)     # noqa: E731
    pnl = S(out_pnl, "pnl_net")
    frictions = out_cost + out_slip + out_borrow
    return {
        "pnl_net": pnl,
        "pnl_gross": S(out_pnl + frictions, "pnl_gross"),
        "cost": S(out_cost, "cost"), "slip": S(out_slip, "slip"), "borrow": S(out_borrow, "borrow"),
        "turnover_exec": S(out_to_exec, "turnover_exec"),
        "turnover_signal": S(out_to_sig, "turnover_signal"),
        "gross": S(out_gross, "gross"), "net": S(out_net, "net"),
        "shares": F(out_shares), "w_held": F(out_wheld), "pnl_asset": F(out_pnl_asset),
        "trade_dollars": F(out_trade_dollars),
        "params": dict(lag=lag, exec_price=exec_price, size_price=size_price, cost_bp=cost_bp,
                       slip_bp=slip_bp, borrow_bp=borrow_bp, deadband=deadband, capital=capital),
    }
