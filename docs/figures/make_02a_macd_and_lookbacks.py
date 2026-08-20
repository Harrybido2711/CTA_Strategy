"""Figures for docs/02a-macd-and-lookbacks.md.

Run from anywhere:

    python docs/figures/make_02a_macd_and_lookbacks.py

Writes light- and dark-mode PNGs into docs/figures/. The chapter references
them through a <picture> element so GitHub serves the variant matching the
reader's theme.

Figures produced
----------------
    signal-kernels  MACD is momentum with a hump-shaped kernel, not a box

All are schematics drawn from illustrative values.

Formulas stay in the markdown as LaTeX rather than being rendered here: text in
an image is neither selectable nor searchable.
"""

import matplotlib.pyplot as plt
import numpy as np
from _style import THEMES, save, style_axes, titles


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

FIGURES = (signal_kernels,)

if __name__ == "__main__":
    for mode in ("light", "dark"):
        for f in FIGURES:
            f(mode)
    print(f"wrote {2 * len(FIGURES)} figures for 02a-macd-and-lookbacks.md")
