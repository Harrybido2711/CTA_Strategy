"""Nothing chosen for a quarter may depend on prices from that quarter or later (OUTLINE 4.5)."""
import numpy as np
import pandas as pd
import pytest

import config as C
import rr_data as D
import rr_signals as S
import rr_split as SP


@pytest.fixture(scope="module")
def world():
    etfs = D.load_etfs()
    cal = D.calendar(etfs)
    return cal, D.panel(etfs, "close", cal)


def scramble_after(close, start):
    """Multiply every price from `start` on by an independent random factor per asset and day."""
    out = close.copy()
    rng = np.random.default_rng(7)
    m = out.index >= start
    out.loc[m] = out.loc[m] * rng.uniform(0.7, 1.3, size=out.loc[m].shape)
    return out


def test_every_label_ends_before_the_next_window(world):
    cal, _ = world
    for r in SP.rungs(cal):
        assert r["train"][-1] + C.SKIP + C.H < r["val"][0] + C.PURGE      # train labels end inside val's purge
        assert r["refit"][-1] + C.SKIP + C.H < r["test"][0], r["test_q"]  # refit labels end before test
        assert r["val"][-1] + C.SKIP + C.H < r["test"][0], r["test_q"]


def test_scores_are_causal(world):
    cal, close = world
    t0 = pd.Timestamp("2023-06-30")
    alt = scramble_after(close, t0 + pd.Timedelta(days=1))
    for f in (lambda c: S.mom_score(c), lambda c: S.macd_score(c, 12, 26, "proportional", 5),
              lambda c: S.macd_score(c, 5, 21, "crossover")):
        a, b = f(close).loc[:t0], f(alt).loc[:t0]
        pd.testing.assert_frame_equal(a, b)


def test_rung_choice_ignores_its_test_quarter(world):
    cal, close = world
    rung = SP.rungs(cal)[0]                         # 2022Q1, the rung that found a band
    alt = scramble_after(close, cal[rung["test"][0]])
    picks = []
    for c in (close, alt):
        fwd = S.forward_return(c)
        cells = {k: S.macd_score(c, k[0], k[1], "proportional") for k in S.macd_cells()}
        picks.append(S.select_rung(rung, cal, c, fwd, cells, []))
    a, b = picks
    assert a["band"] == b["band"] and a["q"] == b["q"] and a["fallback_mom_only"] == b["fallback_mom_only"]
    assert a["val_spread"] == pytest.approx(b["val_spread"])
