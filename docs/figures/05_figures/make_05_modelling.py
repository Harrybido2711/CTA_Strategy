"""Figures for docs/05_modelling.tex.

Run from anywhere:

    python docs/figures/make_05_modelling.py

Writes light- and dark-mode PNGs into docs/figures/. The chapter references
them through a <picture> element so GitHub serves the variant matching the
reader's theme.

Figures produced
----------------
    split-vs-ladder     one train/validation/test split, and the walk-forward
                        ladder that replaces it
    fold-anatomy        one rung of the ladder: select on validation, refit up
                        to the prediction date, score once on test
    outer-validation    where the held-out block sits, and what it alone is
                        allowed to choose
    winsorize-band      the barbell a signal actually has, and the rolling band
                        the tails are clipped onto
    beta-paths          standardized coefficients over time, read as a rotation
                        between signals

All are schematics drawn from illustrative values -- the point is the shape of
the split and of the distribution, never a measured level. Measured results
live in the prototype notes.

Formulas stay in the markdown as LaTeX rather than being rendered here: text in
an image is neither selectable nor searchable.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # figures/, for _style

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch
from _style import THEMES, rounded_bar, save, set_out, style_axes, titles

set_out(Path(__file__).resolve().parent)

BAR_H = 0.30            # height of a timeline block
ROUND = "round,pad=0.0,rounding_size=0.07"


def _block(ax, x0, x1, y, colour, t, label=None, alpha=1.0, fontsize=8.0):
    """One span of a timeline, drawn as a rounded block centred on ``y``."""
    ax.add_patch(FancyBboxPatch((x0, y - BAR_H / 2), x1 - x0, BAR_H,
                                boxstyle=ROUND, facecolor=colour, alpha=alpha,
                                edgecolor="none", zorder=3))
    if label:
        ax.text((x0 + x1) / 2, y, label, ha="center", va="center",
                color=t["surface"], fontsize=fontsize, fontweight="600", zorder=4)


def _caption(ax, x, y, text, t, colour=None, ha="left", fontsize=8.0, weight=None):
    ax.text(x, y, text, ha=ha, va="center", color=colour or t["ink_secondary"],
            fontsize=fontsize, fontweight=weight, linespacing=1.5, zorder=5)


# ------------------------------------------- fig: one split, then the ladder
def split_vs_ladder(mode):
    """05 ss 1-2 -- why the textbook split is replaced by a sliding one.

    Schematic. Above: the whole history cut once, so the model is fitted once
    and scored once. Below: the same history cut into short segments, with a
    train / validation / test frame that slides forward one segment at a time.
    The violet arrow is the structural point -- each iteration's test segment
    is the next iteration's validation segment, so every segment is eventually
    scored out of sample.
    """
    t = THEMES[mode]
    train, valid, test = t["ramp"][5], t["validation"], t["muted"]

    fig, ax = plt.subplots(figsize=(9.4, 5.2))
    fig.patch.set_facecolor(t["surface"])
    ax.set_facecolor(t["surface"])
    ax.set_xlim(0, 12.3)
    ax.set_ylim(0.22, 6.10)
    ax.axis("off")

    # ---- panel A: the single split
    yA = 5.55
    _caption(ax, 0.55, yA + 0.62, "A  ·  one split, one fit", t,
             colour=t["muted"], fontsize=8.6, weight="600")
    _block(ax, 0.55, 6.30, yA, train, t, "train")
    _block(ax, 6.30, 7.95, yA, valid, t, "validation")
    _block(ax, 7.95, 9.30, yA, test, t, "test")
    ax.annotate("", xy=(9.85, yA), xytext=(9.30, yA),
                arrowprops=dict(arrowstyle="-|>", color=t["baseline"],
                                linewidth=1.0, shrinkA=0, shrinkB=0))
    _caption(ax, 0.55, yA - 0.52,
             "several years of market, one set of coefficients,\n"
             "and roughly 250 days of out-of-sample score", t)

    # ---- panel B: the ladder
    x0, segw, nseg = 0.55, 0.72, 12
    yruler = 4.05
    _caption(ax, 0.55, yruler + 0.55, "B  ·  the same history, cut into segments", t,
             colour=t["muted"], fontsize=8.6, weight="600")
    ax.plot([x0, x0 + nseg * segw], [yruler] * 2, color=t["baseline"], linewidth=1.0)
    for i in range(nseg + 1):
        ax.plot([x0 + i * segw] * 2, [yruler - 0.11, yruler + 0.11],
                color=t["baseline"], linewidth=1.0)
    _caption(ax, x0 + nseg * segw + 0.25, yruler,
             "one segment $\\approx$ two to three months —\nabout one regime's worth of market", t)

    rows = ["1st", "2nd", "3rd"]
    ys = [3.25, 2.55, 1.85]
    for i, (name, y) in enumerate(zip(rows, ys)):
        a = x0 + i * segw
        _caption(ax, x0 - 0.18, y, name, t, ha="right", fontsize=8.2)
        _block(ax, a, a + 3 * segw, y, train, t, "train" if i == 0 else None)
        _block(ax, a + 3 * segw, a + 4 * segw, y, valid, t)
        _block(ax, a + 4 * segw, a + 5 * segw, y, test, t)
        if i == 0:
            _caption(ax, a + 3.5 * segw, y + 0.42, "validation", t,
                     ha="center", fontsize=7.6)
            _caption(ax, a + 4.5 * segw, y + 0.42, "test", t,
                     ha="center", fontsize=7.6)

    ax.text(x0 + 3 * segw, 1.30, "$\\vdots$", ha="center", va="center",
            color=t["muted"], fontsize=13)

    # the rung-to-rung identity: this test is the next validation
    xa = x0 + 4.5 * segw
    ax.annotate("", xy=(xa, ys[1] + BAR_H / 2 + 0.03),
                xytext=(xa, ys[0] - BAR_H / 2 - 0.03),
                arrowprops=dict(arrowstyle="-|>", color=t["accent"],
                                linewidth=1.3, shrinkA=0, shrinkB=0), zorder=6)
    _caption(ax, xa + 0.30, (ys[0] + ys[1]) / 2,
             "each iteration's test segment becomes\nthe next iteration's validation segment",
             t, colour=t["accent"], fontsize=8.0, weight="600")

    # colour key
    key = [(0.55, train, "train — the model is fitted here"),
           (4.65, valid, "validation — chooses the features"),
           (8.35, test, "test — scored once, chooses nothing")]
    for kx, colour, label in key:
        ax.add_patch(FancyBboxPatch((kx, 0.36), 0.42, 0.20, boxstyle=ROUND,
                                    facecolor=colour, edgecolor="none", zorder=3))
        _caption(ax, kx + 0.56, 0.46, label, t, fontsize=7.8)

    titles(ax, t, "One split fits once; the ladder keeps fitting",
           "schematic — the frame slides forward one segment per iteration")
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    save(fig, t, f"split-vs-ladder-{mode}.png")


# ------------------------------------------------------ fig: one rung, in full
def fold_anatomy(mode):
    """05 s 2.3 -- what actually happens inside a single iteration.

    Schematic. The features are chosen on the validation segment, the surviving
    features are refitted on a window that ends where the prediction starts --
    which is why the refit window is shifted forward, dotted at its old left
    edge -- and only then is the test segment scored.
    """
    t = THEMES[mode]
    train, valid, test = t["ramp"][5], t["validation"], t["muted"]

    fig, ax = plt.subplots(figsize=(9.4, 3.9))
    fig.patch.set_facecolor(t["surface"])
    ax.set_facecolor(t["surface"])
    ax.set_xlim(0.35, 11.75)
    ax.set_ylim(0.42, 3.72)
    ax.axis("off")

    xa, xb, xc, xd = 0.85, 4.45, 5.65, 6.85     # train | valid | test edges
    xshift = 1.75                                # left edge of the refit window
    ys = [3.20, 2.45, 1.70, 0.95]

    _block(ax, xa, xb, ys[0], train, t, "train")
    _caption(ax, xd + 0.55, ys[0], "fit the candidate signals", t)

    _block(ax, xb, xc, ys[1], valid, t, "valid", fontsize=7.4)
    _caption(ax, xd + 0.55, ys[1],
             "select features — the $L_1$ penalty drops the rest", t,
             colour=t["accent"], weight="600")

    ax.plot([xa, xshift], [ys[2]] * 2, color=t["baseline"], linewidth=1.1,
            linestyle=(0, (1.6, 2.2)), zorder=2)
    _block(ax, xshift, xc, ys[2], train, t, "re-train")
    _caption(ax, xd + 0.55, ys[2],
             "refit the survivors, penalty off, on the window\n"
             "that ends where the prediction starts", t)

    _block(ax, xc, xd, ys[3], test, t, "test", fontsize=7.4)
    _caption(ax, xd + 0.55, ys[3], "apply once — it chooses nothing", t)

    ax.plot([xc] * 2, [ys[3] - 0.42, ys[0] + 0.42], color=t["accent"],
            linewidth=1.0, linestyle=(0, (3, 2.4)), zorder=2)
    _caption(ax, xc + 0.10, ys[0] + 0.56, "the prediction date", t,
             colour=t["accent"], fontsize=7.8, weight="600")

    titles(ax, t, "One rung of the ladder",
           "schematic — select on validation, refit up to the prediction date, then score")
    fig.tight_layout(rect=(0, 0, 1, 0.88))
    save(fig, t, f"fold-anatomy-{mode}.png")


# --------------------------------------- fig: the held-out block and its job
def outer_validation(mode):
    """05 s 3 -- two validation layers, and the different questions they answer.

    Schematic. The ladder of section 2 runs entirely inside the training block
    and settles which features survive. The large held-out block, ringed in
    violet, is the only place a model class, its hyperparameters, or the
    optimizer's parameters may be chosen. Test sits beyond both.
    """
    t = THEMES[mode]
    train, valid, test = t["ramp"][5], t["validation"], t["muted"]

    fig, ax = plt.subplots(figsize=(9.8, 4.6))
    fig.patch.set_facecolor(t["surface"])
    ax.set_facecolor(t["surface"])
    ax.set_xlim(0.30, 13.35)
    ax.set_ylim(0.55, 4.50)
    ax.axis("off")

    xa, xb, xc, xd = 0.60, 5.60, 7.30, 8.80
    ytop = 4.00

    _block(ax, xa, xb, ytop, train, t, "train")
    _block(ax, xb, xc, ytop, valid, t, "validation")
    _block(ax, xc, xd, ytop, test, t, "test")
    ax.add_patch(FancyBboxPatch((xb - 0.07, ytop - BAR_H / 2 - 0.09),
                                xc - xb + 0.14, BAR_H + 0.18,
                                boxstyle="round,pad=0.0,rounding_size=0.12",
                                facecolor="none", edgecolor=t["accent"],
                                linewidth=1.5, zorder=5))

    # the ladder, in miniature, inside the training block
    segw = 0.62
    for i, y in enumerate((3.05, 2.45, 1.85)):
        a = xa + 0.30 + i * segw
        _block(ax, a, a + 3 * segw, y, train, t)
        _block(ax, a + 3 * segw, a + 4 * segw, y, valid, t)
        _block(ax, a + 4 * segw, a + 5 * segw, y, test, t)
    ax.text(xa + 0.30 + 2.6 * segw, 1.36, "$\\vdots$", ha="center", va="center",
            color=t["muted"], fontsize=12)

    _caption(ax, xa + 0.30, 0.85,
             "inner layer — the ladder of § 2, run inside the training block.\n"
             "It chooses which features survive, and nothing else.", t)

    # what the outer block alone may choose
    ax.annotate("", xy=(9.55, 3.05), xytext=((xb + xc) / 2, ytop - BAR_H / 2 - 0.16),
                arrowprops=dict(arrowstyle="-|>", color=t["accent"], linewidth=1.2,
                                connectionstyle="angle3,angleA=-70,angleB=10",
                                shrinkA=2, shrinkB=4), zorder=5)
    _caption(ax, 9.75, 3.30, "the outer block alone chooses", t,
             colour=t["accent"], fontsize=8.6, weight="600")
    lines = [
        ("the model class", "Lasso · Ridge · decision tree"),
        ("its hyperparameters", "the penalty grid $\\lambda$"),
        ("the optimizer's parameters", "risk aversion $\\gamma$, the per-asset cap"),
    ]
    for i, (head, detail) in enumerate(lines):
        y = 2.80 - i * 0.62
        _caption(ax, 9.75, y, head, t, colour=t["ink"], fontsize=8.2, weight="600")
        _caption(ax, 9.75, y - 0.27, detail, t, fontsize=7.8)

    _caption(ax, 9.75, 0.85, "test answers one question, once:\n"
                             "does any of this survive?", t, colour=t["muted"])

    titles(ax, t, "Two validation layers, two different jobs",
           "schematic — features are chosen inside train; everything else, in the held-out block")
    fig.tight_layout(rect=(0, 0, 1, 0.89))
    save(fig, t, f"outer-validation-{mode}.png")


# --------------------------------------- fig: the barbell, and the clip band
def winsorize_band(mode):
    """05 s 4.1 -- the distribution a signal actually has, and what clipping does.

    Schematic. Left: ranked signal values are expected to fill the unit
    interval evenly, and do not -- the mass piles at both ends. Right: one
    signal against its own rolling 1st and 99th percentiles. The spikes are
    pulled onto the band rather than deleted, and because the band is
    re-estimated each step, a value that is extreme against one quarter is
    ordinary against the next.
    """
    t = THEMES[mode]

    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.7),
                             gridspec_kw=dict(width_ratios=[1.0, 1.45]))
    fig.patch.set_facecolor(t["surface"])

    # ---- left: expected uniform against the observed barbell
    ax = axes[0]
    share = np.array([0.19, 0.13, 0.08, 0.06, 0.05, 0.05, 0.06, 0.08, 0.13, 0.17])
    for i, v in enumerate(share):
        rounded_bar(ax, i, v, width=0.62, color=t["ramp"][5])
    ax.axhline(0.10, color=t["accent"], linewidth=1.2, linestyle=(0, (3, 2)), zorder=4)
    ax.text(4.5, 0.106, "what an even spread\nwould have given",
            ha="center", va="bottom", color=t["accent"], fontsize=7.8,
            fontweight="600", linespacing=1.4)
    style_axes(ax, t, ylabel="share of observations",
               xlabel="decile of the ranked signal $x_{j,t}$")
    ax.set_xticks(range(10))
    ax.set_xticklabels(["1", "", "3", "", "5", "", "7", "", "9", ""], fontsize=8)
    ax.set_xlim(-0.7, 9.7)
    ax.set_ylim(0, 0.225)
    ax.set_yticks([0, 0.05, 0.10, 0.15, 0.20])

    # ---- right: the raw series, the rolling band, the clipped series
    ax = axes[1]
    rng = np.random.default_rng(11)
    L, n = 60, 320
    raw = np.cumsum(rng.normal(0, 0.16, n))
    raw = raw - raw.mean()
    for centre, size in ((118, 3.0), (210, -2.8), (274, 3.2)):
        raw[centre] += size

    # the band is estimated from history only, so today's value cannot widen it
    lo = np.full(n, np.nan)
    hi = np.full(n, np.nan)
    for i in range(L, n):
        window = raw[i - L:i]
        lo[i], hi[i] = np.quantile(window, 0.02), np.quantile(window, 0.98)
    clipped = np.clip(raw, lo, hi)

    x = np.arange(L, n)
    ax.fill_between(x, lo[L:], hi[L:], color=t["ramp"][1], alpha=0.32,
                    linewidth=0, zorder=1)
    ax.plot(x, raw[L:], color=t["ramp"][5], linewidth=1.15, zorder=3)
    ax.plot(x, clipped[L:], color=t["accent"], linewidth=1.5, zorder=4)
    for centre in (118, 210, 274):
        # offset the arrow so it never sits on top of the raw spike it describes
        ax.annotate("", xy=(centre + 7, clipped[centre]), xytext=(centre + 7, raw[centre]),
                    arrowprops=dict(arrowstyle="-|>", color=t["accent"],
                                    linewidth=1.0, shrinkA=1, shrinkB=1), zorder=5)
    ax.axhline(0, color=t["baseline"], linewidth=0.8, zorder=2)

    ax.text(L + 4, -2.55, "rolling 2nd–98th percentile band, estimated\nfrom the raw series and from history only",
            ha="left", va="bottom", color=t["ink_secondary"], fontsize=7.6,
            linespacing=1.45)
    ax.text(274, raw[274] + 0.15, "pulled onto the band,\nnot deleted", ha="right",
            va="bottom", color=t["accent"], fontsize=7.6, fontweight="600",
            linespacing=1.45)

    style_axes(ax, t, ylabel="signal value $x_{j,t}$",
               xlabel="trading day $t$ over one sample")
    ax.set_xlim(L, n - 1)
    ax.set_ylim(-3.4, 3.4)
    ax.set_xticks([100, 150, 200, 250, 300])
    ax.set_yticks([-3, 0, 3])

    titles(axes[0], t, "The tails are not a mistake to delete",
           "schematic — the mass piles at both ends, and clipping keeps the observation")
    fig.tight_layout(rect=(0, 0, 1, 0.86))
    save(fig, t, f"winsorize-band-{mode}.png")


# ------------------------------------- fig: comparable coefficients over time
def beta_paths(mode):
    """05 s 4.2 -- what standardizing the signals buys, drawn.

    Schematic. Once every signal is on one scale, the fitted coefficients can
    be plotted on one axis and read against one another: which signal the model
    is leaning on, and when the lean rotates. On raw scales the same chart is
    meaningless, because a coefficient's size is set by the signal's units.
    """
    t = THEMES[mode]

    n = 260
    x = np.arange(n)
    u = x / (n - 1)
    mom = 0.62 - 0.75 * np.clip((u - 0.34) / 0.30, 0, 1) + 0.30 * np.clip((u - 0.74) / 0.26, 0, 1)
    vol = 0.05 + 0.62 * np.clip((u - 0.30) / 0.26, 0, 1) - 0.34 * np.clip((u - 0.72) / 0.28, 0, 1)
    macd = 0.28 + 0.10 * np.sin(2 * np.pi * u * 1.6)

    rng = np.random.default_rng(5)
    wobble = lambda s: np.convolve(rng.normal(0, s, n + 20), np.ones(21) / 21, "same")[10:-10]
    mom, vol, macd = mom + wobble(0.10), vol + wobble(0.10), macd + wobble(0.08)

    fig, ax = plt.subplots(figsize=(8.0, 3.9))
    fig.patch.set_facecolor(t["surface"])

    ax.axvspan(0, 78, color=t["ramp"][1], alpha=0.22, linewidth=0, zorder=0)
    ax.axvspan(96, 188, color=t["validation"], alpha=0.12, linewidth=0, zorder=0)
    ax.axhline(0, color=t["baseline"], linewidth=0.9, zorder=2)

    for series, colour, label, ly in ((mom, t["ramp"][5], "momentum", mom[6]),
                                      (macd, t["ramp"][3], "MACD", macd[6]),
                                      (vol, t["validation"], "volatility regime", vol[6])):
        ax.plot(x, series, color=colour, linewidth=1.6, zorder=4)
        ax.text(-6, ly, label, ha="right", va="center", color=colour,
                fontsize=8.2, fontweight="600")

    ax.text(39, 0.93, "momentum carries the book", ha="center", va="center",
            color=t["ink_secondary"], fontsize=7.8)
    ax.text(142, 0.93, "the lean rotates to the regime signal", ha="center",
            va="center", color=t["ink_secondary"], fontsize=7.8)

    style_axes(ax, t, ylabel="fitted coefficient $\\beta_j$,\nstandardized signals",
               xlabel="trading day $t$, refitted at every step of the ladder")
    ax.set_xlim(-72, n - 1)
    ax.set_ylim(-0.35, 1.05)
    ax.set_xticks([0, 50, 100, 150, 200, 250])
    ax.set_yticks([0, 0.5, 1.0])

    titles(ax, t, "Comparable coefficients are a regime read",
           "schematic — only readable because every signal was put on the same scale")
    fig.tight_layout(rect=(0, 0, 1, 0.87))
    save(fig, t, f"beta-paths-{mode}.png")


FIGURES = (split_vs_ladder, fold_anatomy, outer_validation, winsorize_band, beta_paths)

if __name__ == "__main__":
    for mode in ("light", "dark"):
        for fn in FIGURES:
            fn(mode)
    print(f"wrote {2 * len(FIGURES)} figures for 05_modelling")
