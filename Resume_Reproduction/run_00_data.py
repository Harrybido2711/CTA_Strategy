"""W1: build the adjusted data, fetch the external series, and check everything.

    .venv/bin/python Resume_Reproduction/run_00_data.py

Writes data/adjusted/ (five SPDRs, corrected VIX), data/external/ (DTB3, Cboe VIX, Yahoo
distributions) and results/00_*.csv. Only data validation reads the Test quarters here: no
signal, weight or PnL is computed.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C          # noqa: E402
import rr_data as D         # noqa: E402
from rr_io import write_result  # noqa: E402


def etf_checks(etfs, cal):
    rows = []
    for t, d in etfs.items():
        r = d["close"].pct_change()
        i = r.abs().idxmax()
        tol = 1e-9 * d["close"].abs()
        missing = cal.difference(d.index)
        rows.append({
            "ticker": t,
            "category": C.UNIVERSE_CATEGORY[t],
            "rows": len(d),
            "first": d.index.min().date(),
            "last": d.index.max().date(),
            "missing_on_union_calendar": len(missing),
            "missing_dates": " ".join(str(x.date()) for x in missing),
            "largest_move": round(float(r[i]), 4),
            "largest_move_date": i.date(),
            "moves_over_40pct": int((r.abs() > 0.4).sum()),
            "high_below_low": int((d["high"] < d["low"] - tol).sum()),
            "close_outside_range": int(((d["close"] > d["high"] + tol) | (d["close"] < d["low"] - tol)).sum()),
            "open_outside_range": int(((d["open"] > d["high"] + tol) | (d["open"] < d["low"] - tol)).sum()),
            "nonpositive_prices": int((d[D.PRICE_COLS] <= 0).any(axis=1).sum()),
            "split_adjusted": t in C.SPLIT_TICKERS,
            "bar_fixed_rows": int(d["bar_fixed"].sum()),
        })
    return pd.DataFrame(rows).set_index("ticker")


def index_checks(cal):
    rows = []
    cboe = D.load_cboe_vix()
    for name in ("VIX", "MOVE"):
        raw = D._read_index(name)
        s, n_filled = D.load_index(name, cal)
        in_range = raw[(raw.index >= cal.min()) & (raw.index <= cal.max())]
        row = {
            "index": name,
            "file_rows": len(raw),
            "file_first": raw.index.min().date(),
            "file_last": raw.index.max().date(),
            "rows_in_sample": len(in_range),
            "dropped_not_etf_days": " ".join(str(x.date()) for x in in_range.index.difference(cal)),
            "filled_one_day": n_filled,
            "still_missing": int(s.isna().sum()),
        }
        if name == "VIX":
            m = pd.concat([s, cboe], axis=1, keys=["vix", "cboe"]).dropna()
            row["corrections_applied"] = len(C.VIX_CORRECTIONS)
            row["days_differing_from_cboe_after_correction"] = int(((m.vix - m.cboe).abs() >= 0.005).sum())
        rows.append(row)
    rf = D.load_dtb3(cal)
    rows.append({"index": "DTB3", "file_rows": None, "still_missing": int(rf.isna().sum()),
                 "file_first": None, "file_last": None,
                 "mean_annual_pct": round(float(rf.mean() * 252 * 100), 3)})
    return pd.DataFrame(rows).set_index("index")


def distribution_checks(etfs, cal):
    close = D.panel(etfs, "close", cal)
    dist = D.load_distributions(cal, close.columns)
    years = (cal.max() - cal.min()).days / 365.25
    out = pd.DataFrame({
        "ex_dates": (dist > 0).sum(),
        "cash_per_share": dist.sum().round(4),
        "approx_yield_pct_per_year": (100 * (dist / close.ffill()).sum() / years).round(2),
    })
    return out.sort_values("approx_yield_pct_per_year", ascending=False)


def main():
    D.build_adjusted()
    D.build_vix_corrected()
    etfs = D.load_etfs()
    cal = D.calendar(etfs)
    D.fetch_external(sorted(etfs))

    e = etf_checks(etfs, cal)
    meta = {"what": "per-ticker data checks after the split fix (DATA.md 4)",
            "calendar": f"{len(cal)} union trading days {cal.min().date()} to {cal.max().date()}"}
    write_result(e, "00_data_checks", meta)
    ix = index_checks(cal)
    write_result(ix, "00_index_checks", {"what": "VIX/MOVE handout and DTB3 alignment checks"})
    dc = distribution_checks(etfs, cal)
    write_result(dc, "00_distributions", {"what": "Yahoo distribution events, approximate yield on adjusted prices"})

    print(f"calendar: {len(cal)} days {cal.min().date()} -> {cal.max().date()}; weekends: "
          f"{int((cal.weekday >= 5).sum())}")
    print(f"moves over 40% after adjustment: {int(e.moves_over_40pct.sum())} (must be 0)")
    print(f"OHLC violations: high<low {int(e.high_below_low.sum())}, close outside "
          f"{int(e.close_outside_range.sum())}, open outside {int(e.open_outside_range.sum())}")
    print("largest remaining moves:")
    print(e.reindex(e.largest_move.abs().sort_values(ascending=False).index)[["largest_move", "largest_move_date"]].head(6).to_string())
    print("vendor gaps:", e.loc[e.missing_on_union_calendar > 0, "missing_on_union_calendar"].to_dict())
    print(ix.to_string())
    print(dc.head(6).to_string())
    ok = int(e.moves_over_40pct.sum()) == 0 and int(e.high_below_low.sum()) == 0
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
