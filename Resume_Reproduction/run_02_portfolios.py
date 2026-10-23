"""W4, part 1 (homework A1, A3): every book under the three execution variants.

    .venv/bin/python Resume_Reproduction/run_02_portfolios.py

Train-ladder and OV quarters only (2022Q1 -> 2025Q2); Test is read in W10.
"""
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C                       # noqa: E402
import rr_metrics as M                   # noqa: E402
import rr_portfolio as PF                # noqa: E402
from rr_engine import simulate           # noqa: E402
from rr_io import write_result           # noqa: E402


def main():
    wd = PF.World()
    bk = PF.books(wd)
    rows, conc = [], []
    for name, w in bk.items():
        for var, kw in PF.VARIANTS.items():
            res = simulate(wd.open, wd.close, w, **kw)
            for sname, m in wd.samples.items():
                s0 = M.book_summary(res, mask=m)
                s1 = M.book_summary(res, rf=wd.rf, mask=m)
                row = s0.to_dict()
                row.update({"sharpe_rf0": s0["sharpe"], "sharpe_dtb3": s1["sharpe"], "book": name,
                            "variant": var, "sample": sname})
                row.pop("sharpe"); row.pop("rf")
                rows.append(row)
            if var == "realistic":
                c = M.concentration(res, C.UNIVERSE_CATEGORY, mask=wd.wf)
                conc.append(dict(c.to_dict(), book=name))
    out = pd.DataFrame(rows).set_index(["book", "variant", "sample"])
    meta = {"what": "every book under naive_0 (same close, no cost), naive_1 (next close, no cost) and "
                    "realistic (next close, 5 bp + 2 bp)",
            "samples": "WF = 2022Q1-2025Q2; train-ladder = 2022Q1-2024Q2; OV = 2024Q3-2025Q2",
            "capital": "$1 constant notional; returns additive; drawdown in units of initial capital",
            "rf": "sharpe_rf0 and sharpe_dtb3 (DTB3 x net exposure) side by side"}
    write_result(out, "02_portfolio_metrics", meta)
    write_result(pd.DataFrame(conc).set_index("book"), "02_concentration",
                 {"what": "largest weight, Herfindahl and PnL share by category, realistic, WF 2022Q1-2025Q2"})
    show = out.xs("WF", level="sample")[["cum_pnl", "ann_return", "ann_vol", "sharpe_rf0", "sharpe_dtb3",
                                          "max_dd_units", "turnover_ann_per_gross", "net_mean"]]
    print(show.round(4).to_string())


if __name__ == "__main__":
    main()
