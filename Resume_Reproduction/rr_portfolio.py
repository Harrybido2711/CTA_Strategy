"""Books: weights from scores, the execution variants, and the samples they are scored on.

Every book starts trading at the first walk-forward quarter, so each pays the same build cost and
is scored on the same days. Nothing here reads a Test quarter unless the caller asks for it.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

import config as C
import rr_data as D
import rr_signals as S
import rr_split as SP

sys.path.insert(0, os.path.join(C.ROOT, "Backtest_prototype"))
import backtest as P  # noqa: E402

VARIANTS = {
    "naive_0": dict(lag=0, exec_price="close", cost_bp=0.0, slip_bp=0.0),   # same-close, not executable
    "naive_1": dict(lag=1, exec_price="close", cost_bp=0.0, slip_bp=0.0),   # feasible, frictionless
    "realistic": dict(lag=C.LAG, exec_price=C.EXEC_PRICE, cost_bp=C.COST_BP, slip_bp=C.SLIP_BP),
}


class World:
    """Prices, signals and the ladder, built once."""

    def __init__(self, include_test=False, end=C.SAMPLE_END, universe=None, total_return=False):
        self.etfs = D.load_etfs(end)
        if universe is not None:
            self.etfs = {t: d for t, d in self.etfs.items() if t in set(universe)}
        self.cal = D.calendar(self.etfs)
        self.close = D.panel(self.etfs, "close", self.cal)
        self.open = D.panel(self.etfs, "open", self.cal)
        self.total_return = total_return
        if total_return:
            dist = D.load_distributions(self.cal, self.close.columns)
            self.open, self.close = D.total_return_prices(self.open, self.close, dist)
        self.rf = D.load_dtb3(self.cal)
        self.fwd = S.forward_return(self.close)
        self.mom = S.mom_score(self.close)
        self.cells = {c: S.macd_score(self.close, c[0], c[1], "proportional") for c in S.macd_cells()}
        rs = SP.rungs(self.cal)
        self.rungs = rs if include_test else SP.pre_test(rs)
        self.start = self.cal[self.rungs[0]["test"][0]]
        self.wf = pd.Series(False, index=self.cal)
        self.block = pd.Series("", index=self.cal)
        for r in self.rungs:
            self.wf.iloc[r["test"]] = True
            self.block.iloc[r["test"]] = r["block"]
        self.samples = {"WF": self.wf, "train-ladder": self.wf & (self.block == "train-ladder"),
                        "OV": self.wf & (self.block == "OV")}
        if include_test:
            self.samples["Test"] = self.wf & (self.block == "Test")
        self._sel = None

    def selections(self, ledger=None):
        if self._sel is None:
            ledger = [] if ledger is None else ledger
            self._sel = [S.select_rung(r, self.cal, self.close, self.fwd, self.cells, ledger) for r in self.rungs]
        return self._sel

    def from_start(self, w):
        w = w.copy()
        w.loc[w.index < self.start] = 0.0
        return w

    def b0_score(self):
        return S.b0_score(self.close, self.mom, self.cells, self.selections(), self.cal, self.rungs)


def books(world):
    """Target weights for every book W4 reports (homework A1 and A3)."""
    wd = world
    mom_raw = S.mom_raw(wd.close)
    out = {
        "B0 (MOM + MACD band, walk-forward)": S.prop_weights(wd.b0_score()),
        "MOM prop-signal": S.prop_weights(wd.mom),
        "MACD 12/26 prop-signal": S.prop_weights(wd.cells[(12, 26)]),
        "MACD 12/26 zero-line": S.prop_weights(S.macd_score(wd.close, 12, 26, "zero")),
        "MACD 12/26 crossover": S.prop_weights(S.macd_score(wd.close, 12, 26, "crossover")),
        "P1 150/50 (prototype)": P.overlap_weights(P.target_weights_p1(mom_raw)),
        "P2 median L/S (prototype)": P.overlap_weights(P.target_weights_p2(mom_raw)),
    }
    return {k: wd.from_start(v.fillna(0.0)) for k, v in out.items()}


def b0_deadband_scale(world):
    """Per-quarter deadband scale: median daily |change in held weight| of B0 in each rung's training window.

    For rung k the book is B0 under rung k's own choice, run on rung k's training window only; the
    median is over asset-days with a position. The scale then applies to rung k's test quarter.
    """
    from rr_engine import simulate
    wd = world
    scale = pd.Series(0.0, index=wd.cal)
    per_rung = {}
    for r, sel in zip(wd.rungs, wd.selections()):
        if sel["fallback_mom_only"]:
            sc = wd.mom
        else:
            sc = 0.5 * wd.mom + 0.5 * S.band_score(wd.cells, sel["band"], sel["q"], wd.close)
        w = S.prop_weights(sc)
        tr = wd.cal[r["train"]]
        w = w.copy()
        w.loc[~w.index.isin(tr)] = 0.0
        res = simulate(wd.open, wd.close, w, **VARIANTS["realistic"])
        dw = res["w_held"].diff().abs().loc[tr[C.HOLD:]]
        held = res["w_held"].loc[tr[C.HOLD:]].abs() > 0
        m = float(dw[held].stack().median())
        per_rung[r["test_q"]] = m
        scale.iloc[r["test"]] = m
    return scale, per_rung
