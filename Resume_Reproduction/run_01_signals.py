"""W3 (homework A2-A4): signals, the MACD grid, the smoother, and walk-forward selection of B0.

    .venv/bin/python Resume_Reproduction/run_01_signals.py

Every number here covers 2022Q1 -> 2025Q2 only (train-ladder and OV quarters); Test quarters
are produced and read in W10. Each quarter's MACD band, smoother and MOM-only fallback come from
the rung that trades it, using the quarters before it only.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C              # noqa: E402
import rr_data as D             # noqa: E402
import rr_metrics as M          # noqa: E402
import rr_signals as S          # noqa: E402
import rr_split as SP           # noqa: E402
from rr_io import write_result  # noqa: E402


def masks(cal, rs):
    wf = np.zeros(len(cal), bool); blk = pd.Series("", index=cal)
    for r in rs:
        wf[r["test"]] = True
        blk.iloc[r["test"]] = r["block"]
    return pd.Series(wf, index=cal), blk


def main():
    etfs = D.load_etfs()
    cal = D.calendar(etfs)
    close = D.panel(etfs, "close", cal)
    fwd = S.forward_return(close)
    mom = S.mom_score(close)
    cells = S.macd_cells()
    cell_scores = {c: S.macd_score(close, c[0], c[1], "proportional") for c in cells}

    rs = SP.pre_test(SP.rungs(cal))
    wf, blk = masks(cal, rs)
    samples = {"WF 2022Q1-2025Q2": wf, "train-ladder quarters": wf & (blk == "train-ladder"),
               "OV quarters": wf & (blk == "OV")}
    base_meta = {"alignment": "signal uses closes through t; scored return close_{t+1} -> close_{t+6} (h=5)",
                 "buckets": "fixed 0.2 cuts of the trailing-252-day percentile, pooled across 37 assets",
                 "se": f"Newey-West, lag {C.NW_LAG}, across per-date means"}

    # --- A3 / C7: momentum bar plot, IC and win rate
    rows = []
    for name, m in samples.items():
        bt = M.bucket_test(mom[m], fwd[m], nw_lag=C.NW_LAG)
        rows.append(bt.assign(sample=name))
    write_result(pd.concat(rows).reset_index().set_index(["sample", "bucket"]), "01_bucket_mom",
                 dict(base_meta, what="risk-adjusted 21-day momentum, bucket test (C7)"))

    # --- A2 / A3 / C8: MACD grid, every cell and rule, on the stitched record and per block
    grid = []
    for c in cells:
        for rule in C.BASELINE["macd_rules"]:
            sc = cell_scores[c] if rule == "proportional" else S.macd_score(close, c[0], c[1], rule)
            for name, m in samples.items():
                bt = M.bucket_test(sc[m], fwd[m], nw_lag=C.NW_LAG).loc["G5-G1"]
                wr = M.win_rate(sc[m], fwd[m])
                row = {"nf": c[0], "ns": c[1], "rule": rule, "sample": name, "spread": bt["mean"],
                       "se_nw": bt["se_nw"], "t": bt["t"], "dates": bt["dates"],
                       "win_rate": wr["win_rate"], "base_rate": wr["base_rate"],
                       "win_rate_relative": wr["win_rate_relative"]}
                if rule == "proportional":
                    row["mean_ic"] = M.ic_summary(sc[m], fwd[m])["mean_ic"]
                grid.append(row)
    write_result(pd.DataFrame(grid).set_index(["nf", "ns", "rule", "sample"]), "01_macd_grid",
                 dict(base_meta, what="MACD grid (chapter 03 ladder + 12/26), G5-G1 spread per cell and rule; "
                                      "descriptive, no selection is made from this file"))
    conv = []
    for rule in C.BASELINE["macd_rules"]:
        sc = S.macd_score(close, 12, 26, rule)
        bt = M.bucket_test(sc[wf], fwd[wf], nw_lag=C.NW_LAG)
        conv.append(bt.assign(rule=rule))
    write_result(pd.concat(conv).reset_index().set_index(["rule", "bucket"]), "01_bucket_macd_12_26",
                 dict(base_meta, what="conventional MACD 12/26/9 through the bar plot, three rules (homework A3)",
                      sample_rows="WF 2022Q1-2025Q2"))

    # --- A4, descriptive: every cell under every admissible smoother, on the stitched record
    sm = []
    for c in cells:
        for q in C.BASELINE["smoothers"]:
            if q > 1 and q >= c[0]:
                continue
            sc = S.macd_score(close, c[0], c[1], "proportional", q)
            bt = M.bucket_test(sc[wf], fwd[wf], nw_lag=C.NW_LAG).loc["G5-G1"]
            sm.append({"nf": c[0], "ns": c[1], "q": q, "spread": bt["mean"], "se_nw": bt["se_nw"], "t": bt["t"],
                       "score_turnover": S.score_turnover(sc[wf])})
    write_result(pd.DataFrame(sm).set_index(["nf", "ns", "q"]), "01_smoother_descriptive",
                 dict(base_meta, what="homework A4, descriptive: smoother q on every cell, WF 2022Q1-2025Q2; "
                                      "no selection is made from this file", sample_rows="WF 2022Q1-2025Q2"))

    # --- walk-forward selection: band, smoother, fallback per rung (A2, A4, C8, C19)
    ledger, selections = [], []
    for r in rs:
        selections.append(S.select_rung(r, cal, close, fwd, cell_scores, ledger))
    sel = pd.DataFrame(selections).set_index("test_q")
    sel["band"] = sel["band"].map(lambda b: " ".join(f"{f}/{s}" for f, s in b))
    write_result(sel, "01_selected_signals", dict(base_meta, what="per-rung choice: MACD band, smoother q, MOM-only fallback"))
    led = pd.DataFrame(ledger)
    smooth = led[led.stage == "smoother"].set_index(["test_q", "params"])
    write_result(smooth, "01_smoother_grid", dict(base_meta, what="smoother candidates per rung, on the rung's training window (A4)"))
    led.insert(0, "workstream", "W3")
    write_result(led, "run_ledger", {"what": "every candidate tried, per rung, with whether it was selected"}, index=False)

    # --- B0's score over the record, its bar plot, IC and win rate
    b0 = S.b0_score(close, mom, cell_scores, selections, cal, rs)
    out = []
    for name, m in samples.items():
        bt = M.bucket_test(b0[m], fwd[m], nw_lag=C.NW_LAG)
        ic = M.ic_summary(b0[m], fwd[m]); wr = M.win_rate(b0[m], fwd[m])
        icm = M.ic_summary(mom[m], fwd[m]); wrm = M.win_rate(mom[m], fwd[m])
        out.append({"sample": name, "b0_spread": bt.loc["G5-G1", "mean"], "b0_se": bt.loc["G5-G1", "se_nw"],
                    "b0_mean_ic": ic["mean_ic"], "b0_icir": ic["icir"], "b0_t_ic": ic["t_deflated"],
                    "b0_win": wr["win_rate"], "b0_base": wr["base_rate"], "b0_win_rel": wr["win_rate_relative"],
                    "mom_mean_ic": icm["mean_ic"], "mom_icir": icm["icir"], "mom_t_ic": icm["t_deflated"],
                    "mom_win": wrm["win_rate"], "mom_base": wrm["base_rate"], "mom_win_rel": wrm["win_rate_relative"],
                    "dates": ic["dates"]})
    write_result(pd.DataFrame(out).set_index("sample"), "01_signal_quality",
                 dict(base_meta, what="IC (C5) and signal win rate (C6) for MOM and B0's stitched score",
                      ic="per-date Spearman across 37 assets; t deflated by sqrt(h)"))

    print(pd.read_csv(os.path.join(C.RESULTS, "01_bucket_mom.csv"), comment="#").round(5).to_string(index=False))
    print(sel[["block", "band", "q", "fallback_mom_only", "val_spread", "n_warm"]].to_string())
    print(pd.read_csv(os.path.join(C.RESULTS, "01_signal_quality.csv"), comment="#").round(4).T.to_string())


if __name__ == "__main__":
    main()
