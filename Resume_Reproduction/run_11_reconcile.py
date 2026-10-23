"""W11: export what the figures plot, and fill the claims ledger's status column from the results.

    .venv/bin/python Resume_Reproduction/run_11_reconcile.py

Re-evaluates the frozen books with the same builders as run_09 (deterministic, no choice is made)
to save their daily PnL, adds the 18-quarter waterfall components, then writes each claim's
measured status into OUTLINE.md section 2 from the result files.
"""
import json
import os
import re
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C                       # noqa: E402
import rr_models as MD                   # noqa: E402
import rr_optimizer as OP                # noqa: E402
import rr_portfolio as PF                # noqa: E402
from rr_engine import simulate           # noqa: E402
from rr_io import write_result           # noqa: E402
from run_09_test import build            # noqa: E402


def rd(name):
    return pd.read_csv(os.path.join(C.RESULTS, f"{name}.csv"), comment="#")


def export_series():
    wd = PF.World(include_test=True)
    runs, inp, bk = build(wd)
    choice = json.load(open(os.path.join(C.RESULTS, "08_optimizer_choice.json")))
    panel = MD.build_panel(wd)
    mu, chol = OP.model_inputs(wd, panel, choice["model"])
    tau = choice["tau_multiple"] * (C.COST_BP + C.SLIP_BP) / 1e4
    w = OP.optimized_weights(wd, mu, chol, choice["gamma"], choice["cap"], tau, 0.0, "sample", wd.cal[wd.wf.to_numpy()])
    runs["Optimizer, net 0"] = simulate(wd.open, wd.close, w, **PF.VARIANTS["realistic"])
    keep = ["B0 naive_0", "B0 naive_1", "B0", "B1", "Optimizer, net 0"]
    daily = pd.DataFrame({k: runs[k]["pnl_net"] for k in keep})
    daily["block"] = wd.block
    daily = daily[wd.wf]
    write_result(daily, "11_daily_pnl", {"what": "daily net PnL per $1 of the frozen books, all 18 walk-forward quarters",
                                         "note": "re-evaluated with run_09's builders for plotting; no choice is made here"})
    # waterfall over all 18 quarters, stated order naive_0 -> delay -> cost -> slippage
    w0 = bk["B0 (MOM + MACD band, walk-forward)"]
    m = wd.samples["WF"]; yrs = m.sum() / 252
    steps = [("naive_0", dict(lag=0, cost_bp=0, slip_bp=0)), ("+ one-day delay", dict(lag=1, cost_bp=0, slip_bp=0)),
             ("+ 5 bp cost", dict(lag=1, cost_bp=C.COST_BP, slip_bp=0)), ("+ 2 bp slippage", dict(lag=1, cost_bp=C.COST_BP, slip_bp=C.SLIP_BP))]
    rows = []
    for name, kw in steps:
        r = simulate(wd.open, wd.close, w0, exec_price="close", **kw)["pnl_net"][m]
        rows.append({"step": name, "ann_return_bp": float(r.sum() / yrs * 1e4)})
    wf = pd.DataFrame(rows)
    wf["change_bp"] = wf["ann_return_bp"].diff()
    write_result(wf.set_index("step"), "11_waterfall_wf", {"what": "B0 annual return after each execution assumption, "
                                                           "stated order, all 18 quarters", "units": "bp per year"})


def status_lines():
    sc = rd("06_scorecard").set_index(["book", "sample"])
    boot = rd("08_robustness_rebuild_bootstrap").set_index(["sample", "mean_block"])
    hc = rd("03_haircut_waterfall_test").set_index(["book", "sample"])
    hrob = rd("08_robustness_haircut")
    rb = rd("04_regime_bootstrap")
    per = rd("04_regime_by_period_with_test")
    sel = rd("09_selected_signals_all_rungs")
    mom = rd("01_bucket_mom").set_index(["sample", "bucket"])
    q = rd("01_signal_quality").set_index("sample")
    mt = rd("07_model_test").set_index("model")
    ot = rd("08_optimizer_test").set_index(["book", "sample"])
    b0, b1 = sc.loc[("B0", "WF")], sc.loc[("B1", "WF")]
    bw = boot.loc[("WF", 21)]
    wide = boot.loc["WF"]
    roll = per[(per.cut == "rolling") & (per.period == "WF 2022Q1-2026Q2")].iloc[0]
    has_band = sel["band"].fillna("").astype(str).str.strip() != ""
    n_band = int(has_band.sum())
    n_kept = int((has_band & ~sel["fallback_mom_only"].astype(bool)).sum())
    naive_ci = hrob[(hrob.check.str.contains("bootstrap")) & (hrob.mean_block == 21)].iloc[0]
    hcw, hct = hc.loc[("B0", "WF")], hc.loc[("B0", "train-ladder")]
    f = lambda x, d=2: f"{x:+.{d}f}"  # noqa: E731
    pct = lambda x: f"{100 * x:+.1f}%"  # noqa: E731
    S = {}
    S["C1"] = "**reproduced** — engine equals backtest.py per asset to 1e-9 (tests/test_parity.py)"
    S["C2"] = f"**measured** — B0 Sharpe {f(b0.sharpe)}, 90% CI [{f(bw.sharpe_B0_90_lo)}, {f(bw.sharpe_B0_90_hi)}], 18 quarters"
    S["C3"] = f"**measured** — B0 max drawdown {b0.max_dd_units:.3f} of initial capital"
    S["C4"] = f"**measured** — B0 {b0.turnover_ann_per_gross:.1f} turns of gross a year"
    S["C5"] = (f"**measured** — B0 score mean IC {q.loc['WF 2022Q1-2025Q2', 'b0_mean_ic']:+.3f} (2022Q1–2025Q2); "
               f"OV-chosen model on Test {mt.loc['EW', 'test_mean_ic']:+.3f}")
    S["C6"] = (f"**measured** — win rate {q.loc['WF 2022Q1-2025Q2', 'b0_win']:.3f} vs base {q.loc['WF 2022Q1-2025Q2', 'b0_base']:.3f}; "
               f"relative {q.loc['WF 2022Q1-2025Q2', 'b0_win_rel']:.3f} vs 0.5")
    g = mom.loc[("WF 2022Q1-2025Q2", "G5-G1")]
    S["C7"] = f"**measured, no edge** — G5−G1 {100 * g['mean']:+.2f}% per 5 days, t {g['t']:+.2f}, not monotone"
    S["C8"] = (f"**not supported** — {n_band} of {len(sel)} rungs found a MACD band, {n_kept} passed validation; "
               f"B0 traded MOM only in {int(sel['fallback_mom_only'].astype(bool).sum())} of {len(sel)} quarters")
    S["C9"] = S["C10"] = S["C11"] = S["C12"] = "**implemented and swept** — 03_haircut_*, 08_robustness_haircut"
    S["C13"] = (f"**not supported as a ratio** — naive_1 return {pct(hcw.naive_1_ann)}/yr, 90% CI "
                f"[{pct(naive_ci.ci90_lo)}, {pct(naive_ci.ci90_hi)}], so H is undefined; friction {hcw.drag_bp_yr:.0f} bp/yr; "
                f"on the train-ladder quarters alone H_1 = {100 * hct.H_1:.0f}%")
    S["C14"] = "**computed** — V and σ per asset, through t−1"
    S["C15"] = "**computed** — D, S2, S3 cuts (+ S1 demonstration); all nine cells measurable"
    S["C16"] = (f"**not supported** — HV/LV − LV/HV {roll.diff_bp:+.1f} bp per 5 days (t {roll.t:+.2f}), "
                f"{int(roll.periods_positive_of_5)} of 5 periods positive, 90% CI "
                f"[{rb.ci90_lo_bp.min():+.0f}, {rb.ci90_hi_bp.max():+.0f}] bp (widest over blocks)")
    S["C17"] = S["C18"] = S["C19"] = "**implemented** — rr_rebuild, frozen in config.REBUILD before any rung ran"
    S["C20"] = (f"**not supported** — ΔSR {f(b1.d_sharpe_vs_B0)} over 18 quarters, 90% CI [{f(wide.d_sharpe_90_lo.min())}, "
                f"{f(wide.d_sharpe_90_hi.max())}] (widest over blocks); {f(sc.loc[('B1', 'Test'), 'd_sharpe_vs_B0'])} on Test; "
                f"B0's Sharpe CI includes 0, so a percentage is undefined")
    S["C21"] = (f"**partly** — ΔTO {pct(b1.d_turnover_pct_vs_B0)} over 18 quarters, 90% CI "
                f"[{pct(wide.d_turnover_pct_90_lo.min())}, {pct(wide.d_turnover_pct_90_hi.max())}]; "
                f"{pct(sc.loc[('B1', 'Test'), 'd_turnover_pct_vs_B0'])} on Test; −14% not reached")
    o = ot.loc[("Optimizer, net 0", "WF")]
    S["optimizer"] = f"OV-chosen optimizer: {pct(o.ann_return)}/yr, Sharpe {f(o.sharpe)}, {o.turnover_ann_per_gross:.1f} turns, 18 quarters"
    return S


def fill_outline(S):
    p = os.path.join(C.HERE, "OUTLINE.md")
    s = open(p, encoding="utf-8").read()
    for cid, text in S.items():
        if not re.fullmatch(r"C\d+", cid):
            continue
        pat = re.compile(rf"^(\| {cid} \|.*?\| )(unmeasured|\*\*[^|]*)( \| [^|]*\|)$", re.M)
        s, n = pat.subn(lambda m: m.group(1) + text + m.group(3), s)
        if n != 1:
            raise SystemExit(f"could not place the status of {cid}")
    s = s.replace("Status of every number below: **unmeasured**.", "Status column filled from the results by run_11_reconcile.py.")
    open(p, "w", encoding="utf-8").write(s)


def main():
    export_series()
    S = status_lines()
    fill_outline(S)
    with open(os.path.join(C.RESULTS, "11_claim_status.json"), "w") as fh:
        json.dump(S, fh, indent=2, ensure_ascii=False)
    for k, v in S.items():
        print(f"{k}: {v}")
    print(rd("11_waterfall_wf").round(1).to_string(index=False))


if __name__ == "__main__":
    main()
