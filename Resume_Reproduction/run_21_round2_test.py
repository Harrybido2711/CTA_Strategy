"""Round 2: the single Test read (2025-07 -> 2026-06) and its robustness protocol.

    .venv/bin/python Resume_Reproduction/run_21_round2_test.py

Refuses to run unless config.py and every rr_*.py match HEAD. T0-T3 are frozen: the paper's
parameters, T2's and T3's m from results/20_regime_multiplier and 20b_t3_multiplier. Test was read
once already in Round 1 for different books; this is the second look at those quarters.
"""
import datetime
import itertools
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C                       # noqa: E402
import rr_data as D                      # noqa: E402
import rr_metrics as M                   # noqa: E402
import rr_regimes as R                   # noqa: E402
import rr_tsmom as T                     # noqa: E402
from rr_engine import simulate           # noqa: E402
from rr_io import write_result           # noqa: E402
from run_09_test import frozen_commit    # noqa: E402
from run_20_round2 import R2              # noqa: E402

P = C.ROUND2
SAMPLES = {"full 2021-02..2026-06": ("2021-02-01", "2026-06-29"), "pre-Test 2021-02..2025-06": ("2021-02-01", "2025-06-30"),
           "Test 2025-07..2026-06": ("2025-07-01", "2026-06-29")}
BLOCKS = (5, 10, 21, 42, 63)
BONDS = [t for t, c in C.UNIVERSE_CATEGORY.items() if c == "bonds"]


def chosen(name):
    return float(pd.read_csv(os.path.join(C.RESULTS, f"{name}.csv"), comment="#").query("chosen == True").iloc[0]["m"])


def books(r2, m2, m3, last_day):
    w0 = r2.t0()
    w1, lev = T.t1_targets(w0, r2.xr)
    w2 = T.t2_targets(w1, r2.high.reindex(w1.index), m2)
    w3, lev3 = T.t3_targets(w0, r2.xr, r2.cal, r2.high, m3, P["first_signal"], last_day)
    sim3 = lambda **kw: simulate(r2.wd.open, r2.wd.close, w3, lag=C.LAG, exec_price="close", deadband=P["deadband"], **kw)  # noqa: E731
    runs = {"T0 naive_0": r2.run(w0, "naive_0"), "T0 naive_1": r2.run(w0, "naive_1"), "T0": r2.run(w0, "realistic"),
            "T1": r2.run(w1, "realistic"), "T1 naive_1": r2.run(w1, "naive_1"),
            f"T2 (m={m2})": r2.run(w2, "realistic", trade_deadband=P["deadband"]),
            f"T3 (m={m3})": sim3(cost_bp=C.COST_BP, slip_bp=C.SLIP_BP), f"T3 (m={m3}) naive_1": sim3(cost_bp=0, slip_bp=0)}
    return runs, (w0, w1, w2, w3), lev


def main():
    commit = frozen_commit()
    stamp = datetime.datetime.now().isoformat(timespec="seconds")
    m2, m3 = chosen("20_regime_multiplier"), chosen("20b_t3_multiplier")
    r2 = R2(last_me="2026-05-29")
    rf = r2.wd.rf
    runs, ws, lev = books(r2, m2, m3, "2026-06-26")
    meta = {"round": "2 (ROUND2.md)", "test_read": f"Round 2 Test read at {stamp}, frozen at {commit}; "
            "Round 1 had already read these quarters for other books", "sharpe": "excess of DTB3 x net",
            "execution": "realistic = next close, 5 bp + 2 bp", "m": f"T2 m={m2}, T3 m={m3} (chosen pre-Test)"}

    rows = []
    for name, res in runs.items():
        for sn, (a, b) in SAMPLES.items():
            rows.append(dict(r2.summary(res, r2.mask(a, b)), book=name, sample=sn))
    sc = pd.DataFrame(rows).set_index(["book", "sample"])
    write_result(sc, "21_scorecard", dict(meta, what="T0-T3 on the full record, pre-Test and Test"))

    hc = []
    for sn, (a, b) in SAMPLES.items():
        m = r2.mask(a, b); yrs = m.sum() / 252
        z, n1, r = (float(runs[k]["pnl_net"][m].sum()) for k in ("T0 naive_0", "T0 naive_1", "T0"))
        c = float(r2.run(ws[0], "realistic", slip_bp=0)["pnl_net"][m].sum())
        hc.append({"sample": sn, "naive_0_ann_bp": z / yrs * 1e4, "delay_bp": (n1 - z) / yrs * 1e4, "cost_bp": (c - n1) / yrs * 1e4,
                   "slip_bp": (r - c) / yrs * 1e4, "realistic_ann_bp": r / yrs * 1e4,
                   "H_1": 1 - r / n1 if n1 > 0 else np.nan, "H_0": 1 - r / z if z > 0 else np.nan,
                   "note": "" if n1 > 0 else "H_1 undefined: naive_1 PnL <= 0"})
    write_result(pd.DataFrame(hc).set_index("sample"), "21_haircut_T0", dict(meta, what="T0 haircut, raw PnL per $1, stated order"))

    reg = []
    for name in ("T0", "T1", f"T3 (m={m3})"):
        res = runs[name]
        x = M.excess_returns(res["pnl_net"], rf, res["net"])
        for cut in ("D rolling", "S1 data-free"):
            lab = r2.vix_lab[cut]
            for sn, (a, b) in SAMPLES.items():
                for st in (0, 1, 2):
                    mm = r2.mask(a, b) & (lab == st)
                    xs = x[mm]
                    reg.append({"book": name, "cut": cut, "sample": sn, "state": ["low", "mid", "high"][st], "days": int(len(xs)),
                                "ann_excess": float(xs.mean() * 252) if len(xs) else np.nan,
                                "sharpe": float(xs.mean() / xs.std() * np.sqrt(252)) if len(xs) > 2 and xs.std() > 0 else np.nan,
                                "measurable": int(len(xs)) >= 60})
    write_result(pd.DataFrame(reg).set_index(["book", "cut", "sample", "state"]), "21_regime_returns",
                 dict(meta, what="excess returns by VIX state, with Test"))

    vol_panel = D.panel(r2.wd.etfs, "volume", r2.cal)
    vlab, slab = R.cut_rolling(R.volume_measure(vol_panel)), R.cut_rolling(R.sigma_measure(r2.wd.close))
    sig = T.tsmom_signal(r2.xr, P["lookback_months"]).loc[r2.me]
    c = r2.wd.close.ffill()
    fwd = (c.shift(-(1 + P["month_days"])) / c.shift(-1) - 1).loc[r2.me]
    fwd = fwd.sub(rf.rolling(P["month_days"]).sum().shift(-(1 + P["month_days"])).reindex(r2.me), axis=0)
    swr = sig * fwd
    pm = {}
    for vn, sn_ in (("high", "low"), ("low", "high")):
        inc = (vlab.loc[r2.me] == R.LABELS.index(vn)) & (slab.loc[r2.me] == R.LABELS.index(sn_)) & swr.notna()
        pm[(vn, sn_)] = swr.where(inc).mean(axis=1)
    cd = (pm[("high", "low")] - pm[("low", "high")]).dropna()
    periods = {"2021": ("2021-01-01", "2021-12-31"), "2022": ("2022-01-01", "2022-12-31"), "2023": ("2023-01-01", "2023-12-31"),
               "2024": ("2024-01-01", "2024-12-31"), "2025H1": ("2025-01-01", "2025-06-30"), "Test 2025H2-2026H1": ("2025-07-01", "2026-06-30")}
    cr = []
    for pn, (a, b) in list(periods.items()) + [("full", ("2021-01-01", "2026-06-30"))]:
        x = cd[(cd.index >= a) & (cd.index <= b)]
        se = M.newey_west_se(x, 1) if len(x) > 2 else np.nan
        cr.append({"period": pn, "corner_pct_per_month": float(x.mean() * 100) if len(x) else np.nan,
                   "t": float(x.mean() / se) if se and se > 0 else np.nan, "months": int(len(x))})
    crd = pd.DataFrame(cr)
    crd.loc[crd.period == "full", "periods_positive"] = f"{int((crd[crd.period != 'full'].corner_pct_per_month > 0).sum())} of {len(periods)}"
    write_result(crd.set_index("period"), "21_regime_corner_tsmom",
                 dict(meta, what="HV/LV minus LV/HV, sign(12-month excess return) x next-month excess return, rolling cut"))

    # ---- robustness
    boot = []
    x0 = M.excess_returns(runs["T0"]["pnl_net"], rf, runs["T0"]["net"])
    for name in ("T1", f"T3 (m={m3})"):
        x1 = M.excess_returns(runs[name]["pnl_net"], rf, runs[name]["net"])
        for sn, (a, b) in SAMPLES.items():
            m = r2.mask(a, b)
            a0, a1 = x0[m].to_numpy(), x1[m].to_numpy()
            t0, t1 = runs["T0"]["turnover_exec"][m].to_numpy(), runs[name]["turnover_exec"][m].to_numpy()
            for bl in BLOCKS:
                idx = M.stationary_bootstrap_indices(len(a0), bl, 2000, seed=bl)
                s0, s1 = M.sharpe_rows(a0[idx]), M.sharpe_rows(a1[idx])
                d = s1 - s0
                dto = t1[idx].mean(axis=1) / t0[idx].mean(axis=1) - 1
                boot.append({"book": name, "sample": sn, "mean_block": bl, "d_sharpe_90_lo": np.quantile(d, 0.05),
                             "d_sharpe_90_hi": np.quantile(d, 0.95), "sharpe_T0_90_lo": np.quantile(s0, 0.05),
                             "sharpe_T0_90_hi": np.quantile(s0, 0.95), "sharpe_book_90_lo": np.quantile(s1, 0.05),
                             "sharpe_book_90_hi": np.quantile(s1, 0.95), "d_turnover_90_lo": np.quantile(dto, 0.05),
                             "d_turnover_90_hi": np.quantile(dto, 0.95)})
    write_result(pd.DataFrame(boot).set_index(["book", "sample", "mean_block"]), "21_bootstrap",
                 dict(meta, what="paired stationary bootstrap against T0, 2000 draws, 90% intervals"))

    chk = []
    full = r2.mask(*SAMPLES["full 2021-02..2026-06"])
    for cst, slp, brw in itertools.product((2, 5, 10), (0, 2, 5), (0, 25, 50)):
        for name, w in (("T0", ws[0]), ("T1", ws[1])):
            res = r2.run(w, "realistic", cost_bp=cst, slip_bp=slp, borrow_bp=brw)
            s = r2.summary(res, full)
            chk.append({"check": f"cost {cst} bp, slip {slp} bp, borrow {brw} bp/yr", "book": name, "sample": "full",
                        "sharpe": s["sharpe"], "ann_excess": s["ann_excess"]})
    alts = {"price return, no distributions": dict(total_return=False), "without the 7 bond ETFs": dict(universe=[t for t in C.UNIVERSE_CATEGORY if t not in BONDS]),
            "truncated at 2025-12-04": dict(end="2025-12-04", last_me="2025-10-31")}
    for an, kw in alts.items():
        last_me = kw.pop("last_me", "2026-05-29")
        ra = R2(last_me=last_me, **kw)
        last_day = str(ra.cal.max().date())
        rr_, _, _ = books(ra, m2, m3, last_day)
        for name in ("T0", "T1", f"T3 (m={m3})"):
            for sn, (a, b) in SAMPLES.items():
                m = ra.mask(a, b)
                if m.sum() < 20:
                    continue
                s = ra.summary(rr_[name], m)
                chk.append({"check": an, "book": name, "sample": sn, "sharpe": s["sharpe"], "ann_excess": s["ann_excess"],
                            "max_dd_units": s["max_dd_units"]})
    write_result(pd.DataFrame(chk).set_index(["check", "book", "sample"]), "21_robustness",
                 dict(meta, what="cost and borrow grid, price-return, ex-bond and truncated reruns"))

    grid = []
    for k in P["lookback_grid_months"]:
        for h in P["holding_grid_months"]:
            res = r2.run(r2.t0(k, h), "realistic")
            for sn, (a, b) in SAMPLES.items():
                s = r2.summary(res, r2.mask(a, b))
                grid.append({"k_months": k, "h_months": h, "sample": sn, "sharpe": s["sharpe"], "ann_excess": s["ann_excess"],
                             "turnover_ann": s["turnover_ann"]})
    write_result(pd.DataFrame(grid).set_index(["k_months", "h_months", "sample"]), "21_tsmom_grid",
                 dict(meta, what="the truncated Table 2 grid on every sample, realistic, descriptive"))

    with open(os.path.join(C.RESULTS, "21_test_read.json"), "w") as fh:
        json.dump({"read_at": stamp, "frozen_commit": commit, "m_T2": m2, "m_T3": m3,
                   "note": "second look at these quarters; Round 1 read them first"}, fh, indent=2)

    cols = ["ann_return", "ann_excess", "ann_vol", "sharpe", "t_excess", "max_dd_units", "turnover_ann", "gross_mean", "net_mean"]
    for sn in SAMPLES:
        print(f"== {sn}"); print(sc.xs(sn, level="sample")[cols].round(3).to_string())
    print(pd.DataFrame(hc).round(3).to_string(index=False))
    print(crd.round(3).to_string(index=False))
    b = pd.DataFrame(boot).query("mean_block == 21")
    print(b.round(3).to_string(index=False))
    print(pd.DataFrame(chk).query("check in @list(@alts)").round(3).to_string(index=False))
    print(pd.DataFrame(reg).query("cut == 'D rolling' and book == 'T0'").round(3).to_string(index=False))


if __name__ == "__main__":
    main()
