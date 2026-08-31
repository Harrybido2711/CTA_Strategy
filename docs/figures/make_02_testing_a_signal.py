"""Figures for docs/02-testing-a-signal.md.

Run from anywhere:

    python docs/figures/make_02_testing_a_signal.py

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
    bucket-time-collapse     every date gives one draw; pooling them spends the t axis
    signal-return-alignment  the lookback, the discarded gap, and the paired return

scatter-ladder's last panel, alpha-opacity, bucket-construction's lower row and
all of noise-shrinks are measured on CTA_data/ through _data.py. The rest are
schematics: they explain a definition or a procedure, where invented numbers
are clearer than real ones.

Formulas stay in the markdown as LaTeX rather than being rendered here: text in
an image is neither selectable nor searchable.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, Polygon
from _data import bucket_stats, momentum_panel, pooled
from _style import THEMES, rounded_bar, save, style_axes, titles

_PANEL = None


def panel():
    """The chapter's measured panel, loaded once: signal, return in bp, bucket.

    21-day risk-adjusted momentum against the next session's return, every date
    ranked against its own asset's history. 57,649 asset-dates across the 37
    ETFs of CTA_data/.
    """
    global _PANEL
    if _PANEL is None:
        _PANEL = pooled(*momentum_panel(lookback=21, vol_window=63, gap=0))
    return _PANEL


def standardized(rng, n=4000):
    """A rendering-sized subsample of the panel, both axes in sigma units."""
    x, y, _ = panel()
    pick = rng.choice(len(x), size=n, replace=False)
    x, y = x[pick], y[pick]
    return (x - x.mean()) / x.std(), (y - y.mean()) / y.std()


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


# ------------- fig: what turning the marker opacity down does and does not buy
def alpha_opacity(mode):
    """02 s3.1 -- alpha turns ink into density; whether density reads is another matter.

    Measured. The same 6,000 asset-dates from CTA_data/ drawn opaque and at a
    low opacity, so the panels differ only in the thing being demonstrated.
    Nothing appears in the second that was not visible in the first, which is
    the point.
    """
    t = THEMES[mode]
    rng = np.random.RandomState(23)
    x, y = standardized(rng, n=6000)

    panels = (
        (1.00, "alpha = 1", "the default — one solid mass"),
        (0.01, "alpha = 0.01", "the same points, rendered as density"),
    )

    fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.9), sharex=True, sharey=True,
                             gridspec_kw=dict(wspace=0.10))
    fig.patch.set_facecolor(t["surface"])

    for ax, (alpha, head, sub) in zip(axes, panels):
        style_axes(ax, t, grid=False)
        ax.scatter(x, y, s=8.0, color=t["series"], alpha=alpha, linewidths=0, zorder=3)
        ax.set_xlim(-3.6, 3.6)
        ax.set_ylim(-3.6, 3.6)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.spines["bottom"].set_visible(False)
        ax.text(0, 1.13, head, transform=ax.transAxes, color=t["ink"],
                fontsize=10.2, fontweight="600", va="bottom")
        ax.text(0, 1.03, sub, transform=ax.transAxes, color=t["ink_secondary"],
                fontsize=8.5, va="bottom")

    axes[0].set_ylabel("forward return $r_{s,t}$   (σ)", color=t["ink_secondary"],
                       fontsize=9, labelpad=8)
    fig.text(0.5, 0.01, "signal $MOM_{s,t}$   (σ)", ha="center", color=t["muted"], fontsize=8.5)
    fig.text(0.5, -0.09,
             "Measured on CTA_data/ — 6,000 asset-dates, both axes standardized. A smooth density "
             "renders faithfully as a smooth density.",
             ha="center", color=t["ink_secondary"], fontsize=8.6)
    save(fig, t, f"alpha-opacity-{mode}.png")

# --------------------- fig: how the bar chart is built, and why averaging is
def bucket_construction(mode):
    """02 s3.2 -- draw five, rank them, repeat, average — invented and measured.

    Top row invented: a perfect relationship, where every draw of five comes out
    ordered and 400 of them average into a clean staircase. Bottom row measured
    on CTA_data/: the same two steps on the real cloud, closing on the actual
    bucket chart over all 57,649 asset-dates rather than on a resampling device,
    because with real fat-tailed returns a single 20-sigma session would own the
    average of 400 draws. Every drawn point is the same colour: any five will
    do, and no draw is special. Whiskers are +/- 2 SE.
    """
    t = THEMES[mode]
    rng = np.random.RandomState(9)
    n, shown, total = 4000, 6, 400

    lx = rng.uniform(0, 10, n)
    ly = lx.copy()                                   # perfect: return is the signal
    cx, cy = standardized(rng, n=n)                  # measured: CTA_data/

    def slots(px, py, k):
        """k draws of five dates, each sorted by signal into rank slots G1..G5"""
        idx = rng.randint(0, len(px), size=(k, 5))
        order = np.argsort(px[idx], axis=1)
        return np.take_along_axis(py[idx], order, axis=1), idx

    rows = (
        (lx, ly, False, "If the relationship were perfect",
         "every draw comes out ordered", f"{total} draws, averaged"),
        (cx, cy, True, "On the measured cloud",
         "every draw comes back tangled", "all 57,649, averaged"),
    )

    fig, axes = plt.subplots(2, 3, figsize=(10.6, 6.6),
                             gridspec_kw=dict(wspace=0.30, hspace=0.58))
    fig.patch.set_facecolor(t["surface"])

    for (px, py, measured, head, mid_sub, right_head), (ax, bx, cxx) in zip(rows, axes):
        ranked, idx = slots(px, py, shown)
        picked = idx[:3].ravel()                     # three draws' worth, one colour

        # ---- where the points come from
        style_axes(ax, t, ylabel="forward return $r_{s,t}$",
                   xlabel="signal $MOM_{s,t}$", grid=False)
        ax.scatter(px, py, s=3.0, color=t["series"], alpha=0.10, linewidths=0, zorder=2)
        ax.scatter(px[picked], py[picked], s=34, color=t["series"], zorder=4)
        if measured:                                 # a 20-sigma session would flatten it
            ax.set_xlim(-4, 4)
            ax.set_ylim(-4, 4)
        ax.set_xticks([])
        ax.set_yticks([])
        titles(ax, t, head, "any five dates, taken at random")

        # ---- each draw, at the rank slot its five points fell into
        style_axes(bx, t, ylabel="forward return $r_{s,t}$",
                   xlabel="rank slot (G1 = lowest signal)", grid=False)
        for row in ranked:
            bx.plot(range(5), row, color=t["series"], alpha=0.42, linewidth=1.1,
                    marker="o", markersize=4.6, zorder=4)
        if measured:
            bx.set_ylim(-4, 4)
        bx.set_xticks(range(5))
        bx.set_xticklabels(["G1", "G2", "G3", "G4", "G5"])
        bx.set_yticks([])
        titles(bx, t, f"{shown} draws, ranked", mid_sub)

        # ---- and the answer, with the error on it
        if measured:
            _, y, g = panel()
            means, errs, _ = bucket_stats(y, g)
            errs = 2 * errs
            right_sub = "bars with ± 2 SE, in basis points"
            ylab = "mean forward return (bp)"
        else:
            allr, _ = slots(px, py, total)
            means = allr.mean(axis=0)
            errs = 2 * allr.std(axis=0) / total ** 0.5
            right_sub = "bars with ± 2 SE"
            ylab = "mean forward return $r_{s,t}$"

        style_axes(cxx, t, ylabel=ylab, xlabel="signal bucket ($MOM$)")
        for i, v in enumerate(means):
            rounded_bar(cxx, i, v, color=t["series"], width=0.34)
        cxx.errorbar(range(5), means, yerr=errs, fmt="none", ecolor=t["muted"],
                     elinewidth=1.1, capsize=3, capthick=1.1, zorder=5)
        cxx.axhline(0, color=t["baseline"], linewidth=0.9, zorder=2)
        lo, hi = (means - errs).min(), (means + errs).max()
        pad = 0.18 * (hi - lo)
        cxx.set_ylim(min(0, lo) - pad, hi + pad)
        cxx.set_xlim(-0.6, 4.6)
        cxx.set_xticks(range(5))
        cxx.set_xticklabels(["G1", "G2", "G3", "G4", "G5"])
        if not measured:
            cxx.set_yticks([])
        titles(cxx, t, right_head, right_sub)

    fig.text(0.5, -0.03,
             "Upper row invented, lower row measured on CTA_data/. Each row is scaled to its own "
             "height — the measured staircase carries a small fraction of the rise, and it descends.",
             ha="center", color=t["ink_secondary"], fontsize=8.8)
    save(fig, t, f"bucket-construction-{mode}.png")


# ------------------ fig: the staircase is an estimate, and m is what sharpens it
def noise_shrinks(mode):
    """02 s3.2 -- the measured buckets at m = 30, 300, 3,000 and every observation.

    Measured. Each panel draws m observations from each real bucket, so the
    quantity being estimated is identical in all four and only the error on it
    changes -- 149 bp over root m, which is 27, 8.6, 2.7 and 1.4 bp. Bars are
    the bucket mean; whiskers are +/- 2 SE, as everywhere in the chapter.
    """
    t = THEMES[mode]
    rng = np.random.RandomState(17)
    _, y, g = panel()
    full = min((g == k).sum() for k in range(1, 6))

    fig, axes = plt.subplots(1, 4, figsize=(11.4, 3.5), sharey=True,
                             gridspec_kw=dict(wspace=0.14))
    fig.patch.set_facecolor(t["surface"])

    for ax, m in zip(axes, (30, 300, 3000, full)):
        means, errs = [], []
        for k in range(1, 6):
            vals = y[g == k]
            draw = rng.choice(vals, size=m, replace=False)
            means.append(draw.mean())
            errs.append(2 * draw.std(ddof=1) / m ** 0.5)
        means, errs = np.array(means), np.array(errs)

        style_axes(ax, t, ylabel="mean forward return (bp)" if ax is axes[0] else None,
                   xlabel="signal bucket ($MOM$)")
        for i, v in enumerate(means):
            rounded_bar(ax, i, v, color=t["series"], width=0.34)
        ax.errorbar(range(5), means, yerr=errs, fmt="none", ecolor=t["muted"],
                    elinewidth=1.1, capsize=3, capthick=1.1, zorder=5)
        ax.axhline(0, color=t["baseline"], linewidth=0.9, zorder=2)
        ax.set_xlim(-0.62, 4.62)
        ax.set_ylim(-99, 99)
        ax.set_xticks(range(5))
        ax.set_xticklabels(["G1", "G2", "G3", "G4", "G5"], fontsize=7.6)
        head = f"m = {m:,}" + (" (all)" if m == full else "")
        ax.text(0, 1.14, head, transform=ax.transAxes, color=t["ink"],
                fontsize=10.2, fontweight="600", va="bottom")
        half = errs.mean()
        ax.text(0, 1.03, f"± 2 SE = {half:.1f} bp" if half < 10 else f"± 2 SE = {half:.0f} bp",
                transform=ax.transAxes, color=t["ink_secondary"], fontsize=8.5, va="bottom")

    axes[-1].annotate("G1 stands clear\nof its own error",
                      xy=(0.16, 11), xytext=(1.5, 62), color=t["ink_secondary"], fontsize=8.4,
                      arrowprops=dict(arrowstyle="-", color=t["muted"], linewidth=1.0,
                                      connectionstyle="arc3,rad=0.24"))

    fig.text(0.5, -0.10,
             "Measured on CTA_data/. The quantity estimated is the same in all four panels — the "
             "real bucket means, near +11 bp at G1 and 0 at G5. Only the error changes, as the "
             "square root of m.",
             ha="center", color=t["ink_secondary"], fontsize=8.6)
    save(fig, t, f"noise-shrinks-{mode}.png")

# ----------------------- fig: the calibration ladder, and where reality sits
def scatter_ladder(mode):
    """02 s2 -- what each correlation looks like, and which one the data gives.

    The first three panels are synthetic: no liquid market hands you an 80%
    correlation, so the only way to show one is to draw it. The fourth is
    measured: 4,000 asset-dates drawn from CTA_data/ for rendering, both axes
    standardized so the panel sits on the same scale as the three it is compared
    against. Its label is the correlation of the whole 57,649-row panel, not of
    the subsample being drawn -- a subsample's own correlation carries a 1.6
    point standard error and would print a number the chapter does not use.
    """
    t = THEMES[mode]
    rng = np.random.RandomState(11)
    n = 1500
    x = rng.standard_normal(n)
    e = rng.standard_normal(n)

    xm, ym = standardized(rng, n=4000)
    fx, fy, _ = panel()                              # label the population, not the subsample
    rho = np.corrcoef(fx, fy)[0, 1]

    panels = [
        (0.80, x, 0.80 * x + (1 - 0.80 ** 2) ** 0.5 * e, "what you pictured", False),
        (0.45, x, 0.45 * x + (1 - 0.45 ** 2) ** 0.5 * e, "convincing", False),
        (0.30, x, 0.30 * x + (1 - 0.30 ** 2) ** 0.5 * e, "the eye's floor", False),
        (rho, xm, ym, "measured, CTA_data", True),
    ]

    fig, axes = plt.subplots(1, 4, figsize=(9.6, 3.1), sharex=True, sharey=True,
                             gridspec_kw=dict(wspace=0.16))
    fig.patch.set_facecolor(t["surface"])

    for ax, (r, px, py, verdict, live) in zip(axes, panels):
        style_axes(ax, t, grid=False)
        ax.scatter(px, py, s=3.2, color=t["series"], alpha=0.16, linewidths=0, zorder=3)
        ax.set_xlim(-3.6, 3.6)
        ax.set_ylim(-3.6, 3.6)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.spines["bottom"].set_visible(False)
        label = f"corr = {r * 100:+.1f}%" if live else f"corr = {int(r * 100)}%"
        ax.text(0, 1.15, label, transform=ax.transAxes,
                color=t["ink"], fontsize=10.4, fontweight="600", va="bottom")
        ax.text(0, 1.04, verdict, transform=ax.transAxes,
                color=t["ink"] if live else t["muted"],
                fontsize=8.8, fontweight="600" if live else "normal", va="bottom")
        if live:
            ax.plot([0, 0.78], [1.005, 1.005], transform=ax.transAxes,
                    color=t["series"], linewidth=1.6, solid_capstyle="butt",
                    clip_on=False, zorder=5)

    axes[0].set_ylabel("forward return $r_{s,t}$   (σ)", color=t["ink_secondary"],
                       fontsize=9, labelpad=8)
    fig.text(0.5, 0.01, "signal $MOM_{s,t}$   (σ)", ha="center", color=t["muted"], fontsize=8.5)
    fig.text(0.5, -0.09,
             "First three panels drawn at a stated correlation. The fourth is measured on "
             "CTA_data/ — the correlation is the whole panel\'s, rendered from a 4,000-point "
             "subsample. Every panel holds a real relationship; only the first two show it.",
             ha="center", color=t["ink_secondary"], fontsize=8.6)
    save(fig, t, f"scatter-ladder-{mode}.png")


# ------------------------- fig: how the time axis collapses into five bars
def bucket_time_collapse(mode):
    """02 s3.2.3 -- every date lands in one slot; pooling them spends the t axis.

    Schematic. Left: one asset's dates along t, each drawn at the slot its
    signal scored into, so the same asset visits all five over the years and a
    violent stretch is shaded. Right: step 5 averages down every column, which
    hands back five numbers and no t at all.
    """
    t = THEMES[mode]
    rng = np.random.RandomState(6)
    T, rho = 1400, 0.12

    z = rng.standard_normal(T)
    fwd = 100 * (rho * z + (1 - rho ** 2) ** 0.5 * rng.standard_normal(T))
    slot = np.digitize(z, np.quantile(z, [0.2, 0.4, 0.6, 0.8]))
    day = np.arange(T)

    fig, (ax, bx) = plt.subplots(
        1, 2, figsize=(10.4, 4.0), gridspec_kw=dict(width_ratios=[2.35, 1], wspace=0.42))
    fig.patch.set_facecolor(t["surface"])

    # ---- left: where each date landed, laid out along t
    style_axes(ax, t, ylabel="slot the date scored into", xlabel="date $t$", grid=False)
    ax.axvspan(900, T, color=t["grid"], zorder=0)
    ax.text(1150, 4.72, "a violent stretch", color=t["muted"], fontsize=8.2, ha="center")
    ax.scatter(day, slot + rng.uniform(-0.22, 0.22, T), s=5.0, color=t["series"],
               alpha=0.30, linewidths=0, zorder=3)
    ax.set_xlim(-30, T + 30)
    ax.set_ylim(-0.75, 5.05)
    ax.set_xticks([])
    ax.set_yticks(range(5))
    ax.set_yticklabels(["G1", "G2", "G3", "G4", "G5"], fontsize=8.4)
    titles(ax, t, "Every date lands in one slot",
           "one asset, and over the years it visits all five")

    # ---- right: average down each column and t is gone
    means = np.array([fwd[slot == j].mean() for j in range(5)])
    errs = np.array([fwd[slot == j].std() / (slot == j).sum() ** 0.5 for j in range(5)])
    style_axes(bx, t, ylabel="mean forward return $r_{s,t}$ (bp)", xlabel="signal bucket ($MOM$)")
    for i, v in enumerate(means):
        rounded_bar(bx, i, v, color=t["series"], width=0.34)
    bx.errorbar(range(5), means, yerr=errs, fmt="none", ecolor=t["muted"],
                elinewidth=1.1, capsize=3, capthick=1.1, zorder=5)
    bx.axhline(0, color=t["baseline"], linewidth=0.9, zorder=2)
    bx.set_xlim(-0.6, 4.6)
    bx.set_xticks(range(5))
    bx.set_xticklabels(["G1", "G2", "G3", "G4", "G5"], fontsize=8.4)
    titles(bx, t, "Pooled over $t$", "five averages, and no $t$ left")

    # ---- the collapse itself
    fig.text(0.615, 0.46, "average\ndown each\ncolumn", ha="center", va="center",
             color=t["ink_secondary"], fontsize=8.4)
    fig.patches.append(plt.matplotlib.patches.FancyArrowPatch(
        (0.578, 0.60), (0.652, 0.60), transform=fig.transFigure, figure=fig,
        arrowstyle="-|>", mutation_scale=13, color=t["muted"], linewidth=1.1))

    fig.text(0.5, -0.07,
             "Illustrative. The left panel holds the whole sample and the right holds the same "
             "observations with the date thrown away — which is why a staircase cannot say whether "
             "the edge held throughout or only for a stretch.",
             ha="center", color=t["ink_secondary"], fontsize=8.6)
    save(fig, t, f"bucket-time-collapse-{mode}.png")


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
           signal_return_alignment,
           bucket_time_collapse)

if __name__ == "__main__":
    for mode in ("light", "dark"):
        for fn in FIGURES:
            fn(mode)
    print(f"wrote {2 * len(FIGURES)} figures for 02-testing-a-signal.md")
