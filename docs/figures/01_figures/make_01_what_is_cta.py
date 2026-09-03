"""Figures for docs/01_what_is_cta.tex.

Run from anywhere:

    python docs/figures/make_01_what_is_cta.py

Writes light- and dark-mode PNGs into docs/figures/. The chapter references
them through a <picture> element so GitHub serves the variant matching the
reader's theme.

Figures produced
----------------
    levels-vs-rebased  raw closes vs rebased: SPY looks highest, GLD returned more
    payoff-asymmetry   a static long's loss is floored at zero; a short's is not

All are schematics drawn from illustrative values, except levels-vs-rebased,
which reads CTA_data/ because its claim is about this dataset rather than about
a shape.

Formulas stay in the markdown as LaTeX rather than being rendered here: text in
an image is neither selectable nor searchable.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # figures/, for _style

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from _style import DATA, THEMES, save, set_out, style_axes, titles

set_out(Path(__file__).resolve().parent)


# --------------------------------------------- fig: raw levels vs rebased
def levels_vs_rebased(mode):
    """01 -- why a price level says nothing across tickers.

    The only figure here plotted from real data, because the claim is about
    this dataset rather than about a shape in general.
    """
    t = THEMES[mode]
    tickers = ["GLD", "SPY", "TLT"]          # ordered by final performance
    series = {}
    for tk in tickers:
        d = pd.read_csv(DATA / f"{tk}_ohlcv_1d.csv", usecols=["ts_event", "close"])
        d["ts_event"] = pd.to_datetime(d["ts_event"])
        series[tk] = d.sort_values("ts_event").set_index("ts_event")["close"]
    close = pd.DataFrame(series).dropna()
    rebased = close.div(close.iloc[0]) * 100
    x = close.index

    # three steps of the single hue, darkest for the best performer
    colours = [t["ramp"][6], t["ramp"][4], t["ramp"][2]]

    fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.3))
    fig.patch.set_facecolor(t["surface"])

    panels = [
        (close, "Raw closing price", "SPY sits highest for the whole sample", "\\$"),
        (rebased, "Rebased to 100", "but GLD returned the most, and TLT lost", ""),
    ]

    for ax, (frame, title, subtitle, unit) in zip(axes, panels):
        style_axes(ax, t, ylabel=f"close ({unit})" if unit else "index (start = 100)",
                   xlabel="date")
        for tk, c in zip(tickers, colours):
            ax.plot(x, frame[tk], color=c, linewidth=1.6, zorder=3)
            ax.text(x[-1], frame[tk].iloc[-1], f"  {tk}", color=c, fontsize=8.8,
                    fontweight="600", va="center", ha="left")
        ax.set_xlim(x[0], x[-1] + (x[-1] - x[0]) * 0.13)
        ax.tick_params(axis="x", labelrotation=0)
        titles(ax, t, title, subtitle)

    # the right panel has a meaningful baseline; the left does not
    axes[1].axhline(100, color=t["baseline"], linewidth=0.9,
                    linestyle=(0, (4, 3)), zorder=2)

    fig.tight_layout(rect=(0, 0, 1, 0.92))
    save(fig, t, f"levels-vs-rebased-{mode}.png")

# ------------------------------------------- fig: long/short payoff asymmetry
def payoff_asymmetry(mode):
    """01 -- why a short is not a mirrored long.

    P&L per $1 of exposure against the terminal price. Both legs are straight
    lines of slope +-1, so the asymmetry is not in the rate: it is that the
    long's line stops at P_T = 0 while the short's has no right-hand edge.
    """
    t = THEMES[mode]
    x = np.linspace(0.0, 3.0, 400)          # terminal price as a multiple of entry
    long_pnl = x - 1.0
    short_pnl = 1.0 - x

    fig, ax = plt.subplots(figsize=(6.8, 4.4))
    fig.patch.set_facecolor(t["surface"])
    style_axes(ax, t, ylabel="P&L per \\$1 of exposure",
               xlabel="terminal price   $P_T / P_0$")

    # the region no long position can reach, but a short can
    ax.axhspan(-2.35, -1.0, color=t["wash"], alpha=0.07, zorder=0)

    ax.plot(x, long_pnl, color=t["muted"], linewidth=1.8, zorder=3)
    ax.plot(x, short_pnl, color=t["series"], linewidth=2.3, zorder=4)

    ax.axhline(0, color=t["baseline"], linewidth=0.9, zorder=2)
    ax.axhline(-1.0, color=t["baseline"], linewidth=0.9,
               linestyle=(0, (4, 3)), zorder=2)

    # the long's worst case is a reachable endpoint; mark it
    ax.plot([0], [-1.0], marker="o", markersize=5.5, color=t["muted"],
            markeredgecolor=t["surface"], markeredgewidth=1.2, zorder=6)

    ax.set_xlim(0, 3.0)
    ax.set_ylim(-2.35, 2.15)
    ax.set_xticks([0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0])
    ax.set_yticks([-2, -1, 0, 1, 2])

    ax.text(2.86, 1.94, "long", color=t["muted"], fontsize=9.2,
            fontweight="600", ha="right", va="center")
    ax.text(2.86, -2.08, "short", color=t["series"], fontsize=9.2,
            fontweight="600", ha="right", va="center")

    # both notes sit in the lower-left wedge, the only region neither line crosses
    ax.text(0.12, -1.14, "below $-100\\%$: unreachable for a long.",
            color=t["ink_secondary"], fontsize=8.4, ha="left", va="top")
    ax.text(0.12, -1.42, "$P_T \\geq 0$ caps its loss at the full outlay.",
            color=t["muted"], fontsize=8.4, ha="left", va="top")

    # the point of the chart: the short line leaves the frame and keeps going
    ax.annotate("", xy=(2.30, -2.28), xytext=(2.30, -1.66),
                arrowprops=dict(arrowstyle="-|>", color=t["series"], linewidth=1.2))
    ax.text(2.18, -1.99, "no floor —\nloss grows with $P_T$",
            color=t["ink_secondary"], fontsize=8.4, ha="right", va="center")

    titles(ax, t, "A short is not a mirrored long",
           "same slope, different domain: $P_T\\in[0,\\infty)$ bounds one leg and not the other")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    save(fig, t, f"payoff-asymmetry-{mode}.png")

FIGURES = (levels_vs_rebased, payoff_asymmetry)

if __name__ == "__main__":
    for mode in ("light", "dark"):
        for fn in FIGURES:
            fn(mode)
    print(f"wrote {2 * len(FIGURES)} figures for 01_what_is_cta")
