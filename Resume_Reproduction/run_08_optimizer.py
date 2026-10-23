"""W9 (homework D and E): the optimizer on the chosen model's predictions, gamma by target vol.

    .venv/bin/python Resume_Reproduction/run_08_optimizer.py

mu = the chosen model's prediction per asset; Sigma = sample covariance of its refit-window
residuals, per rung; cap and tau are per-asset vectors. The (gamma, cap, tau) choice is the outer
layer, made once on the OV quarters (config.OPTIMIZER). Train-ladder and OV quarters only.
"""
import itertools
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C                       # noqa: E402
import rr_metrics as M                   # noqa: E402
import rr_models as MD                   # noqa: E402
import rr_optimizer as OP                # noqa: E402
import rr_portfolio as PF                # noqa: E402
from rr_engine import simulate           # noqa: E402
from rr_io import write_result           # noqa: E402

CFG = C.OPTIMIZER


def main():
    wd = PF.World()
    assets = list(wd.close.columns)
    panel = MD.build_panel(wd)
    chosen = json.load(open(os.path.join(C.RESULTS, "07_model_selection.json")))["chosen"]

    mu = pd.DataFrame(np.nan, index=wd.cal, columns=assets)
    chol = {}
    for r in wd.rungs:
        _, p, resid = MD.fit_rung(chosen, panel, wd.cal, r)
        mu.update(p.unstack("asset").reindex(columns=assets))
        for method in ("sample", "ledoit_wolf"):
            chol[(r["test_q"], method)] = OP.chol_t(OP.residual_covariance(resid, assets, method))
    quarter = pd.Series([str(q) for q in wd.cal.to_period("Q")], index=wd.cal)
    tau_unit = (C.COST_BP + C.SLIP_BP) / 1e4

    def weights(gamma, cap, tau_mult, net, method, dates):
        opt = OP.MeanVariance(len(assets), gross=C.GROSS, net=net)
        out = pd.DataFrame(0.0, index=wd.cal, columns=assets)
        w_prev = np.zeros(len(assets))
        for d in dates:
            m = mu.loc[d].to_numpy()
            ok = np.isfinite(m)
            capv = np.where(ok, cap, 0.0)
            w = opt.solve(np.where(ok, m, 0.0), chol[(quarter[d], method)], w_prev, gamma, capv,
                          np.full(len(assets), tau_mult * tau_unit))
            w = np.where(np.abs(w) < 1e-9, 0.0, w)
            out.loc[d] = w
            w_prev = w
        return out

    def score(w, mask, rf=None):
        res = simulate(wd.open, wd.close, w, **PF.VARIANTS["realistic"])
        s = M.book_summary(res, rf=rf, mask=mask)
        return res, s

    # ---- OV grid
    ov = wd.samples["OV"]
    ov_dates = wd.cal[ov.to_numpy()]
    grid, series = [], {}
    for g, cap, tm in itertools.product(CFG["gamma_grid"], CFG["cap_grid"], CFG["tau_multiple_grid"]):
        w = weights(g, cap, tm, 0.0, "sample", ov_dates)
        res, s = score(w, ov)
        series[(g, cap, tm)] = res["pnl_net"][ov]
        grid.append({"gamma": g, "cap": cap, "tau_multiple": tm, "ann_vol": s["ann_vol"], "ann_return": s["ann_return"],
                     "sharpe": s["sharpe"], "turnover_ann_per_gross": s["turnover_ann_per_gross"], "gross_mean": s["gross_mean"]})
    G = pd.DataFrame(grid)
    G["vol_gap"] = (G.ann_vol - CFG["target_vol"]).abs()
    cand = G.loc[G.groupby(["cap", "tau_multiple"]).vol_gap.idxmin()].copy()
    best = cand.loc[cand.ann_return.idxmax()]
    rb = series[(best.gamma, best.cap, best.tau_multiple)]
    for i, row in cand.iterrows():
        d = (rb - series[(row.gamma, row.cap, row.tau_multiple)]).dropna()
        se = M.newey_west_se(d, C.H)
        cand.loc[i, "shortfall_vs_best_bp_day"] = float(d.mean() * 1e4)
        cand.loc[i, "shortfall_se_bp_day"] = float(se * 1e4)
        cand.loc[i, "within_one_se"] = bool(d.mean() <= se)
    cand = cand.sort_values(["cap", "tau_multiple"], ascending=[True, False])
    pick = cand[cand.within_one_se].iloc[0]
    G["candidate"] = G.index.isin(cand.index)
    G["chosen"] = (G.gamma == pick.gamma) & (G.cap == pick.cap) & (G.tau_multiple == pick.tau_multiple)
    write_result(G.set_index(["gamma", "cap", "tau_multiple"]), "08_optimizer_grid_OV",
                 {"what": "optimizer grid on the OV quarters, realistic execution, net 0", "model": chosen,
                  "rule": CFG["rule"], "target_vol": CFG["target_vol"]})
    write_result(cand.set_index(["cap", "tau_multiple"]), "08_optimizer_candidates_OV",
                 {"what": "per (cap, tau): the gamma closest to the target vol, and the one-SE comparison"})
    choice = {"model": chosen, "gamma": float(pick.gamma), "cap": float(pick.cap), "tau_multiple": float(pick.tau_multiple),
              "target_vol": CFG["target_vol"], "chosen_on": "OV quarters 2024Q3-2025Q2"}
    with open(os.path.join(C.RESULTS, "08_optimizer_choice.json"), "w") as fh:
        json.dump(choice, fh, indent=2)

    # ---- the chosen configuration over the record, beside B0 and P1
    wf_dates = wd.cal[wd.wf.to_numpy()]
    books = {"Optimizer, net 0 (vs B0)": weights(pick.gamma, pick.cap, pick.tau_multiple, 0.0, "sample", wf_dates),
             "Optimizer, net 0, Ledoit-Wolf": weights(pick.gamma, pick.cap, pick.tau_multiple, 0.0, "ledoit_wolf", wf_dates),
             "Optimizer, net 1 (lecture, vs P1)": weights(pick.gamma, pick.cap, pick.tau_multiple, 1.0, "sample", wf_dates)}
    bk = PF.books(wd)
    books["B0"] = bk["B0 (MOM + MACD band, walk-forward)"]
    books["P1 150/50 (prototype)"] = bk["P1 150/50 (prototype)"]
    rows = []
    for name, w in books.items():
        for sname, m in wd.samples.items():
            res, s = score(w, m, rf=wd.rf)
            _, s0 = score(w, m)
            rows.append(dict(s.to_dict(), sharpe_rf0=s0["sharpe"], book=name, sample=sname))
    out = pd.DataFrame(rows).rename(columns={"sharpe": "sharpe_dtb3"}).set_index(["book", "sample"])
    write_result(out, "08_optimizer_books", dict({"what": "the OV-chosen optimizer over the record, beside B0 and P1",
                                                  "class_note": "train-ladder rows use an outer layer chosen later, on OV"},
                                                 **{k: str(v) for k, v in choice.items()}))

    p = os.path.join(C.RESULTS, "run_ledger.csv")
    head = [l for l in open(p) if l.startswith("#")]
    led = pd.read_csv(p, comment="#")
    led = led[led.workstream != "W9"]
    add = [{"workstream": "W9", "test_q": "OV", "stage": "optimizer OV grid", "sample": "OV quarters",
            "params": f"gamma={r.gamma} cap={r.cap} tau={r.tau_multiple}", "spread": r.ann_return,
            "selected": bool(r.chosen)} for r in G.itertuples()]
    led = pd.concat([led, pd.DataFrame(add)], ignore_index=True)
    with open(p, "w") as fh:
        fh.writelines(head); led.to_csv(fh, index=False)

    print(cand.round(4).to_string(index=False))
    print("chosen:", choice)
    print(out[["ann_return", "ann_vol", "sharpe_rf0", "sharpe_dtb3", "turnover_ann_per_gross", "gross_mean", "net_mean"]].round(3).to_string())


if __name__ == "__main__":
    main()
