"""Round 3, Part B before Test: the learning path's pipeline, the procedures, the OV choice (ROUND3.md section 5).

    .venv/bin/python Resume_Reproduction/run_31_round3_pipeline.py

Apply quarters 2022Q1 -> 2025Q2 only; the last month-end used is 2025-05-30 and every statistic
is masked at 2025-06-30. B2's EW uses only the trend features, so "EW | regime on" would equal
"EW | regime off": nine distinct procedures, not ten.
"""
import os
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C                       # noqa: E402
import rr_metrics as M                   # noqa: E402
import rr_round3 as R3                   # noqa: E402
import rr_tsmom as T                     # noqa: E402
from rr_io import write_result           # noqa: E402
from run_20_round2 import R2             # noqa: E402

P3 = C.ROUND3
LAST_ME = "2025-05-30"
LAST_Q = pd.Period("2025Q2", "Q")
WINDOWS = {"train-ladder 2022Q1-2024Q2": ("2022-01-01", "2024-06-30"),
           "OV 2024Q3-2025Q2": ("2024-07-01", "2025-06-30"),
           "WF pre-Test 2022Q1-2025Q2": ("2022-01-01", "2025-06-30")}
VARIANTS = {"naive_0 (same close, free)": dict(lag=0, cost_bp=0, slip_bp=0),
            "naive_1 (next close, free)": dict(lag=1, cost_bp=0, slip_bp=0),
            "+ cost 5 bp": dict(lag=1, cost_bp=C.COST_BP, slip_bp=0),
            "realistic (+ slippage 2 bp)": dict(lag=1, cost_bp=C.COST_BP, slip_bp=C.SLIP_BP)}


def stats(ctx, res, a, b):
    cal = ctx.cal
    m = pd.Series((cal >= pd.Timestamp(a)) & (cal <= pd.Timestamp(b)), index=cal)
    first = cal[m.to_numpy()][0]
    m_to = m & (cal != first)                                  # the first day of the record holds the build from zero
    s = M.book_summary(res, rf=ctx.rf, mask=m)
    x = res["excess"][m]
    return {"ann_excess": float(x.mean() * 252), "sharpe": float(x.mean() / x.std() * np.sqrt(252)),
            "max_dd_units": M.max_drawdown(x)[0], "turnover_ann": M.annual_turnover(res["turnover_exec"][m_to]),
            "cost_ann_bp": s["cost_ann_bp"] + s["slip_ann_bp"], "gross_mean": s["gross_mean"], "net_mean": s["net_mean"],
            "days": int(m.sum())}


def main():
    t_start = time.time()
    r2 = R2()
    wd, cal, xr = r2.wd, r2.cal, r2.xr
    me = T.month_ends(cal, start=C.ROUND2["first_signal"])
    me = me[me <= pd.Timestamp(LAST_ME)]
    ms = R3.measures(wd, xr)
    rungs = [rg for rg in R3.monthly_rungs() if rg["q"] <= LAST_Q]
    meta = {"round": "3, Part B before Test (ROUND3.md section 5, amendment 1)",
            "apply_quarters": f"{rungs[0]['q']}..{rungs[-1]['q']}, {len(rungs)} rungs", "last_month_end": LAST_ME,
            "execution": "next close (d = 1), 5 bp + 2 bp; excess of DTB3; optimizer prices phi x kappa = 7 bp + gamma"}

    ctx = R3.Context(wd, xr, r2.vol, ms, me, d=1)
    books, logs = {}, []
    for model, on in R3.PROCEDURES:
        t0 = time.time()
        pr = R3.Procedure(ctx, model, on)
        books[pr.name] = pr.run(rungs)
        logs += pr.log
        print(f"{pr.name}: {time.time() - t0:.0f} s", flush=True)
    w0 = r2.t0()
    w1, _ = T.t1_targets(w0, xr)
    base = {"R0 = T0 (paper)": w0.loc[w0.index <= pd.Timestamp(LAST_ME)], "T1 (10% vol target)": w1.loc[w1.index <= pd.Timestamp(LAST_ME)]}
    runs = {k: ctx.run_engine(v) for k, v in {**base, **books}.items()}

    rows = [dict(stats(ctx, res, a, b), book=k, window=wn) for k, res in runs.items() for wn, (a, b) in WINDOWS.items()]
    write_result(pd.DataFrame(rows).set_index(["book", "window"]), "31_procedures",
                 dict(meta, what="every procedure and the two baselines, realistic execution",
                      turnover="executed, per $1 a year, the record's first day (the build from zero) excluded"))

    # ---- the outer layer: OV chooses the procedure
    a, b = WINDOWS["OV 2024Q3-2025Q2"]
    ov = {k: runs[k]["excess"][(cal >= pd.Timestamp(a)) & (cal <= pd.Timestamp(b))] for k in books}
    pick, tab = R3.choose(ov)
    write_result(tab, "31_choice", dict(meta, what="OV comparison of the procedures by chapter 09's rule", chosen=pick,
                                        rule=P3["pair_rule"]))
    lg = pd.DataFrame(logs)
    coefs = pd.DataFrame([dict(procedure=l["procedure"], apply_q=l["apply_q"], **l["coefs"]) for l in logs])
    write_result(lg.drop(columns=["coefs"]).set_index(["procedure", "apply_q"]), "31_rung_log",
                 dict(meta, what="per rung: model grid point (validation MSE), the (sigma_0, gamma) pair, rows"))
    write_result(coefs.set_index(["procedure", "apply_q"]), "31_coefficients",
                 dict(meta, what="refit coefficients (Ridge, Lasso; standardized features) or feature importances (trees) per rung"))

    # ---- the chosen procedure's ablations (amendment 1): costs, turnover, delay
    model, on = next((m_, o_) for m_, o_ in R3.PROCEDURES if f"{m_} | regime {'on' if o_ else 'off'}" == pick)
    abl = {"P": runs[pick]}
    for nm, kw in {"P, phi = 0 (blind to costs)": dict(phi=0.0), "P, gamma = 1e-4": dict(gamma_fixed=1e-4),
                   "P, phi = 0 and gamma = 1e-4": dict(phi=0.0, gamma_fixed=1e-4),
                   f"P, regime features {'off' if on else 'on'}": dict(regime_on=not on)}.items():
        kw2 = dict(kw); ro = kw2.pop("regime_on", on)
        pr = R3.Procedure(ctx, model, ro, **kw2)
        abl[nm] = ctx.run_engine(pr.run(rungs))
        print(f"{nm}: done", flush=True)
    for d in P3["delay_grid"]:
        cd = R3.Context(wd, xr, r2.vol, ms, me, d=d)
        pr = R3.Procedure(cd, model, on)
        abl[f"P at d = {d} (re-trained)"] = cd.run_engine(pr.run(rungs))
        abl[f"R0 at d = {d}"] = cd.run_engine(base["R0 = T0 (paper)"])
        print(f"d = {d}: done", flush=True)
    ab = [dict(stats(ctx, res, a_, b_), book=k, window=wn) for k, res in abl.items() for wn, (a_, b_) in WINDOWS.items()]
    write_result(pd.DataFrame(ab).set_index(["book", "window"]), "31_ablations",
                 dict(meta, what=f"the chosen procedure P = {pick}: the cost term off, gamma off, both, the other feature set, delay 2 and 3"))

    # ---- the execution waterfall (bullet 2), P beside R0
    wf = []
    for k, w in (("R0 = T0 (paper)", base["R0 = T0 (paper)"]), ("P", books[pick])):
        for wn, (a_, b_) in WINDOWS.items():
            m = (cal >= pd.Timestamp(a_)) & (cal <= pd.Timestamp(b_))
            pnl = {}
            for vn, kw in VARIANTS.items():
                res = ctx.run_engine(w, **kw)
                pnl[vn] = float(res["pnl_net"][m].sum())
                wf.append({"book": k, "window": wn, "variant": vn, "cum_pnl": pnl[vn], "ann_pnl": pnl[vn] / (m.sum() / 252),
                           "sharpe_excess": float(res["excess"][m].mean() / res["excess"][m].std() * np.sqrt(252))})
            n0, n1, rl = pnl["naive_0 (same close, free)"], pnl["naive_1 (next close, free)"], pnl["realistic (+ slippage 2 bp)"]
            wf.append({"book": k, "window": wn, "variant": "H_1 = 1 - realistic / naive_1", "cum_pnl": 1 - rl / n1 if n1 > 0 else np.nan})
            wf.append({"book": k, "window": wn, "variant": "H_0 = 1 - realistic / naive_0", "cum_pnl": 1 - rl / n0 if n0 > 0 else np.nan})
    write_result(pd.DataFrame(wf).set_index(["book", "window", "variant"]), "31_waterfall",
                 dict(meta, what="raw PnL per $1 (not excess) under each execution assumption; H undefined when the naive PnL <= 0"))

    # ---- paired bootstrap, P against R0 and T1
    bs = []
    for ref in ("R0 = T0 (paper)", "T1 (10% vol target)"):
        for wn, (a_, b_) in WINDOWS.items():
            m = (cal >= pd.Timestamp(a_)) & (cal <= pd.Timestamp(b_))
            x0, x1 = runs[ref]["excess"][m].to_numpy(), runs[pick]["excess"][m].to_numpy()
            t0_, t1_ = runs[ref]["turnover_exec"][m].to_numpy(), runs[pick]["turnover_exec"][m].to_numpy()
            t0_[0] = t1_[0] = 0.0
            for bl in (5, 21, 63):
                idx = M.stationary_bootstrap_indices(len(x0), bl, 2000, seed=bl)
                d = M.sharpe_rows(x1[idx]) - M.sharpe_rows(x0[idx])
                dto = t1_[idx].mean(axis=1) / t0_[idx].mean(axis=1) - 1
                bs.append({"against": ref, "window": wn, "mean_block": bl,
                           "d_sharpe": float(M.sharpe_rows(x1[None])[0] - M.sharpe_rows(x0[None])[0]),
                           "d_sharpe_90_lo": np.quantile(d, 0.05), "d_sharpe_90_hi": np.quantile(d, 0.95),
                           "d_turnover": float(t1_.mean() / t0_.mean() - 1),
                           "d_turnover_90_lo": np.quantile(dto, 0.05), "d_turnover_90_hi": np.quantile(dto, 0.95)})
    write_result(pd.DataFrame(bs).set_index(["against", "window", "mean_block"]), "31_bootstrap",
                 dict(meta, what=f"P = {pick} minus the baseline, paired stationary bootstrap, 2000 draws, 90% intervals"))

    ovx = {k: v.dropna().to_numpy() for k, v in ov.items()}
    dsr = M.deflated_sharpe(ov[pick], [x.mean() / x.std(ddof=1) for x in ovx.values()], len(ovx))
    write_result(pd.DataFrame([dict(dsr, procedure=pick)]).set_index("procedure"), "31_deflated_sharpe",
                 dict(meta, what="deflated Sharpe of OV's winner against the procedures it was chosen from (daily units)"))
    print(f"chosen: {pick}; {time.time() - t_start:.0f} s")


if __name__ == "__main__":
    main()
