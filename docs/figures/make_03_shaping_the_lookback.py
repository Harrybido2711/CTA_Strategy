"""Figures for docs/03-shaping-the-lookback.md.

Run from anywhere:

    python docs/figures/make_03_shaping_the_lookback.py

Writes light- and dark-mode PNGs into docs/figures/. The chapter references
them through a <picture> element so GitHub serves the variant matching the
reader's theme.

Figures produced
----------------
    ratio-grid           the (slow, fast) search space, and the 2:1 band it returns
    fast-times-slow  a fast window fires before a slow one at both ends
    ewma-weights     an SMA weights every lag alike; an EWMA decays from the newest
    whipsaw-and-smoother  a volatility cluster whipsaws the fast leg, and what a smoother removes
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
    a slow moving average drawn over it. The lower panel is each of those two
    lines' own momentum -- how far it has travelled over its own window -- so
    the bottom panel is computed from the lines drawn in the top one rather
    than from a separate series. Each rule fires where its own line crosses
    zero; the short window crosses first at both ends, and that gap is the
    reason to carry two.
    """
    t = THEMES[mode]
    rng = np.random.RandomState(7)
    N_F, N_S = 20, 40                                    # the conventional 2:1

    n = 210
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

    def momentum(v, N):                    # how far a line has moved over N days
        m = np.full(n, np.nan)
        m[N:] = v[N:] - v[:-N]
        return m

    # Taken on the two averages drawn above, each over its own window, so the
    # lower panel is a statement about the lines in the upper one.
    fast_m, slow_m = momentum(fast_ma, N_F), momentum(slow_ma, N_S)

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

    ax.text(126, fast_ma[126] + 1.4, f"fast, {N_F}-day", color=t["ink"],
            fontsize=8.6, fontweight="600", ha="right", va="bottom")
    ax.text(140, slow_ma[140] - 1.4, f"slow, {N_S}-day", color=t["ink"],
            fontsize=8.6, fontweight="600", ha="left", va="top")
    ax.text(5, 97.0, "price", color=t["muted"], fontsize=8.6, ha="left")

    for y, (p0, p1), colour, label in (
            (90.6, (f_in, f_out), t["ramp"][2], "held by the fast rule"),
            (88.2, (s_in, s_out), t["ramp"][5], "held by the slow rule alone")):
        ax.plot([p0, p1], [y, y], color=colour, linewidth=3.6,
                solid_capstyle="butt", zorder=5)
        ax.text(p0 - 3, y, label, color=t["ink_secondary"], fontsize=8.3,
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
        bx.text(i + (-4 if ha == "right" else 4), y, label, color=t["ink"],
                fontsize=8.5, fontweight="600", ha=ha, va="center")

    for (p0, p1), note in (((f_in, s_in), "of the rally the slow rule sits out"),
                           ((f_out, s_out), "of the giveback it sits through")):
        bx.annotate("", xy=(p1, 19.0), xytext=(p0, 19.0),
                    arrowprops=dict(arrowstyle="<->", color=t["ink_secondary"],
                                    linewidth=1.0, shrinkA=0, shrinkB=0))
        mid = (p0 + p1) / 2
        ha = "center" if mid < n * 0.75 else "right"
        bx.text(mid if ha == "center" else p1 + 6, 20.4, f"{p1 - p0} days\n{note}",
                color=t["ink_secondary"], fontsize=8.2, ha=ha, va="bottom",
                linespacing=1.45)

    fig.text(0.5, -0.005,
             "Each rule is the sign of its own momentum: in when the line crosses zero from below, "
             "out when it crosses back.\nThe short window crosses first at both ends, and that gap "
             "is the only thing the combination trades on.",
             ha="center", color=t["ink_secondary"], fontsize=8.6)
    save(fig, t, f"fast-times-slow-{mode}.png")


# ---------------------- fig: the grid the fast/slow pairing is searched over
def ratio_grid(mode):
    """03 s1 -- the search space for (slow, fast), and why 2:1 shows up as a band.

    Schematic. A geometric ladder on both axes. Half the grid is empty by
    construction because the fast leg must be the shorter one; the rest is
    shaded by an illustrative score that peaks where the slow window is about
    twice the fast. Warm cells fall on a diagonal, which is the whole point:
    the ratio is what carries, not the absolute windows.
    """
    t = THEMES[mode]
    labels = ["1d", "1w", "2w", "1m", "1q"]
    days = np.array([1.0, 5.0, 10.0, 21.0, 63.0])
    n = len(labels)

    fig, ax = plt.subplots(figsize=(6.6, 5.2))
    fig.patch.set_facecolor(t["surface"])
    ax.set_facecolor(t["surface"])

    for i in range(n):                                  # i indexes the slow leg, on y
        for j in range(n):                              # j indexes the fast leg, on x
            if j >= i:                                  # fast must be strictly shorter
                ax.add_patch(plt.Rectangle((j, i), 1, 1, facecolor=t["grid"],
                                           edgecolor=t["surface"], linewidth=1.6, zorder=2))
                ax.plot([j + 0.28, j + 0.72], [i + 0.28, i + 0.72],
                        color=t["baseline"], linewidth=1.1, zorder=3)
                continue
            score = np.exp(-((np.log(days[i] / days[j]) - np.log(2.0)) ** 2) / (2 * 0.55 ** 2))
            shade = t["ramp"][int(round(score * (len(t["ramp"]) - 1)))]
            ax.add_patch(plt.Rectangle((j, i), 1, 1, facecolor=shade,
                                       edgecolor=t["surface"], linewidth=1.6, zorder=2))

    for i, j in ((2, 1), (3, 2)):                       # the 2:1 pairs, as drawn on the board
        ax.add_patch(plt.Rectangle((j + 0.06, i + 0.06), 0.88, 0.88, fill=False,
                                   edgecolor=t["ink"], linewidth=1.8, zorder=5))

    ax.text(3.5, 3.5, "≈ 2:1", color=t["ink"], fontsize=9.8, fontweight="600",
            ha="center", va="center", zorder=6)
    ax.text(3.0, 0.5, "the fast leg must be the shorter one", color=t["ink_secondary"],
            fontsize=8.8, ha="center", va="center", zorder=6)

    ax.set_xlim(0, n)
    ax.set_ylim(0, n)
    ax.set_xticks(np.arange(n) + 0.5)
    ax.set_yticks(np.arange(n) + 0.5)
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_yticklabels(labels, fontsize=9)
    ax.tick_params(colors=t["muted"], length=0)
    for side in ax.spines.values():
        side.set_visible(False)
    ax.set_xlabel("fast lookback $N_f$", color=t["ink_secondary"], fontsize=9.4, labelpad=8)
    ax.set_ylabel("slow lookback $N_s$", color=t["ink_secondary"], fontsize=9.4, labelpad=8)

    titles(ax, t, "One grid search, and the band it comes back with",
           "illustrative — darker is better, and the warm cells run diagonally")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    save(fig, t, f"ratio-grid-{mode}.png")


# ------------------------ fig: what an SMA and an EWMA weight a past return by
def ewma_weights(mode):
    """03 s2 -- an SMA gives every lag the same weight; an EWMA decays from the newest.

    Schematic. Weight carried by the return at each lag, both normalised to sum
    to one, so only the shape is compared. The box is a 21-day mean; the curve
    is an EWMA with a 10-day half-life.
    """
    t = THEMES[mode]
    lags = np.arange(0, 46)

    box = np.where(lags < 21, 1.0 / 21, 0.0)
    lam = 0.5 ** (1 / 10)                              # 10-day half-life
    ewma = (1 - lam) * lam ** lags

    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    fig.patch.set_facecolor(t["surface"])
    style_axes(ax, t, ylabel="weight on that return",
               xlabel="lag in trading days   (0 = the newest return)")

    ax.plot(lags, box, color=t["ramp"][2], linewidth=2.0, zorder=3)
    ax.plot(lags, ewma, color=t["ramp"][5], linewidth=2.0, zorder=4)
    ax.scatter([0], [ewma[0]], s=30, color=t["ramp"][5], zorder=5)

    lead = dict(arrowstyle="-", color=t["muted"], linewidth=1.0)
    top = ewma[0]
    ax.annotate("EWMA", xy=(4, ewma[4]), xytext=(8.5, top * 1.10), color=t["ink"],
                fontsize=9.2, fontweight="600", ha="left",
                arrowprops=dict(connectionstyle="arc3,rad=0.2", **lead), zorder=6)
    ax.annotate("21-day SMA", xy=(15, 1.0 / 21), xytext=(22.5, top * 0.94), color=t["ink"],
                fontsize=9.2, fontweight="600", ha="left",
                arrowprops=dict(connectionstyle="arc3,rad=-0.2", **lead), zorder=6)
    ax.annotate("over-weighted", xy=(0.5, top * 0.99), xytext=(6.2, top * 0.80),
                color=t["ink_secondary"], fontsize=8.8, ha="left",
                arrowprops=dict(connectionstyle="arc3,rad=0.25", **lead), zorder=6)
    ax.annotate("under-weighted", xy=(27, ewma[27]), xytext=(31, top * 0.30),
                color=t["ink_secondary"], fontsize=8.8, ha="left",
                arrowprops=dict(connectionstyle="arc3,rad=-0.25", **lead), zorder=6)

    ax.set_xlim(-1.5, 46)
    ax.set_ylim(0, ewma[0] * 1.24)
    ax.set_yticks([])
    titles(ax, t, "The same total weight, spread two different ways",
           "illustrative — a 21-day box against a 10-day half-life")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    save(fig, t, f"ewma-weights-{mode}.png")


# --------------- fig: what a volatility cluster does to the fast leg, and the fix
def whipsaw_and_smoother(mode):
    """03 s4 -- a volatility cluster whipsaws the fast leg; a smoother removes most of it.

    Schematic. One price path, calm at both ends and violent in the shaded
    middle, carrying a slow average and a fast one. Left: the raw fast leg
    crosses the slow leg repeatedly inside the cluster, and every crossing is a
    round trip. Right: the same fast leg passed through a short smoother first.
    """
    t = THEMES[mode]
    rng = np.random.RandomState(41)
    T = 420
    day = np.arange(T)

    vol = np.where((day > 150) & (day < 300), 5.0, 0.75)       # the cluster
    drift = np.where(day < 230, 0.10, -0.07)
    px = 100 + np.cumsum(drift + vol * rng.standard_normal(T))

    def ema(x, span):
        a = 2.0 / (span + 1)
        out = np.empty_like(x)
        out[0] = x[0]
        for i in range(1, len(x)):
            out[i] = a * x[i] + (1 - a) * out[i - 1]
        return out

    slow = ema(px, 90)
    fast = ema(px, 8)
    smoothed = ema(fast, 4)                                    # shorter than the fast period

    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.2), sharey=True,
                             gridspec_kw=dict(wspace=0.10))
    fig.patch.set_facecolor(t["surface"])

    for ax, (leg, head, sub) in zip(axes, (
            (fast, "The fast leg, raw", "every dot is a crossing — and a round trip"),
            (smoothed, "The fast leg, smoothed first", "the same cluster, most of the churn gone"))):
        style_axes(ax, t, ylabel="price" if ax is axes[0] else None, xlabel="date $t$", grid=False)
        ax.axvspan(150, 300, color=t["grid"], zorder=0)
        ax.plot(day, px, color=t["ramp"][0], linewidth=0.8, zorder=2)
        ax.plot(day, slow, color=t["ramp"][6], linewidth=2.0, zorder=4)
        ax.plot(day, leg, color=t["ramp"][3], linewidth=1.7, zorder=3)

        cross = np.flatnonzero(np.diff(np.sign(leg - slow)) != 0) + 1
        inside = cross[(cross >= 150) & (cross < 300)]
        ax.scatter(day[cross], leg[cross], s=26, color=t["ink"], zorder=6)

        ax.set_xticks([])
        ax.set_yticks([])
        titles(ax, t, head, sub)
        ax.text(225, ax.get_ylim()[0] + 0.06 * np.ptp(ax.get_ylim()),
                f"{inside.size} crossings inside the cluster",
                color=t["ink"], fontsize=9.0, fontweight="600", ha="center", zorder=6)

    lead = dict(arrowstyle="-", color=t["muted"], linewidth=1.0)
    axes[0].annotate("slow  $MOM_L$", xy=(95, slow[95]), xytext=(112, slow[95] - 26),
                     color=t["ink"], fontsize=9.0, ha="left",
                     arrowprops=dict(connectionstyle="arc3,rad=-0.2", **lead), zorder=7)
    axes[0].annotate("fast  $MOM_S$", xy=(60, fast[60]), xytext=(14, fast[60] + 30),
                     color=t["ink"], fontsize=9.0, ha="left",
                     arrowprops=dict(connectionstyle="arc3,rad=0.2", **lead), zorder=7)
    fig.text(0.5, -0.05,
             "Illustrative. The shaded stretch is a volatility cluster: the same trend underneath, "
             "several times the amplitude on top.",
             ha="center", color=t["ink_secondary"], fontsize=8.6)
    save(fig, t, f"whipsaw-and-smoother-{mode}.png")


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

FIGURES = (fast_times_the_slow, ratio_grid, ewma_weights, whipsaw_and_smoother,
           signal_kernels)

if __name__ == "__main__":
    for mode in ("light", "dark"):
        for f in FIGURES:
            f(mode)
    print(f"wrote {2 * len(FIGURES)} figures for 03-shaping-the-lookback.md")
