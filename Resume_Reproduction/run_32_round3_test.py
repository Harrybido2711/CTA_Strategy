"""Round 3, Part B: the single Test read of the procedure OV chose (ROUND3.md B4, B5, section 7).

    .venv/bin/python Resume_Reproduction/run_32_round3_test.py

Refuses to run unless config.py and every rr_*.py match HEAD. Reads the chosen procedure from
results/31b_choice.json (amendment 2), re-runs it unchanged through all 18 rungs (deterministic, so its pre-Test
part reproduces run_31), and reads Test 2025Q3 -> 2026Q2 once. That is the third look at those
quarters: Round 1 and Round 2 read them first. Only P and the baselines are read on Test.
"""
import datetime
import glob
import itertools
import json
import os
import subprocess
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C                       # noqa: E402
import rr_metrics as M                   # noqa: E402
import rr_round3 as R3                   # noqa: E402
import rr_tsmom as T                     # noqa: E402
from rr_io import write_result           # noqa: E402
from run_20_round2 import R2             # noqa: E402
from run_31_round3_pipeline import VARIANTS, stats   # noqa: E402

P3 = C.ROUND3
LAST_ME = "2026-05-29"
WINDOWS = {"Test 2025Q3-2026Q2": ("2025-07-01", "2026-06-29"),
           "WF 2022Q1-2026Q2": ("2022-01-01", "2026-06-29"),
           "WF pre-Test 2022Q1-2025Q2": ("2022-01-01", "2025-06-30")}
BONDS = [t for t, c in C.UNIVERSE_CATEGORY.items() if c == "bonds"]


def frozen_commit():
    files = [os.path.relpath(p, C.ROOT) for p in [os.path.join(C.HERE, "config.py")] + glob.glob(os.path.join(C.HERE, "rr_*.py"))]
    if subprocess.run(["git", "-C", C.ROOT, "diff", "--quiet", "HEAD", "--"] + files).returncode:
        raise SystemExit("config.py or an rr_*.py differs from HEAD: commit before the Test read")
    return subprocess.check_output(["git", "-C", C.ROOT, "rev-parse", "--short", "HEAD"], text=True).strip()


def chosen():
    with open(os.path.join(C.RESULTS, "31b_choice.json")) as fh:   # amendment 2's run
        name = json.load(fh)["chosen"]
    model, on = next((m, o) for m, o in R3.PROCEDURES if f"{m} | regime {'on' if o else 'off'}" == name)
    return name, model, on


def world(universe=None, end=C.SAMPLE_END, last_me=LAST_ME, d=1):
    r2 = R2(universe=universe, end=end, last_me=last_me)
    me = T.month_ends(r2.cal, start=C.ROUND2["first_signal"])
    me = me[me <= pd.Timestamp(last_me)]
    ms = R3.measures(r2.wd, r2.xr)
    return r2, R3.Context(r2.wd, r2.xr, r2.vol, ms, me, d=d), ms, me


def baselines(r2, last_me=LAST_ME):
    w0 = r2.t0()
    w1, _ = T.t1_targets(w0, r2.xr)
    cut = lambda w: w.loc[w.index <= pd.Timestamp(last_me)]   # noqa: E731
    return {"R0 = T0 (paper)": cut(w0), "T1 (10% vol target)": cut(w1)}


def main():
    commit = frozen_commit()
    stamp = datetime.datetime.now().isoformat(timespec="seconds")
    name, model, on = chosen()
    rungs = R3.monthly_rungs()
    meta = {"round": "3, Part B, the Test read", "test_read": f"single read at {stamp}, frozen at commit {commit}",
            "procedure": name, "third_look": "Round 1 and Round 2 read these Test quarters first",
            "execution": "next close (d = 1), 5 bp + 2 bp; excess of DTB3"}

    r2, ctx, ms, me = world()
    P = R3.Procedure(ctx, model, on)
    wP = P.run(rungs)
    base = baselines(r2)
    runs = {**{k: ctx.run_engine(v) for k, v in base.items()}, "P": ctx.run_engine(wP)}
    rows = [dict(stats(ctx, res, a, b), book=k, window=wn) for k, res in runs.items() for wn, (a, b) in WINDOWS.items()]
    write_result(pd.DataFrame(rows).set_index(["book", "window"]), "32_books", dict(meta, what="P and the baselines on Test and the full record"))
    write_result(pd.DataFrame(P.log).drop(columns=["coefs"]).set_index("apply_q"), "32_rung_log", dict(meta, what="P's per-rung choices, all 18 rungs"))
    write_result(pd.DataFrame([dict(apply_q=l["apply_q"], **l["coefs"]) for l in P.log]).set_index("apply_q"), "32_coefficients",
                 dict(meta, what="P's refit coefficients or importances per rung"))

    # ---- ablations on Test: costs, turnover, delay, features
    abl = {"P": runs["P"]}
    for nm, kw in {"P, phi = 0 (blind to costs)": dict(phi=0.0), "P, gamma = 0 (the cost term alone)": dict(gamma_fixed=0.0),
                   "P, phi = 0 and gamma = 0 (blind to trading)": dict(phi=0.0, gamma_fixed=0.0)}.items():
        abl[nm] = ctx.run_engine(R3.Procedure(ctx, model, on, **kw).run(rungs))
    abl[f"P, regime features {'off' if on else 'on'}"] = ctx.run_engine(R3.Procedure(ctx, model, not on).run(rungs))
    for d in P3["delay_grid"]:
        _, cd, _, _ = world(d=d)
        abl[f"P at d = {d} (re-trained)"] = cd.run_engine(R3.Procedure(cd, model, on).run(rungs))
        abl[f"R0 at d = {d}"] = cd.run_engine(base["R0 = T0 (paper)"])
    ab = [dict(stats(ctx, res, a, b), book=k, window=wn) for k, res in abl.items() for wn, (a, b) in WINDOWS.items()]
    write_result(pd.DataFrame(ab).set_index(["book", "window"]), "32_ablations", dict(meta, what="amendment 1's ablations through Test"))

    # ---- execution waterfall
    wf = []
    for k, w in (("R0 = T0 (paper)", base["R0 = T0 (paper)"]), ("P", wP)):
        for wn, (a, b) in WINDOWS.items():
            m = (ctx.cal >= pd.Timestamp(a)) & (ctx.cal <= pd.Timestamp(b))
            pnl = {}
            for vn, kw in VARIANTS.items():
                res = ctx.run_engine(w, **kw)
                pnl[vn] = float(res["pnl_net"][m].sum())
                wf.append({"book": k, "window": wn, "variant": vn, "cum_pnl": pnl[vn], "ann_pnl": pnl[vn] / (m.sum() / 252)})
            n0, n1, rl = pnl["naive_0 (same close, free)"], pnl["naive_1 (next close, free)"], pnl["realistic (+ slippage 2 bp)"]
            wf.append({"book": k, "window": wn, "variant": "H_1 = 1 - realistic / naive_1", "cum_pnl": 1 - rl / n1 if n1 > 0 else np.nan})
            wf.append({"book": k, "window": wn, "variant": "H_0 = 1 - realistic / naive_0", "cum_pnl": 1 - rl / n0 if n0 > 0 else np.nan})
    write_result(pd.DataFrame(wf).set_index(["book", "window", "variant"]), "32_waterfall",
                 dict(meta, what="raw PnL per $1 under each execution assumption; H undefined when the naive PnL <= 0"))

    # ---- paired bootstrap, drop-best-days, per year
    bs, dd = [], []
    for ref in base:
        for wn, (a, b) in WINDOWS.items():
            m = (ctx.cal >= pd.Timestamp(a)) & (ctx.cal <= pd.Timestamp(b))
            x0, x1 = runs[ref]["excess"][m], runs["P"]["excess"][m]
            t0_, t1_ = runs[ref]["turnover_exec"][m].to_numpy().copy(), runs["P"]["turnover_exec"][m].to_numpy().copy()
            t0_[0] = t1_[0] = 0.0
            for bl in (5, 21, 63):
                idx = M.stationary_bootstrap_indices(len(x0), bl, 2000, seed=bl)
                d = M.sharpe_rows(x1.to_numpy()[idx]) - M.sharpe_rows(x0.to_numpy()[idx])
                dto = t1_[idx].mean(axis=1) / t0_[idx].mean(axis=1) - 1
                bs.append({"against": ref, "window": wn, "mean_block": bl,
                           "d_sharpe": float(M.sharpe_rows(x1.to_numpy()[None])[0] - M.sharpe_rows(x0.to_numpy()[None])[0]),
                           "d_sharpe_90_lo": np.quantile(d, 0.05), "d_sharpe_90_hi": np.quantile(d, 0.95),
                           "d_turnover": float(t1_.mean() / t0_.mean() - 1),
                           "d_turnover_90_lo": np.quantile(dto, 0.05), "d_turnover_90_hi": np.quantile(dto, 0.95)})
            gap = (x1 - x0).abs().sort_values(ascending=False)
            for k in (0, 5, 10):
                keep = ~x0.index.isin(gap.index[:k])
                dd.append({"against": ref, "window": wn, "check": f"drop the {k} largest |r_P - r_ref| days",
                           "d_sharpe": float(M.sharpe_rows(x1[keep].to_numpy()[None])[0] - M.sharpe_rows(x0[keep].to_numpy()[None])[0])})
        xs0, xs1 = runs[ref]["excess"], runs["P"]["excess"]
        for y in range(2022, 2027):
            m = (ctx.cal.year == y) & (ctx.cal <= pd.Timestamp("2026-06-29"))
            dd.append({"against": ref, "window": f"year {y}", "check": "per-year Sharpe difference",
                       "d_sharpe": float(M.sharpe_rows(xs1[m].to_numpy()[None])[0] - M.sharpe_rows(xs0[m].to_numpy()[None])[0])})
    write_result(pd.DataFrame(bs).set_index(["against", "window", "mean_block"]), "32_bootstrap",
                 dict(meta, what="P minus the baseline, paired stationary bootstrap, 2000 draws, 90% intervals"))
    write_result(pd.DataFrame(dd).set_index(["against", "window", "check"]), "32_drop_best_days",
                 dict(meta, what="the 'two good days' check and the per-year sign count"))

    # ---- robustness: the cost grid (the optimizer re-priced at each rate), ex-bond, truncated
    rb = []
    for c, s in itertools.product((2, 5, 10), (0, 2, 5)):
        wc = R3.Procedure(ctx, model, on, kappa_bp=c + s).run(rungs)
        for k, w in (("P", wc), ("R0 = T0 (paper)", base["R0 = T0 (paper)"])):
            res = ctx.run_engine(w, cost_bp=c, slip_bp=s)
            for wn, (a, b) in WINDOWS.items():
                rb.append(dict(stats(ctx, res, a, b), check=f"cost {c} bp, slip {s} bp", book=k, window=wn))
    for an, kw in {"without the 7 bond ETFs": dict(universe=[t for t in C.UNIVERSE_CATEGORY if t not in BONDS]),
                   "data truncated at 2025-12-04": dict(end="2025-12-04", last_me="2025-10-31")}.items():
        ra, ca, _, _ = world(**kw)
        last_q = pd.Period(pd.Timestamp(kw.get("last_me", LAST_ME)) + pd.offsets.MonthEnd(1), "Q")
        rr = [rg for rg in rungs if rg["q"] <= last_q]
        rres = {"P": ca.run_engine(R3.Procedure(ca, model, on).run(rr)),
                "R0 = T0 (paper)": ca.run_engine(baselines(ra, kw.get("last_me", LAST_ME))["R0 = T0 (paper)"])}
        for k, res in rres.items():
            for wn, (a, b) in WINDOWS.items():
                b = min(pd.Timestamp(b), ra.cal.max())
                if (ra.cal >= pd.Timestamp(a)).sum() and pd.Timestamp(a) < b:
                    rb.append(dict(stats(ca, res, a, b), check=an, book=k, window=wn))
    write_result(pd.DataFrame(rb).set_index(["check", "book", "window"]), "32_robustness",
                 dict(meta, what="cost grid with the optimizer re-priced at each rate; ex-bond and truncated reruns"))
    with open(os.path.join(C.RESULTS, "32_test_read.json"), "w") as fh:
        json.dump({"read_at": stamp, "commit": commit, "procedure": name}, fh, indent=2)
    print(f"Test read done: {name} at {commit}")


if __name__ == "__main__":
    main()
