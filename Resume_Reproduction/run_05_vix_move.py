"""W6 (homework B): VIX and MOVE regimes, and the residual test of lecture 5.

    .venv/bin/python Resume_Reproduction/run_05_vix_move.py

(i)  VIX x MOVE 2-D tables of B0's daily return, under S1 (the homework's ceil(log(VIX^2))),
     D, S2 and S3, on the walk-forward quarters 2022Q1 -> 2025Q2; a descriptive version from 2020
     with the momentum book, which is the only place the 2020 crash appears.
(ii) the homework's rolling quintiles of each index, and chapter 04's two-way sort.
(iii) lecture 5's residual: each asset's VIX sensitivity regressed across assets on its MOM and
     MACD scores; the residual through the bar plot and through the engine.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C                       # noqa: E402
import rr_data as D                      # noqa: E402
import rr_metrics as M                   # noqa: E402
import rr_portfolio as PF                # noqa: E402
import rr_regimes as R                   # noqa: E402
import rr_signals as S                   # noqa: E402
from rr_engine import simulate           # noqa: E402
from rr_io import write_result           # noqa: E402

NAMES = {0: "low", 1: "mid", 2: "high"}


def vix_beta(r, dln, n):
    """Trailing-n slope of each asset's daily return on the daily change in ln(index), through t."""
    x = pd.DataFrame(np.repeat(dln.to_numpy()[:, None], r.shape[1], axis=1), index=r.index, columns=r.columns)
    cov = (r * x).rolling(n).mean() - r.rolling(n).mean() * x.rolling(n).mean()
    var = (x * x).rolling(n).mean() - x.rolling(n).mean() ** 2
    return cov.div(var, axis=0)


def cross_section_residual(y, regressors, min_assets=10):
    """Each date, OLS across assets of y on the regressors with an intercept; returns the residuals."""
    out = pd.DataFrame(np.nan, index=y.index, columns=y.columns)
    X = [x.reindex_like(y) for x in regressors]
    for i, t in enumerate(y.index):
        yt = y.iloc[i].to_numpy()
        xt = np.column_stack([np.ones_like(yt)] + [x.iloc[i].to_numpy() for x in X])
        ok = np.isfinite(yt) & np.isfinite(xt).all(axis=1)
        if ok.sum() < min_assets:
            continue
        coef, *_ = np.linalg.lstsq(xt[ok], yt[ok], rcond=None)
        res = np.full_like(yt, np.nan)
        res[ok] = yt[ok] - xt[ok] @ coef
        out.iloc[i] = res
    return out


def main():
    wd = PF.World()
    cal = wd.cal
    vix, _ = D.load_index("VIX", cal)
    move, _ = D.load_index("MOVE", cal)
    bk = PF.books(wd)
    b0 = bk["B0 (MOM + MACD band, walk-forward)"]
    res_real = simulate(wd.open, wd.close, b0, **PF.VARIANTS["realistic"])
    res_n1 = simulate(wd.open, wd.close, b0, **PF.VARIANTS["naive_1"])
    mom_from_2020 = S.prop_weights(wd.mom).fillna(0.0)
    res_mom2020 = simulate(wd.open, wd.close, mom_from_2020, **PF.VARIANTS["naive_1"])

    lv = R.index_labels(vix, cal, wd.rungs, C.PRE_TEST_END)
    lm = R.index_labels(move, cal, wd.rungs, C.PRE_TEST_END)
    wf = wd.wf
    meta = {"what": "B0's mean daily return per VIX x MOVE state (bp per day), NW SE (lag 5), days per cell",
            "sample_rows": "WF quarters 2022Q1-2025Q2 unless the row says descriptive-from-2020",
            "S1": "ceil(2 ln v): VIX <= 20.1 / 20.1-33.1 / > 33.1; MOVE <= 90.0 / 90.0-148.4 / > 148.4",
            "cuts": "S1 data-free, D rolling 252-day tercile, S2 frozen per rung, S3 full-sample (look-ahead)",
            "measurable": "display flag: a state with fewer than 60 days (about a quarter) is marked not measurable; "
                          "the flag was added after the first run showed cells of 0-15 days"}

    # ---- (i) 2-D tables
    tabs = []
    for cut in lv:
        for book, res in (("B0 realistic", res_real), ("B0 naive_1", res_n1)):
            r = res["pnl_net"][wf]
            t = R.returns_by_state(r, lv[cut][wf], lm[cut][wf])
            tabs.append(t.assign(cut=cut, book=book, sample="WF 2022Q1-2025Q2"))
    for cut in ("S1 data-free", "S3 full-sample LOOKAHEAD"):
        m = (cal >= pd.Timestamp("2020-08-01")) & (cal <= pd.Timestamp(C.PRE_TEST_END))
        r = res_mom2020["pnl_net"][m]
        t = R.returns_by_state(r, lv[cut][m], lm[cut][m])
        tabs.append(t.assign(cut=cut, book="MOM prop-signal naive_1", sample="descriptive-from-2020 (2020-08 to 2025-06)"))
    tab = pd.concat(tabs)
    tab["vix"] = tab["a"].map(NAMES); tab["move"] = tab["b"].map(NAMES)
    write_result(tab.drop(columns=["a", "b"]).set_index(["sample", "book", "cut", "vix", "move"]), "05_vix_move_table", meta)

    # ---- (ii) homework's rolling quintiles, each index alone; chapter 04's two-way sort
    st = []
    for name, v in (("VIX", vix), ("MOVE", move)):
        qn = R.index_quintile_rolling(v)
        t = R.returns_by_state(res_real["pnl_net"][wf], qn[wf]).rename(columns={"a": "quintile"}).drop(columns="b")
        st.append(t.assign(index=name, book="B0 realistic"))
    write_result(pd.concat(st).set_index(["index", "book", "quintile"]), "05_vix_move_states",
                 dict(meta, what="B0's mean daily return per rolling-252-day quintile of each index (homework B, second cut)"))
    two = []
    for cut in ("S1 data-free", "D rolling"):
        for k, nm in NAMES.items():
            m = wf & (lv[cut] == k)
            if m.sum() == 0:
                continue
            bt = M.bucket_test(wd.mom[m], wd.fwd[m], nw_lag=C.NW_LAG)
            two.append(bt.reset_index().assign(cut=cut, vix=nm, days=int(m.sum())))
    write_result(pd.concat(two).set_index(["cut", "vix", "bucket"]), "05_vix_conditioning",
                 dict(meta, what="chapter 04's two-way sort: MOM buckets G1-G5 within each VIX state, mean forward return"))

    # ---- (iii) lecture 5's residual test
    r = S.returns(wd.close)
    rows = []
    for idx_name, v in (("VIX", vix), ("MOVE", move)):
        dln = np.log(v).diff()
        for n in (126, 63):
            beta = vix_beta(r, dln, n)
            for regs_name, regs in (("MOM, MACD", [wd.mom, wd.cells[(12, 26)]]),
                                    ("MOM, MACD, |MACD|", [wd.mom, wd.cells[(12, 26)], wd.cells[(12, 26)].abs()])):
                if (idx_name, n) != ("VIX", 126) and regs_name != "MOM, MACD":
                    continue
                eps = cross_section_residual(beta, regs)
                score = S.centred(eps)
                bt = M.bucket_test(score[wf], wd.fwd[wf], nw_lag=C.NW_LAG)
                ic = M.ic_summary(eps[wf], wd.fwd[wf])
                ic_raw = M.ic_summary(beta[wf], wd.fwd[wf])
                w = wd.from_start(S.prop_weights(score).fillna(0.0))
                out = {"index": idx_name, "beta_window": n, "regressors": regs_name,
                       "spread_g5_g1": bt.loc["G5-G1", "mean"], "spread_t": bt.loc["G5-G1", "t"],
                       "monotone_g1_to_g5": bool(np.all(np.diff(bt.loc[["G1", "G2", "G3", "G4", "G5"], "mean"]) > 0)),
                       "residual_mean_ic": ic["mean_ic"], "residual_ic_t": ic["t_deflated"],
                       "raw_beta_mean_ic": ic_raw["mean_ic"]}
                for var in ("naive_1", "realistic"):
                    rr = simulate(wd.open, wd.close, w, **PF.VARIANTS[var])
                    sm = M.book_summary(rr, mask=wf)
                    out[f"book_{var}_ann_return"] = sm["ann_return"]; out[f"book_{var}_sharpe"] = sm["sharpe"]
                rows.append(out)
                if (idx_name, n, regs_name) == ("VIX", 126, "MOM, MACD"):
                    write_result(bt, "05_vix_residual_buckets",
                                 dict(meta, what="bar plot of the lecture-5 residual (VIX beta on MOM and MACD), "
                                                 "centred trailing percentile, WF 2022Q1-2025Q2"))
    write_result(pd.DataFrame(rows).set_index(["index", "beta_window", "regressors"]), "05_vix_residual",
                 dict(meta, what="lecture 5 residual test: beta to d ln(index) over the trailing window, regressed "
                                 "across assets each date on MOM and MACD 12/26; residual -> bar plot, IC, prop-signal book",
                      macd="the conventional 12/26 cell, fixed a priori, since B0 retained no MACD band in 2022Q1-2025Q2"))

    show = tab[(tab.book == "B0 realistic")].pivot_table(index=["cut", "vix"], columns="move", values="mean_bp_per_day")
    days = tab[(tab.book == "B0 realistic")].pivot_table(index=["cut", "vix"], columns="move", values="days")
    print("B0 realistic, mean bp/day by VIX (rows) x MOVE (cols):"); print(show.round(2).to_string())
    print("days:"); print(days.fillna(0).astype(int).to_string())
    print(pd.read_csv(os.path.join(C.RESULTS, "05_vix_move_states.csv"), comment="#").round(2).to_string(index=False))
    print(pd.DataFrame(rows).round(4).to_string(index=False))


if __name__ == "__main__":
    main()
