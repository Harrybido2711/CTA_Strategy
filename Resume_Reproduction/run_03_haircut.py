"""W4, part 2 (C9-C13): the execution haircut, its attribution, its sensitivity, and the deadband.

    .venv/bin/python Resume_Reproduction/run_03_haircut.py

H = 1 - PnL_realistic / PnL_naive, cumulative PnL per $1 on identical dates (OUTLINE C13).
H_1 is against the feasible frictionless book (next close, no cost); H_0 against the same-close
book, which no one can trade. When the naive PnL is not positive the ratio is undefined and only
the drag in bp per year is reported. Train-ladder and OV quarters only; Test is read in W10.
"""
import itertools
import math
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C                       # noqa: E402
import rr_metrics as M                   # noqa: E402
import rr_portfolio as PF                # noqa: E402
from rr_engine import simulate           # noqa: E402
from rr_io import write_result           # noqa: E402

HAIRCUT_BOOKS = ("B0 (MOM + MACD band, walk-forward)", "MACD 12/26 prop-signal", "P1 150/50 (prototype)",
                 "P2 median L/S (prototype)")


def cum(res, m):
    return float(res["pnl_net"][m].sum())


def ratio(naive, real):
    return 1.0 - real / naive if naive > 0 else np.nan


def main():
    wd = PF.World()
    bk = PF.books(wd)
    years = {k: m.sum() / 252.0 for k, m in wd.samples.items()}

    def run(w, **kw):
        base = dict(PF.VARIANTS["realistic"]); base.update(kw)
        return simulate(wd.open, wd.close, w, **base)

    # ---- waterfall and attribution per book and sample
    wf_rows, shap_rows = [], []
    for name in HAIRCUT_BOOKS:
        w = bk[name]
        n1 = run(w, cost_bp=0, slip_bp=0)                     # naive_1
        n1c = run(w, slip_bp=0)                               # + cost
        real = run(w)                                         # + cost + slip
        real_d2 = run(w, lag=2)
        cfg = {}
        for d, c, s in itertools.product((0, 1), (0, 1), (0, 1)):
            cfg[(d, c, s)] = run(w, lag=d, cost_bp=C.COST_BP * c, slip_bp=C.SLIP_BP * s)
        for sname, m in wd.samples.items():
            a, b, r, r2 = cum(n1, m), cum(n1c, m), cum(real, m), cum(real_d2, m)
            naive0 = cum(cfg[(0, 0, 0)], m)
            nw_se = M.newey_west_se(n1["pnl_net"][m], C.H) * 252
            wf_rows.append({
                "book": name, "sample": sname, "years": years[sname],
                "naive_0_cum": naive0, "naive_1_cum": a, "after_cost_cum": b, "realistic_cum": r,
                "naive_1_ann": a / years[sname], "naive_1_ann_t": (a / years[sname]) / nw_se if nw_se > 0 else np.nan,
                "cost_drag_bp_yr": (a - b) / years[sname] * 1e4, "slip_drag_bp_yr": (b - r) / years[sname] * 1e4,
                "delay_d1_to_d2_bp_yr": (r - r2) / years[sname] * 1e4,
                "H_1": ratio(a, r), "H_0": ratio(naive0, r),
                "H_1_note": "" if a > 0 else "undefined: naive_1 PnL <= 0",
                "turnover_ann_per_gross": M.annual_turnover(real["turnover_exec"][m], real["gross"][m]),
            })
            # Shapley over delay, cost, slip from naive_0 to realistic
            v = {k: cum(res, m) for k, res in cfg.items()}
            phi = {}
            for i, label in enumerate(("delay", "cost", "slip")):
                tot = 0.0
                for order in itertools.permutations(range(3)):
                    on = [0, 0, 0]
                    for j in order:
                        before = v[tuple(on)]
                        on[j] = 1
                        if j == i:
                            tot += before - v[tuple(on)]
                            break
                phi[label] = tot / 6.0
            orders = []
            for order in itertools.permutations(range(3)):
                on = [0, 0, 0]; contrib = {}
                for j in order:
                    before = v[tuple(on)]; on[j] = 1
                    contrib[j] = before - v[tuple(on)]
                orders.append(contrib)
            for i, label in enumerate(("delay", "cost", "slip")):
                vals = [o[i] for o in orders]
                shap_rows.append({"book": name, "sample": sname, "switch": label,
                                  "shapley_cum": phi[label], "shapley_bp_yr": phi[label] / years[sname] * 1e4,
                                  "min_over_orders_bp_yr": min(vals) / years[sname] * 1e4,
                                  "max_over_orders_bp_yr": max(vals) / years[sname] * 1e4,
                                  "share_of_naive_0": phi[label] / v[(0, 0, 0)] if v[(0, 0, 0)] > 0 else np.nan})
    meta = {"what": "execution haircut: naive -> realistic, cumulative PnL per $1 on identical dates",
            "realistic": "lag 1 trading row, next close, 5 bp per side + 2 bp slippage, no borrow",
            "H_1": "1 - realistic / naive_1 (feasible frictionless); undefined when naive_1 <= 0",
            "H_0": "1 - realistic / naive_0 (same-close, non-executable benchmark)",
            "samples": "WF = 2022Q1-2025Q2; train-ladder = 2022Q1-2024Q2; OV = 2024Q3-2025Q2"}
    write_result(pd.DataFrame(wf_rows).set_index(["book", "sample"]), "03_haircut_waterfall", meta)
    write_result(pd.DataFrame(shap_rows).set_index(["book", "sample", "switch"]), "03_haircut_shapley",
                 dict(meta, what="Shapley attribution of naive_0 -> realistic over delay (0->1), cost (0->5), slip (0->2)"))

    # ---- sensitivity of B0's drag to the cost model (C9, C10, C12)
    w = bk["B0 (MOM + MACD band, walk-forward)"]
    m = wd.samples["WF"]
    n1 = cum(run(w, cost_bp=0, slip_bp=0), m)
    sens = []
    grid = [dict(cost_bp=c, slip_bp=s) for c in (0, 2, 5, 10, 20) for s in (0, 2, 5, 10)]
    grid += [dict(lag=d) for d in (2, 3)] + [dict(exec_price="twap")] + [dict(borrow_bp=b) for b in (25, 50)]
    for g in grid:
        res = run(w, **g)
        r = cum(res, m)
        sens.append(dict(g, realistic_cum=r, ann_return=r / years["WF"], drag_vs_naive1_bp_yr=(n1 - r) / years["WF"] * 1e4,
                         sharpe=M.sharpe(res["pnl_net"][m]),
                         turnover_ann_per_gross=M.annual_turnover(res["turnover_exec"][m], res["gross"][m])))
    write_result(pd.DataFrame(sens), "03_haircut_sensitivity",
                 dict(meta, what="B0 under alternative cost, slippage, lag, fill and borrow settings (one change "
                                 "from realistic per row unless cost and slip are both given)", sample_rows="WF 2022Q1-2025Q2"),
                 index=False)

    # ---- turnover constraint on B0 (C11): deadband multiples of the per-rung scale
    scale, per_rung = PF.b0_deadband_scale(wd)
    base_res = run(w)
    tc = []
    for k in (0.0, 0.25, 0.5, 1.0, 2.0):
        res = base_res if k == 0 else run(w, deadband=scale * k)
        to = M.annual_turnover(res["turnover_exec"][m], res["gross"][m])
        tc.append({"deadband_multiple": k, "ann_return": cum(res, m) / years["WF"], "sharpe": M.sharpe(res["pnl_net"][m]),
                   "turnover_ann_per_gross": to, "signal_turnover_ann": M.annual_turnover(res["turnover_signal"][m]),
                   "drift_turnover_ann": M.annual_turnover(res["turnover_exec"][m]) - M.annual_turnover(res["turnover_signal"][m]),
                   "gross_mean": float(res["gross"][m].mean()),
                   "cost_plus_slip_bp_yr": float((res["cost"][m] + res["slip"][m]).sum() / years["WF"] * 1e4)})
    tcd = pd.DataFrame(tc).set_index("deadband_multiple")
    tcd["turnover_change_vs_0"] = tcd["turnover_ann_per_gross"] / tcd.loc[0.0, "turnover_ann_per_gross"] - 1
    write_result(tcd, "03_turnover_constraint",
                 dict(meta, what="B0 with a deadband of k x the per-rung median daily |dw_held| (C11)",
                      per_rung_scale=" ".join(f"{q}:{v:.5f}" for q, v in per_rung.items()), sample_rows="WF 2022Q1-2025Q2"))

    print(pd.DataFrame(wf_rows).query("sample == 'WF'")[["book", "naive_0_cum", "naive_1_cum", "realistic_cum", "naive_1_ann_t",
                                                         "cost_drag_bp_yr", "slip_drag_bp_yr", "delay_d1_to_d2_bp_yr", "H_1", "H_1_note"]].round(4).to_string(index=False))
    print(pd.DataFrame(shap_rows).query("sample == 'WF'")[["book", "switch", "shapley_bp_yr", "min_over_orders_bp_yr", "max_over_orders_bp_yr"]].round(1).to_string(index=False))
    print(tcd.round(4).to_string())


if __name__ == "__main__":
    main()
