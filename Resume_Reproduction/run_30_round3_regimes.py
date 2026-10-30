"""Round 3, Part A: the regime analysis under the dynamic cut D (ROUND3.md section 4).

    .venv/bin/python Resume_Reproduction/run_30_round3_regimes.py

Pre-Test only. Month-ends run through 2025-05-30, and every return after 2025-06-30 is masked
out, so the last holding month loses its one July day rather than reaching into Test.
Descriptive: nothing here chooses anything in Part B, whose grids are fixed in config.ROUND3.
"""
import os
import sys

import numpy as np
import pandas as pd
import statsmodels.api as sm

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C                       # noqa: E402
import rr_metrics as M                   # noqa: E402
import rr_round3 as R3                   # noqa: E402
import rr_tsmom as T                     # noqa: E402
from rr_io import write_result           # noqa: E402
from run_20_round2 import R2             # noqa: E402

P3, P2 = C.ROUND3, C.ROUND2
START, END = "2021-02-01", C.PRE_TEST_END
PERIODS = {"2021": ("2021-01-01", "2021-12-31"), "2022": ("2022-01-01", "2022-12-31"),
           "2023": ("2023-01-01", "2023-12-31"), "2024": ("2024-01-01", "2024-12-31"),
           "2025H1": ("2025-01-01", "2025-06-30")}
EQUITY_PARTS = {"U.S. broad": ["SPY", "QQQ", "IWM", "DIA", "MDY"],
                "U.S. sectors": ["XLK", "XLF", "XLE", "XLV", "XLI", "XLY", "XLP", "XLU", "XLB", "XLRE", "XLC"],
                "international": ["EFA", "EEM", "VGK", "EWJ", "FXI"]}
L = R3.LABELS


def t_of(mean, se):
    return float(mean / se) if se and np.isfinite(se) and se > 0 else np.nan


def cell_stats(y, inc, scale=100.0):
    d, m, se = R3.month_mean_se(y, inc)
    return {"mean_pct_per_month": m * scale, "se_pct": se * scale, "t": t_of(m, se), "months": int(len(d)),
            "asset_months": int(inc.sum().sum()), "episodes": R3.R.episodes(inc)}, d


def corner_rows(d, label):
    lo, hi, per = R3.block_bootstrap_ci(d)
    se = M.newey_west_se(d, 1)
    rows = [{"y": label, "period": "full", "corner_pct_per_month": d.mean() * 100, "se_pct": se * 100,
             "t": t_of(d.mean(), se), "months": len(d), "ci90_lo_pct": lo * 100, "ci90_hi_pct": hi * 100,
             "ci90_by_block": " ".join(f"b{b}:[{a * 100:+.2f},{c * 100:+.2f}]" for b, (a, c) in per.items())}]
    for pn, (a, b) in PERIODS.items():
        x = d[(d.index >= a) & (d.index <= b)]
        rows.append({"y": label, "period": pn, "corner_pct_per_month": x.mean() * 100 if len(x) else np.nan,
                     "months": len(x)})
    pos = sum(1 for r in rows[1:] if r["corner_pct_per_month"] > 0)
    rows[0]["periods_positive"] = f"{pos} of {len(PERIODS)}"
    rows[0]["c16_consistently"] = bool(pos == len(PERIODS) and lo > 0)
    return rows


def by_state(x, lab, scale, nw):
    out = []
    for k, name in enumerate(L):
        v = x[lab == k].dropna()
        se = M.newey_west_se(v, nw)
        out.append({"state": name, "n": int(len(v)), "ann_excess": float(v.mean() * scale) if len(v) else np.nan,
                    "se_ann": float(se * scale) if len(v) > 2 else np.nan, "t": t_of(v.mean(), se)})
    return out


def main():
    r2 = R2()
    wd, cal, xr, me, rf = r2.wd, r2.cal, r2.xr, r2.me, r2.wd.rf
    rec = r2.mask(START, END)
    pre = pd.Series(cal <= pd.Timestamp(END), index=cal)
    xr_pre = xr.where(pre, axis=0)
    meta = {"round": "3, Part A (ROUND3.md section 4)", "cut": P3["regime_cut"],
            "sample_window": f"{START}..{END}, pre-Test; month-ends {me[0].date()}..{me[-1].date()}",
            "execution": "realistic = next close, 5 bp + 2 bp; excess of DTB3"}

    ms = R3.measures(wd, xr)
    w0 = r2.t0()
    w1, lev = T.t1_targets(w0, xr)
    res = {"T0": r2.run(w0), "T1": r2.run(w1)}
    xb = {k: M.excess_returns(v["pnl_net"], rf, v["net"]).where(pre) for k, v in res.items()}

    # ---- A1: coverage and counts of every label
    cov = []
    for name in ("V_lab", "sigma_lab", "index_lab"):
        lab = ms[name]
        first = lab.notna().any(axis=1)
        cov.append({"measure": name, "level": "per asset", "first_labelled": str(lab.index[first.argmax()].date()),
                    **{f"{L[k]}_asset_days": int((lab[rec] == k).sum().sum()) for k in range(3)},
                    **{f"{L[k]}_asset_months": int((lab.loc[me] == k).sum().sum()) for k in range(3)}})
    for name in ("VIX_lab", "MOVE_lab", "corr_lab", "mkt_volume_lab"):
        lab = ms[name]
        cov.append({"measure": name, "level": "market", "first_labelled": str(lab.first_valid_index().date()),
                    **{f"{L[k]}_days": int((lab[rec] == k).sum()) for k in range(3)},
                    **{f"{L[k]}_months": int((lab.loc[me] == k).sum()) for k in range(3)}})
    write_result(pd.DataFrame(cov).set_index("measure"), "30_measures",
                 dict(meta, what="A1: first labelled date and days / month-ends per D tercile on the pre-Test record"))

    # ---- A4: the per-asset map, sign x next-month excess return, and the book's risk-scaled version
    me_all = T.month_ends(cal, start=P2["first_signal"])
    fwd = R3.holding_return(xr_pre, cal, me_all).loc[me]
    sign = T.tsmom_signal(xr, P2["lookback_months"]).loc[me]
    sig_f = r2.vol.loc[me]
    ys = {"sign x return": sign * fwd, "sign x 40%/sigma x return": sign * (P2["asset_vol_target"] / sig_f) * fwd}
    vl, sl, il = ms["V_lab"].loc[me], ms["sigma_lab"].loc[me], ms["index_lab"].loc[me]
    cells, per_month = [], {}
    for yn, y in ys.items():
        for vi in range(3):
            for si in range(3):
                inc = (vl == vi) & (sl == si) & y.notna()
                st, d = cell_stats(y, inc)
                per_month[(yn, vi, si)] = y.where(inc).mean(axis=1)
                cells.append({"y": yn, "volume": L[vi], "sigma": L[si], **st})
    write_result(pd.DataFrame(cells).set_index(["y", "volume", "sigma"]), "30_regime_map",
                 dict(meta, what="A4: per-asset V x sigma map at month-ends, mean over months of the cell's cross-sectional mean",
                      se="Newey-West lag 1 across months"))

    crn = []
    for yn in ys:
        d = (per_month[(yn, 2, 0)] - per_month[(yn, 0, 2)]).dropna()
        crn += corner_rows(d, yn)
    write_result(pd.DataFrame(crn).set_index(["y", "period"]), "30_regime_corner",
                 dict(meta, what="A4: HV/LV minus LV/HV per month; C16 = positive in every period and bootstrap CI excludes 0",
                      bootstrap="stationary over months, mean block 1, 3, 6 months, 4000 draws, widest 90% interval"))

    marg = []
    groups = {"all": list(wd.close.columns)}
    groups.update({c: [t for t in wd.close.columns if C.UNIVERSE_CATEGORY[t] == c] for c in ("equity", "bonds", "commodities", "alternatives")})
    groups.update({f"equity: {k}": v for k, v in EQUITY_PARTS.items()})
    for gn, cols in groups.items():
        for yn, y in ys.items():
            yg = y[cols]
            for mname, lab in (("volume", vl[cols]), ("sigma", sl[cols]), ("index", il[cols])):
                for k in range(3):
                    st, _ = cell_stats(yg, (lab == k) & yg.notna())
                    marg.append({"group": gn, "assets": len(cols), "y": yn, "measure": mname, "state": L[k], **st})
            a = yg.where((vl[cols] == 2) & (sl[cols] == 0)).mean(axis=1)
            b = yg.where((vl[cols] == 0) & (sl[cols] == 2)).mean(axis=1)
            d = (a - b).dropna()
            se = M.newey_west_se(d, 1)
            marg.append({"group": gn, "assets": len(cols), "y": yn, "measure": "corner HV/LV - LV/HV", "state": "",
                         "mean_pct_per_month": d.mean() * 100 if len(d) else np.nan, "se_pct": se * 100,
                         "t": t_of(d.mean(), se), "months": int(len(d))})
    write_result(pd.DataFrame(marg).set_index(["group", "y", "measure", "state"]), "30_regime_marginals",
                 dict(meta, what="A4: one-way marginals by volume, sigma and index tercile, per asset class; corner per class",
                      index="VIX for the 30 non-bond ETFs, MOVE for the 7 bond ETFs"))

    # ---- A4 regression and A7: is it new information? Pooled asset-months, SEs clustered by month
    long = pd.DataFrame({"y": ys["sign x 40%/sigma x return"].stack() * 100,
                         "y_raw": ys["sign x return"].stack() * 100,
                         "v": (ms["V_pct"].loc[me] - 0.5).stack(), "s": (ms["sigma_pct"].loc[me] - 0.5).stack(),
                         "V": vl.stack(), "S": sl.stack(), "I": il.stack(),
                         "log_sigma": np.log(sig_f).stack(),
                         "abs_z12": R3.trend_z(xr, r2.vol, 12).loc[me].abs().stack()}).dropna()
    long["month"] = long.index.get_level_values(0)
    for k, nm in ((1, "mid"), (2, "high")):
        for c in ("V", "S", "I"):
            long[f"{c}_{nm}"] = (long[c] == k).astype(float)
    specs = {
        "A4 continuous: y ~ v + s + v*s": ["v", "s", "vs"],
        "A7 model 1: y ~ regime dummies": ["V_mid", "V_high", "S_mid", "S_high", "I_mid", "I_high"],
        "A7 model 2: + log sigma, |z12|": ["V_mid", "V_high", "S_mid", "S_high", "I_mid", "I_high", "log_sigma", "abs_z12"],
    }
    long["vs"] = long["v"] * long["s"]
    reg = []
    for yname in ("y", "y_raw"):
        for sn, xs in specs.items():
            X = sm.add_constant(long[xs])
            f = sm.OLS(long[yname], X).fit(cov_type="cluster", cov_kwds={"groups": long["month"].factorize()[0]})
            for v in X.columns:
                reg.append({"y": "sign x 40%/sigma x return" if yname == "y" else "sign x return", "spec": sn, "term": v,
                            "coef_pct_per_month": float(f.params[v]), "t_cluster_month": float(f.tvalues[v]),
                            "n_asset_months": int(f.nobs), "months": int(long["month"].nunique())})
    write_result(pd.DataFrame(reg).set_index(["y", "spec", "term"]), "30_regime_regressions",
                 dict(meta, what="A4 interaction and A7 residual test; baseline categories are the low terciles; v, s are D percentiles - 0.5"))

    # ---- A3 and A5: the book by market state, contemporaneous and predictive
    states = {"VIX": ms["VIX_lab"], "MOVE": ms["MOVE_lab"], "correlation": ms["corr_lab"], "market volume": ms["mkt_volume_lab"]}
    me_rec = me[me >= pd.Timestamp(START) - pd.Timedelta(days=5)]
    bk = []
    for book, x in xb.items():
        xm = R3.book_holding_return(x, cal, me_all).reindex(me_rec)
        for sn, lab in states.items():
            for al, (xx, ll, sc, nw) in {
                "contemporaneous, daily (state t, return t)": (x[rec], lab[rec], 252, C.H),
                "predictive, daily (state t-1, return t)": (x[rec], lab.shift(1)[rec], 252, C.H),
                "predictive, monthly (state at month-end F, next month)": (xm, lab.reindex(me_rec), 12, 1),
            }.items():
                for row in by_state(xx, ll, sc, nw):
                    bk.append({"book": book, "state_of": sn, "alignment": al, **row})
    write_result(pd.DataFrame(bk).set_index(["book", "state_of", "alignment", "state"]), "30_book_by_state",
                 dict(meta, what="A3 / A5: T0 and T1 excess returns by market state, both alignments; n = days or months",
                      se="Newey-West, lag 5 days or 1 month"))

    two = []
    for book, x in xb.items():
        xm = R3.book_holding_return(x, cal, me_all).reindex(me_rec)
        for al, (xx, va, vo, sc) in {
            "contemporaneous, daily": (x[rec], ms["VIX_lab"][rec], ms["mkt_volume_lab"][rec], 252),
            "predictive, monthly": (xm, ms["VIX_lab"].reindex(me_rec), ms["mkt_volume_lab"].reindex(me_rec), 12),
        }.items():
            for a in range(3):
                for b in range(3):
                    v = xx[(va == a) & (vo == b)].dropna()
                    two.append({"book": book, "alignment": al, "VIX": L[a], "market_volume": L[b], "n": int(len(v)),
                                "ann_excess": float(v.mean() * sc) if len(v) else np.nan})
    write_result(pd.DataFrame(two).set_index(["book", "alignment", "VIX", "market_volume"]), "30_book_vix_x_volume",
                 dict(meta, what="A5: homework B's 2-D table, VIX state x market-volume state"))

    # ---- A5 check: is the predictive high-VIX month one year, or two months?
    chk = []
    for book, x in xb.items():
        xm = R3.book_holding_return(x, cal, me_all).reindex(me_rec) * 100
        for sn in ("VIX", "market volume"):
            lab = states[sn].reindex(me_rec)
            df = pd.DataFrame({"r": xm, "lab": lab, "year": xm.index.year}).dropna()
            gap = lambda d: d[d.lab == 2].r.mean() - d[d.lab == 0].r.mean()
            for y in sorted(df.year.unique()):
                d = df[df.year == y]
                chk.append({"book": book, "state_of": sn, "check": f"year {y}", "high_minus_low_pct_per_month": gap(d),
                            "high_months": int((d.lab == 2).sum()), "low_months": int((d.lab == 0).sum())})
            chk.append({"book": book, "state_of": sn, "check": "all", "high_minus_low_pct_per_month": gap(df),
                        "high_months": int((df.lab == 2).sum()), "low_months": int((df.lab == 0).sum())})
            for y in sorted(df.year.unique()):
                chk.append({"book": book, "state_of": sn, "check": f"drop year {y}", "high_minus_low_pct_per_month": gap(df[df.year != y])})
            best = df[df.lab == 2].r.nlargest(2).index
            chk.append({"book": book, "state_of": sn, "check": "drop the 2 best high months: " + " ".join(str(d.date()) for d in best),
                        "high_minus_low_pct_per_month": gap(df.drop(best))})
    write_result(pd.DataFrame(chk).set_index(["book", "state_of", "check"]), "30_book_predictive_checks",
                 dict(meta, what="A5: predictive monthly high-minus-low state gap by year, leaving a year out, and without the 2 best months"))

    # ---- A6: the regime lag, around VIX entering its high tercile
    lo_, hi_ = P3["event_window"]
    vlab = ms["VIX_lab"]
    enter = (vlab == 2) & (vlab.shift(1) != 2) & vlab.shift(1).notna()
    pos_all = np.flatnonzero(enter.to_numpy())
    first, last = cal.get_loc(cal[rec.to_numpy()][0]), cal.get_loc(cal[rec.to_numpy()][-1])
    ev, prev = [], -10 ** 9
    for p in pos_all:
        if p + lo_ - 1 >= first and p + hi_ <= last and p - prev >= P3["event_min_gap"]:
            ev.append(p); prev = p
    ratio = (ms["sigma_fast"] / ms["sigma_slow"]).mean(axis=1)
    path = []
    for k in range(lo_, hi_ + 1):
        row = {"day": k, "events": len(ev), "VIX_mean": float(np.mean([ms["VIX"].iloc[p + k] for p in ev])),
               "sigma_fast_over_slow": float(np.nanmean([ratio.iloc[p + k] for p in ev]))}
        for book, x in xb.items():
            v = x.to_numpy()
            row[f"{book}_cum_excess_pct"] = float(np.mean([np.nansum(v[p + lo_:p + k + 1]) for p in ev]) * 100)
        path.append(row)
    seg = []
    for book, x in xb.items():
        v = x.to_numpy()
        for nm, (a, b) in {"before: days -20..-1": (-20, -1), "entry day 0": (0, 0), "after: days 1..20": (1, 20),
                           "after: days 21..60": (21, 60)}.items():
            s = np.array([np.nansum(v[p + a:p + b + 1]) for p in ev]) * 100
            seg.append({"book": book, "window": nm, "events": len(ev), "mean_pct": float(s.mean()),
                        "se_pct": float(s.std(ddof=1) / np.sqrt(len(s))), "share_negative": float((s < 0).mean())})
    write_result(pd.DataFrame(path).set_index("day"), "30_regime_lag",
                 dict(meta, what="A6: mean cumulative excess return from day -20, around VIX entering its D high tercile",
                      events=" ".join(str(cal[p].date()) for p in ev), min_gap_days=P3["event_min_gap"]))
    write_result(pd.DataFrame(seg).set_index(["book", "window"]), "30_regime_lag_windows",
                 dict(meta, what="A6: excess return per window around each event, mean and SE across events"))

    # ---- A8: where the turnover comes from
    a_size = P2["asset_vol_target"] / r2.vol.loc[me]
    s0 = R3.turnover_sources_t0(sign, a_size, w0)
    s1 = R3.turnover_sources_t1(w0, lev, w1)
    yrs = len(s0) / 12.0
    ts = []
    for book, src in (("T0", s0), ("T1", s1)):
        parts = [c for c in src.columns if c not in ("actual", "check")]
        tot = src[parts].sum().sum()
        for c in parts + ["actual"]:
            ts.append({"book": book, "source": c, "per_year": float(src[c].sum() / yrs),
                       "share_of_parts": float(src[c].sum() / tot) if c != "actual" else np.nan, "rebalances": len(src)})
        s = M.book_summary(res[book], rf=rf, mask=rec)
        ts.append({"book": book, "source": "engine turnover_ann (executed, record)", "per_year": float(s["turnover_ann"]),
                   "rebalances": len(src)})
        vs = ms["VIX_lab"].reindex(src.index)
        for k in range(3):
            sub = src[vs == k]
            for c in parts + ["actual"]:
                ts.append({"book": book, "source": f"{c} | VIX {L[k]} at formation", "per_year": float(sub[c].mean() * 12) if len(sub) else np.nan,
                           "rebalances": int(len(sub))})
    write_result(pd.DataFrame(ts).set_index(["book", "source"]), "30_turnover_sources",
                 dict(meta, what="A8: sum |dw| at month-end targets split into its sources; per year = parts summed / years",
                      check_max=f"T0 {s0['check'].max():.1e}, T1 {s1['check'].max():.1e} (parts sum exactly to the change)",
                      by_state="per_year there = mean per rebalance x 12, the rate the book would run at in that state"))
    print("Part A written: results/30_*")


if __name__ == "__main__":
    main()
