"""Data layer: the 37 ETFs, the class VIX/MOVE files, and the external series (DATA.md).

Everything returned here is aligned to one union calendar of ETF trading days, tz-naive and
normalised to the date. CTA_data/ is never written to: the five split-adjusted SPDRs and the
corrected VIX live in data/adjusted/, and downloads live in data/external/.
"""
import glob
import json
import os
import urllib.request

import numpy as np
import pandas as pd

import config as C

PRICE_COLS = ["open", "high", "low", "close"]


# ----------------------------------------------------------------------------- ETFs
def _read_ohlcv(path):
    d = pd.read_csv(path)
    d.index = pd.to_datetime(d["ts_event"], utc=True).dt.tz_convert(None).dt.normalize()
    d.index.name = "date"
    return d


def split_adjust(raw):
    """Restate a 2-for-1 split ticker on the post-split basis and repair the split-day bar.

    Rows before the split date get OHLC / 2 and volume x 2. On the split date itself the open and
    high were printed at the old basis (chapter 100), so open := close and high := max(low, close),
    flagged bar_fixed = 1.
    """
    d = raw.copy()
    split = pd.Timestamp(C.SPLIT_DATE)
    pre = d.index < split
    d.loc[pre, PRICE_COLS] = d.loc[pre, PRICE_COLS] / C.SPLIT_RATIO
    d.loc[pre, "volume"] = d.loc[pre, "volume"] * C.SPLIT_RATIO
    d["bar_fixed"] = 0
    day = d.index == split
    d.loc[day, "open"] = d.loc[day, "close"]
    d.loc[day, "high"] = d.loc[day, ["low", "close"]].max(axis=1)
    d.loc[day, "bar_fixed"] = 1
    return d


def build_adjusted():
    """Write the five split-adjusted SPDRs to data/adjusted/. Returns the paths written."""
    os.makedirs(C.DATA_ADJ, exist_ok=True)
    out = []
    for t in C.SPLIT_TICKERS:
        raw = _read_ohlcv(os.path.join(C.CTA_DATA, f"{t}_ohlcv_1d.csv"))
        adj = split_adjust(raw)
        path = os.path.join(C.DATA_ADJ, f"{t}_ohlcv_1d.csv")
        adj.reset_index(drop=True).to_csv(path, index=False)
        out.append(path)
    return out


def load_etfs(end=C.SAMPLE_END):
    """Dict ticker -> OHLCV frame, split-adjusted, ending at `end` (a truncated copy for robustness)."""
    etfs = {}
    for path in sorted(glob.glob(os.path.join(C.CTA_DATA, "*_ohlcv_1d.csv"))):
        t = os.path.basename(path).split("_")[0]
        adj = os.path.join(C.DATA_ADJ, f"{t}_ohlcv_1d.csv")
        if t in C.SPLIT_TICKERS:
            if not os.path.exists(adj):
                raise FileNotFoundError(f"{adj} missing: run run_00_data.py first")
            d = _read_ohlcv(adj)
        else:
            d = _read_ohlcv(path)
            d["bar_fixed"] = 0
        d = d[(d.index >= pd.Timestamp(C.SAMPLE_START)) & (d.index <= pd.Timestamp(end))]
        etfs[t] = d[PRICE_COLS + ["volume", "bar_fixed"]]
    return etfs


def calendar(etfs):
    """Union calendar of ETF trading days."""
    idx = sorted(set().union(*[set(d.index) for d in etfs.values()]))
    return pd.DatetimeIndex(idx, name="date")


def panel(etfs, field, cal=None):
    """Wide frame, union calendar x ticker; NaN where a ticker has no bar (vendor gap)."""
    cal = calendar(etfs) if cal is None else cal
    return pd.DataFrame({t: d[field] for t, d in etfs.items()}).reindex(cal)


# ----------------------------------------------------------------------------- VIX / MOVE
def _read_index(name):
    d = pd.read_csv(os.path.join(C.INDICES, f"{name}_index_1d_2020_now.csv"), parse_dates=["Date"])
    return d.set_index("Date")["Close"].astype(float).sort_index()


def build_vix_corrected():
    """The class VIX close with the three Cboe corrections, written to data/adjusted/."""
    v = _read_index("VIX")
    corrected = pd.Series(0, index=v.index)
    for day, value in C.VIX_CORRECTIONS.items():
        v.loc[pd.Timestamp(day)] = value
        corrected.loc[pd.Timestamp(day)] = 1
    out = pd.DataFrame({"Date": v.index.date, "Close": v.values, "corrected_to_cboe": corrected.values})
    path = os.path.join(C.DATA_ADJ, "VIX_index_1d_2020_now_corrected.csv")
    out.to_csv(path, index=False)
    return path


def load_index(name, cal):
    """VIX (corrected) or MOVE close on the ETF calendar, forward-filled at most one day.

    Returns (series, number_of_days_filled). Index dates that are not ETF trading days are dropped.
    """
    if name == "VIX":
        d = pd.read_csv(os.path.join(C.DATA_ADJ, "VIX_index_1d_2020_now_corrected.csv"), parse_dates=["Date"])
        s = d.set_index("Date")["Close"].astype(float)
    elif name == "MOVE":
        s = _read_index("MOVE")
    else:
        raise ValueError(name)
    on_cal = s.reindex(cal)
    filled = on_cal.ffill(limit=C.INDEX_FFILL_LIMIT)
    n_filled = int(on_cal.isna().sum() - filled.isna().sum())
    return filled.rename(name), n_filled


# ----------------------------------------------------------------------------- external
def _ext(name):
    return os.path.join(C.DATA_EXT, f"{name}_{C.EXTERNAL_STAMP}.csv")


def _get(url):
    """HTTPS GET with certificate verification against certifi's bundle.

    The python.org build of Python 3.8 ships without root certificates, so the default context
    cannot verify anything; certifi supplies them. Verification is never turned off.
    """
    import ssl
    import certifi
    ctx = ssl.create_default_context(cafile=certifi.where())
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60, context=ctx) as r:
        return r.read()


SOURCES = {
    "FRED_DTB3": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DTB3&cosd=2019-01-01",
    "Cboe_VIX_History": "https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv",
    "Yahoo_distributions": "https://query2.finance.yahoo.com/v8/finance/chart/{t}"
                           "?period1=1577836800&period2=1782864000&interval=1d&events=div",
}


def fetch_external(tickers):
    """Download DTB3, the Cboe VIX history and Yahoo distribution events, if not already present."""
    os.makedirs(C.DATA_EXT, exist_ok=True)
    written = []
    def missing(path):
        return not os.path.exists(path) or os.path.getsize(path) == 0

    for key in ("FRED_DTB3", "Cboe_VIX_History"):
        path = _ext(key)
        if missing(path):
            body = _get(SOURCES[key])          # download first, so a failure leaves no file
            with open(path, "wb") as fh:
                fh.write(body)
            written.append(path)
    path = _ext("Yahoo_distributions")
    if missing(path):
        rows = []
        for t in tickers:
            res = json.loads(_get(SOURCES["Yahoo_distributions"].format(t=t)))["chart"]["result"][0]
            for ev in res.get("events", {}).get("dividends", {}).values():
                rows.append({"ticker": t,
                             "ex_date": pd.Timestamp(ev["date"], unit="s").date(),
                             "amount": ev["amount"]})
        pd.DataFrame(rows).sort_values(["ticker", "ex_date"]).to_csv(path, index=False)
        written.append(path)
    meta = {k: {"url": v, "downloaded": C.EXTERNAL_STAMP} for k, v in SOURCES.items()}
    with open(os.path.join(C.DATA_EXT, "sources.json"), "w") as fh:
        json.dump(meta, fh, indent=2)
    return written


def load_dtb3(cal):
    """Daily T-bill rate (annual percent / 100 / 252) on the ETF calendar, forward-filled."""
    d = pd.read_csv(_ext("FRED_DTB3"), parse_dates=["observation_date"])
    s = pd.to_numeric(d.set_index("observation_date")["DTB3"], errors="coerce") / 100.0 / 252.0
    return s.reindex(s.index.union(cal)).ffill().reindex(cal).rename("rf_daily")


def load_cboe_vix():
    d = pd.read_csv(_ext("Cboe_VIX_History"))
    d["DATE"] = pd.to_datetime(d["DATE"])
    return d.set_index("DATE")["CLOSE"].astype(float)


def load_distributions(cal, tickers):
    """Cash distribution per share on each ex-date, union calendar x ticker (0 where none).

    An ex-date that is not an ETF trading day moves to the next one. Yahoo's amounts are
    split-adjusted, which matches the split-adjusted prices of the five SPDRs.
    """
    d = pd.read_csv(_ext("Yahoo_distributions"), parse_dates=["ex_date"])
    d = d[d["ex_date"] >= cal.min()]          # an earlier ex-date must not land on the first day
    out = pd.DataFrame(0.0, index=cal, columns=list(tickers))
    pos = cal.searchsorted(d["ex_date"].values)
    for (t, amt), p in zip(d[["ticker", "amount"]].itertuples(index=False), pos):
        if p < len(cal) and t in out.columns:
            out.iloc[p, out.columns.get_loc(t)] += amt
    return out


def total_return_prices(open_, close, dist):
    """Forward-adjust open and close so close-to-close returns include distributions.

    TR_t = close_t * prod over ex-dates k <= t of (1 + D_k / close_k), so on an ex-date
    TR_t / TR_{t-1} = (close_t + D_t) / close_{t-1}. Opens get the same multiplier.
    """
    c = close.ffill()
    factor = (1.0 + dist.reindex_like(c).fillna(0.0) / c).fillna(1.0).cumprod()
    return open_ * factor, close * factor
