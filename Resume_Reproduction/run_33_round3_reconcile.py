"""Round 3: the step-3 feature screen and the series the Round 3 figures plot (no choice is made here).

    .venv/bin/python Resume_Reproduction/run_33_round3_reconcile.py

B0's step 3 (IC of every feature) is descriptive and chose nothing; it was computed after the
Test read and is labelled so. The pre-Test formations only: month-ends through 2025-05-30.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C                       # noqa: E402
import rr_metrics as M                   # noqa: E402
import rr_round3 as R3                   # noqa: E402
from rr_io import write_result           # noqa: E402
from run_32_round3_test import baselines, chosen, world   # noqa: E402


def main():
    name, model, on = chosen()
    r2, ctx, ms, me = world()
    meta = {"round": "3, reconcile", "computed": "after the Test read; chooses nothing"}

    # ---- B0 step 3: IC of each feature against the next-month label, pre-Test formations
    pre = ctx.panel[ctx.panel.index.get_level_values(0) <= pd.Timestamp("2025-05-30")]
    y = pre["y"].unstack()
    rows = []
    for f in R3.FEATURES_ON:
        ic = M.ic_series(pre[f].unstack(), y, min_assets=10).dropna()
        se = M.newey_west_se(ic, 1)
        rows.append({"feature": f, "mean_ic": float(ic.mean()), "t": float(ic.mean() / se) if se > 0 else np.nan,
                     "share_positive": float((ic > 0).mean()), "months": int(len(ic))})
    write_result(pd.DataFrame(rows).set_index("feature"), "33_feature_ic",
                 dict(meta, what="B0 step 3: Spearman IC per month of each feature with y = next-month return / sigma, 2021-01..2025-05"))

    # ---- daily excess series for the figures
    P = R3.Procedure(ctx, model, on)
    wP = P.run(R3.monthly_rungs())
    base = baselines(r2)
    runs = {**{k: ctx.run_engine(v) for k, v in base.items()}, f"P ({name})": ctx.run_engine(wP)}
    out = pd.DataFrame({k: v["excess"] for k, v in runs.items()})
    for k, v in runs.items():
        out[f"{k} gross"] = v["gross"]
        out[f"{k} turnover"] = v["turnover_exec"]
    out["block"] = ["Test" if d >= pd.Timestamp("2025-07-01") else ("OV" if d >= pd.Timestamp("2024-07-01")
                    else ("train-ladder" if d >= pd.Timestamp("2022-01-01") else "before")) for d in ctx.cal]
    write_result(out, "33_daily_excess", dict(meta, what="daily excess return, gross and executed turnover of R0, T1 and P"))
    print("reconcile written: results/33_*")


if __name__ == "__main__":
    main()
