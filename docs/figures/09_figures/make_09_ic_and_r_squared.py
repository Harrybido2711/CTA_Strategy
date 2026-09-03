"""Figures for docs/09_ic_and_r_squared.tex.

Run from anywhere:

    python docs/figures/make_09_ic_and_r_squared.py

Writes light- and dark-mode PNGs into docs/figures/. The chapter references
them through a <picture> element so GitHub serves the variant matching the
reader's theme.

Figures produced
----------------
    prediction-shrinkage  a low-R2 model predicts a far narrower range than reality
    ic-series-vs-r2       squaring a noisy IC series manufactures explained variance

All are schematics drawn from illustrative values.

Formulas stay in the markdown as LaTeX rather than being rendered here: text in
an image is neither selectable nor searchable.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # figures/, for _style

import matplotlib.pyplot as plt
import numpy as np
from _style import THEMES, save, set_out, style_axes, titles

set_out(Path(__file__).resolve().parent)


# ------------------------------------------- fig: predictions shrink to the mean
def prediction_shrinkage(mode):
    """00-pipeline -- a low-R2 model must predict a far narrower range than reality.

    Schematic. Illustrative widths: realised 5-day returns at 2.5% standard
    deviation against predictions at 0.2%, the ratio implied by R2 = 0.005.
    """
    t = THEMES[mode]
    x = np.linspace(-0.08, 0.08, 900)

    def normal(x, s):
        return np.exp(-0.5 * (x / s) ** 2) / (s * np.sqrt(2 * np.pi))

    s = 0.025 / np.sqrt(1.8)                       # mixture gives fat tails
    realised = 0.9 * normal(x, s) + 0.1 * normal(x, 3 * s)
    predicted = normal(x, 0.002)

    fig, axes = plt.subplots(2, 1, figsize=(7.4, 5.0), sharex=True,
                             gridspec_kw=dict(hspace=0.42))
    fig.patch.set_facecolor(t["surface"])

    panels = [
        (axes[0], realised, t["muted"], "Realised 5-day returns",
         "standard deviation $\\approx$ 2.5%"),
        (axes[1], predicted, t["series"], "Model predictions",
         "standard deviation $\\approx$ 0.2% — about 12$\\times$ narrower"),
    ]
    for ax, y, colour, title, subtitle in panels:
        style_axes(ax, t, ylabel="density", grid=False)
        ax.plot(x, y, color=colour, linewidth=1.9, zorder=3)
        ax.fill_between(x, y, color=colour, alpha=0.13, zorder=2)
        ax.set_yticks([])
        ax.set_ylim(0, y.max() * 1.28)
        titles(ax, t, title, subtitle)

    # project the prediction's range onto the realised panel
    axes[0].axvspan(-0.004, 0.004, color=t["series"], alpha=0.16, zorder=1)
    axes[0].annotate("", xy=(0.004, realised.max() * 0.62),
                     xytext=(0.030, realised.max() * 0.62),
                     arrowprops=dict(arrowstyle="-|>", color=t["series"], linewidth=1.1))
    axes[0].text(0.032, realised.max() * 0.62,
                 "everything the model ever says\nfits inside this sliver",
                 color=t["series"], fontsize=8.4, ha="left", va="center", linespacing=1.5)

    axes[1].set_xlabel("5-day return", color=t["muted"], fontsize=8.5, labelpad=7)
    axes[1].set_xticks([-0.08, -0.04, 0, 0.04, 0.08])
    axes[1].set_xticklabels(["−8%", "−4%", "0", "+4%", "+8%"])
    axes[1].set_xlim(-0.08, 0.08)

    save(fig, t, f"prediction-shrinkage-{mode}.png")   # save() already crops tight

# ------------------------------- fig: IC keeps the time axis, R2 does not
def ic_series_vs_r2(mode):
    """08 -- IC keeps the time axis; squaring it folds noise into apparent skill.

    Schematic. Illustrative daily rank IC at mean 0.03 against a day-to-day
    standard deviation of 0.33 -- roughly what a ~30-name cross-section of
    correlated ETFs produces. The point is that the lower panel is almost
    entirely the variance term, not the mean.
    """
    t = THEMES[mode]
    rng = np.random.RandomState(8)
    n = 520
    ic = 0.03 + 0.33 * rng.standard_normal(n)
    x = np.arange(n)

    fig, axes = plt.subplots(2, 1, figsize=(7.4, 5.4), sharex=True,
                             gridspec_kw=dict(hspace=0.54))
    fig.patch.set_facecolor(t["surface"])

    # ---- top: the series itself, with its barely-visible mean
    ax = axes[0]
    style_axes(ax, t, ylabel="daily IC")
    ax.plot(x, ic, color=t["series"], linewidth=0.6, alpha=0.5, zorder=3)
    ax.axhline(0, color=t["baseline"], linewidth=0.9, zorder=2)
    ax.axhline(ic.mean(), color=t["ink"], linewidth=1.4, zorder=5)
    ax.set_ylim(-1.15, 1.15)
    ax.set_yticks([-1, -0.5, 0, 0.5, 1])
    ax.annotate("", xy=(n * 0.995, ic.mean()), xytext=(n * 0.995, 0.62),
                arrowprops=dict(arrowstyle="-|>", color=t["muted"], linewidth=1.0))
    ax.text(n * 0.975, 0.70, "mean IC $= 0.03$ — the entire edge",
            color=t["ink_secondary"], fontsize=8.4, ha="right", va="bottom")
    titles(ax, t, "IC keeps the time axis", "one value per day: a series, not a number")

    # ---- bottom: the same series squared -- noise folded upward
    ax = axes[1]
    style_axes(ax, t, ylabel="daily $R^2 = $ IC$^2$",
               xlabel="trading day")
    ax.fill_between(x, ic ** 2, color=t["series"], alpha=0.30, linewidth=0, zorder=3)
    ax.axhline(0, color=t["baseline"], linewidth=0.9, zorder=2)
    ax.axhline((ic ** 2).mean(), color=t["ink"], linewidth=1.4, zorder=5)
    ax.set_ylim(0, 1.15)
    ax.set_yticks([0, 0.5, 1])
    ax.text(n * 0.985, (ic ** 2).mean() + 0.07,
            "mean $R^2 \\approx 0.11$", color=t["ink"],
            fontsize=8.6, fontweight="600", ha="right", va="bottom")
    ax.text(n * 0.985, 0.80,
            "$0.109$ of it is Var(IC); only $0.0009$ is the edge",
            color=t["ink_secondary"], fontsize=8.4, ha="right", va="bottom")
    titles(ax, t, "Squaring folds the noise upward",
           "$R^2$ cannot be negative, so day-to-day scatter reappears as explained variance")

    save(fig, t, f"ic-series-vs-r2-{mode}.png")   # save() already crops tight

FIGURES = (prediction_shrinkage, ic_series_vs_r2)

if __name__ == "__main__":
    for mode in ("light", "dark"):
        for fn in FIGURES:
            fn(mode)
    print(f"wrote {2 * len(FIGURES)} figures for 09_ic_and_r_squared")
