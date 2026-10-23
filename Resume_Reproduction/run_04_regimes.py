"""W5 (resume bullet 3, C14-C16): per-asset volume and volatility regimes, dynamic and static cuts.

    .venv/bin/python Resume_Reproduction/run_04_regimes.py

Scored on the walk-forward quarters 2022Q1 -> 2025Q2 (Test is added in W10). MOM is the quoted
signal; MACD 12/26 is the companion. Every file names its cut; full-sample cuts carry _LOOKAHEAD.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C                       # noqa: E402
import rr_data as D                      # noqa: E402
import rr_portfolio as PF                # noqa: E402
import rr_regimes as R                   # noqa: E402
from rr_io import write_result           # noqa: E402

PERIODS = {"2022": ("2022-01-01", "2022-12-31"), "2023": ("2023-01-01", "2023-12-31"),
           "2024H1": ("2024-01-01", "2024-06-30"), "2024H2-2025H1 (OV)": ("2024-07-01", "2025-06-30")}
BONDS = [t for t, c in C.UNIVERSE_CATEGORY.items() if c == "bonds"]


def main():
    wd = PF.World()
    vol = D.panel(wd.etfs, "volume", wd.cal)
    V = R.volume_measure(vol)
    SIG = R.sigma_measure(wd.close)
    cuts = {
        "rolling": (R.cut_rolling(V), R.cut_rolling(SIG)),
        "frozen": (R.cut_frozen_per_rung(V, wd.cal, wd.rungs), R.cut_frozen_per_rung(SIG, wd.cal, wd.rungs)),
        "fullsample_LOOKAHEAD": (R.cut_fullsample(V, C.PRE_TEST_END), R.cut_fullsample(SIG, C.PRE_TEST_END)),
    }
    fwd_norm = wd.fwd / (SIG * np.sqrt(C.H))
    signals = {"MOM": wd.mom, "MACD 12/26": wd.cells[(12, 26)]}
    rho = np.nanmean([V[t].corr(SIG[t], method="spearman") for t in V.columns])
    meta = {"what": "3x3 grid of the signal-weighted forward return (bp per 5-day window) inside each volume x sigma cell; "
                    "pooled G5-G1 beside it, descriptive",
            "signal": "MOM quoted; MACD 12/26 companion", "sample_rows": "WF quarters 2022Q1-2025Q2",
            "floors": "a cell is measurable only if it has >= 250 dates, >= 1000 asset-days and >= 10 episodes",
            "volume_sigma_rank_corr": f"{rho:.3f} (mean per-asset Spearman)"}

    corners, by_period = [], []
    for cname, (vl, sl) in cuts.items():
        frames = []
        for sname, sc in signals.items():
            for universe, cols in (("all 37", list(wd.close.columns)), ("ex-bonds", [c for c in wd.close.columns if c not in BONDS])):
                for target, fw in (("return", wd.fwd), ("sigma-normalised", fwd_norm)):
                    if universe == "ex-bonds" and target != "return":
                        continue
                    g, per_date = R.regime_grid(sc[cols], fw[cols], vl[cols], sl[cols], wd.wf)
                    cd = R.corner_difference(per_date)
                    units = "bp of return per 5-day window"
                    if target == "sigma-normalised":          # a z-score, not a return: undo the bp scaling
                        units = "z-score units x 100 per 5-day window"
                        for col in ("signal_weighted_bp", "se_bp", "pooled_g5_g1_bp"):
                            g[col] = g[col] / 100.0
                        cd["diff_bp"], cd["se_bp"] = cd["diff_bp"] / 100.0, cd["se_bp"] / 100.0
                    frames.append(g.assign(signal=sname, universe=universe, target=target, units=units))
                    corners.append(dict(cd, cut=cname, signal=sname, universe=universe, target=target, units=units))
                    if universe == "all 37" and target == "return":
                        for pname, (a, b) in PERIODS.items():
                            m = (wd.cal >= a) & (wd.cal <= b)
                            pdiff = {k: v[m] for k, v in per_date.items()}
                            r = R.corner_difference(pdiff)
                            by_period.append(dict(r, cut=cname, signal=sname, period=pname,
                                                  block="OV" if "OV" in pname else "train-ladder"))
        grid = pd.concat(frames).reset_index().set_index(["signal", "universe", "target", "volume", "sigma"])
        write_result(grid, f"04_regime_grid_{cname}", dict(meta, cut=cname))
    cmeta = dict(meta, what="corner difference: high-volume/low-sigma minus low-volume/high-sigma, per-date signal-weighted return, NW SE")
    write_result(pd.DataFrame(corners).set_index(["cut", "signal", "universe", "target"]), "04_regime_corner", cmeta)
    write_result(pd.DataFrame(by_period).set_index(["cut", "signal", "period"]), "04_regime_by_period",
                 dict(cmeta, what="corner difference by period; 'consistently' needs 5 of 5 periods once Test is added (W10)"))

    # S1 on sigma: does a fixed absolute cut label the regime or the asset?
    s1 = R.cut_datafree_sigma(SIG)
    rows = []
    for name, lab in (("S1 data-free", s1), ("D rolling", cuts["rolling"][1])):
        l = lab.loc[wd.wf.to_numpy()]
        usual = l.mode().iloc[0]
        share = float((l == usual).sum().sum() / l.notna().sum().sum())
        always = [t for t in l.columns if l[t].dropna().nunique() == 1]
        rows.append({"cut": name, "share_of_asset_days_on_the_assets_usual_label": share,
                     "assets_always_one_label": " ".join(always)})
    write_result(pd.DataFrame(rows).set_index("cut"), "04_sigma_fixed_cut_demo",
                 {"what": "S1 demonstration: a fixed absolute cut on per-asset sigma sorts assets, not regimes",
                  "sample_rows": "WF quarters 2022Q1-2025Q2"})

    for cname in cuts:
        g = pd.read_csv(os.path.join(C.RESULTS, f"04_regime_grid_{cname}.csv"), comment="#")
        g = g[(g.signal == "MOM") & (g.universe == "all 37") & (g.target == "return")]
        print(f"== {cname}: MOM signal-weighted return, bp per 5 days (t); * = not measurable")
        print(g.assign(cellv=g.signal_weighted_bp.round(1).astype(str) + " (" + g.t.round(2).astype(str) + ")" + np.where(g.measurable, "", " *"))
              .pivot(index="sigma", columns="volume", values="cellv").reindex(index=list(R.LABELS), columns=list(R.LABELS)).to_string())
    cc = pd.read_csv(os.path.join(C.RESULTS, "04_regime_corner.csv"), comment="#")
    print(cc.round(2).to_string(index=False))
    print(pd.read_csv(os.path.join(C.RESULTS, "04_regime_by_period.csv"), comment="#").query("signal == 'MOM'")[["cut", "period", "diff_bp", "t", "dates"]].round(2).to_string(index=False))
    print(pd.read_csv(os.path.join(C.RESULTS, "04_sigma_fixed_cut_demo.csv"), comment="#").to_string(index=False))


if __name__ == "__main__":
    main()
