"""W10, part 2: the robustness protocol of OUTLINE 6, run once alongside the Test read.

    .venv/bin/python Resume_Reproduction/run_10_robustness.py

6.1  B1 vs B0: paired stationary bootstrap at five block lengths, drop-best-days, cost grid,
     truncated sample, universe without bonds, total-return prices, deflated Sharpe.
6.2  the haircut: naive edge CI, cost grid on the whole record.
6.3  the regime corner: date-block bootstrap of the corner difference.
"""
import itertools
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C                       # noqa: E402
import rr_data as D                      # noqa: E402
import rr_metrics as M                   # noqa: E402
import rr_portfolio as PF                # noqa: E402
import rr_rebuild as RB                  # noqa: E402
import rr_regimes as R                   # noqa: E402
from rr_engine import simulate           # noqa: E402
from rr_io import write_result           # noqa: E402
from run_09_test import build, frozen_commit  # noqa: E402

BLOCKS = (5, 10, 21, 42, 63)
DRAWS = 2000
BONDS = [t for t, c in C.UNIVERSE_CATEGORY.items() if c == "bonds"]


def ci(x, lo, hi):
    x = x[np.isfinite(x)]
    return (float(np.quantile(x, lo)), float(np.quantile(x, hi))) if len(x) else (np.nan, np.nan)


def paired_bootstrap(r0, r1, to0, g0, to1, g1, label):
    rows = []
    a0, a1 = r0.to_numpy(), r1.to_numpy()
    t0, gg0, t1, gg1 = (x.to_numpy() for x in (to0, g0, to1, g1))
    for b in BLOCKS:
        idx = M.stationary_bootstrap_indices(len(a0), b, DRAWS, seed=b)
        s0, s1 = M.sharpe_rows(a0[idx]), M.sharpe_rows(a1[idx])
        d = s1 - s0
        dto = (t1[idx].mean(axis=1) / gg1[idx].mean(axis=1)) / (t0[idx].mean(axis=1) / gg0[idx].mean(axis=1)) - 1
        pct = np.where(np.abs(s0) > 1e-12, d / s0, np.nan)
        row = {"sample": label, "mean_block": b, "draws": DRAWS}
        for name, x in (("sharpe_B0", s0), ("d_sharpe", d), ("d_turnover_pct", dto), ("pct_d_sharpe", pct)):
            row[f"{name}_90_lo"], row[f"{name}_90_hi"] = ci(x, 0.05, 0.95)
            row[f"{name}_95_lo"], row[f"{name}_95_hi"] = ci(x, 0.025, 0.975)
        rows.append(row)
    return rows


def delta(runs, m):
    s0, s1 = M.book_summary(runs["B0"], mask=m), M.book_summary(runs["B1"], mask=m)
    return {"sharpe_B0": s0["sharpe"], "sharpe_B1": s1["sharpe"], "d_sharpe": s1["sharpe"] - s0["sharpe"],
            "turnover_B0": s0["turnover_ann_per_gross"], "turnover_B1": s1["turnover_ann_per_gross"],
            "d_turnover_pct": s1["turnover_ann_per_gross"] / s0["turnover_ann_per_gross"] - 1,
            "ret_B0": s0["ann_return"], "ret_B1": s1["ann_return"]}


def main():
    commit = frozen_commit()
    meta0 = {"frozen_commit": commit, "draws": DRAWS, "blocks": " ".join(map(str, BLOCKS)),
             "samples": "WF = 2022Q1-2026Q2 (18 quarters); Test = 2025Q3-2026Q2"}
    wd = PF.World(include_test=True)
    runs, inp, bk = build(wd)
    wf, test = wd.samples["WF"], wd.samples["Test"]

    # ---- 6.1 bootstrap
    rows = []
    for label, m in (("WF", wf), ("Test", test)):
        rows += paired_bootstrap(runs["B0"]["pnl_net"][m], runs["B1"]["pnl_net"][m], runs["B0"]["turnover_exec"][m],
                                 runs["B0"]["gross"][m], runs["B1"]["turnover_exec"][m], runs["B1"]["gross"][m], label)
    boot = pd.DataFrame(rows).set_index(["sample", "mean_block"])

    # ---- 6.1 point checks: drop best days, cost grid, alternative worlds
    checks = [dict(delta(runs, wf), check="headline", sample="WF"), dict(delta(runs, test), check="headline", sample="Test")]
    d = (runs["B1"]["pnl_net"] - runs["B0"]["pnl_net"])[wf]
    top = d.abs().sort_values(ascending=False)
    for k in (5, 10):
        m = wf.copy(); m.loc[top.index[:k]] = False
        checks.append(dict(delta(runs, m), check=f"drop the {k} days with the largest |r_B1 - r_B0|", sample="WF"))
    share_top5 = float(d.loc[top.index[:5]].sum() / d.sum()) if d.sum() != 0 else np.nan
    w0, w1 = bk["B0 (MOM + MACD band, walk-forward)"], RB.b1_weights(wd, inp)
    db = inp["scale"] * C.REBUILD["deadband_multiple"]
    for c, s, b in itertools.product((2, 5, 10), (0, 2, 5), (0, 25, 50)):
        kw = dict(lag=C.LAG, exec_price=C.EXEC_PRICE, cost_bp=c, slip_bp=s, borrow_bp=b)
        rr = {"B0": simulate(wd.open, wd.close, w0, **kw), "B1": simulate(wd.open, wd.close, w1, deadband=db, **kw)}
        checks.append(dict(delta(rr, wf), check=f"cost {c} bp, slip {s} bp, borrow {b} bp/yr", sample="WF"))
    alt = {"truncated at 2025-12-04": dict(end="2025-12-04"),
           "universe without the 7 bond ETFs": dict(universe=[t for t in C.UNIVERSE_CATEGORY if t not in BONDS]),
           "total-return prices (distributions reinvested)": dict(total_return=True)}
    for name, kw in alt.items():
        w2 = PF.World(include_test=True, **kw)
        r2, _, _ = build(w2)
        for label in ("WF", "Test"):
            if label in w2.samples and w2.samples[label].any():
                checks.append(dict(delta(r2, w2.samples[label]), check=name, sample=label))
    chk = pd.DataFrame(checks).set_index(["check", "sample"])

    # ---- 6.1 deflation on the OV Sharpe of B1
    ov = wd.samples["OV"]
    sens = C.REBUILD["ov_sensitivity"]
    trials, srs = [], []
    for eta, kap, scope in itertools.product(sens["deadband_multiple"], sens["kappa"], sens["kappa_scope"]):
        res = simulate(wd.open, wd.close, RB.b1_weights(wd, inp, True, kap, scope), deadband=inp["scale"] * eta,
                       **PF.VARIANTS["realistic"])
        x = res["pnl_net"][ov].to_numpy()
        trials.append(x); srs.append(x.mean() / x.std(ddof=1))
    led = pd.read_csv(os.path.join(C.RESULTS, "run_ledger.csv"), comment="#")
    n_ov_reads = int(led["stage"].isin(["rebuild OV grid", "optimizer OV grid"]).sum()) + 12   # + the 12 models compared on OV
    b1_ov = runs["B1"]["pnl_net"][ov]
    defl = []
    for label, n in (("B1 family on OV (32)", len(trials)), ("every OV read (W7 + W8 + W9)", n_ov_reads),
                     ("B1 family, effective at corr 0.9", M.effective_trials(trials, 0.9)),
                     ("B1 family, effective at corr 0.8", M.effective_trials(trials, 0.8))):
        defl.append(dict(M.deflated_sharpe(b1_ov, srs, n), trials_label=label))
    dfl = pd.DataFrame(defl).set_index("trials_label")

    # ---- 6.2 haircut robustness
    hc = []
    n1 = runs["B0 naive_1"]["pnl_net"][wf].to_numpy()
    for b in BLOCKS:
        idx = M.stationary_bootstrap_indices(len(n1), b, DRAWS, seed=100 + b)
        mean_ann = n1[idx].mean(axis=1) * 252
        lo90, hi90 = ci(mean_ann, 0.05, 0.95)
        hc.append({"check": "B0 naive_1 annual return, bootstrap", "mean_block": b, "point": float(n1.mean() * 252),
                   "ci90_lo": lo90, "ci90_hi": hi90})
    yrs = wf.sum() / 252
    base = float(runs["B0 naive_1"]["pnl_net"][wf].sum())
    grid = [dict(cost_bp=c, slip_bp=s) for c in (0, 2, 5, 10, 20) for s in (0, 2, 5, 10)]
    grid += [dict(lag=dd) for dd in (2, 3)] + [dict(exec_price="twap")] + [dict(borrow_bp=bb) for bb in (25, 50)]
    for g in grid:
        kw = dict(PF.VARIANTS["realistic"]); kw.update(g)
        r = float(simulate(wd.open, wd.close, w0, **kw)["pnl_net"][wf].sum())
        hc.append({"check": "B0 cost grid, WF", **g, "realistic_cum": r, "drag_vs_naive1_bp_yr": (base - r) / yrs * 1e4,
                   "H_1": 1 - r / base if base > 0 else np.nan})
    hcd = pd.DataFrame(hc)

    # ---- 6.3 regime corner bootstrap (rolling cut, MOM, all 18 quarters)
    vol = D.panel(wd.etfs, "volume", wd.cal)
    vl, sl = R.cut_rolling(R.volume_measure(vol)), R.cut_rolling(R.sigma_measure(wd.close))
    _, pdd = R.regime_grid(wd.mom, wd.fwd, vl, sl, wd.wf)
    cd = (pdd[("high", "low")] - pdd[("low", "high")]).dropna().to_numpy()
    rb = []
    for b in BLOCKS:
        idx = M.stationary_bootstrap_indices(len(cd), b, DRAWS, seed=200 + b)
        mm = cd[idx].mean(axis=1) * 1e4
        lo, hi = ci(mm, 0.05, 0.95)
        rb.append({"mean_block": b, "point_bp": float(cd.mean() * 1e4), "ci90_lo_bp": lo, "ci90_hi_bp": hi, "dates": len(cd)})

    write_result(boot, "08_robustness_rebuild_bootstrap", dict(meta0, what="paired stationary bootstrap of B1 vs B0 (C20, C21)"))
    write_result(chk, "08_robustness_rebuild", dict(meta0, what="B1 vs B0 under drop-best-days, cost grid and alternative samples",
                                                    share_of_d_pnl_in_top5_days=f"{share_top5:.3f}"))
    write_result(dfl, "08_deflation", dict(meta0, what="deflated Sharpe of B1's OV Sharpe against the trials read on OV"))
    write_result(hcd, "08_robustness_haircut", dict(meta0, what="naive edge CI and B0's cost grid over all 18 quarters (C13)"), index=False)
    write_result(pd.DataFrame(rb).set_index("mean_block"), "04_regime_bootstrap",
                 dict(meta0, what="HV/LV minus LV/HV, rolling cut, MOM: date-block bootstrap of the per-date difference (C16)"))

    print(boot[["d_sharpe_90_lo", "d_sharpe_90_hi", "sharpe_B0_90_lo", "sharpe_B0_90_hi", "d_turnover_pct_90_lo", "d_turnover_pct_90_hi"]].round(3).to_string())
    print(chk[["sharpe_B0", "sharpe_B1", "d_sharpe", "d_turnover_pct"]].round(3).to_string())
    print("share of B1-B0 PnL from its top 5 days:", round(share_top5, 3))
    print(dfl.round(4).to_string())
    print(hcd[hcd.check.str.contains("bootstrap")].round(4).to_string(index=False))
    print(pd.DataFrame(rb).round(2).to_string(index=False))


if __name__ == "__main__":
    main()
