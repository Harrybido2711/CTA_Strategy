"""Round 2, before Test: the paper's grid, T0 and T1, the haircut, the regime analysis, and m.

    .venv/bin/python Resume_Reproduction/run_20_round2.py

No position is held past 2025-06-30: the last month-end used is 2025-05-30, whose month ends
before Test. Parameters are config.ROUND2; the only one chosen here is m, on 2021-02 -> 2024-06.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C                       # noqa: E402
import rr_data as D                      # noqa: E402
import rr_metrics as M                   # noqa: E402
import rr_portfolio as PF                # noqa: E402
import rr_regimes as R                   # noqa: E402
import rr_tsmom as T                     # noqa: E402
from rr_engine import simulate           # noqa: E402
from rr_io import write_result           # noqa: E402

P = C.ROUND2
LAST_ME = "2025-05-30"
WINDOWS = {"record 2021-02..2025-06": ("2021-02-01", "2025-06-30"),
           "choice window 2021-02..2024-06": ("2021-02-01", "2024-06-30"),
           "OV 2024-07..2025-06": ("2024-07-01", "2025-06-30")}
VARIANTS = {"naive_0": dict(lag=0, cost_bp=0, slip_bp=0), "naive_1": dict(lag=1, cost_bp=0, slip_bp=0),
            "realistic": dict(lag=C.LAG, cost_bp=C.COST_BP, slip_bp=C.SLIP_BP)}


class R2:
    def __init__(self, total_return=True, universe=None, end=C.SAMPLE_END, last_me=LAST_ME):
        self.wd = PF.World(include_test=True, total_return=total_return, universe=universe, end=end)
        self.cal = self.wd.cal
        self.xr = T.excess_returns(self.wd.close, self.wd.rf)
        self.vol = T.ewma_vol(self.xr)
        me = T.month_ends(self.cal, start=P["first_signal"])
        self.me = me[me <= pd.Timestamp(last_me)]
        vix, _ = D.load_index("VIX", self.cal)
        self.vix_lab = R.index_labels(vix, self.cal, self.wd.rungs, C.PRE_TEST_END)
        self.high = (self.vix_lab["D rolling"] == 2)

    def t0(self, k=P["lookback_months"], h=1):
        return T.overlap_months(T.t0_targets(self.xr, self.vol, self.me, k), h)

    def run(self, w_me, variant="realistic", trade_deadband=0.0, **over):
        kw = dict(VARIANTS[variant]); kw.update(over)
        db = T.rebalance_deadband(w_me, self.cal, lag=kw["lag"], trade_deadband=trade_deadband)
        return simulate(self.wd.open, self.wd.close, T.daily_weights(w_me, self.cal), exec_price="close", deadband=db, **kw)

    def mask(self, a, b):
        return pd.Series((self.cal >= pd.Timestamp(a)) & (self.cal <= pd.Timestamp(b)), index=self.cal)

    def summary(self, res, m):
        s = M.book_summary(res, rf=self.wd.rf, mask=m)
        x = M.excess_returns(res["pnl_net"][m], self.wd.rf, res["net"][m])
        se = M.newey_west_se(x, C.H)
        return dict(s.to_dict(), ann_excess=float(x.mean() * 252), t_excess=float(x.mean() / se) if se > 0 else np.nan,
                    gross_max=float(res["gross"][m].max()), months=int(pd.Index(self.cal[m.to_numpy()]).to_period("M").nunique()))


def main():
    r2 = R2()
    rf = r2.wd.rf
    meta = {"round": "2 (time-series momentum, ROUND2.md)", "prices": "total return; excess of DTB3",
            "last_month_end": LAST_ME, "sharpe": "excess of DTB3 x net exposure",
            "execution": "realistic = next close, 5 bp + 2 bp; naive_1 = next close, no cost; naive_0 = same close"}

    # ---- A. the paper's grid, truncated
    grid = []
    for k in P["lookback_grid_months"]:
        for h in P["holding_grid_months"]:
            w = r2.t0(k, h)
            for var in ("naive_1", "realistic"):
                res = r2.run(w, var)
                for wn, (a, b) in WINDOWS.items():
                    s = r2.summary(res, r2.mask(a, b))
                    grid.append({"k_months": k, "h_months": h, "variant": var, "window": wn, "ann_excess": s["ann_excess"],
                                 "sharpe": s["sharpe"], "t_excess": s["t_excess"], "turnover_ann": s["turnover_ann"],
                                 "gross_mean": s["gross_mean"], "net_mean": s["net_mean"]})
    write_result(pd.DataFrame(grid).set_index(["k_months", "h_months", "variant", "window"]), "20_tsmom_grid",
                 dict(meta, what="paper Table 2 analogue: sign(k-month excess return) x 40%/sigma / S, held h months (overlapping)"))

    # ---- B. T0 and T1, three execution variants
    w0 = r2.t0()
    w1, lev = T.t1_targets(w0, r2.xr)
    books = {"T0 (paper)": w0, "T1 (vol-targeted 10%)": w1}
    rows, runs = [], {}
    for name, w in books.items():
        for var in VARIANTS:
            res = r2.run(w, var)
            runs[(name, var)] = res
            for wn, (a, b) in WINDOWS.items():
                rows.append(dict(r2.summary(res, r2.mask(a, b)), book=name, variant=var, window=wn))
    bt = pd.DataFrame(rows).set_index(["book", "variant", "window"])
    write_result(bt, "20_books", dict(meta, what="T0 and T1 under three execution variants"))
    levdf = pd.DataFrame({"leverage_target_over_T0": lev, "T0_gross": w0.abs().sum(axis=1), "T1_gross": w1.abs().sum(axis=1),
                          "T0_net": w0.sum(axis=1), "T1_net": w1.sum(axis=1),
                          "gross_cap_binds_T1": w1.abs().sum(axis=1) >= P["gross_cap"] - 1e-9,
                          "vix_state_D": r2.vix_lab["D rolling"].reindex(w0.index)})
    write_result(levdf, "20_leverage_path", dict(meta, what="month-end leverage: T1's multiplier on T0, gross and net, VIX state"))

    # ---- C. haircut of T0 (bullet 2 at the paper's horizon)
    hc = []
    for wn, (a, b) in WINDOWS.items():
        m = r2.mask(a, b); yrs = m.sum() / 252
        z, n1 = float(runs[("T0 (paper)", "naive_0")]["pnl_net"][m].sum()), float(runs[("T0 (paper)", "naive_1")]["pnl_net"][m].sum())
        c = float(r2.run(w0, "realistic", slip_bp=0)["pnl_net"][m].sum()); r = float(runs[("T0 (paper)", "realistic")]["pnl_net"][m].sum())
        hc.append({"window": wn, "naive_0_ann_bp": z / yrs * 1e4, "delay_bp": (n1 - z) / yrs * 1e4, "cost_bp": (c - n1) / yrs * 1e4,
                   "slip_bp": (r - c) / yrs * 1e4, "realistic_ann_bp": r / yrs * 1e4,
                   "H_1": 1 - r / n1 if n1 > 0 else np.nan, "H_0": 1 - r / z if z > 0 else np.nan,
                   "note": "" if n1 > 0 else "H_1 undefined: naive_1 PnL <= 0"})
    write_result(pd.DataFrame(hc).set_index("window"), "20_haircut_T0",
                 dict(meta, what="T0 haircut, raw PnL per $1 (not excess), stated order naive_0 -> delay -> cost -> slippage"))

    # ---- D. regime analysis on the record (pre-Test)
    rec = r2.mask(*WINDOWS["record 2021-02..2025-06"])
    move, _ = D.load_index("MOVE", r2.cal)
    mlab = R.index_labels(move, r2.cal, r2.wd.rungs, C.PRE_TEST_END)
    reg = []
    own = {}
    for name in books:
        res = runs[(name, "realistic")]
        x = M.excess_returns(res["pnl_net"], rf, res["net"])
        rv = x.rolling(63).std() * np.sqrt(252)
        own[name] = pd.Series(np.where(rv.rolling(252, min_periods=126).rank(pct=True) <= 1 / 3, 0,
                                       np.where(rv.rolling(252, min_periods=126).rank(pct=True) <= 2 / 3, 1, 2)), index=r2.cal).where(rv.notna())
        states = {f"VIX {k}": v for k, v in r2.vix_lab.items()}
        states.update({"MOVE D rolling": mlab["D rolling"], f"own vol ({name}) D rolling": own[name].shift(1)})
        for sname, lab in states.items():
            for st in (0, 1, 2):
                mm = rec & (lab == st)
                xs = x[mm]
                if len(xs) < 2:
                    reg.append({"book": name, "states": sname, "state": ["low", "mid", "high"][st], "days": int(len(xs))})
                    continue
                se = M.newey_west_se(xs, C.H)
                reg.append({"book": name, "states": sname, "state": ["low", "mid", "high"][st], "days": int(len(xs)),
                            "months": int(pd.Index(r2.cal[mm.to_numpy()]).to_period("M").nunique()),
                            "ann_excess": float(xs.mean() * 252), "ann_vol": float(xs.std() * np.sqrt(252)),
                            "sharpe": float(xs.mean() / xs.std() * np.sqrt(252)), "t": float(xs.mean() / se) if se > 0 else np.nan,
                            "mean_gross": float(res["gross"][mm].mean()), "measurable": int(len(xs)) >= 60})
    write_result(pd.DataFrame(reg).set_index(["book", "states", "state"]), "20_regime_returns",
                 dict(meta, what="realistic excess returns of T0 and T1 by volatility state, 2021-02..2025-06",
                      measurable="display flag: >= 60 days"))

    # ---- E. per-asset regime map at the paper's horizon (bullet 3)
    vol_panel = D.panel(r2.wd.etfs, "volume", r2.cal)
    vlab, slab = R.cut_rolling(R.volume_measure(vol_panel)), R.cut_rolling(R.sigma_measure(r2.wd.close))
    sig = T.tsmom_signal(r2.xr, P["lookback_months"]).loc[r2.me]
    c = r2.wd.close.ffill()
    fwd = (c.shift(-(1 + P["month_days"])) / c.shift(-1) - 1).loc[r2.me]
    rfm = rf.rolling(P["month_days"]).sum().shift(-(1 + P["month_days"])).reindex(r2.me)
    fwd = fwd.sub(rfm, axis=0)
    swr = sig * fwd
    cells, per_month = [], {}
    for vi, vn in enumerate(R.LABELS):
        for si, sn in enumerate(R.LABELS):
            inc = (vlab.loc[r2.me] == vi) & (slab.loc[r2.me] == si) & swr.notna()
            d = swr.where(inc).mean(axis=1).dropna()
            se = M.newey_west_se(d, 1)
            per_month[(vn, sn)] = swr.where(inc).mean(axis=1)
            cells.append({"volume": vn, "sigma": sn, "signal_weighted_pct_per_month": float(d.mean() * 100),
                          "se_pct": float(se * 100), "t": float(d.mean() / se) if se > 0 else np.nan,
                          "months": int(len(d)), "asset_months": int(inc.sum().sum()), "episodes": R.episodes(inc)})
    cd = (per_month[("high", "low")] - per_month[("low", "high")]).dropna()
    se = M.newey_west_se(cd, 1)
    yearly = {str(y): float(cd[cd.index.year == y].mean() * 100) for y in sorted(set(cd.index.year))}
    write_result(pd.DataFrame(cells).set_index(["volume", "sigma"]), "20_regime_map_tsmom",
                 dict(meta, what="sign(12-month excess return) x next-month excess return, per volume x sigma cell, rolling cut",
                      corner=f"HV/LV - LV/HV = {cd.mean() * 100:+.3f}% per month, t {cd.mean() / se:+.2f}, {len(cd)} months",
                      corner_by_year=" ".join(f"{k}:{v:+.2f}%" for k, v in yearly.items())))

    # ---- F. choose m for T2 on the choice window, confirm on OV
    cw, ov = r2.mask(*WINDOWS["choice window 2021-02..2024-06"]), r2.mask(*WINDOWS["OV 2024-07..2025-06"])
    cand = {}
    for m in P["regime_multiplier_grid"]:
        w2 = T.t2_targets(w1, r2.high.reindex(w1.index), m)
        res = r2.run(w2, "realistic", trade_deadband=P["deadband"])
        cand[m] = res
    ex = {m: M.excess_returns(res["pnl_net"], rf, res["net"]) for m, res in cand.items()}
    srs = {m: M.sharpe(ex[m][cw]) for m in cand}
    best = max(srs, key=srs.get)
    idx = M.stationary_bootstrap_indices(int(cw.sum()), 21, 1000, seed=7)
    xb = ex[best][cw].to_numpy()
    choose = []
    for m in P["regime_multiplier_grid"]:
        xm = ex[m][cw].to_numpy()
        dsr = M.sharpe_rows(xb[idx]) - M.sharpe_rows(xm[idx])
        se_d = float(np.nanstd(dsr))
        choose.append({"m": m, "sharpe_choice_window": srs[m], "shortfall_vs_best": srs[best] - srs[m], "se_shortfall": se_d,
                       "within_one_se": srs[best] - srs[m] <= se_d, "sharpe_OV": M.sharpe(ex[m][ov]),
                       "turnover_choice_window": M.annual_turnover(cand[m]["turnover_exec"][cw])})
    ch = pd.DataFrame(choose)
    picked = float(ch[ch.within_one_se].sort_values("m", ascending=False).iloc[0]["m"])
    ch["chosen"] = ch.m == picked
    write_result(ch.set_index("m"), "20_regime_multiplier",
                 dict(meta, what="T2's high-VIX leverage multiplier: chosen on the choice window by Sharpe, one-SE rule toward 1.0; "
                                 "OV column is the confirmation", chosen=picked))

    # ---- G. the rebuild comparison: T1 and T2 against T0
    w2 = T.t2_targets(w1, r2.high.reindex(w1.index), picked)
    res2 = r2.run(w2, "realistic", trade_deadband=P["deadband"])
    cmp_rows = []
    for wn, (a, b) in WINDOWS.items():
        m = r2.mask(a, b)
        s0 = r2.summary(runs[("T0 (paper)", "realistic")], m)
        for name, res in (("T1 (vol-targeted 10%)", runs[("T1 (vol-targeted 10%)", "realistic")]), (f"T2 (m = {picked})", res2)):
            s = r2.summary(res, m)
            cmp_rows.append({"book": name, "window": wn, "sharpe_T0": s0["sharpe"], "sharpe": s["sharpe"], "d_sharpe": s["sharpe"] - s0["sharpe"],
                             "ann_excess_T0": s0["ann_excess"], "ann_excess": s["ann_excess"], "ann_vol": s["ann_vol"],
                             "turnover_T0": s0["turnover_ann"], "turnover": s["turnover_ann"],
                             "d_turnover_pct": s["turnover_ann"] / s0["turnover_ann"] - 1 if s0["turnover_ann"] > 0 else np.nan,
                             "max_dd_T0": s0["max_dd_units"], "max_dd": s["max_dd_units"], "gross_mean": s["gross_mean"]})
    write_result(pd.DataFrame(cmp_rows).set_index(["book", "window"]), "20_rebuild",
                 dict(meta, what="T1 and T2 against T0, realistic; T2's m was chosen on the choice window, so OV is its out-of-sample row"))

    p = os.path.join(C.RESULTS, "run_ledger.csv")
    head = [l for l in open(p) if l.startswith("#")]
    led = pd.read_csv(p, comment="#")
    led = led[led.workstream != "R2"]
    add = [{"workstream": "R2", "test_q": "choice window", "stage": "regime multiplier m", "sample": "2021-02..2024-06",
            "params": f"m={r.m}", "spread": r.sharpe_choice_window, "selected": bool(r.chosen)} for r in ch.itertuples()]
    led = pd.concat([led, pd.DataFrame(add)], ignore_index=True)
    with open(p, "w") as fh:
        fh.writelines(head); led.to_csv(fh, index=False)

    show = pd.DataFrame(grid).query("window == 'record 2021-02..2025-06'").pivot_table(index=["k_months", "h_months"], columns="variant", values=["sharpe", "ann_excess", "turnover_ann"])
    print(show.round(3).to_string())
    print(bt.xs("record 2021-02..2025-06", level="window")[["ann_return", "ann_excess", "ann_vol", "sharpe", "t_excess", "max_dd_units", "turnover_ann", "gross_mean", "gross_max", "net_mean"]].round(3).to_string())
    print(pd.DataFrame(hc).round(3).to_string(index=False))
    print(pd.DataFrame(reg).query("states in ['VIX D rolling', 'VIX S1 data-free'] or states.str.startswith('own vol')")[["book", "states", "state", "days", "ann_excess", "ann_vol", "sharpe", "mean_gross"]].round(3).to_string(index=False))
    print(pd.DataFrame(cells).round(3).to_string(index=False)); print("corner", round(cd.mean() * 100, 3), "t", round(cd.mean() / se, 2), yearly)
    print(ch.round(3).to_string(index=False))
    print(pd.DataFrame(cmp_rows).round(3).to_string(index=False))
    print("leverage: T1/T0 mean", round(lev.mean(), 2), "| T1 gross mean", round(w1.abs().sum(axis=1).mean(), 2), "| cap binds in",
          int(levdf.gross_cap_binds_T1.sum()), "of", len(levdf), "month-ends")


if __name__ == "__main__":
    main()
