"""W7: B1 through the ladder, its ablation, and the OV sensitivity grid.

    .venv/bin/python Resume_Reproduction/run_06_rebuild.py

B1 is config.REBUILD, written before any rung ran; the OV grid is a read, not a selection.
Train-ladder and OV quarters only; Test is read in W10.
"""
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
import rr_portfolio as PF                # noqa: E402
import rr_rebuild as RB                  # noqa: E402
import rr_regimes as R                   # noqa: E402
import rr_signals as S                   # noqa: E402
from rr_engine import simulate           # noqa: E402
from rr_io import write_result           # noqa: E402

RB_CFG = C.REBUILD


def main():
    wd = PF.World()
    score = wd.b0_score()
    sig = S.sigma(S.returns(wd.close))
    vol = D.panel(wd.etfs, "volume", wd.cal)
    vlab, slab = R.cut_rolling(R.volume_measure(vol)), R.cut_rolling(R.sigma_measure(wd.close))
    scale, per_rung = PF.b0_deadband_scale(wd)

    def book(vol_scaling, kappa, scope, eta):
        w = wd.from_start(RB.overlap(RB.targets(score, sig, vlab, slab, vol_scaling, kappa, scope)))
        return simulate(wd.open, wd.close, w, deadband=scale * eta, **PF.VARIANTS["realistic"])

    k, sc, e = RB_CFG["kappa"], RB_CFG["kappa_scope"], RB_CFG["deadband_multiple"]
    variants = {
        "B0": (False, 1, sc, 0.0),
        "B0 + deadband": (False, 1, sc, e),
        "B0 + deadband + vol scaling": (True, 1, sc, e),
        "B1 = B0 + deadband + vol scaling + regime": (True, k, sc, e),
        "B1 without deadband": (True, k, sc, 0.0),
        "B1 without vol scaling": (False, k, sc, e),
        "B1 without regime": (True, 1, sc, e),
    }
    runs = {name: book(*cfg) for name, cfg in variants.items()}
    rows = []
    for name, res in runs.items():
        for sname, m in wd.samples.items():
            s = M.book_summary(res, mask=m)
            c = M.concentration(res, C.UNIVERSE_CATEGORY, mask=m)
            rows.append(dict(s.to_dict(), **c.to_dict(), variant=name, sample=sname))
    ab = pd.DataFrame(rows).set_index(["variant", "sample"])
    for sname in wd.samples:
        b0 = ab.loc[("B0", sname)]
        for name in variants:
            ab.loc[(name, sname), "d_sharpe_vs_B0"] = ab.loc[(name, sname), "sharpe"] - b0["sharpe"]
            ab.loc[(name, sname), "d_turnover_pct_vs_B0"] = ab.loc[(name, sname), "turnover_ann_per_gross"] / b0["turnover_ann_per_gross"] - 1
    meta = {"what": "B0 -> B1 ablation, realistic execution (next close, 5 bp + 2 bp), rf = 0 (net 0 books)",
            "B1": json.dumps({k2: v for k2, v in RB_CFG.items() if k2 != "ov_sensitivity"}),
            "deadband_scale_per_rung": " ".join(f"{q}:{v:.5f}" for q, v in per_rung.items()),
            "samples": "WF = 2022Q1-2025Q2; train-ladder = 2022Q1-2024Q2; OV = 2024Q3-2025Q2"}
    write_result(ab, "06_rebuild_ablation", meta)

    # cap binding share for B1's daily targets
    t1 = RB.targets(score, sig, vlab, slab, True, k, sc)
    pre = RB.demean_renorm(score / sig)
    m = wd.wf
    cap_share = float((pre[m].abs() > RB_CFG["cap"]).sum().sum() / pre[m].notna().sum().sum())

    # OV sensitivity grid: a read, not a selection
    grid = []
    sens = RB_CFG["ov_sensitivity"]
    ov = wd.samples["OV"]
    for eta, kap, scope in itertools.product(sens["deadband_multiple"], sens["kappa"], sens["kappa_scope"]):
        res = book(True, kap, scope, eta)
        r = res["pnl_net"][ov]
        grid.append({"deadband_multiple": eta, "kappa": kap, "scope": scope, "sharpe": M.sharpe(r),
                     "mean_net_per_gross_bp_day": float((r / res["gross"][ov]).mean() * 1e4),
                     "se_bp_day": float(M.newey_west_se(r / res["gross"][ov], C.H) * 1e4),
                     "turnover_ann_per_gross": M.annual_turnover(res["turnover_exec"][ov], res["gross"][ov]),
                     "pre_specified": (eta, kap, scope) == (e, k, sc)})
    g = pd.DataFrame(grid)
    best = g.loc[g.mean_net_per_gross_bp_day.idxmax()]
    g["within_one_se_of_best"] = g.mean_net_per_gross_bp_day >= best.mean_net_per_gross_bp_day - best.se_bp_day
    write_result(g.set_index(["deadband_multiple", "kappa", "scope"]), "06_rebuild_grid_OV",
                 dict(meta, what="OV sensitivity grid for B1: a read, not a selection; B1 is the pre_specified row",
                      plateau=f"{int(g.within_one_se_of_best.sum())} of {len(g)} cells within one SE of the best OV mean",
                      cap_binding_share=f"{cap_share:.3f} of asset-days where |w| would exceed {RB_CFG['cap']} before the cap"))

    # what each switch did on OV, written before Test is read
    ovr = ab.xs("OV", level="sample")
    wording = {
        "written": "before any Test quarter is read (W7)",
        "deadband": {"d_sharpe": float(ovr.loc["B0 + deadband", "d_sharpe_vs_B0"]),
                     "d_turnover_pct": float(ovr.loc["B0 + deadband", "d_turnover_pct_vs_B0"])},
        "vol scaling (after deadband)": {"d_sharpe": float(ovr.loc["B0 + deadband + vol scaling", "sharpe"] - ovr.loc["B0 + deadband", "sharpe"]),
                                         "d_turnover_pct": float(ovr.loc["B0 + deadband + vol scaling", "turnover_ann_per_gross"] / ovr.loc["B0 + deadband", "turnover_ann_per_gross"] - 1)},
        "regime (after both)": {"d_sharpe": float(ovr.loc["B1 = B0 + deadband + vol scaling + regime", "sharpe"] - ovr.loc["B0 + deadband + vol scaling", "sharpe"]),
                                "d_turnover_pct": float(ovr.loc["B1 = B0 + deadband + vol scaling + regime", "turnover_ann_per_gross"] / ovr.loc["B0 + deadband + vol scaling", "turnover_ann_per_gross"] - 1)},
        "B1 vs B0 on OV": {"d_sharpe": float(ovr.loc["B1 = B0 + deadband + vol scaling + regime", "d_sharpe_vs_B0"]),
                           "d_turnover_pct": float(ovr.loc["B1 = B0 + deadband + vol scaling + regime", "d_turnover_pct_vs_B0"])},
    }
    with open(os.path.join(C.RESULTS, "06_rebuild_wording_OV.json"), "w") as fh:
        json.dump(wording, fh, indent=2)

    # ledger: every OV read
    p = os.path.join(C.RESULTS, "run_ledger.csv")
    head = [l for l in open(p) if l.startswith("#")]
    led = pd.read_csv(p, comment="#")
    led = led[led.workstream != "W7"]
    add = [{"workstream": "W7", "test_q": "OV", "stage": "rebuild OV grid", "sample": "OV quarters",
            "params": f"eta={r.deadband_multiple} kappa={r.kappa} scope={r.scope}", "spread": r.mean_net_per_gross_bp_day,
            "selected": bool(r.pre_specified)} for r in g.itertuples()]
    led = pd.concat([led, pd.DataFrame(add)], ignore_index=True)
    with open(p, "w") as fh:
        fh.writelines(head); led.to_csv(fh, index=False)

    cols = ["ann_return", "sharpe", "d_sharpe_vs_B0", "turnover_ann_per_gross", "d_turnover_pct_vs_B0", "max_abs_weight", "pnl_share_bonds"]
    for sname in wd.samples:
        print(f"== {sname}"); print(ab.xs(sname, level="sample")[cols].round(3).to_string())
    print(f"cap binding share {cap_share:.3f}; OV plateau {int(g.within_one_se_of_best.sum())}/{len(g)}")
    print(g.sort_values("mean_net_per_gross_bp_day", ascending=False).head(6).round(3).to_string(index=False))


if __name__ == "__main__":
    main()
