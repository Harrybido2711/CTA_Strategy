"""Figures for docs/03-from-signal-to-position.md.

Run from anywhere:

    python docs/figures/make_03_from_signal_to_position.py

Writes light- and dark-mode PNGs into docs/figures/. The chapter references
them through a <picture> element so GitHub serves the variant matching the
reader's theme.

Figures produced
----------------
    overlap-tranches  the five overlapping 1/5 tranches of a 5-day hold

All are schematics drawn from illustrative values.

Formulas stay in the markdown as LaTeX rather than being rendered here: text in
an image is neither selectable nor searchable.
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from _style import THEMES, save


# ------------------------------------------------- fig: overlapping 1/5 tranches
def overlap_tranches(mode):
    t = THEMES[mode]
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Mon", "Tue", "Wed", "Thu", "Fri"]

    fig, ax = plt.subplots(figsize=(9.4, 3.9))
    fig.patch.set_facecolor(t["surface"])
    ax.set_facecolor(t["surface"])

    for i in range(5):
        y = 4 - i
        ax.add_patch(FancyBboxPatch(
            (i + 0.07, y - 0.19), 5 - 0.14, 0.38,
            boxstyle="round,pad=0,rounding_size=0.11",
            facecolor=t["series"], edgecolor="none", zorder=3))
        ax.text(i + 2.5, y, "20% of book", ha="center", va="center",
                color="#ffffff", fontsize=8.4, fontweight="600", zorder=4)
        ax.text(-0.35, y, f"tranche {i + 1}", ha="right", va="center",
                color=t["ink_secondary"], fontsize=8.8)

    # the window where all five are simultaneously live
    ax.axvspan(4, 5, color=t["wash"], alpha=0.09, zorder=1)
    ax.text(4.5, -0.42, "all five live", ha="center", va="top",
            color=t["ink_secondary"], fontsize=8.6)

    for i in range(len(days)):
        ax.axvline(i, color=t["grid"], linewidth=0.8, zorder=0)
        ax.text(i + 0.5, 5.05, days[i], ha="center", va="bottom",
                color=t["muted"], fontsize=8.5)

    ax.set_xlim(-2.0, len(days))
    ax.set_ylim(-1.35, 5.6)
    ax.axis("off")
    ax.text(-2.0, 5.72, "A 5-day hold is five overlapping tranches, not a Monday rebalance",
            color=t["ink"], fontsize=11.5, fontweight="600", va="bottom")
    ax.text(-2.0, -1.30,
            "held weight = mean of the last 5 daily targets  $\\rightarrow$  entry spread across every "
            "weekday, so no day-of-week bias",
            color=t["ink_secondary"], fontsize=8.8, va="top")

    fig.tight_layout(rect=(0, 0, 1, 0.94))
    save(fig, t, f"overlap-tranches-{mode}.png")

FIGURES = (overlap_tranches,)

if __name__ == "__main__":
    for mode in ("light", "dark"):
        for fn in FIGURES:
            fn(mode)
    print(f"wrote {2 * len(FIGURES)} figures for 03-from-signal-to-position.md")
