"""Signals: risk-adjusted momentum and MACD as chapter 02 and chapter 03 define them.

Every score is centred on [-0.5, 0.5]: the value's percentile against the asset's own trailing
252 days, minus one half (chapter 02 4, second route). That puts every asset and every signal on
one scale, so 37 assets share one pool of buckets and two signals can be averaged.

Timing: a score dated t uses closes through t. It trades on t + LAG and is scored on the return
close_{t+1} -> close_{t+6}.
"""
import itertools

import numpy as np
import pandas as pd

import config as C
import rr_metrics as M

B = C.BASELINE


# ----------------------------------------------------------------------------- building blocks
def returns(close):
    """Daily close-to-close return; a missing bar carries the last close (no return that day)."""
    return close.ffill().pct_change(fill_method=None)


def sigma(r, n=B["vol_window"]):
    """Trailing volatility estimated strictly before t (chapter 02 4)."""
    return r.rolling(n).std().shift(1)


def centred(x, n=B["pct_window"], minp=B["pct_min_periods"]):
    """Percentile of today's value against the asset's own trailing n days, minus one half."""
    return x.rolling(n, min_periods=minp).rank(pct=True) - 0.5


def ema(x, span):
    """Exponential moving average with alpha = 2 / (span + 1) (chapter 03 3.1)."""
    return x if span <= 1 else x.ewm(span=span, adjust=False).mean()


def forward_return(close, h=C.H, skip=C.SKIP):
    """close_{t+skip+h} / close_{t+skip} - 1: one skipped day, then h days."""
    c = close.ffill()
    fwd = c.shift(-(skip + h)) / c.shift(-skip) - 1.0
    return fwd.where(close.shift(-(skip + h)).notna() & close.shift(-skip).notna())


# ----------------------------------------------------------------------------- momentum
def mom_raw(close, n=B["mom_lookback"]):
    return returns(close).rolling(n).mean()


def mom_score(close):
    """Risk-adjusted momentum: 21-day mean return over trailing sigma, as a centred percentile."""
    r = returns(close)
    return centred(r.rolling(B["mom_lookback"]).mean() / sigma(r))


# ----------------------------------------------------------------------------- MACD
def macd_line(close, nf, ns):
    """EMA_nf(P) - EMA_ns(P), divided by P so it is in return units and comparable across assets."""
    p = close.ffill()
    return (ema(p, nf) - ema(p, ns)) / p


def macd_score(close, nf, ns, rule="proportional", q=1):
    """One MACD cell as a score in [-0.5, 0.5].

    q is the smoother: an EMA of span q on the MACD line, used only when q < n_f (chapter 03 4).
    zero-line: +-0.5 by the sign of the (smoothed) line. crossover: +-0.5 by the sign of the
    histogram, line minus its 9-day signal line. proportional: the line's centred percentile.
    """
    m = macd_line(close, nf, ns)
    if q > 1 and q < nf:
        m = ema(m, q)
    if rule == "proportional":
        return centred(m)
    if rule == "zero":
        return 0.5 * np.sign(m).where(m.notna())
    if rule == "crossover":
        h = m - ema(m, B["macd_signal_span"])
        return 0.5 * np.sign(h).where(h.notna())
    raise ValueError(rule)


def macd_cells():
    lad = B["macd_ladder"]
    cells = [(f, s) for f, s in itertools.combinations(lad, 2)]
    return cells + [B["macd_reference_cell"]]


def neighbours(cell):
    """Adjacent cells on the ladder grid; the reference cell (12, 26) sits next to (10, 21)."""
    lad = list(B["macd_ladder"])
    if cell == B["macd_reference_cell"]:
        return [(10, 21)]
    f, s = lad.index(cell[0]), lad.index(cell[1])
    out = []
    for df, ds in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nf, ns = f + df, s + ds
        if 0 <= nf < ns < len(lad):
            out.append((lad[nf], lad[ns]))
    if cell == (10, 21):
        out.append(B["macd_reference_cell"])
    return out


_SMOOTHED = {}


def _smoothed_cell(close, c, q):
    key = (id(close), c, q)
    if key not in _SMOOTHED:
        _SMOOTHED[key] = macd_score(close, c[0], c[1], "proportional", q)
    return _SMOOTHED[key]


def band_score(cell_scores, band, q=1, close=None):
    """Equal-weight mean of the band cells' centred scores (recomputed with smoother q if given)."""
    parts = [(_smoothed_cell(close, c, q) if (q > 1 and close is not None) else cell_scores[c]) for c in band]
    return sum(parts) / len(parts)


def score_turnover(score):
    """Mean daily sum over assets of |change in score|: how much the score asks the book to trade."""
    return float(score.diff().abs().sum(axis=1).mean())


# ----------------------------------------------------------------------------- per-rung selection
def select_rung(rung, cal, close, fwd, cell_scores, ledger):
    """Choose the MACD band, the smoother and the fallback for one rung from its own quarters only."""
    tr, va = cal[rung["train"]], cal[rung["val"]]
    stats = {}
    for c in macd_cells():
        bt = M.bucket_test(cell_scores[c].loc[tr], fwd.loc[tr], nw_lag=C.NW_LAG).loc["G5-G1"]
        stats[c] = bt
    warm = {c for c, s in stats.items() if s["t"] >= B["band_t_min"]}
    band = sorted(c for c in warm if any(n in warm for n in neighbours(c))) if B["band_needs_neighbour"] else sorted(warm)
    for c, s in stats.items():
        ledger.append({"test_q": rung["test_q"], "stage": "macd_cell", "sample": "rung train",
                       "params": f"nf={c[0]} ns={c[1]} rule=proportional", "spread": s["mean"],
                       "se_nw": s["se_nw"], "t": s["t"], "selected": c in band})
    chosen_q, fallback, val_spread = 1, False, np.nan
    if not band:
        fallback = True
    else:
        best = None
        for q in B["smoothers"]:
            bs = band_score(cell_scores, band, q, close)
            bt = M.bucket_test(centred(bs).loc[tr], fwd.loc[tr], nw_lag=C.NW_LAG).loc["G5-G1"]
            to = score_turnover(bs.loc[tr])
            ratio = bt["mean"] / to if to > 0 else np.nan
            ledger.append({"test_q": rung["test_q"], "stage": "smoother", "sample": "rung train",
                           "params": f"q={q}", "spread": bt["mean"], "se_nw": bt["se_nw"], "t": bt["t"],
                           "turnover": to, "ratio": ratio, "selected": False})
            if best is None or ratio > best[1]:
                best = (q, ratio)
        chosen_q = best[0]
        for row in ledger[::-1]:
            if row["test_q"] == rung["test_q"] and row["stage"] == "smoother" and row["params"] == f"q={chosen_q}":
                row["selected"] = True
                break
        bs = band_score(cell_scores, band, chosen_q, close)
        vt = M.bucket_test(centred(bs).loc[va], fwd.loc[va], nw_lag=C.NW_LAG).loc["G5-G1"]
        val_spread = vt["mean"]
        fallback = not (val_spread > 0)
        ledger.append({"test_q": rung["test_q"], "stage": "val_check", "sample": "rung val",
                       "params": f"band={band} q={chosen_q}", "spread": vt["mean"], "se_nw": vt["se_nw"],
                       "t": vt["t"], "selected": not fallback})
    return {"test_q": rung["test_q"], "block": rung["block"], "band": band, "q": chosen_q,
            "fallback_mom_only": fallback, "val_spread": val_spread, "n_warm": len(warm)}


def b0_score(close, mom, cell_scores, selections, cal, rs):
    """Stitch B0's score over the walk-forward record: each test quarter uses its own rung's choice."""
    out = pd.DataFrame(np.nan, index=cal, columns=close.columns)
    for rung, sel in zip(rs, selections):
        d = cal[rung["test"]]
        if sel["fallback_mom_only"]:
            out.loc[d] = mom.loc[d]
        else:
            bs = band_score(cell_scores, sel["band"], sel["q"], close)
            out.loc[d] = (0.5 * mom + 0.5 * bs).loc[d]
    return out


def prop_weights(score, gross=C.GROSS, hold=C.HOLD):
    """Weights proportional to the score: demeaned across assets, scaled to the gross, overlapped."""
    w = score.sub(score.mean(axis=1), axis=0)
    g = w.abs().sum(axis=1).replace(0, np.nan)
    w = w.mul(gross / g, axis=0)
    return w.fillna(0.0).rolling(hold, min_periods=1).mean() if hold > 1 else w.fillna(0.0)
