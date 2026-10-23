"""The walk-forward ladder (OUTLINE.md 4.5, chapter 05 2.1-2.3).

Each calendar quarter q from 2022Q1 to 2026Q2 is traded by a rung that trains on q-4 .. q-2,
validates on q-1, refits on both, and applies once to q. PURGE rows are dropped from the end of
every fitting window so no label (close_{t+1} -> close_{t+6}) reaches into the next window.
"""
import numpy as np
import pandas as pd

import config as C


def block_of(q):
    q = str(q)
    if q in C.TEST_QUARTERS:
        return "Test"
    if q in C.OV_QUARTERS:
        return "OV"
    return "train-ladder"


def rungs(cal, first=C.WF_FIRST_TEST_Q, last=C.WF_LAST_TEST_Q):
    """List of rungs; each holds integer positions into `cal` for train, val, refit and test."""
    q = cal.to_period("Q")
    out = []
    for tq in pd.period_range(first, last, freq="Q"):
        train = np.flatnonzero(q.isin([tq - 4, tq - 3, tq - 2]))
        val = np.flatnonzero(q == tq - 1)
        test = np.flatnonzero(q == tq)
        refit = np.concatenate([train, val])
        out.append({
            "test_q": str(tq), "block": block_of(tq),
            "train": train[:-C.PURGE], "val": val[:-C.PURGE], "refit": refit[:-C.PURGE], "test": test,
            "train_dates": (cal[train[0]].date(), cal[train[-1]].date()),
            "val_dates": (cal[val[0]].date(), cal[val[-1]].date()),
            "test_dates": (cal[test[0]].date(), cal[test[-1]].date()),
        })
    return out


def pre_test(rs):
    """Rungs whose test quarter ends on or before PRE_TEST_END (everything before W10)."""
    return [r for r in rs if r["block"] != "Test"]
