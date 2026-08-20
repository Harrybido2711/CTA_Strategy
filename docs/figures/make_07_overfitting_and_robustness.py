"""Figures for docs/07-overfitting-and-robustness.md.

Run from anywhere:

    python docs/figures/make_07_overfitting_and_robustness.py

Writes light- and dark-mode PNGs into docs/figures/. The chapter references
them through a <picture> element so GitHub serves the variant matching the
reader's theme.

Figures produced
----------------
    param-heatmap  a plateau (real edge) vs a spike (artifact)

All are schematics drawn from illustrative values.

Formulas stay in the markdown as LaTeX rather than being rendered here: text in
an image is neither selectable nor searchable.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from _style import THEMES, save, titles


# ------------------------------------------------------- fig: parameter sweep
def param_heatmap(mode):
    t = THEMES[mode]
    cmap = LinearSegmentedColormap.from_list("seq_blue", t["ramp"])

    fast = np.arange(2, 22, 2)
    slow = np.arange(10, 70, 6)
    FX, SY = np.meshgrid(fast, slow)
    rng = np.random.default_rng(7)

    plateau = 1.05 * np.exp(-(((FX - 11) / 6.5) ** 2 + ((SY - 36) / 17.0) ** 2))
    plateau += rng.normal(0, 0.045, plateau.shape)

    spike = rng.normal(0.10, 0.055, plateau.shape)
    spike[len(slow) // 2, len(fast) // 2] = 1.05

    fig, axes = plt.subplots(1, 2, figsize=(9.4, 4.1))
    fig.patch.set_facecolor(t["surface"])

    panels = [(plateau, "Plateau", "neighbours perform too — trust it"),
              (spike, "Spike", "one cell, cold all around — an artifact")]

    for ax, (grid, title, subtitle) in zip(axes, panels):
        ax.set_facecolor(t["surface"])
        im = ax.pcolormesh(fast, slow, grid, cmap=cmap, vmin=0, vmax=1.1,
                           shading="nearest", edgecolors=t["surface"], linewidth=1.4)
        for side in ax.spines.values():
            side.set_visible(False)
        ax.tick_params(colors=t["muted"], length=0, labelsize=8.5)
        ax.set_xticks(fast[::2])
        ax.set_yticks(slow[::2])
        ax.set_xlabel("fast lookback (days)", color=t["muted"], fontsize=8.5, labelpad=7)
        titles(ax, t, title, subtitle)

    axes[0].set_ylabel("slow lookback (days)", color=t["ink_secondary"],
                       fontsize=9, labelpad=8)

    cbar = fig.colorbar(im, ax=axes, fraction=0.026, pad=0.022)
    cbar.set_label("Sharpe", color=t["ink_secondary"], fontsize=9)
    cbar.ax.tick_params(colors=t["muted"], length=0, labelsize=8)
    cbar.outline.set_visible(False)

    save(fig, t, f"param-heatmap-{mode}.png")

FIGURES = (param_heatmap,)

if __name__ == "__main__":
    for mode in ("light", "dark"):
        for fn in FIGURES:
            fn(mode)
    print(f"wrote {2 * len(FIGURES)} figures for 07-overfitting-and-robustness.md")
