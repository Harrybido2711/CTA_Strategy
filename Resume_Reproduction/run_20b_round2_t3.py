"""Round 2, amendment 1, before Test: T3, daily leverage and a daily high-VIX multiplier.

    .venv/bin/python Resume_Reproduction/run_20b_round2_t3.py

Same choice rule as T2 (one-SE toward m = 1 on 2021-02 -> 2024-06, OV confirms), same grid.
No position past 2025-06-30.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C                       # noqa: E402
import rr_metrics as M                   # noqa: E402
import rr_tsmom as T                     # noqa: E402
from rr_engine import simulate           # noqa: E402
from rr_io import write_result           # noqa: E402
from run_20_round2 import R2, WINDOWS    # noqa: E402

P = C.ROUND2


def main():
    r2 = R2()
    rf = r2.wd.rf
    w0 = r2.t0()
    res0 = r2.run(w0, "realistic")
    ex0 = M.excess_returns(res0["pnl_net"], rf, res0["net"])
    cw, ov, rec = (r2.mask(*WINDOWS[k]) for k in ("choice window 2021-02..2024-06", "OV 2024-07..2025-06", "record 2021-02..2025-06"))
    runs, ex = {}, {}
    for m in P["regime_multiplier_grid"]:
        w3, lev = T.t3_targets(w0, r2.xr, r2.cal, r2.high, m, "2021-01-29", "2025-06-27")
        res = simulate(r2.wd.open, r2.wd.close, w3, lag=C.LAG, exec_price="close", cost_bp=C.COST_BP, slip_bp=C.SLIP_BP,
                       deadband=P["deadband"])
        runs[m], ex[m] = res, M.excess_returns(res["pnl_net"], rf, res["net"])
    srs = {m: M.sharpe(ex[m][cw]) for m in runs}
    best = max(srs, key=srs.get)
    idx = M.stationary_bootstrap_indices(int(cw.sum()), 21, 1000, seed=11)
    xb = ex[best][cw].to_numpy()
    rows = []
    for m in P["regime_multiplier_grid"]:
        d = M.sharpe_rows(xb[idx]) - M.sharpe_rows(ex[m][cw].to_numpy()[idx])
        se = float(np.nanstd(d))
        rows.append({"m": m, "sharpe_choice_window": srs[m], "shortfall_vs_best": srs[best] - srs[m], "se_shortfall": se,
                     "within_one_se": srs[best] - srs[m] <= se, "sharpe_OV": M.sharpe(ex[m][ov]),
                     "sharpe_record": M.sharpe(ex[m][rec]), "ann_excess_record": float(ex[m][rec].mean() * 252),
                     "max_dd_record": M.max_drawdown(runs[m]["pnl_net"][rec])[0],
                     "turnover_record": M.annual_turnover(runs[m]["turnover_exec"][rec]),
                     "gross_mean_record": float(runs[m]["gross"][rec].mean())})
    ch = pd.DataFrame(rows)
    picked = float(ch[ch.within_one_se].sort_values("m", ascending=False).iloc[0]["m"])
    ch["chosen"] = ch.m == picked
    t0row = {"m": "T0 reference", "sharpe_choice_window": M.sharpe(ex0[cw]), "sharpe_OV": M.sharpe(ex0[ov]),
             "sharpe_record": M.sharpe(ex0[rec]), "ann_excess_record": float(ex0[rec].mean() * 252),
             "max_dd_record": M.max_drawdown(res0["pnl_net"][rec])[0], "turnover_record": M.annual_turnover(res0["turnover_exec"][rec]),
             "gross_mean_record": float(res0["gross"][rec].mean())}
    out = pd.concat([ch, pd.DataFrame([t0row])], ignore_index=True)
    write_result(out.set_index("m"), "20b_t3_multiplier",
                 {"round": "2, amendment 1 (ROUND2.md)", "what": "T3: daily book leverage to 10% vol and a daily high-VIX multiplier m; "
                  "m chosen on 2021-02..2024-06 by Sharpe, one-SE rule toward 1.0", "chosen": picked,
                  "execution": "next close, 5 bp + 2 bp, deadband 0.5% of capital every day", "sharpe": "excess of DTB3 x net"})
    p = os.path.join(C.RESULTS, "run_ledger.csv")
    head = [l for l in open(p) if l.startswith("#")]
    led = pd.read_csv(p, comment="#")
    led = led[led.workstream != "R2-T3"]
    add = [{"workstream": "R2-T3", "test_q": "choice window", "stage": "T3 regime multiplier m", "sample": "2021-02..2024-06",
            "params": f"m={r.m}", "spread": r.sharpe_choice_window, "selected": bool(r.chosen)} for r in ch.itertuples()]
    led = pd.concat([led, pd.DataFrame(add)], ignore_index=True)
    with open(p, "w") as fh:
        fh.writelines(head); led.to_csv(fh, index=False)
    print(out.round(3).to_string(index=False))
    print("chosen m:", picked)


if __name__ == "__main__":
    main()
