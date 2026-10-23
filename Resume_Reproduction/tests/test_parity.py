"""The engine reproduces Backtest_prototype/backtest.py exactly at the prototype's own settings.

Settings: lag 2 trading rows, fill at TWAP = (open + close) / 2, shares sized at the previous
close, no frictions. That is what the prototype's one-calendar-day merge_asof delay plus its
one-row .shift() amount to. Rows from a ticker's first vendor-gap day on are excluded, because
the prototype re-times trades across a gap and the engine carries the position instead.
"""
import os
import sys
from datetime import timedelta

import numpy as np
import pandas as pd
import pytest

import config as C
import rr_data as D
from rr_engine import simulate

sys.path.insert(0, os.path.join(C.ROOT, "Backtest_prototype"))
import backtest as P  # noqa: E402

GAP_TICKERS = ("IEF", "QQQ", "SHY", "TLT")


@pytest.fixture(scope="module")
def data():
    etfs = D.load_etfs()
    cal = D.calendar(etfs)
    proto = {t: d.reset_index().rename(columns={"date": "ts_event"}).assign(symbol=t) for t, d in etfs.items()}
    return etfs, cal, proto


@pytest.mark.parametrize("book", ["p1", "p2"])
def test_parity(data, book):
    etfs, cal, proto = data
    mom = P.momentum(P.close_matrix(proto))
    tw = P.target_weights_p1(mom) if book == "p1" else P.target_weights_p2(mom)
    w = P.overlap_weights(tw)
    res = simulate(D.panel(etfs, "open", cal), D.panel(etfs, "close", cal), w,
                   lag=2, exec_price="twap", size_price="prev_close")
    eng = res["pnl_asset"].cumsum()
    worst = 0.0
    for t in w.columns:
        dollar = pd.DataFrame({"ts_event": w.index, "dollar": w[t].values})
        pr = P.backtester(proto[t], dollar, delay=timedelta(days=1)).set_index("ts_event")["portfolio"]
        both = pd.concat([pr, eng[t].reindex(pr.index)], axis=1, keys=["proto", "engine"]).dropna()
        if t in GAP_TICKERS:
            both = both[both.index < pd.Timestamp(C.VENDOR_GAP[0])]
        assert len(both) > (700 if t in GAP_TICKERS else 1500), (t, len(both))
        worst = max(worst, float((both.proto - both.engine).abs().max()))
    assert worst < 1e-9, worst
