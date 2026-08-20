"""Figures for docs/03-shaping-the-lookback.md.

Run from anywhere:

    python docs/figures/make_03_shaping_the_lookback.py

Writes light- and dark-mode PNGs into docs/figures/. The chapter references
them through a <picture> element so GitHub serves the variant matching the
reader's theme.

Figures produced
----------------
    fast-times-slow  a fast window fires before a slow one at both ends
    signal-kernels   MACD is momentum with a hump-shaped kernel, not a box

All are schematics drawn from illustrative values.

Formulas stay in the markdown as LaTeX rather than being rendered here: text in
an image is neither selectable nor searchable.
"""

import matplotlib.pyplot as plt
import numpy as np
from _style import THEMES, save, style_axes, titles


# ------------------- fig: a fast leg times the turns a slow one arrives late for
def fast_times_the_slow(mode):
    """03 s1 -- the same trend, entered and exited by two different lookbacks.

    Schematic. One price path that falls, turns and rolls over, with a fast and
    a slow moving average drawn over it. The lower panel is the momentum each
    window produces; each rule fires where its own line crosses zero. The short
    window crosses first at both ends, and the gap is the reason to carry two.
    """
    t = THEMES[mode]
    rng = np.random.RandomState(7)
    N_F, N_S = 20, 40                                    # the conventional 2:1

    n = 170
    kx = [0, 0.13, 0.19, 0.27, 0.34, 0.47, 0.59, 0.67, 0.75, 1.0]
    ky = [101.5, 102, 97, 93, 93.2, 103, 114, 119.5, 118, 111]
    level = np.interp(np.linspace(0, 1, n), kx, ky)
    k = np.ones(21) / 21                                 # round off the corners
    level = np.convolve(np.pad(level, 10, mode="edge"), k, mode="valid")[:n]
    price = level + rng.standard_normal(n) * 0.8

    def ewma(v, span):
        a = 2.0 / (span + 1.0)
        out = np.empty_like(v)
        out[0] = v[0]
        for i in range(1, len(v)):
            out[i] = a * v[i] + (1 - a) * out[i - 1]
        return out

    fast_ma, slow_ma = ewma(price, N_F), ewma(price, N_S)

    def momentum(v, N):                                  # price change over the window
        m = np.full(n, np.nan)
        m[N:] = v[N:] - v[:-N]
        return m

    fast_m, slow_m = momentum(level, N_F), momentum(level, N_S)

    def cross(m, lo, hi, up):
        for i in range(lo + 1, hi):
            if np.isnan(m[i - 1]):
                continue
            if (m[i] > 0 >= m[i - 1]) if up else (m[i] < 0 <= m[i - 1]):
                return i
        return None

    peak = int(np.nanargmax(level))
    f_in, s_in = cross(fast_m, N_S, peak, True), cross(slow_m, N_S, peak, True)
    f_out, s_out = cross(fast_m, peak, n, False), cross(slow_m, peak, n, False)

    fig, (ax, bx) = plt.subplots(
        2, 1, figsize=(9.2, 6.4), sharex=True,
        gridspec_kw=dict(height_ratios=[1.6, 1.0], hspace=0.15))
    fig.patch.set_facecolor(t["surface"])

    # ---- top: the price, and the two windows drawn over it
    style_axes(ax, t, ylabel="price, rebased to 100")
    lo, hi = 86, 128
    ax.set_ylim(lo, hi)
    ax.set_xlim(0, n)
    for i, colour in ((f_in, t["ramp"][2]), (s_in, t["ramp"][5]),
                      (f_out, t["ramp"][2]), (s_out, t["ramp"][5])):
        ax.plot([i, i], [lo, hi], color=colour, linewidth=1.0,
                linestyle=(0, (2, 2.4)), zorder=1)
    ax.plot(price, color=t["muted"], linewidth=0.8, alpha=0.75, zorder=2)
    ax.plot(slow_ma, color=t["ramp"][5], linewidth=2.1, zorder=4)
    ax.plot(fast_ma, color=t["ramp"][2], linewidth=2.1, zorder=3)

    ax.text(86, fast_ma[86] - 2.2, f"fast, {N_F}-day", color=t["ramp"][2],
            fontsize=8.6, fontweight="600", ha="left", va="top")
    ax.text(118, slow_ma[118] - 2.2, f"slow, {N_S}-day", color=t["ramp"][5],
            fontsize=8.6, fontweight="600", ha="left", va="top")
    ax.text(5, 97.0, "price", color=t["muted"], fontsize=8.6, ha="left")

    for y, (p0, p1), colour, label in (
            (90.6, (f_in, f_out), t["ramp"][2], "held by the fast rule"),
            (88.2, (s_in, s_out), t["ramp"][5], "held by the slow rule alone")):
        ax.plot([p0, p1], [y, y], color=colour, linewidth=3.6,
                solid_capstyle="butt", zorder=5)
        ax.text(p0 - 3, y, label, color=colour, fontsize=8.3,
                fontweight="600", ha="right", va="center")

    titles(ax, t, "A fast window fires at both ends before a slow one does",
           "illustrative — one price path, two lookbacks, and the four dates their rules produce")

    # ---- bottom: the momentum each window produces, and where it crosses zero
    style_axes(bx, t, ylabel="momentum over the window", xlabel="trading day")
    ylo, yhi = -18, 34
    bx.set_ylim(ylo, yhi)
    bx.set_xlim(0, n)
    for i, colour in ((f_in, t["ramp"][2]), (s_in, t["ramp"][5]),
                      (f_out, t["ramp"][2]), (s_out, t["ramp"][5])):
        bx.plot([i, i], [ylo, yhi], color=colour, linewidth=1.0,
                linestyle=(0, (2, 2.4)), zorder=1)
    bx.axhline(0, color=t["baseline"], linewidth=1.0, zorder=2)
    bx.plot(slow_m, color=t["ramp"][5], linewidth=2.0, zorder=4)
    bx.plot(fast_m, color=t["ramp"][2], linewidth=2.0, zorder=3)

    for i, colour, y, ha, label in (
            (f_in,  t["ramp"][2], 30.0, "right", "new entry"),
            (s_in,  t["ramp"][5], 30.0, "left",  "old entry"),
            (f_out, t["ramp"][2], -13.5, "right", "new exit"),
            (s_out, t["ramp"][5], -13.5, "left",  "old exit")):
        bx.plot([i], [0], marker="o", markersize=5.2, color=colour,
                markeredgecolor=t["surface"], markeredgewidth=1.2, zorder=6)
        bx.text(i + (-4 if ha == "right" else 4), y, label, color=colour,
                fontsize=8.5, fontweight="600", ha=ha, va="center")

    for (p0, p1), note in (((f_in, s_in), "of the rally the slow rule sits out"),
                           ((f_out, s_out), "of the giveback it sits through")):
        bx.annotate("", xy=(p1, 19.0), xytext=(p0, 19.0),
                    arrowprops=dict(arrowstyle="<->", color=t["ink_secondary"],
                                    linewidth=1.0, shrinkA=0, shrinkB=0))
        bx.text((p0 + p1) / 2, 20.4, f"{p1 - p0} days\n{note}",
                color=t["ink_secondary"], fontsize=8.2, ha="center", va="bottom",
                linespacing=1.45)

    fig.text(0.5, -0.005,
             "Each rule is the sign of its own momentum: in when the line crosses zero from below, "
             "out when it crosses back.\nThe short window crosses first at both ends, and that gap "
             "is the only thing the combination trades on.",
             ha="center", color=t["ink_secondary"], fontsize=8.6)
    save(fig, t, f"fast-times-slow-{mode}.png")


# --------------------------------------------------------- fig: signal kernels
def signal_kernels(mode):
    """02 -- MACD is momentum with a different weighting of past returns.

    Both curves are the weight each past daily return carries in the signal,
    normalised to sum to one so only the shape is being compared.
    """
    t = THEMES[mode]
    lags = np.arange(0, 61)

    box = np.where(lags < 21, 1.0 / 21, 0.0)          # 21-day mean of returns

    a_fast, a_slow = 2 / 13, 2 / 27                    # MACD spans 12 and 26
    w = (1 - a_slow) ** (lags + 1) - (1 - a_fast) ** (lags + 1)
    w = w / (1 / a_slow - 1 / a_fast)                  # the exact total, = 7

    fig, ax = plt.subplots(figsize=(7.0, 4.3))
    fig.patch.set_facecolor(t["surface"])
    style_axes(ax, t, ylabel="weight the signal puts on $r_{s,t-i}$",
               xlabel="lag $i$ (trading days before $t$)")

    ax.step(lags, box, where="post", color=t["muted"], linewidth=1.7, zorder=3)
    ax.fill_between(lags, 0, box, step="post", color=t["muted"], alpha=0.13, zorder=2)
    ax.plot(lags, w, color=t["series"], linewidth=2.1, zorder=4)
    ax.fill_between(lags, 0, w, color=t["series"], alpha=0.13, zorder=2)

    ax.axhline(0, color=t["baseline"], linewidth=0.9, zorder=2)
    ax.set_xlim(0, 60)
    ax.set_ylim(0, 0.058)

    ax.text(21.6, 0.0455, "21-day momentum — a box:\nevery day inside counts equally,\nnothing outside counts at all",
            color=t["muted"], fontsize=8.6, ha="left", va="top", linespacing=1.5)
    ax.text(33, 0.0148, "MACD (12/26) — a hump:\npeaks at lag 8, never reaches zero",
            color=t["series"], fontsize=8.6, ha="left", va="center", linespacing=1.5)
    ax.plot([8], [w[8]], marker="o", markersize=4.5, color=t["series"],
            markeredgecolor=t["surface"], markeredgewidth=1.2, zorder=6)

    titles(ax, t, "MACD is momentum with a different kernel",
           "both weight past returns; only the shape of the weighting differs")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    save(fig, t, f"signal-kernels-{mode}.png")

FIGURES = (fast_times_the_slow, signal_kernels)

if __name__ == "__main__":
    for mode in ("light", "dark"):
        for f in FIGURES:
            f(mode)
    print(f"wrote {2 * len(FIGURES)} figures for 03-shaping-the-lookback.md")
