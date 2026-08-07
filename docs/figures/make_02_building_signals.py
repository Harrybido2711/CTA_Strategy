"""Figures for docs/02-building-signals.md.

Run from anywhere:

    python docs/figures/make_02_building_signals.py

Writes light- and dark-mode PNGs into docs/figures/. The chapter references
them through a <picture> element so GitHub serves the variant matching the
reader's theme.

Figures produced
----------------
    binary-momentum      sign() maps two very different trends onto the same position
    scatter-ladder       what each correlation looks like, and which one you get
    alpha-opacity        what turning the marker opacity down does and does not buy
    bucket-chart         the core signal test: mean forward return per signal bucket
    reversal-buckets     expected monotone buckets vs the reversal-broken version
    signal-distribution  why fixed-interval cuts starve the tails, and what fixes it
    signal-kernels       MACD is momentum with a hump-shaped kernel, not a box

All are schematics drawn from illustrative values.

Formulas stay in the markdown as LaTeX rather than being rendered here: text in
an image is neither selectable nor searchable.
"""

import matplotlib.pyplot as plt
import numpy as np
from _style import THEMES, rounded_bar, save, style_axes, titles


# -------------------------------------------------- fig: what sign() discards
def binary_momentum(mode):
    """02 s1 -- sign() collapses trend strength; both assets get the same weight.

    Schematic. Two illustrative paths over one lookback window, ending at +20%
    and +10%. The right panel is the signal each produces: identical.
    """
    t = THEMES[mode]
    rng = np.random.RandomState(3)
    n = 120

    def path(total):
        steps = rng.standard_normal(n) * 0.007
        steps = steps - steps.mean() + np.log1p(total) / n
        return 100 * np.exp(np.concatenate([[0.0], np.cumsum(steps)]))

    strong, weak = path(0.20), path(0.10)
    x = np.arange(n + 1)
    c_strong, c_weak = t["ramp"][5], t["ramp"][2]

    fig, (ax, bx) = plt.subplots(
        1, 2, figsize=(7.8, 3.9), gridspec_kw=dict(width_ratios=[2.5, 1], wspace=0.34))
    fig.patch.set_facecolor(t["surface"])

    # ---- left: what actually happened over the lookback
    style_axes(ax, t, ylabel="rebased to 100", xlabel="lookback window $R_{s,t-1}$")
    for series, colour, label in ((strong, c_strong, "+20%"), (weak, c_weak, "+10%")):
        ax.plot(x, series, color=colour, linewidth=1.9, zorder=3)
        ax.text(n + 3, series[-1], label, color=t["ink"], fontsize=9.4,
                fontweight="600", ha="left", va="center")
    ax.set_xlim(0, n + 22)
    ax.set_xticks([])
    ax.set_ylim(94, 126)
    titles(ax, t, "Two different trends", "one is twice the other over the same window")

    # ---- right: what sign() says about them
    style_axes(bx, t, ylabel="$MOM_{s,t}$")
    for i, colour in enumerate((c_strong, c_weak)):
        rounded_bar(bx, i, 1.0, color=colour, width=0.42)
    bx.axhline(0, color=t["baseline"], linewidth=0.9, zorder=2)
    bx.set_xlim(-0.7, 1.7)
    bx.set_xticks([0, 1])
    bx.set_xticklabels(["+20%", "+10%"])
    bx.set_ylim(0, 1.5)
    bx.set_yticks([0, 1])
    bx.text(0.5, 1.20, "identical", color=t["ink"], fontsize=9.2,
            fontweight="600", ha="center", va="bottom")
    bx.annotate("", xy=(-0.05, 1.14), xytext=(1.05, 1.14),
                arrowprops=dict(arrowstyle="<->", color=t["muted"], linewidth=1.0))
    titles(bx, t, "One signal", "$\\mathrm{sign}(\\cdot)=+1$")

    save(fig, t, f"binary-momentum-{mode}.png")   # save() already crops tight

# ------------------------------ fig: what turning the opacity down buys you
def alpha_opacity(mode):
    """02 s3.1 -- alpha turns ink into density; whether density reads is another matter.

    Schematic. Left and right are the same 55,000 illustrative points at 12%
    correlation -- about what 37 ETFs over six years give you -- drawn opaque
    and at alpha=0.01. The middle panel is a different, invented dataset: what
    the fix looks like when it works, a corner thin enough to read.
    """
    t = THEMES[mode]
    rng = np.random.RandomState(23)
    n = 55000
    r = 0.12
    x = rng.standard_normal(n)
    y = r * x + (1 - r ** 2) ** 0.5 * rng.standard_normal(n)

    # a hypothetical book where a high signal rules out the worst losses: thin
    # the bottom-right corner smoothly, so it reads as data and not as a mask
    xs = rng.standard_normal(n)
    ys = r * xs + (1 - r ** 2) ** 0.5 * rng.standard_normal(n)
    carve = np.clip((xs + 0.3) / 1.8, 0, 1) * np.clip((-ys + 0.3) / 1.8, 0, 1)
    keep = rng.random_sample(n) > 0.97 * carve

    panels = (
        (x, y, 1.00, "alpha = 1", "the default — one solid mass", False),
        (xs[keep], ys[keep], 0.01, "alpha = 0.01, and it worked",
         "one corner thin enough to read", True),
        (x, y, 0.01, "alpha = 0.01, and it did not",
         "the same points — round, and untilted", False),
    )

    fig, axes = plt.subplots(1, 3, figsize=(11.0, 3.9), sharex=True, sharey=True,
                             gridspec_kw=dict(wspace=0.12))
    fig.patch.set_facecolor(t["surface"])

    for ax, (px, py, alpha, head, sub, mark) in zip(axes, panels):
        style_axes(ax, t, grid=False)
        ax.scatter(px, py, s=8.0, color=t["series"], alpha=alpha, linewidths=0, zorder=3)
        ax.set_xlim(-3.6, 3.6)
        ax.set_ylim(-3.6, 3.6)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.spines["bottom"].set_visible(False)
        ax.text(0, 1.13, head, transform=ax.transAxes, color=t["ink"],
                fontsize=10.2, fontweight="600", va="bottom")
        ax.text(0, 1.03, sub, transform=ax.transAxes, color=t["ink_secondary"],
                fontsize=8.5, va="bottom")
        if mark:
            ax.annotate("high signal, no\ndeep loss", xy=(2.0, -2.0), xytext=(-0.4, -3.3),
                        color=t["ink_secondary"], fontsize=8.4, ha="center",
                        arrowprops=dict(arrowstyle="-", color=t["muted"], linewidth=1.0,
                                        connectionstyle="arc3,rad=-0.25"))

    axes[0].set_ylabel("forward return", color=t["ink_secondary"], fontsize=9, labelpad=8)
    fig.text(0.5, 0.01, "signal value", ha="center", color=t["muted"], fontsize=8.5)
    fig.text(0.5, -0.09,
             "Illustrative. Outer panels are one dataset of 55,000 asset-dates at 12% correlation, "
             "differing only in opacity. The middle is a different, invented book — what success "
             "would look like, and it would be a result.",
             ha="center", color=t["ink_secondary"], fontsize=8.6)
    save(fig, t, f"alpha-opacity-{mode}.png")


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

# ----------------------- fig: the calibration ladder, and where reality sits
def scatter_ladder(mode):
    """02 s2 -- what each correlation looks like; the eye's floor is ~30%.

    Schematic. The same 1,500 illustrative points redrawn at four correlations,
    so the panels differ only in the quantity being demonstrated. The leftmost
    is the picture you had in mind; the rightmost is what the data returns.
    """
    t = THEMES[mode]
    rng = np.random.RandomState(11)
    n = 1500
    x = rng.standard_normal(n)
    e = rng.standard_normal(n)

    panels = [
        (0.80, "what you pictured", False),
        (0.45, "convincing", False),
        (0.30, "the eye's floor", False),
        (0.12, "what you observe", True),
    ]

    fig, axes = plt.subplots(1, 4, figsize=(9.6, 3.1), sharex=True, sharey=True,
                             gridspec_kw=dict(wspace=0.16))
    fig.patch.set_facecolor(t["surface"])

    for ax, (r, verdict, live) in zip(axes, panels):
        style_axes(ax, t, grid=False)
        y = r * x + (1 - r ** 2) ** 0.5 * e
        ax.scatter(x, y, s=3.2, color=t["series"], alpha=0.16, linewidths=0, zorder=3)
        ax.set_xlim(-3.6, 3.6)
        ax.set_ylim(-3.6, 3.6)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.spines["bottom"].set_visible(False)
        ax.text(0, 1.15, f"corr = {int(r * 100)}%", transform=ax.transAxes,
                color=t["ink"], fontsize=10.4, fontweight="600", va="bottom")
        ax.text(0, 1.04, verdict, transform=ax.transAxes,
                color=t["ink"] if live else t["muted"],
                fontsize=8.8, fontweight="600" if live else "normal", va="bottom")
        # underscore the panel the reader will actually meet
        if live:
            ax.plot([0, 0.62], [1.005, 1.005], transform=ax.transAxes,
                    color=t["series"], linewidth=1.6, solid_capstyle="butt",
                    clip_on=False, zorder=5)

    axes[0].set_ylabel("forward return", color=t["ink_secondary"], fontsize=9, labelpad=8)
    fig.text(0.5, 0.01, "signal value", ha="center", color=t["muted"], fontsize=8.5)
    fig.text(0.5, -0.09,
             "Illustrative. Every panel holds a real relationship — only the first two are "
             "strong enough for the eye to find it.",
             ha="center", color=t["ink_secondary"], fontsize=8.6)
    save(fig, t, f"scatter-ladder-{mode}.png")   # save() already crops tight


FIGURES = (binary_momentum, scatter_ladder, alpha_opacity, bucket_chart, reversal_buckets,
           signal_distribution, signal_kernels)

if __name__ == "__main__":
    for mode in ("light", "dark"):
        for fn in FIGURES:
            fn(mode)
    print(f"wrote {2 * len(FIGURES)} figures for 02-building-signals.md")
