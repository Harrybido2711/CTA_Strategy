"""Figures for docs/04-volatility-regimes.md.

Run from anywhere:

    python docs/figures/make_04_volatility_regimes.py

Writes light- and dark-mode PNGs into docs/figures/. The chapter references
them through a <picture> element so GitHub serves the variant matching the
reader's theme.

Figures produced
----------------
    regime-lag          a trailing volatility estimate peaks long after the burst it is measuring
    vix-bucketing       why the raw level will not bucket, and what the log fixes
    regime-signal-grid  the same signal, conditioned on the volatility regime

All are schematics drawn from illustrative values. regime-lag is the one
exception worth naming: the realized-volatility line really is a rolling
standard deviation of the synthetic return path drawn beneath it, so the lag
shown is the estimator's own lag rather than a hand-drawn curve.

Formulas stay in the markdown as LaTeX rather than being rendered here: text in
an image is neither selectable nor searchable.
"""

import matplotlib.pyplot as plt
import numpy as np
from _style import THEMES, save, style_axes, titles

ANNUALIZE = np.sqrt(252.0)


def _label_ink(hex_colour):
    """Black or white for text sitting on a filled cell, by the fill's luminance."""
    r, g, b = (int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return "#0b0b0b" if 0.299 * r + 0.587 * g + 0.114 * b > 0.6 else "#ffffff"


# -------------------- fig: a trailing estimate answers after the question is moot
def regime_lag(mode):
    """04 s2 -- realized volatility peaks two weeks after the news that caused it.

    Schematic, with one honest part. A synthetic return path is calm, bursts for
    eight sessions from day 0, then settles. The realized line is a genuine
    21-day rolling standard deviation of that path, annualized, so its delay is
    the estimator's own. The implied line is drawn: it steps up on the day the
    news lands and decays, which is the behaviour the chapter is buying.
    """
    t = THEMES[mode]
    rng = np.random.RandomState(11)

    days = np.arange(-40, 61)
    k = 21

    # daily volatility of the path: calm, an eight-session burst, then a settle
    vol = np.full(days.shape, 0.0060)
    burst = (days >= 0) & (days < 8)
    vol[burst] = 0.0300
    tail = days >= 8
    vol[tail] = 0.0075 + 0.0135 * np.exp(-(days[tail] - 8) / 16.0)

    rets = vol * rng.standard_normal(days.size)

    realized = np.full(days.shape, np.nan)
    for i in range(k - 1, days.size):
        realized[i] = rets[i - k + 1:i + 1].std(ddof=1) * ANNUALIZE * 100

    # implied: on the floor, a jump the day the news prints, then decay
    implied = 10.5 + 0.9 * np.exp(-((days + 4) / 9.0) ** 2)
    after = days >= 0
    implied[after] = 12.5 + 31.0 * np.exp(-days[after] / 11.0)

    fig, (ax_r, ax) = plt.subplots(
        2, 1, figsize=(9.2, 5.6), sharex=True,
        gridspec_kw=dict(height_ratios=[1.0, 2.5], hspace=0.16))
    fig.patch.set_facecolor(t["surface"])

    # upper: the tape itself, so the burst is visible rather than asserted
    ax_r.vlines(days, 0, np.abs(rets) * 100, color=t["wash"], alpha=0.55, linewidth=1.5)
    style_axes(ax_r, t, ylabel="|daily return|  (%)", grid=False)
    ax_r.set_ylim(0, 7.2)
    ax_r.set_yticks([0, 3, 6])

    ax.plot(days, realized, color=t["series"], linewidth=2.2, zorder=4)
    ax.plot(days, implied, color=t["accent"], linewidth=2.2, zorder=5)
    style_axes(ax, t,
               ylabel="annualized volatility  (%)",
               xlabel="trading days since the news")

    peak = int(np.nanargmax(realized))
    ax.axvline(0, color=t["baseline"], linewidth=1.0, linestyle=(0, (4, 3)), zorder=1)
    ax_r.axvline(0, color=t["baseline"], linewidth=1.0, linestyle=(0, (4, 3)), zorder=1)
    ax.axvline(days[peak], color=t["baseline"], linewidth=1.0, linestyle=(0, (4, 3)), zorder=1)

    ax.annotate("", xy=(days[peak], 8), xytext=(0, 8),
                arrowprops=dict(arrowstyle="<->", color=t["ink_secondary"], linewidth=1.1))
    ax.text(days[peak] / 2, 10.6, f"{days[peak]} sessions late", ha="center",
            color=t["ink_secondary"], fontsize=8.8)

    ax.text(60, 21.5, "realized, 21-day\ntrailing window",
            color=t["series"], fontsize=9, fontweight="600", ha="right", va="bottom")
    ax.text(6.5, 40, "implied, from\nthe option strip",
            color=t["accent"], fontsize=9, fontweight="600", va="top")
    ax.text(0.8, 3.0, "news", color=t["muted"], fontsize=8.6, va="bottom")

    ax.set_xlim(-40, 60)
    ax.set_ylim(0, 50)

    titles(ax_r, t, "A trailing estimate answers after the question stops mattering",
           "illustrative — the burst lasts 8 sessions; the 21-day estimate does not peak until session 21")
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    save(fig, t, f"regime-lag-{mode}.png")


# ------------------------- fig: the raw level will not bucket, the log will
def vix_bucketing(mode):
    """04 s4 -- one distribution, two axes, and where the integer cuts land.

    Schematic. A log-normal-ish sample of index levels. On the linear axis the
    mass piles into a narrow band with a long empty tail, so equal-width bins
    put nearly everything in one bin. On the log axis the same sample is nearly
    symmetric, and the integer cuts of ceil(ln v) fall at e^3 and e^4 -- which
    is where a reader would draw the regime boundaries anyway.
    """
    t = THEMES[mode]
    rng = np.random.RandomState(4)

    calm = np.exp(rng.normal(2.80, 0.26, 3400))
    stress = np.exp(rng.normal(3.35, 0.30, 900))
    crisis = np.exp(rng.normal(4.05, 0.26, 130))
    v = np.clip(np.concatenate([calm, stress, crisis]), 8.5, 88.0)

    fig, (ax_l, ax_g) = plt.subplots(1, 2, figsize=(9.6, 3.9))
    fig.patch.set_facecolor(t["surface"])

    ax_l.hist(v, bins=np.arange(8, 92, 2), color=t["series"], edgecolor="none", zorder=3)
    style_axes(ax_l, t, ylabel="number of days", xlabel="index level  $v_t$")
    ax_l.set_xlim(8, 90)
    ax_l.text(34, ax_l.get_ylim()[1] * 0.72,
              "half the sample inside\na 6-point band, and\n60 points of empty tail",
              color=t["ink_secondary"], fontsize=8.6, va="top")

    ax_g.hist(np.log(v), bins=np.arange(2.1, 4.62, 0.06), color=t["series"],
              edgecolor="none", zorder=3)
    style_axes(ax_g, t, ylabel="number of days", xlabel=r"$\ln v_t$")
    ax_g.set_xlim(2.1, 4.6)

    top = ax_g.get_ylim()[1]
    for cut, note in ((3.0, "$e^3 \\approx 20$"), (4.0, "$e^4 \\approx 55$")):
        ax_g.axvline(cut, color=t["baseline"], linewidth=1.2, linestyle=(0, (4, 3)), zorder=4)
        ax_g.text(cut, top * 1.02, note, ha="center", va="bottom",
                  color=t["muted"], fontsize=8.4)
    for centre, name in ((2.40, "calm\n$g_t=3$"), (3.48, "stressed\n$g_t=4$"),
                         (4.30, "crisis\n$g_t=5$")):
        ax_g.text(centre, top * 0.74, name, ha="center", va="top",
                  color=t["ink_secondary"], fontsize=8.6)

    titles(ax_l, t, "The level will not bucket; its logarithm will",
           "illustrative — the same sample on a linear and a log axis, with the cuts of $\\lceil \\ln v_t \\rceil$")
    fig.tight_layout(rect=(0, 0, 1, 0.88))
    save(fig, t, f"vix-bucketing-{mode}.png")


# --------------------- fig: the same staircase, cut by the volatility regime
def regime_signal_grid(mode):
    """04 s5 -- a two-way sort: signal across, volatility regime up.

    Schematic. Mean forward return in basis points for each (regime, signal)
    cell. The calm row is the monotone staircase chapter 02 draws; it flattens
    through the stressed row and is gone in the crisis row. That difference is
    the finding -- an unconditional bar plot averages all three rows into one.
    """
    t = THEMES[mode]

    rows = ["crisis\n$g_t = 5$", "stressed\n$g_t = 4$", "calm\n$g_t = 3$"]
    cols = ["G1", "G2", "G3", "G4", "G5"]
    share = ["3%", "22%", "75%"]
    cells = np.array([
        [+4, -3, +2, -5, +3],          # crisis     -- no ordering left
        [-14, -6, +1, +8, +15],        # stressed   -- half the staircase
        [-24, -11, +2, +13, +26],      # calm       -- chapter 02's staircase
    ], dtype=float)

    lo, hi = cells.min(), cells.max()
    ramp = t["ramp"]

    fig, ax = plt.subplots(figsize=(7.4, 4.3))
    fig.patch.set_facecolor(t["surface"])
    ax.set_facecolor(t["surface"])

    for i in range(cells.shape[0]):
        for j in range(cells.shape[1]):
            score = (cells[i, j] - lo) / (hi - lo)
            shade = ramp[int(round(score * (len(ramp) - 1)))]
            ax.add_patch(plt.Rectangle((j, i), 1, 1, facecolor=shade,
                                       edgecolor=t["surface"], linewidth=1.6, zorder=2))
            ax.text(j + 0.5, i + 0.5, f"{cells[i, j]:+.0f}", ha="center", va="center",
                    color=_label_ink(shade), fontsize=9.4, fontweight="600", zorder=4)

    for i, s in enumerate(share):
        ax.text(5.16, i + 0.5, s, ha="left", va="center",
                color=t["muted"], fontsize=8.6)
    ax.text(5.16, 3.08, "share of\nsample", ha="left", va="bottom",
            color=t["muted"], fontsize=8.2)

    ax.set_xlim(0, 6.1)
    ax.set_ylim(0, 3)
    ax.set_xticks(np.arange(len(cols)) + 0.5)
    ax.set_yticks(np.arange(len(rows)) + 0.5)
    ax.set_xticklabels(cols, fontsize=9)
    ax.set_yticklabels(rows, fontsize=8.8)
    ax.tick_params(colors=t["muted"], length=0)
    for side in ax.spines.values():
        side.set_visible(False)
    ax.set_xlabel("signal bucket, lowest to highest", color=t["ink_secondary"],
                  fontsize=9.4, labelpad=8)
    ax.set_ylabel("volatility regime", color=t["ink_secondary"], fontsize=9.4, labelpad=8)

    titles(ax, t, "One signal, three regimes, three different answers",
           "illustrative — mean forward return in basis points; the shade tracks the value")
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    save(fig, t, f"regime-signal-grid-{mode}.png")


FIGURES = (regime_lag, vix_bucketing, regime_signal_grid)

if __name__ == "__main__":
    for mode in ("light", "dark"):
        for fn in FIGURES:
            fn(mode)
    print(f"wrote {2 * len(FIGURES)} figures for 04-volatility-regimes.md")
