"""Round 2: export what the Round 2 figures plot (no choice is made here).

    .venv/bin/python Resume_Reproduction/run_22_round2_reconcile.py

Re-evaluates the frozen T0, T1 and T3 with run_21's builders (deterministic) to save their daily
excess returns, T1's leverage, and the VIX state.
"""
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C                       # noqa: E402
import rr_metrics as M                   # noqa: E402
from rr_io import write_result           # noqa: E402
from run_20_round2 import R2             # noqa: E402
from run_21_round2_test import books, chosen  # noqa: E402


def main():
    m2, m3 = chosen("20_regime_multiplier"), chosen("20b_t3_multiplier")
    r2 = R2(last_me="2026-05-29")
    runs, ws, lev = books(r2, m2, m3, "2026-06-26")
    rf = r2.wd.rf
    rec = r2.mask("2021-02-01", "2026-06-29")
    out = pd.DataFrame({k: M.excess_returns(runs[k]["pnl_net"], rf, runs[k]["net"]) for k in ("T0 naive_1", "T0", "T1", f"T3 (m={m3})")})
    out["T0_gross"] = runs["T0"]["gross"]; out["T1_gross"] = runs["T1"]["gross"]; out["T1_net"] = runs["T1"]["net"]
    out["vix_state_D"] = r2.vix_lab["D rolling"]
    out["block"] = ["Test" if d >= pd.Timestamp("2025-07-01") else ("OV" if d >= pd.Timestamp("2024-07-01") else "pre-OV") for d in r2.cal]
    write_result(out[rec], "22_daily_excess", {"round": "2", "what": "daily excess returns (DTB3 x net) of the frozen books, "
                                               "gross and net exposure, VIX state; re-evaluated for plotting"})
    lv = pd.DataFrame({"T1_over_T0": lev, "T0_gross": ws[0].abs().sum(axis=1), "T1_gross": ws[1].abs().sum(axis=1)})
    write_result(lv, "22_leverage_month_end", {"round": "2", "what": "month-end leverage of T1 relative to T0, and gross exposure"})
    print(out[rec].describe().round(4).T.to_string())


if __name__ == "__main__":
    main()
