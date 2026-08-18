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
    bucket-construction  draw five, rank them, repeat, average — where the bars come from
    noise-shrinks        why the bucket count m is the method, not a detail
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


# --------------------- fig: how the bar chart is built, and why averaging is
def bucket_construction(mode):
    """02 s3.2 -- draw five, rank them, repeat, average — on a line and on a cloud.

    Schematic. Top row: a perfect relationship, where every draw of five comes
    out ordered. Bottom row: the real 12%-correlation cloud, where each draw is
    tangled and the order survives only in the average of 400 of them. Every
    drawn point is the same colour: any five will do, and no draw is special.
    """
    t = THEMES[mode]
    rng = np.random.RandomState(9)
    n, shown, total = 4000, 6, 400

    lx = rng.uniform(0, 10, n)
    ly = lx.copy()                                   # perfect: return is the signal
    cx = rng.standard_normal(n)
    cy = 0.12 * cx + (1 - 0.12 ** 2) ** 0.5 * rng.standard_normal(n)

    def slots(px, py, k):
        """k draws of five, each sorted by signal into rank slots G1..G5"""
        idx = rng.randint(0, len(px), size=(k, 5))
        order = np.argsort(px[idx], axis=1)
        return np.take_along_axis(py[idx], order, axis=1), idx

    rows = (
        (lx, ly, "If the relationship were perfect", "any five points, taken at random",
         "every draw comes out ordered"),
        (cx, cy, "On the real cloud", "any five points, taken at random",
         "every draw comes back tangled"),
    )

    fig, axes = plt.subplots(2, 3, figsize=(10.6, 6.6),
                             gridspec_kw=dict(wspace=0.30, hspace=0.58))
    fig.patch.set_facecolor(t["surface"])

    for (px, py, head, sub, mid_sub), (ax, bx, cxx) in zip(rows, axes):
        ranked, idx = slots(px, py, shown)
        picked = idx[:3].ravel()                     # three draws' worth, one colour

        # ---- where the points come from
        style_axes(ax, t, ylabel="return", xlabel="$MOM$", grid=False)
        ax.scatter(px, py, s=3.0, color=t["series"], alpha=0.10, linewidths=0, zorder=2)
        ax.scatter(px[picked], py[picked], s=34, color=t["series"], zorder=4)
        ax.set_xticks([])
        ax.set_yticks([])
        titles(ax, t, head, sub)

        # ---- each draw, at the rank slot its five points fell into
        style_axes(bx, t, ylabel="return", xlabel="rank slot", grid=False)
        for row in ranked:
            bx.plot(range(5), row, color=t["series"], alpha=0.42, linewidth=1.1,
                    marker="o", markersize=4.6, zorder=4)
        bx.set_xticks(range(5))
        bx.set_xticklabels(["G1", "G2", "G3", "G4", "G5"])
        bx.set_yticks([])
        titles(bx, t, f"{shown} draws, ranked", mid_sub)

        # ---- and the average of many, with the error on it
        allr, _ = slots(px, py, total)
        means, errs = allr.mean(axis=0), allr.std(axis=0) / total ** 0.5
        style_axes(cxx, t, ylabel="mean return", xlabel="signal bucket")
        for i, v in enumerate(means):
            rounded_bar(cxx, i, v, color=t["series"], width=0.34)
        cxx.errorbar(range(5), means, yerr=errs, fmt="none", ecolor=t["muted"],
                     elinewidth=1.1, capsize=3, capthick=1.1, zorder=5)
        cxx.axhline(0, color=t["baseline"], linewidth=0.9, zorder=2)
        lo, hi = (means - errs).min(), (means + errs).max()
        pad = 0.16 * (hi - lo)
        cxx.set_ylim(min(0, lo) - pad, hi + pad)
        cxx.set_xlim(-0.6, 4.6)
        cxx.set_xticks(range(5))
        cxx.set_xticklabels(["G1", "G2", "G3", "G4", "G5"])
        cxx.set_yticks([])
        titles(cxx, t, f"{total} draws, averaged", "bars with their error bars")

    fig.text(0.5, -0.03,
             "Illustrative. Each row is scaled to its own height — the real staircase has the shape "
             "of the perfect one and a small fraction of the rise.",
             ha="center", color=t["ink_secondary"], fontsize=8.8)
    save(fig, t, f"bucket-construction-{mode}.png")


# ------------------ fig: the staircase is an estimate, and m is what sharpens it
def noise_shrinks(mode):
    """02 s3.2 -- the same buckets at m = 5, 30, 300 and 3,000 observations each.

    Schematic, but the numbers are the chapter's. Population is 12%-correlated
    with a 120 bp return standard deviation, so the true bucket means sit at
    roughly -20, -8, 0, +8 and +20 bp in every panel and only the error on them
    changes: 119 bp over root m, which is 53, 22, 6.9 and 2.2 bp.
    """
    t = THEMES[mode]
    rng = np.random.RandomState(17)
    rho, sig = 0.12, 120.0

    fig, axes = plt.subplots(1, 4, figsize=(11.4, 3.5), sharey=True,
                             gridspec_kw=dict(wspace=0.14))
    fig.patch.set_facecolor(t["surface"])

    for ax, m in zip(axes, (5, 30, 300, 3000)):
        x = rng.standard_normal(5 * m)
        y = sig * (rho * x + (1 - rho ** 2) ** 0.5 * rng.standard_normal(5 * m))
        order = np.argsort(x)
        groups = y[order].reshape(5, m)
        means, errs = groups.mean(axis=1), groups.std(axis=1) / m ** 0.5

        style_axes(ax, t, ylabel="mean forward return (bp)" if ax is axes[0] else None)
        for i, v in enumerate(means):
            rounded_bar(ax, i, v, color=t["series"], width=0.34)
        ax.errorbar(range(5), means, yerr=errs, fmt="none", ecolor=t["muted"],
                    elinewidth=1.1, capsize=3, capthick=1.1, zorder=5)
        ax.axhline(0, color=t["baseline"], linewidth=0.9, zorder=2)
        ax.set_xlim(-0.62, 4.62)
        ax.set_ylim(-95, 95)
        ax.set_xticks(range(5))
        ax.set_xticklabels(["G1", "G2", "G3", "G4", "G5"], fontsize=7.6)
        ax.text(0, 1.14, f"m = {m:,}", transform=ax.transAxes, color=t["ink"],
                fontsize=10.2, fontweight="600", va="bottom")
        sem = 119 / m ** 0.5
        ax.text(0, 1.03, f"noise ± {sem:.1f} bp" if sem < 10 else f"noise ± {sem:.0f} bp",
                transform=ax.transAxes, color=t["ink_secondary"], fontsize=8.5, va="bottom")

    fig.text(0.5, -0.10,
             "Illustrative. The true bucket means are the same in all four panels — near −20 bp at "
             "G1 and +20 bp at G5. Only the error on the estimate changes, and it changes as the "
             "square root of m.",
             ha="center", color=t["ink_secondary"], fontsize=8.6)
    save(fig, t, f"noise-shrinks-{mode}.png")


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


FIGURES = (binary_momentum, scatter_ladder, alpha_opacity, bucket_construction, noise_shrinks,
           signal_distribution, signal_kernels)

if __name__ == "__main__":
    for mode in ("light", "dark"):
        for fn in FIGURES:
            fn(mode)
    print(f"wrote {2 * len(FIGURES)} figures for 02-building-signals.md")
