"""Generate the diagrams used in docs/.

Run from anywhere:

    python docs/figures/make_figures.py

Writes light- and dark-mode PNGs into docs/figures/. The chapters reference them
through a <picture> element so GitHub serves the variant matching the reader's theme.

Figures produced
----------------
strategy-pipeline     00-pipeline  which stages are the strategy and which only measure it
levels-vs-rebased     01 § 1  raw closes vs rebased: SPY looks highest, GLD returned more
payoff-asymmetry      01 § 2  a static long's loss is floored at zero; a short's is not
prediction-shrinkage  08 § 2  a low-R2 model predicts a far narrower range than reality
ic-series-vs-r2       08 § 2  squaring a noisy IC series manufactures explained variance
signal-kernels        02 § 10 MACD is momentum with a hump-shaped kernel, not a box
bucket-chart          02 § 4  the core signal test: mean forward return per signal bucket
reversal-buckets      02 § 5  expected monotone buckets vs the reversal-broken version
signal-distribution   02 § 7  why fixed-interval cuts starve the tails, and what fixes it
overlap-tranches      03      the five overlapping 1/5 tranches of a 5-day hold
param-heatmap         06 § 4  a plateau (real edge) vs a spike (artifact)

All are schematics drawn from illustrative values except levels-vs-rebased, which
reads CTA_data/ because its claim is about this dataset rather than about a shape.

Formulas stay in the markdown as LaTeX rather than being rendered here: text in an
image is neither selectable nor searchable.

All figures follow one spec — single-hue marks, rounded data-ends squared at the
baseline, hairline recessive gridlines, labels in ink tokens (never the series
colour), and light/dark variants stepped for their own surface rather than flipped.
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyBboxPatch, PathPatch
from matplotlib.path import Path as MplPath

OUT = Path(__file__).resolve().parent
DATA = Path(__file__).resolve().parents[2] / "CTA_data"

# ---------------------------------------------------------------- design tokens
THEMES = {
    "light": dict(
        surface="#fcfcfb",
        ink="#0b0b0b",
        ink_secondary="#52514e",
        muted="#898781",
        grid="#e1e0d9",
        baseline="#c3c2b7",
        series="#2a78d6",
        wash="#2a78d6",
        # sequential blue ramp, steps 100 -> 700; lightest = near zero
        ramp=["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"],
    ),
    "dark": dict(
        surface="#1a1a19",
        ink="#ffffff",
        ink_secondary="#c3c2b7",
        muted="#898781",
        grid="#2c2c2a",
        baseline="#383835",
        series="#3987e5",
        wash="#3987e5",
        # on a dark surface "near zero" must recede toward the surface, so the
        # same single hue runs dark -> light instead of light -> dark
        ramp=["#0d366b", "#184f95", "#256abf", "#3987e5", "#6da7ec", "#9ec5f4", "#cde2fb"],
    ),
}

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
    "mathtext.fontset": "dejavusans",
    "axes.linewidth": 0.8,
    "figure.dpi": 200,
    "savefig.dpi": 200,
})


# ------------------------------------------------------------------- primitives
def rounded_bar(ax, x, height, base=0.0, width=0.30, color="#2a78d6", zorder=3):
    """A column with a rounded data-end and a square baseline end.

    bar() gives square corners and FancyBboxPatch rounds all four, so the path is
    built by hand: straight at the baseline, arced at the tip.
    """
    x0, x1 = x - width / 2, x + width / 2
    tip = base + height
    s = 1.0 if height >= 0 else -1.0
    r = min(abs(height) * 0.22, width * 0.30) * s
    k = width * 0.30

    verts = [(x0, base), (x0, tip - r),
             (x0, tip), (x0 + k, tip),
             (x1 - k, tip),
             (x1, tip), (x1, tip - r),
             (x1, base), (x0, base)]
    codes = [MplPath.MOVETO, MplPath.LINETO,
             MplPath.CURVE3, MplPath.CURVE3,
             MplPath.LINETO,
             MplPath.CURVE3, MplPath.CURVE3,
             MplPath.LINETO, MplPath.CLOSEPOLY]
    ax.add_patch(PathPatch(MplPath(verts, codes), facecolor=color,
                           edgecolor="none", zorder=zorder))


def style_axes(ax, t, ylabel=None, xlabel=None, grid=True):
    ax.set_facecolor(t["surface"])
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(t["baseline"])
    ax.tick_params(colors=t["muted"], length=0, labelsize=8.5)
    if grid:
        ax.yaxis.grid(True, color=t["grid"], linewidth=0.8, linestyle="-", zorder=0)
    ax.set_axisbelow(True)
    if ylabel:
        ax.set_ylabel(ylabel, color=t["ink_secondary"], fontsize=9, labelpad=8)
    if xlabel:
        ax.set_xlabel(xlabel, color=t["muted"], fontsize=8.5, labelpad=7)


def titles(ax, t, title, subtitle):
    """Title and subtitle as stacked axes-space text, so they never collide."""
    ax.text(0, 1.145, title, transform=ax.transAxes,
            color=t["ink"], fontsize=11.5, fontweight="600", va="bottom")
    ax.text(0, 1.045, subtitle, transform=ax.transAxes,
            color=t["ink_secondary"], fontsize=8.8, va="bottom")


def save(fig, t, name):
    fig.savefig(OUT / name, facecolor=t["surface"], bbox_inches="tight", pad_inches=0.28)
    plt.close(fig)


# ----------------------------------------------------- fig: the bucket bar chart
def bucket_chart(mode):
    t = THEMES[mode]
    labels = ["G1", "G2", "G3", "G4", "G5"]
    vals = np.array([-1.1, -0.4, 0.3, 1.1, 2.0])   # illustrative; the shape is the point
    err = np.array([0.30, 0.25, 0.24, 0.26, 0.33])

    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    fig.patch.set_facecolor(t["surface"])
    style_axes(ax, t, ylabel="mean forward return (%)",
               xlabel="signal bucket   (low $\\rightarrow$ high)")

    for i, v in enumerate(vals):
        rounded_bar(ax, i, v, color=t["series"])
    ax.errorbar(range(len(vals)), vals, yerr=err, fmt="none", ecolor=t["muted"],
                elinewidth=1.1, capsize=3, capthick=1.1, zorder=4)
    ax.axhline(0, color=t["baseline"], linewidth=0.9, zorder=2)

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels)
    ax.set_xlim(-0.7, 4.9)
    ax.set_ylim(-1.9, 3.0)

    # the long/short spread is what the chart prices — label it, and only it
    ax.annotate("", xy=(4.55, vals[4]), xytext=(4.55, vals[0]),
                arrowprops=dict(arrowstyle="<->", color=t["muted"], linewidth=1.0))
    ax.text(4.42, (vals[0] + vals[4]) / 2, "long/short\nspread ≈ 3.1%",
            color=t["ink_secondary"], fontsize=8.6, ha="right", va="center")

    titles(ax, t, "Sorted into buckets, the signal shows itself",
           "monotone G1 $\\rightarrow$ G5 is the test — not the height of any single bar")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    save(fig, t, f"bucket-chart-{mode}.png")


# ---------------------------------------------------------------- fig: reversal
def reversal_buckets(mode):
    t = THEMES[mode]
    labels = ["G1", "G2", "G3", "G4", "G5"]
    expected = np.array([-1.1, -0.4, 0.3, 1.1, 2.0])
    observed = np.array([1.4, -0.5, 0.2, 1.0, 2.0])
    err = np.array([0.34, 0.28, 0.26, 0.28, 0.36])

    fig, axes = plt.subplots(1, 2, figsize=(9.4, 4.2), sharey=True)
    fig.patch.set_facecolor(t["surface"])

    panels = [(expected, "Expected", "monotone staircase — the signal ranks correctly"),
              (observed, "Observed", "G1 lifts — the worst losers rebound")]

    for ax, (vals, title, subtitle) in zip(axes, panels):
        style_axes(ax, t,
                   ylabel="mean forward return (%)" if ax is axes[0] else None,
                   xlabel="signal bucket   (low $\\rightarrow$ high)")
        for i, v in enumerate(vals):
            rounded_bar(ax, i, v, color=t["series"])
        ax.errorbar(range(len(vals)), vals, yerr=err, fmt="none", ecolor=t["muted"],
                    elinewidth=1.1, capsize=3, capthick=1.1, zorder=4)
        ax.axhline(0, color=t["baseline"], linewidth=0.9, zorder=2)
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels)
        ax.set_xlim(-0.65, 4.65)
        ax.set_ylim(-2.0, 3.0)
        titles(ax, t, title, subtitle)

    # call the broken bucket out with a leader line rather than a second colour
    axes[1].annotate("reversal", xy=(0.30, 1.50), xytext=(1.30, 2.55),
                     color=t["ink_secondary"], fontsize=9,
                     arrowprops=dict(arrowstyle="-", color=t["muted"], linewidth=1.0,
                                     connectionstyle="arc3,rad=-0.25"))

    fig.tight_layout(rect=(0, 0, 1, 0.94))
    save(fig, t, f"reversal-buckets-{mode}.png")


# ------------------------------------------- fig: why fixed intervals starve tails
def signal_distribution(mode):
    t = THEMES[mode]
    x = np.linspace(-3.4, 3.4, 600)
    y = np.exp(-x ** 2 / 2) / np.sqrt(2 * np.pi)

    fig, axes = plt.subplots(1, 2, figsize=(9.4, 4.1), sharey=True)
    fig.patch.set_facecolor(t["surface"])

    fixed_cuts = [-2, -1, 0, 1, 2]
    q = 0.8416  # quintile boundaries of a standard normal
    quant_cuts = [-2 * q, -q, 0, q, 2 * q]

    panels = [
        (fixed_cuts, "Fixed intervals", "the tails you actually trade are nearly empty",
         ["n=12", "n=340", "n=1,290", "n=1,290", "n=331", "n=11"]),
        (quant_cuts, "Rolling quantile", "equal-sized groups, and no look-ahead",
         ["", "n=635", "n=635", "n=635", "n=635", ""]),
    ]

    for ax, (cuts, title, subtitle, counts) in zip(axes, panels):
        style_axes(ax, t, ylabel="density" if ax is axes[0] else None,
                   xlabel="standardized signal   (σ)", grid=False)
        ax.plot(x, y, color=t["series"], linewidth=2.0, solid_capstyle="round", zorder=3)
        ax.fill_between(x, y, color=t["wash"], alpha=0.10, zorder=2)
        for c in cuts:
            ax.axvline(c, color=t["grid"], linewidth=1.0, zorder=1)

        edges = [-3.4] + list(cuts) + [3.4]
        for (lo, hi), label in zip(zip(edges, edges[1:]), counts):
            if label:
                ax.text((lo + hi) / 2, 0.435, label, ha="center", va="bottom",
                        color=t["ink_secondary"], fontsize=8.0)

        ax.set_ylim(0, 0.50)
        ax.set_xlim(-3.4, 3.4)
        ax.set_yticks([])
        titles(ax, t, title, subtitle)

    fig.tight_layout(rect=(0, 0, 1, 0.94))
    save(fig, t, f"signal-distribution-{mode}.png")


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
        style_axes(ax, t, grid=False)
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


# --------------------------------------------------- fig: momentum vs MACD kernel
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
    style_axes(ax, t, ylabel="weight on that day's return",
               xlabel="lag (trading days ago)")

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


# ------------------------------------------------- fig: the strategy pipeline
def strategy_pipeline(mode):
    """00-pipeline -- the two ways a signal gets made, and what validates it.

    Schematic. The point is that a rule and an ML model are alternative ways
    of producing the same object -- a signal -- and that the backtest sits
    downstream of both, validating the whole strategy rather than the model.
    """
    t = THEMES[mode]
    W, H = 4.6, 0.56                    # shared-spine box size
    BW = 3.5                            # branch box width
    CX, LX, RX = 4.7, 2.15, 7.25        # centre, left-branch, right-branch

    #  (x, y, w, label, sublabel, kind)
    nodes = [
        (CX, 6.0, W,  "market data / features", "prices, volume, volatility", "input"),
        (LX, 4.9, BW, "rule", "momentum, MACD", "strat"),
        (RX, 4.9, BW, "ML model", "OLS, ridge, lasso, trees", "strat"),
        (RX, 3.8, BW, "prediction", "return, P(up), volatility", "strat"),
        (CX, 2.7, W,  "signal", "long / short / flat", "strat"),
        (CX, 1.6, W,  "position", "how much to bet, and risk limits", "strat"),
        (CX, 0.5, W,  "backtest", "costs, delay, turnover, execution", "instr"),
        (CX, -0.6, W, "return · Sharpe · drawdown · turnover", "", "instr"),
    ]
    edges = [(0, 1, None), (0, 2, None), (1, 4, "sign / threshold"),
             (2, 3, None), (3, 4, "trading rule"), (4, 5, None),
             (5, 6, None), (6, 7, None)]

    fig, ax = plt.subplots(figsize=(9.0, 6.6))
    fig.patch.set_facecolor(t["surface"])
    ax.set_facecolor(t["surface"])
    ax.set_xlim(0, 9.6)
    ax.set_ylim(-1.25, 6.6)
    ax.axis("off")

    face = {"input": None, "strat": t["ramp"][5], "instr": t["ramp"][1]}
    for x, y, w, label, sub, kind in nodes:
        if kind == "input":
            style = dict(facecolor=t["surface"], edgecolor=t["baseline"], linewidth=1.1)
            ink, subink = t["ink_secondary"], t["muted"]
        else:
            style = dict(facecolor=face[kind], edgecolor="none")
            ink = t["surface"] if kind == "strat" else t["ink"]
            subink = ink
        ax.add_patch(FancyBboxPatch(
            (x - w / 2, y - H / 2), w, H,
            boxstyle="round,pad=0.02,rounding_size=0.15", zorder=3, **style))
        dy = 0.10 if sub else 0.0
        ax.text(x, y + dy, label, ha="center", va="center",
                color=ink, fontsize=9.8, fontweight="600", zorder=4)
        if sub:
            ax.text(x, y - 0.145, sub, ha="center", va="center",
                    color=subink, fontsize=7.8, alpha=0.85, zorder=4)

    for a, b, note in edges:
        xa, ya, _, _, _, _ = nodes[a]
        xb, yb, _, _, _, _ = nodes[b]
        ax.annotate("", xy=(xb, yb + H / 2 + 0.02), xytext=(xa, ya - H / 2 - 0.02),
                    arrowprops=dict(arrowstyle="-|>", color=t["baseline"], linewidth=1.1,
                                    shrinkA=0, shrinkB=0,
                                    connectionstyle="arc3,rad=0"))
        if note:
            ax.text((xa + xb) / 2 + (0.30 if xb < xa else -0.30),
                    (ya + yb) / 2, note, ha="center", va="center",
                    color=t["ink_secondary"], fontsize=7.6, rotation=0,
                    bbox=dict(boxstyle="round,pad=0.18", facecolor=t["surface"],
                              edgecolor="none"), zorder=5)

    # the correction this figure exists to make
    ax.text(9.5, 2.7, "both paths end here —\nML replaces the rule,\nnot the backtest",
            ha="right", va="center", color=t["ramp"][5], fontsize=8.4,
            fontweight="600", linespacing=1.5)
    ax.annotate("", xy=(CX + W / 2 + 0.05, 2.7), xytext=(7.5, 2.7),
                arrowprops=dict(arrowstyle="-", color=t["baseline"], linewidth=0.9))

    ax.plot([0.42, 0.30, 0.30, 0.42], [5.2, 5.2, 1.32, 1.32],
            color=t["ramp"][5], linewidth=1.1, solid_joinstyle="miter", zorder=3)
    ax.text(0.14, 3.26, "the strategy", ha="center", va="center", rotation=90,
            color=t["ramp"][5], fontsize=8.8, fontweight="600")
    ax.plot([0.42, 0.30, 0.30, 0.42], [0.78, 0.78, -0.88, -0.88],
            color=t["muted"], linewidth=1.1, solid_joinstyle="miter", zorder=3)
    ax.text(0.14, -0.05, "validation", ha="center", va="center", rotation=90,
            color=t["muted"], fontsize=8.8, fontweight="600")

    titles(ax, t, "Two ways to make a signal, one way to validate it",
           "a rule and a model are alternatives; the backtest is downstream of both")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    save(fig, t, f"strategy-pipeline-{mode}.png")


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
        style_axes(ax, t, ylabel=f"close ({unit})" if unit else "index (start = 100)")
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


FIGURES = (bucket_chart, reversal_buckets, signal_distribution,
           overlap_tranches, param_heatmap, payoff_asymmetry,
           levels_vs_rebased, strategy_pipeline, signal_kernels,
           prediction_shrinkage, ic_series_vs_r2)

if __name__ == "__main__":
    for mode in ("light", "dark"):
        for fn in FIGURES:
            fn(mode)
    print(f"wrote {len(list(OUT.glob('*.png')))} figures to {OUT}")
