"""W8 (homework C): Equal Weights, OLS / Ridge / Lasso, and two boosted-tree models on the ladder.

    .venv/bin/python Resume_Reproduction/run_07_models.py

Every rung refits; the model class and hyperparameters are chosen once, on the four OV quarters,
by MSE under a one-SE rule (simplest model within one paired NW SE of the best), MAE as tiebreak.
Train-ladder quarters are reported too, labelled: the class was chosen later, on OV.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C                       # noqa: E402
import rr_metrics as M                   # noqa: E402
import rr_models as MD                   # noqa: E402
import rr_portfolio as PF                # noqa: E402
from rr_io import write_result           # noqa: E402


def main():
    wd = PF.World()
    panel = MD.build_panel(wd)
    rows, coefs, preds = [], [], {}
    for name in MD.MODEL_ORDER:
        p_all = []
        for r in wd.rungs:
            model, p, _ = MD.fit_rung(name, panel, wd.cal, r)
            y = panel.loc[p.index, "y"]
            ok = y.notna()
            e = (y[ok] - p[ok])
            pw = p.unstack("asset"); yw = y.unstack("asset")
            ic = M.ic_series(pw, yw).dropna()
            rows.append({"model": name, "test_q": r["test_q"], "block": r["block"],
                         "mse_x1e4": float((e ** 2).mean() * 1e4), "mae_x1e2": float(e.abs().mean() * 1e2),
                         "mse_zero_x1e4": float((y[ok] ** 2).mean() * 1e4), "mean_ic": float(ic.mean()),
                         "n_features": len(getattr(model, "features", MD.FEATURES)),
                         "kept": " ".join(getattr(model, "kept", [])) if name.startswith("Lasso") else ""})
            if getattr(model, "coef", None) is not None:
                coefs.append(dict(model.coef.to_dict(), model=name, test_q=r["test_q"]))
            p_all.append(p)
        preds[name] = pd.concat(p_all)
    lad = pd.DataFrame(rows)
    write_result(lad.set_index(["model", "test_q"]), "07_model_ladder",
                 {"what": "every model on every rung: test-quarter MSE, MAE and IC",
                  "target": "forward return close_{t+1} -> close_{t+6}, raw (winsorised 1/99 only inside fitting windows)",
                  "units": "mse x 1e4, mae x 1e2 (percent)", "sample_rows": "rungs 2022Q1-2025Q2; Test is W10"})
    write_result(pd.DataFrame(coefs).set_index(["model", "test_q"]), "07_coefficients",
                 {"what": "standardised coefficients per rung for the linear models (coefficient path, WF 5.3)"})

    # ---- outer layer: choose on OV by MSE, one-SE rule, MAE tiebreak
    y = panel["y"]
    ov_dates = wd.cal[wd.samples["OV"].to_numpy()]
    per_date = {}
    for name, p in preds.items():
        pp = p[p.index.get_level_values("date").isin(ov_dates)]
        e2 = ((y.loc[pp.index] - pp) ** 2).dropna()
        per_date[name] = e2.groupby(level="date").mean()
    mse = {k: float(v.mean()) for k, v in per_date.items()}
    best = min(mse, key=mse.get)
    sel = []
    for name in MD.MODEL_ORDER:
        d = (per_date[name] - per_date[best]).dropna()
        se = M.newey_west_se(d, C.H)
        pp = preds[name][preds[name].index.get_level_values("date").isin(ov_dates)]
        yy = y.loc[pp.index]
        ok = yy.notna()
        ic = M.ic_series(pp.unstack("asset"), yy.unstack("asset")).dropna()
        r2 = 1 - float(((yy[ok] - pp[ok]) ** 2).sum() / (yy[ok] ** 2).sum())
        sel.append({"model": name, "ov_mse_x1e4": mse[name] * 1e4, "ov_mae_x1e2": float((yy[ok] - pp[ok]).abs().mean() * 1e2),
                    "diff_vs_best_x1e4": float(d.mean() * 1e4), "diff_se_x1e4": float(se * 1e4),
                    "within_one_se": bool(d.mean() <= se), "ov_mean_ic": float(ic.mean()), "ov_r2_vs_zero": r2})
    sd = pd.DataFrame(sel).set_index("model")
    chosen = next(m for m in MD.MODEL_ORDER if sd.loc[m, "within_one_se"])
    sd["chosen"] = sd.index == chosen
    if (sd["ov_r2_vs_zero"] > 0.1).any():
        raise SystemExit("pooled R2 > 0.1: audit the target shift before trusting anything (09 2)")
    write_result(sd, "07_model_selection",
                 {"what": "outer layer: OV MSE per model, paired NW SE of the difference to the best, one-SE rule",
                  "order": " < ".join(MD.MODEL_ORDER), "best_by_mse": best, "chosen": chosen,
                  "sample_rows": "OV quarters 2024Q3-2025Q2"})
    pc = preds[chosen].rename("prediction").to_frame().join(y.rename("y"))
    write_result(pc, "07_predictions", {"what": f"predictions of the chosen model ({chosen}) on rungs 2022Q1-2025Q2"})

    summ = lad.groupby(["model", "block"])[["mse_x1e4", "mse_zero_x1e4", "mean_ic"]].mean().unstack("block")
    print(summ.round(4).to_string())
    print(sd.round(4).to_string())
    print("chosen:", chosen, "| best by MSE:", best)


if __name__ == "__main__":
    main()
