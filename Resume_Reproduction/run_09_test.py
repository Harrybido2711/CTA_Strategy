"""W10, part 1: the single read of the Test quarters (2025Q3 -> 2026Q2).

    .venv/bin/python Resume_Reproduction/run_09_test.py

Refuses to run unless config.py and every rr_*.py match the committed HEAD, and writes that
commit into every sidecar. Everything evaluated here was frozen before: B0's rule and B1's
switches (config.BASELINE / REBUILD), the model class (07_model_selection) and the optimizer
choice (08_optimizer_choice). The Test rungs re-choose only what every rung re-chooses.
"""
import datetime
import glob
import json
import os
import subprocess
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C                       # noqa: E402
import rr_data as D                      # noqa: E402
import rr_metrics as M                   # noqa: E402
import rr_models as MD                   # noqa: E402
import rr_optimizer as OP                # noqa: E402
import rr_portfolio as PF                # noqa: E402
import rr_rebuild as RB                  # noqa: E402
import rr_regimes as R                   # noqa: E402
import rr_signals as S                   # noqa: E402
from rr_engine import simulate           # noqa: E402
from rr_io import write_result           # noqa: E402

B0N, B1N = "B0", "B1"
PERIODS = {"2022": ("2022-01-01", "2022-12-31"), "2023": ("2023-01-01", "2023-12-31"),
           "2024H1": ("2024-01-01", "2024-06-30"), "2024H2-2025H1 (OV)": ("2024-07-01", "2025-06-30"),
           "2025H2-2026H1 (Test)": ("2025-07-01", "2026-06-30")}


def frozen_commit():
    files = [os.path.relpath(p, C.ROOT) for p in [os.path.join(C.HERE, "config.py")] + glob.glob(os.path.join(C.HERE, "rr_*.py"))]
    dirty = subprocess.run(["git", "-C", C.ROOT, "diff", "--quiet", "HEAD", "--"] + files).returncode
    if dirty:
        raise SystemExit("config.py or an rr_*.py differs from HEAD: commit before the Test read")
    return subprocess.check_output(["git", "-C", C.ROOT, "rev-parse", "--short", "HEAD"], text=True).strip()


def build(wd):
    """B0, B1 and the companions, realistic and naive, on one World."""
    bk = PF.books(wd)
    inp = RB.b1_inputs(wd)
    db = inp["scale"] * C.REBUILD["deadband_multiple"]
    w0, w1 = bk["B0 (MOM + MACD band, walk-forward)"], RB.b1_weights(wd, inp)
    run = lambda w, var, **kw: simulate(wd.open, wd.close, w, **dict(PF.VARIANTS[var], **kw))  # noqa: E731
    out = {B0N: run(w0, "realistic"), B1N: run(w1, "realistic", deadband=db),
           "B0 naive_0": run(w0, "naive_0"), "B0 naive_1": run(w0, "naive_1"),
           "B1 naive_1": run(w1, "naive_1", deadband=db),
           "B0 + deadband": run(w0, "realistic", deadband=db),
           "B0 + deadband + vol scaling": run(RB.b1_weights(wd, inp, True, 1), "realistic", deadband=db)}
    for k in ("MOM prop-signal", "MACD 12/26 prop-signal", "P1 150/50 (prototype)", "P2 median L/S (prototype)"):
        out[k] = run(bk[k], "realistic")
        out[k + " naive_1"] = run(bk[k], "naive_1")
    return out, inp, bk


def main():
    commit = frozen_commit()
    stamp = datetime.datetime.now().isoformat(timespec="seconds")
    wd = PF.World(include_test=True)
    meta0 = {"test_read": f"single read at {stamp}, frozen at commit {commit}",
             "samples": "WF = 2022Q1-2026Q2 (18 quarters); train-ladder 2022Q1-2024Q2; OV 2024Q3-2025Q2; Test 2025Q3-2026Q2"}
    runs, inp, bk = build(wd)

    # Test rungs' own choices
    sel = pd.DataFrame(wd.selections()).set_index("test_q")
    sel["band"] = sel["band"].map(lambda b: " ".join(f"{f}/{s}" for f, s in b))
    write_result(sel, "09_selected_signals_all_rungs", dict(meta0, what="per-rung MACD band, smoother and fallback, all 18 rungs"))

    # ---- scorecard (C2-C4, C20, C21)
    rows = []
    for name, res in runs.items():
        for sname, m in wd.samples.items():
            s = M.book_summary(res, mask=m)
            sd = M.book_summary(res, rf=wd.rf, mask=m)
            rows.append(dict(s.to_dict(), sharpe_dtb3=sd["sharpe"], **M.concentration(res, C.UNIVERSE_CATEGORY, mask=m).to_dict(),
                             book=name, sample=sname))
    sc = pd.DataFrame(rows).set_index(["book", "sample"])
    for sname in wd.samples:
        b0 = sc.loc[(B0N, sname)]
        for name in runs:
            sc.loc[(name, sname), "d_sharpe_vs_B0"] = sc.loc[(name, sname), "sharpe"] - b0["sharpe"]
            sc.loc[(name, sname), "d_turnover_pct_vs_B0"] = sc.loc[(name, sname), "turnover_ann_per_gross"] / b0["turnover_ann_per_gross"] - 1
    write_result(sc, "06_scorecard", dict(meta0, what="every book on every block, realistic unless the name says naive"))

    q = pd.Series([str(x) for x in wd.cal.to_period("Q")], index=wd.cal)
    byq = []
    for r in wd.rungs:
        m = pd.Series(False, index=wd.cal); m.iloc[r["test"]] = True
        s0, s1 = M.book_summary(runs[B0N], mask=m), M.book_summary(runs[B1N], mask=m)
        byq.append({"quarter": r["test_q"], "block": r["block"], "sharpe_B0": s0["sharpe"], "sharpe_B1": s1["sharpe"],
                    "d_sharpe": s1["sharpe"] - s0["sharpe"], "turnover_B0": s0["turnover_ann_per_gross"],
                    "turnover_B1": s1["turnover_ann_per_gross"], "d_turnover_pct": s1["turnover_ann_per_gross"] / s0["turnover_ann_per_gross"] - 1,
                    "ret_B0": s0["ann_return"], "ret_B1": s1["ann_return"]})
    write_result(pd.DataFrame(byq).set_index("quarter"), "06_scorecard_by_quarter", dict(meta0, what="B0 vs B1 per walk-forward quarter"))

    # ---- haircut on the full record and on Test (C13)
    hc = []
    for book, real, n1, n0 in ((B0N, runs[B0N], runs["B0 naive_1"], runs["B0 naive_0"]),
                               ("MACD 12/26 prop-signal", runs["MACD 12/26 prop-signal"], runs["MACD 12/26 prop-signal naive_1"], None),
                               ("P1 150/50 (prototype)", runs["P1 150/50 (prototype)"], runs["P1 150/50 (prototype) naive_1"], None),
                               ("P2 median L/S (prototype)", runs["P2 median L/S (prototype)"], runs["P2 median L/S (prototype) naive_1"], None)):
        for sname, m in wd.samples.items():
            yrs = m.sum() / 252
            a, r = float(n1["pnl_net"][m].sum()), float(real["pnl_net"][m].sum())
            se = M.newey_west_se(n1["pnl_net"][m], C.H)
            row = {"book": book, "sample": sname, "naive_1_cum": a, "realistic_cum": r,
                   "naive_1_ann": a / yrs, "naive_1_t": float(n1["pnl_net"][m].mean() / se) if se > 0 else np.nan,
                   "drag_bp_yr": (a - r) / yrs * 1e4, "H_1": 1 - r / a if a > 0 else np.nan,
                   "H_1_note": "" if a > 0 else "undefined: naive_1 PnL <= 0",
                   "turnover_ann_per_gross": M.annual_turnover(real["turnover_exec"][m], real["gross"][m])}
            if n0 is not None:
                z = float(n0["pnl_net"][m].sum())
                row.update({"naive_0_cum": z, "H_0": 1 - r / z if z > 0 else np.nan})
            hc.append(row)
    write_result(pd.DataFrame(hc).set_index(["book", "sample"]), "03_haircut_waterfall_test",
                 dict(meta0, what="execution haircut over all 18 quarters and on Test alone (C13)"))

    # ---- regimes with Test (C16)
    vol = D.panel(wd.etfs, "volume", wd.cal)
    V, SIG = R.volume_measure(vol), R.sigma_measure(wd.close)
    cuts = {"rolling": (R.cut_rolling(V), R.cut_rolling(SIG)),
            "frozen": (R.cut_frozen_per_rung(V, wd.cal, wd.rungs), R.cut_frozen_per_rung(SIG, wd.cal, wd.rungs)),
            "fullsample_LOOKAHEAD": (R.cut_fullsample(V, C.SAMPLE_END), R.cut_fullsample(SIG, C.SAMPLE_END))}
    reg, per = [], []
    for cname, (vl, sl) in cuts.items():
        g, pdd = R.regime_grid(wd.mom, wd.fwd, vl, sl, wd.wf)
        reg.append(g.assign(cut=cname))
        cd = R.corner_difference(pdd)
        per.append(dict(cd, cut=cname, period="WF 2022Q1-2026Q2"))
        for pname, (a, b) in PERIODS.items():
            mm = (wd.cal >= a) & (wd.cal <= b)
            per.append(dict(R.corner_difference({k: v[mm] for k, v in pdd.items()}), cut=cname, period=pname))
    write_result(pd.concat(reg).reset_index().set_index(["cut", "volume", "sigma"]), "04_regime_grid_with_test",
                 dict(meta0, what="MOM signal-weighted return per volume x sigma cell, all 18 quarters"))
    pr = pd.DataFrame(per)
    for cname in cuts:
        m = (pr.cut == cname) & pr.period.isin(PERIODS)
        pr.loc[(pr.cut == cname) & (pr.period == "WF 2022Q1-2026Q2"), "periods_positive_of_5"] = int((pr.loc[m, "diff_bp"] > 0).sum())
    write_result(pr.set_index(["cut", "period"]), "04_regime_by_period_with_test",
                 dict(meta0, what="HV/LV minus LV/HV per period; 'consistently' needs 5 of 5 (P = 1/32 under the null)"))

    # ---- models and optimizer on Test
    panel = MD.build_panel(wd)
    chosen = json.load(open(os.path.join(C.RESULTS, "07_model_selection.json")))["chosen"]
    mt = []
    test_r = [r for r in wd.rungs if r["block"] == "Test"]
    for name in MD.MODEL_ORDER:
        ps = []
        for r in test_r:
            _, p, _ = MD.fit_rung(name, panel, wd.cal, r)
            ps.append(p)
        p = pd.concat(ps); y = panel.loc[p.index, "y"]; ok = y.notna()
        ic = M.ic_series(p.unstack("asset"), y.unstack("asset")).dropna()
        mt.append({"model": name, "test_mse_x1e4": float(((y[ok] - p[ok]) ** 2).mean() * 1e4),
                   "test_mae_x1e2": float((y[ok] - p[ok]).abs().mean() * 1e2), "test_mean_ic": float(ic.mean()),
                   "chosen_on_OV": name == chosen, "zero_forecast_mse_x1e4": float((y[ok] ** 2).mean() * 1e4)})
    write_result(pd.DataFrame(mt).set_index("model"), "07_model_test",
                 dict(meta0, what="every model on the Test quarters; only the chosen one counts, the rest are labelled"))
    choice = json.load(open(os.path.join(C.RESULTS, "08_optimizer_choice.json")))
    mu, chol = OP.model_inputs(wd, panel, choice["model"])
    tau = choice["tau_multiple"] * (C.COST_BP + C.SLIP_BP) / 1e4
    dates = wd.cal[wd.wf.to_numpy()]
    opt_rows = []
    for net, label in ((0.0, "Optimizer, net 0"), (1.0, "Optimizer, net 1 (lecture)")):
        w = OP.optimized_weights(wd, mu, chol, choice["gamma"], choice["cap"], tau, net, "sample", dates)
        res = simulate(wd.open, wd.close, w, **PF.VARIANTS["realistic"])
        for sname, m in wd.samples.items():
            s = M.book_summary(res, mask=m); sd = M.book_summary(res, rf=wd.rf, mask=m)
            opt_rows.append(dict(s.to_dict(), sharpe_dtb3=sd["sharpe"], book=label, sample=sname))
    write_result(pd.DataFrame(opt_rows).set_index(["book", "sample"]), "08_optimizer_test",
                 dict(meta0, what="the OV-chosen optimizer over all 18 quarters", **{k: str(v) for k, v in choice.items()}))

    # ---- VIX / MOVE on Test: counts only
    vix, _ = D.load_index("VIX", wd.cal); move, _ = D.load_index("MOVE", wd.cal)
    lv = R.index_labels(vix, wd.cal, wd.rungs, C.SAMPLE_END); lm = R.index_labels(move, wd.cal, wd.rungs, C.SAMPLE_END)
    tm = wd.samples["Test"]
    t = R.returns_by_state(runs[B0N]["pnl_net"][tm], lv["S1 data-free"][tm], lm["S1 data-free"][tm])
    write_result(t, "05_vix_move_test", dict(meta0, what="B0 by S1 VIX x MOVE state on Test: day counts show it is not measurable"),
                 index=False)

    with open(os.path.join(C.RESULTS, "09_test_read.json"), "w") as fh:
        json.dump({"read_at": stamp, "frozen_commit": commit, "quarters": list(C.TEST_QUARTERS)}, fh, indent=2)
    print(sc.xs("Test", level="sample").loc[[B0N, B1N, "B0 naive_1", "P1 150/50 (prototype)"],
          ["ann_return", "sharpe", "sharpe_dtb3", "turnover_ann_per_gross", "d_sharpe_vs_B0", "d_turnover_pct_vs_B0"]].round(3).to_string())
    print(sc.xs("WF", level="sample").loc[[B0N, B1N], ["ann_return", "sharpe", "turnover_ann_per_gross", "d_sharpe_vs_B0", "d_turnover_pct_vs_B0"]].round(3).to_string())
    print(pd.DataFrame(hc).query("book == 'B0'").round(4).to_string(index=False))
    print(pr.query("cut == 'rolling'")[["period", "diff_bp", "t", "dates", "periods_positive_of_5"]].round(2).to_string(index=False))
    print(pd.DataFrame(mt).round(4).to_string(index=False))
    print(pd.DataFrame(opt_rows).query("sample in ['WF', 'Test']")[["book", "sample", "ann_return", "sharpe", "sharpe_dtb3", "turnover_ann_per_gross"]].round(3).to_string(index=False))
    print(sel[["block", "band", "q", "fallback_mom_only"]].tail(5).to_string())


if __name__ == "__main__":
    main()
