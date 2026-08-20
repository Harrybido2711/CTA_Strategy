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
    three-bucketings     one dataset cut three ways, and what each cut distorts
    signal-distribution  why fixed-interval cuts starve the tails, and what fixes it
    bucket-time-collapse     every date gives one draw; pooling them spends the t axis
    signal-return-alignment  the lookback, the discarded gap, and the paired return

All are schematics drawn from illustrative values.

Formulas stay in the markdown as LaTeX rather than being rendered here: text in
an image is neither selectable nor searchable.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, Polygon
from _style import THEMES, rounded_bar, save, style_axes, titles


# -------------------------------------------------- fig: what sign() discards
def binary_momentum(mode):
    """02 s1 -- sign() collapses trend strength; both windows get the same weight.

    Schematic. One asset over two illustrative lookback windows, ending at +20%
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
    style_axes(ax, t, ylabel="price, rebased to 100",
               xlabel="the lookback window, day 0 to day N")
    for series, colour, label in ((strong, c_strong, "+20%"), (weak, c_weak, "+10%")):
        ax.plot(x, series, color=colour, linewidth=1.9, zorder=3)
        ax.text(n + 3, series[-1], label, color=t["ink"], fontsize=9.4,
                fontweight="600", ha="left", va="center")
    ax.set_xlim(0, n + 22)
    ax.set_xticks([])
    ax.set_ylim(94, 126)
    titles(ax, t, "Two lookback windows", "one trend is twice the other")

    # ---- right: what sign() says about them
    style_axes(bx, t, ylabel="signal $MOM_{s,t}$", xlabel="which window")
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

    Schematic. Left and right are the same 5,000 illustrative points at 12%
    correlation -- asset-date cells pooled across the panel --
    drawn opaque and at a low opacity. The middle panel is a different,
    invented series: what the fix looks like when it works, a corner thin
    enough to read.
    """
    t = THEMES[mode]
    rng = np.random.RandomState(23)
    n = 5000
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

    axes[0].set_ylabel("forward return $r_{s,t}$   (σ)", color=t["ink_secondary"],
                       fontsize=9, labelpad=8)
    fig.text(0.5, 0.01, "signal $MOM_{s,t}$   (σ)", ha="center", color=t["muted"], fontsize=8.5)
    fig.text(0.5, -0.09,
             "Illustrative. Outer panels are 5,000 pooled asset-date observations at 12% "
             "correlation, differing only in opacity. The middle is a different, invented series — "
             "what success would look like, and it would be a result.",
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
        """k dates of five assets, each sorted by signal into rank slots G1..G5"""
        idx = rng.randint(0, len(px), size=(k, 5))
        order = np.argsort(px[idx], axis=1)
        return np.take_along_axis(py[idx], order, axis=1), idx

    rows = (
        (lx, ly, "If the relationship were perfect", "one date's five assets",
         "every date comes out ordered"),
        (cx, cy, "On the real cloud", "one date's five assets",
         "every date comes back tangled"),
    )

    fig, axes = plt.subplots(2, 3, figsize=(10.6, 6.6),
                             gridspec_kw=dict(wspace=0.30, hspace=0.58))
    fig.patch.set_facecolor(t["surface"])

    for (px, py, head, sub, mid_sub), (ax, bx, cxx) in zip(rows, axes):
        ranked, idx = slots(px, py, shown)
        picked = idx[:3].ravel()                     # three dates' worth, one colour

        # ---- where the points come from
        style_axes(ax, t, ylabel="forward return $r_{s,t}$",
                   xlabel="signal $MOM_{s,t}$", grid=False)
        ax.scatter(px, py, s=3.0, color=t["series"], alpha=0.10, linewidths=0, zorder=2)
        ax.scatter(px[picked], py[picked], s=34, color=t["series"], zorder=4)
        ax.set_xticks([])
        ax.set_yticks([])
        titles(ax, t, head, sub)

        # ---- each draw, at the rank slot its five points fell into
        style_axes(bx, t, ylabel="forward return $r_{s,t}$",
                   xlabel="rank slot (G1 = lowest signal)", grid=False)
        for row in ranked:
            bx.plot(range(5), row, color=t["series"], alpha=0.42, linewidth=1.1,
                    marker="o", markersize=4.6, zorder=4)
        bx.set_xticks(range(5))
        bx.set_xticklabels(["G1", "G2", "G3", "G4", "G5"])
        bx.set_yticks([])
        titles(bx, t, f"{shown} dates, ranked", mid_sub)

        # ---- and the average of many, with the error on it
        allr, _ = slots(px, py, total)
        means, errs = allr.mean(axis=0), allr.std(axis=0) / total ** 0.5
        style_axes(cxx, t, ylabel="mean forward return $r_{s,t}$",
                   xlabel="signal bucket ($MOM$)")
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
        titles(cxx, t, f"{total} dates, averaged", "bars with their error bars")

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

        style_axes(ax, t, ylabel="mean forward return (bp)" if ax is axes[0] else None,
                   xlabel="signal bucket ($MOM$)")
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


# ------------------- fig: one dataset, three ways of cutting it into buckets
def three_bucketings(mode):
    """02 s5 -- raw, standardized-at-fixed-intervals, and cross-sectional quantile.

    Schematic. A simulated panel of 20 assets over 1,500 days. Every asset
    carries the same risk-adjusted edge and its own volatility level, which
    doubles on a date of its own. Only the bucketing differs between panels:
    bar heights are mean forward return in bp on a shared scale, n is the count
    behind each bar, and the second line is the share of that bucket drawn from
    the top quartile of contemporaneous volatility -- 25% if the cut is
    vol-neutral.
    """
    t = THEMES[mode]
    rng = np.random.RandomState(12)
    A, T, W, rho = 20, 1500, 250, 0.12

    base = np.exp(rng.uniform(-1.0, 1.0, A))                   # each asset's own vol level
    jump = rng.randint(W, T, A)                                # ... which doubles, on its own date
    vol = base[None, :] * np.where(np.arange(T)[:, None] >= jump[None, :], 2.0, 1.0)

    z = rng.standard_normal((T, A))                            # the risk-adjusted signal
    fwd = 100 * vol * (rho * z + (1 - rho ** 2) ** 0.5 * rng.standard_normal((T, A)))
    raw = z * vol                                              # what you measure before scaling

    sig = np.full((T, A), np.nan)                              # trailing vol, data before t only
    for i in range(W, T):
        sig[i] = raw[i] / raw[i - W:i].std(axis=0)

    xs = np.full((T, A), np.nan)                               # rank within that date's peers
    for i in range(W, T):
        xs[i] = sig[i].argsort().argsort() / (A - 1.0)

    usable = np.zeros((T, A), bool)                            # same cells in all three panels
    usable[W:] = True
    hivol = vol >= np.quantile(vol[usable], 0.75)              # base rate 25% by construction

    def bars(key, edges=None):
        k, y, v = key.ravel(), fwd.ravel(), hivol.ravel()
        ok = ~np.isnan(k) & usable.ravel()
        k, y, v = k[ok], y[ok], v[ok]
        cuts = np.quantile(k, [0.2, 0.4, 0.6, 0.8]) if edges is None else edges
        g = np.digitize(k, cuts)
        m = np.array([y[g == j].mean() if (g == j).sum() else np.nan for j in range(5)])
        e = np.array([y[g == j].std() / max((g == j).sum(), 1) ** 0.5 for j in range(5)])
        n = np.array([(g == j).sum() for j in range(5)])
        share = np.array([100 * v[g == j].mean() if (g == j).sum() else np.nan for j in range(5)])
        return m, e, n, share

    panels = (
        (bars(raw), "Raw values", "cut at the pooled quintiles of raw momentum"),
        (bars(sig, edges=np.array([-2.0, -1.0, 1.0, 2.0])), "Standardized, fixed intervals",
         "divided by trailing vol, then cut at ±1 and ±2"),
        (bars(xs), "Cross-sectional quantile",
         "ranked against that day's peers, then cut at the quintiles"),
    )

    fig, axes = plt.subplots(1, 3, figsize=(11.2, 4.3), sharey=True,
                             gridspec_kw=dict(wspace=0.12))
    fig.patch.set_facecolor(t["surface"])

    for ax, ((m, e, n, share), head, sub) in zip(axes, panels):
        style_axes(ax, t, ylabel="mean forward return (bp)" if ax is axes[0] else None,
                   xlabel="signal bucket ($MOM$)")
        for i, v in enumerate(m):
            if not np.isnan(v):
                rounded_bar(ax, i, v, color=t["series"], width=0.34)
        ax.errorbar(range(5), m, yerr=e, fmt="none", ecolor=t["muted"],
                    elinewidth=1.1, capsize=3, capthick=1.1, zorder=5)
        ax.axhline(0, color=t["baseline"], linewidth=0.9, zorder=2)
        ax.set_xlim(-0.6, 4.6)
        ax.set_ylim(-100, 52)
        ax.set_xticks(range(5))
        ax.set_xticklabels(["G1", "G2", "G3", "G4", "G5"], fontsize=8)
        for i, (c, sh) in enumerate(zip(n, share)):
            ax.text(i, -78, f"n={c:,}", ha="center", color=t["muted"], fontsize=7.2)
            ax.text(i, -90, f"{sh:.0f}%", ha="center", color=t["muted"], fontsize=7.2)
        titles(ax, t, head, sub)

    fig.text(0.5, -0.06,
             "Illustrative. 20 assets over 1,500 days, each carrying the same risk-adjusted edge and "
             "its own volatility level, with identical cells in all three panels — only the cut "
             "differs.\nUnder each bar: how many observations it holds, and what share of them came "
             "from the top quartile of volatility (25% if the cut is vol-neutral).",
             ha="center", color=t["ink_secondary"], fontsize=8.6)
    save(fig, t, f"three-bucketings-{mode}.png")


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
        (quant_cuts, "Cross-sectional quantile", "equal-sized groups, and no look-ahead",
         ["", "n=635", "n=635", "n=635", "n=635", ""]),
    ]

    for ax, (cuts, title, subtitle, counts) in zip(axes, panels):
        style_axes(ax, t, ylabel="density" if ax is axes[0] else None,
                   xlabel="standardized signal $MOM_{s,t}$   (σ)", grid=False)
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

    axes[0].set_ylabel("forward return $r_{s,t}$   (σ)", color=t["ink_secondary"],
                       fontsize=9, labelpad=8)
    fig.text(0.5, 0.01, "signal $MOM_{s,t}$   (σ)", ha="center", color=t["muted"], fontsize=8.5)
    fig.text(0.5, -0.09,
             "Illustrative. Every panel holds a real relationship — only the first two are "
             "strong enough for the eye to find it.",
             ha="center", color=t["ink_secondary"], fontsize=8.6)
    save(fig, t, f"scatter-ladder-{mode}.png")   # save() already crops tight


# ------------------------- fig: how the time axis collapses into five bars
def bucket_time_collapse(mode):
    """02 s3.2.3 -- every date has its own cross-section; pooling them spends t.

    Schematic. Standing on each date is that date's cross-section: five assets,
    ranked by signal into slots G1 to G5 across, forward return up. Not one of
    them is ordered on its own. Pooling every date leaves the five averages --
    and nothing about when any of it happened.
    """
    t = THEMES[mode]
    rng = np.random.RandomState(11)

    AX_Y = 6.6                       # the time axis
    DATES = [1.7, 3.7, 5.7, 7.7, 9.7]
    PW, PH, SHEAR = 1.15, 2.0, 0.5   # panel width, height, top-edge offset

    fig, ax = plt.subplots(figsize=(9.0, 5.3))
    fig.patch.set_facecolor(t["surface"])
    ax.set_facecolor(t["surface"])
    ax.set_xlim(0.2, 14.0)
    ax.set_ylim(1.05, 9.15)
    ax.axis("off")

    # ---- the time axis, with one mark per date
    ax.annotate("", xy=(13.5, AX_Y), xytext=(0.7, AX_Y),
                arrowprops=dict(arrowstyle="-|>", color=t["baseline"], linewidth=1.1,
                                shrinkA=0, shrinkB=0))
    ax.text(13.7, AX_Y - 0.30, "$t$", ha="left", va="center",
            color=t["muted"], fontsize=10)
    for x in DATES:
        ax.plot([x], [AX_Y], marker="o", markersize=4.2, color=t["ink_secondary"],
                zorder=4)

    # ---- each date's own cross-section standing on it
    for x in DATES:
        x0, y0 = x - PW / 2, AX_Y + 0.12
        ax.add_patch(Polygon(
            [(x0, y0), (x0 + PW, y0), (x0 + PW + SHEAR, y0 + PH), (x0 + SHEAR, y0 + PH)],
            closed=True, facecolor=t["surface"], edgecolor=t["baseline"],
            linewidth=1.0, zorder=3))
        for k in range(5):
            fx = 0.16 + 0.17 * k                       # the asset's slot, G1 to G5
            fy = rng.uniform(0.18, 0.82)               # the return it went on to deliver
            ax.plot([x0 + fx * PW + SHEAR * fy], [y0 + fy * PH], marker="o",
                    markersize=3.4, color=t["ramp"][5], zorder=4)

    ax.text(11.1, AX_Y + 1.50,
            "each panel is that date's\ncross-section — five assets,\n"
            "signal slot G1 to G5 across,\nforward return $r_{s,t}$ up.\n"
            "None of them is ordered",
            ha="left", va="center", color=t["ink_secondary"], fontsize=8.3,
            linespacing=1.5)

    # ---- the collapse
    ax.annotate("", xy=(3.7, 4.85), xytext=(3.7, AX_Y - 0.45),
                arrowprops=dict(arrowstyle="-|>", color=t["ramp"][5], linewidth=1.3,
                                shrinkA=0, shrinkB=0))
    ax.text(4.05, 5.78, "pool every date, then average within each slot",
            ha="left", va="center", color=t["ramp"][5], fontsize=8.6, fontweight="600")
    ax.text(4.05, 5.42, "the $t$ axis is spent here, and does not come back",
            ha="left", va="center", color=t["ink_secondary"], fontsize=8.3)

    # ---- what pooling leaves: five averages
    ZERO, SCALE = 3.40, 0.048
    bars = [(-20, "G1"), (-9, "G2"), (2, "G3"), (10, "G4"), (20, "G5")]
    xs = [1.9, 2.8, 3.7, 4.6, 5.5]
    ax.plot([1.35, 6.05], [ZERO, ZERO], color=t["baseline"], linewidth=0.9, zorder=2)
    for x, (bp, label) in zip(xs, bars):
        rounded_bar(ax, x, bp * SCALE, base=ZERO, width=0.56, color=t["ramp"][5])
        tip = ZERO + bp * SCALE
        ax.plot([x, x], [tip - 0.17, tip + 0.17], color=t["ink_secondary"],
                linewidth=1.0, zorder=5)
        ax.text(x, 1.92, label, ha="center", va="center",
                color=t["muted"], fontsize=8.4)
    ax.text(6.35, ZERO, "monotone G1 to G5, and that is\nthe whole claim — it says\nnothing about when",
            ha="left", va="center", color=t["ink_secondary"], fontsize=8.3,
            linespacing=1.5)
    ax.text(3.7, 1.42, "signal bucket ($MOM$)", ha="center", va="center",
            color=t["muted"], fontsize=8.4)
    ax.text(0.95, ZERO, "mean forward return $r_{s,t}$", rotation=90,
            ha="center", va="center", color=t["ink_secondary"], fontsize=8.4)

    titles(ax, t, "Every date brings its own cross-section; the pool keeps only the averages",
           "illustrative — the bar plot is every date's ranking flattened onto one picture")
    save(fig, t, f"bucket-time-collapse-{mode}.png")


# ----------------------------- fig: which return a signal is paired with
def signal_return_alignment(mode):
    """02 background -- the lookback, the discarded gap, and the paired return.

    Schematic. One cell is one period, drawn at an illustrative N = 8 and
    g = 3. The top row is the anatomy of a single observation; the lower rows
    are the two dates that follow, showing that the whole pattern slides one
    cell at a time, so lookbacks overlap almost entirely while the returns they
    are scored on never do.
    """
    t = THEMES[mode]
    N, G = 8, 3
    CW, CH = 0.86, 0.44

    STYLE = {
        "look": (t["ramp"][5], "none", "-"),
        "gap": (t["surface"], t["baseline"], (0, (2, 1.6))),
        "ret": (t["ramp"][2], "none", "-"),
    }

    def cell(ax, i, y, kind):
        face, edge, dash = STYLE[kind]
        ax.add_patch(FancyBboxPatch(
            (i + (1 - CW) / 2, y - CH / 2), CW, CH,
            boxstyle="round,pad=0.004,rounding_size=0.07",
            facecolor=face, edgecolor=edge, linewidth=1.0, linestyle=dash,
            zorder=3))

    def row(ax, y, shift=0):
        """One date's cells: N lookback, G discarded, then the one it is scored on."""
        for i in range(-N, 0):
            cell(ax, i + shift, y, "look")
        for i in range(0, G):
            cell(ax, i + shift, y, "gap")
        cell(ax, G + shift, y, "ret")

    def bracket(ax, x0, x1, y, label, colour):
        ax.plot([x0, x0, x1, x1], [y - 0.06, y, y, y - 0.06],
                color=colour, linewidth=1.0, solid_joinstyle="miter", zorder=4)
        ax.text((x0 + x1) / 2, y + 0.05, label, ha="center", va="bottom",
                color=colour, fontsize=8.5, fontweight="600")

    fig, (ax, bx) = plt.subplots(
        2, 1, figsize=(8.6, 4.6),
        gridspec_kw=dict(height_ratios=[1.0, 1.15], hspace=0.30))
    fig.patch.set_facecolor(t["surface"])

    # ---- top: the anatomy of one observation
    ax.set_facecolor(t["surface"])
    ax.set_xlim(-N - 0.5, G + 1.6)
    ax.set_ylim(-0.78, 0.56)
    ax.axis("off")

    row(ax, 0.0)
    bracket(ax, -N + 0.07, -0.07, 0.29,
            "lookback — the returns the signal averages", t["ramp"][5])
    bracket(ax, 0.07, G - 0.07, 0.29, "gap — discarded", t["muted"])
    bracket(ax, G + 0.07, G + 0.93, 0.29, "scored on", t["ramp"][5])

    for i, lab in ((-1, "$r_{t-1}$"), (0, "$r_t$"), (G, "$r_{t+g}$")):
        ax.text(i + 0.5, -0.29, lab, ha="center", va="top",
                color=t["muted"], fontsize=8.2)
    # the decision instant sits on a boundary, not on a cell
    ax.plot([0, 0], [-0.31, 0.31], color=t["ink_secondary"], linewidth=1.0,
            linestyle=(0, (2, 1.6)), zorder=4)
    ax.text(0.0, -0.52, "computed at $t$ — only the cells left of this line",
            ha="center", va="top", color=t["ink_secondary"], fontsize=8.4)

    titles(ax, t, "Which return a signal is paired with",
           "one cell is one period; the signal at $t$ skips $g$ of them — the likeliest reversal — "
           "before the return it is judged on")

    # ---- bottom: the same pattern, one date later, and one later again
    bx.set_facecolor(t["surface"])
    bx.set_xlim(-N - 1.6, G + 6.4)
    bx.set_ylim(-2.25, 0.78)
    bx.axis("off")

    bx.text(-N - 1.5, 0.52, "the same pattern one date later — and the pairing never repeats",
            ha="left", va="center", color=t["ink_secondary"], fontsize=8.8, fontweight="600")

    for k, lab in enumerate(("$t$", "$t+1$", "$t+2$")):
        dy = -0.72 * k
        row(bx, dy, shift=k)
        bx.text(-N - 1.0, dy, lab, ha="right", va="center",
                color=t["ink_secondary"], fontsize=8.6, fontweight="600")

    corners = [(G + k + (1 + CW) / 2, -0.72 * k + CH / 2) for k in range(3)]
    bx.plot(*zip(*corners), color=t["ramp"][2], linewidth=1.1,
            linestyle=(0, (1.6, 1.6)), zorder=4)
    bx.text(G + 3.2, -1.44,
            "one return per date,\nand no two dates share one",
            ha="left", va="center", color=t["ramp"][5], fontsize=8.4,
            fontweight="600", linespacing=1.45)
    bx.text(-N - 1.0, -1.98,
            "consecutive lookbacks share all but one cell, so neighbouring signals are nearly the same number",
            ha="left", va="center", color=t["ink_secondary"], fontsize=8.2)

    fig.text(0.5, -0.01,
             "Illustrative. Real lookbacks run 20-250 periods and the gap 1 day to 1 month; "
             "the geometry is the same at any size.",
             ha="center", color=t["ink_secondary"], fontsize=8.6)
    save(fig, t, f"signal-return-alignment-{mode}.png")


FIGURES = (binary_momentum, scatter_ladder, alpha_opacity, bucket_construction, noise_shrinks,
           three_bucketings, signal_distribution, signal_return_alignment,
           bucket_time_collapse)

if __name__ == "__main__":
    for mode in ("light", "dark"):
        for fn in FIGURES:
            fn(mode)
    print(f"wrote {2 * len(FIGURES)} figures for 02-building-signals.md")
