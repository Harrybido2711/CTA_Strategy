"""Figures for the resume reproduction, light and dark, from the result files only.

    .venv/bin/python Resume_Reproduction/make_rr_figures.py

  rr-equity-curves     cumulative PnL of B0 (naive and realistic), B1 and the optimizer, 18 quarters
  rr-execution-haircut B0's annual return after each execution assumption, in order
  rr-regime-map        momentum's signal-weighted return in each volume x volatility cell, rolling cut
  rr-rebuild-scorecard B1 minus B0: Sharpe and turnover, with bootstrap intervals
  rr-macd-heatmap      t-statistic of the G5 - G1 spread across the MACD grid
Round 2 (ROUND2.md):
  rr2-equity-curves    cumulative excess return of T0 (before and after costs), T1 and T3
  rr2-regime-bars      T0 and T1 excess return in each VIX state, with day counts
  rr2-leverage-path    gross exposure of T0 and T1 with the high-VIX days shaded
  rr2-tsmom-grid       Sharpe across the paper's look-back x holding grid, truncated
  rr2-haircut          T0's annual return after each execution assumption

Design contract (one claim per figure, written before plotting):
  equity curves   the frictionless edge is about zero and friction turns it into a steady loss;
                  only the turnover-penalised optimizer survives costs
  haircut         cost and slippage, not delay, are what the book loses
  regime map      the high-volume / low-volatility corner does not beat the low-volume /
                  high-volatility corner; every cell's count is printed
  scorecard       B1 cuts turnover a little and its Sharpe change is indistinguishable from zero
  MACD heat map   no contiguous warm band exists, so the walk-forward rule kept no MACD cell
Colours come from docs/figures/_style.py only; the PNGs land in Resume_Reproduction/figures/.
"""
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "docs" / "figures"))
import _style as ST                                              # noqa: E402
from _style import THEMES, rounded_bar, save, style_axes, titles  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap            # noqa: E402
from matplotlib.patches import Rectangle                         # noqa: E402

plt = ST.plt
ST.set_out(HERE / "figures")
RES = HERE / "results"
QA_HOOK = None          # set by a QA harness to inspect a figure before it is saved


def rd(name):
    return pd.read_csv(RES / f"{name}.csv", comment="#")


def finish(fig, t, stem, mode):
    if QA_HOOK is not None:
        QA_HOOK(fig, f"{stem}-{mode}")
    save(fig, t, f"{stem}-{mode}.png")


def backing(t):
    """A surface-coloured box behind a direct label, so gridlines and reference lines pass under it."""
    return dict(facecolor=t["surface"], edgecolor="none", pad=1.2)


def off_grid(ypos, step, span, margin=0.025):
    """Move direct-label heights off the gridlines (multiples of step) they would sit on."""
    out = []
    for y in ypos:
        k = round(y / step) * step
        if abs(y - k) < margin * span:
            y = k + np.sign(y - k or 1.0) * margin * span
        out.append(y)
    return out


def diverging(t):
    return LinearSegmentedColormap.from_list("rr_div", [t["muted"], t["surface"], t["ramp"][5]])


# ----------------------------------------------------------------------------- 1
def equity_curves(mode):
    t = THEMES[mode]
    d = rd("11_daily_pnl")
    d["date"] = pd.to_datetime(d["date"])
    d = d.set_index("date")
    cum = d[["B0 naive_1", "B0", "B1", "Optimizer, net 0"]].cumsum()
    fig, ax = plt.subplots(figsize=(7.2, 3.9), facecolor=t["surface"])
    style_axes(ax, t, ylabel="Cumulative PnL per $1 of capital", xlabel="Date (walk-forward quarters 2022Q1 to 2026Q2)")
    for blk, label in (("OV", "OV"), ("Test", "Test, read once")):
        idx = d.index[d["block"] == blk]
        ax.axvspan(idx.min(), idx.max(), color=t["grid"], alpha=0.55, zorder=0, lw=0)
        ax.text(idx.min() + (idx.max() - idx.min()) / 2, 0.985, label, transform=ax.get_xaxis_transform(),
                ha="center", va="top", color=t["muted"], fontsize=8)
    ax.fill_between(cum.index, cum["B0 naive_1"], cum["B0"], color=t["muted"], alpha=0.16, lw=0, zorder=1)
    lines = [("B0 naive_1", "B0, next close, no cost", t["ramp"][5], "--", 1.3),
             ("B0", "B0, realistic", t["ramp"][5], "-", 2.0),
             ("B1", "B1, realistic", t["ramp"][3], "-", 1.4),
             ("Optimizer, net 0", "Optimizer, realistic", t["accent"], "-", 2.0)]
    for col, label, color, ls, lw in lines:
        ax.plot(cum.index, cum[col], color=color, ls=ls, lw=lw, zorder=3)
    ends = sorted([(cum[c].iloc[-1], lab, colr) for c, lab, colr, _, _ in lines])
    ypos = [e[0] for e in ends]
    span = cum.max().max() - cum.min().min()
    for i in range(1, len(ypos)):                      # keep direct labels apart
        ypos[i] = max(ypos[i], ypos[i - 1] + 0.06 * span)
    grid_y = np.arange(-1.0, 1.01, 0.1)                # the 0.1 gridlines: no label may sit on one
    for i, y in enumerate(ypos):
        k = np.argmin(np.abs(grid_y - y))
        if abs(grid_y[k] - y) < 0.022 * span:
            ypos[i] = grid_y[k] + np.sign(y - grid_y[k] or 1.0) * 0.022 * span
    for (y, lab, colr), yy in zip(ends, ypos):
        ax.text(cum.index[-1] + pd.Timedelta(days=12), yy, f"{lab}  {y:+.2f}", color=colr, fontsize=8, va="center",
                bbox=backing(t), zorder=5)
    ax.axhline(0, color=t["baseline"], lw=0.8, zorder=2)
    ax.set_xlim(cum.index[0], cum.index[-1] + pd.Timedelta(days=300))
    years = [pd.Timestamp(f"{y}-01-01") for y in range(2022, 2027)]
    ax.set_xticks(years); ax.set_xticklabels([str(y.year) for y in years])
    titles(ax, t, "Friction, not the signal, decides the result",
           "B0 earns about nothing before costs (dashed) and loses steadily after them; grey fill is that gap. "
           "Only the turnover-penalised optimizer keeps a gain.")
    finish(fig, t, "rr-equity-curves", mode)


# ----------------------------------------------------------------------------- 2
def execution_haircut(mode):
    t = THEMES[mode]
    w = rd("11_waterfall_wf")
    fig, ax = plt.subplots(figsize=(7.2, 3.7), facecolor=t["surface"])
    style_axes(ax, t, ylabel="B0 annual return (bp per year)", xlabel="Execution assumption added, in order")
    labels = ["Same close,\nno cost", "+ one-day\ndelay", "+ 5 bp\ncost", "+ 2 bp\nslippage", "Realistic"]
    level = w["ann_return_bp"].tolist()
    bars = [(0, level[0], t["ramp"][5])]
    for i in range(1, 4):
        ch = level[i] - level[i - 1]
        bars.append((level[i - 1], ch, t["ramp"][3] if ch > 0 else t["accent"]))
    bars.append((0, level[-1], t["ramp"][5]))
    for x, (base, h, c) in enumerate(bars):
        rounded_bar(ax, x, h, base=base, width=0.56, color=c)
        top = base + h
        ax.text(x, (top if h < 0 else top) + (-28 if h < 0 else 18), f"{h:+.0f}", ha="center",
                va="top" if h < 0 else "bottom", color=t["ink"], fontsize=8.5)
        if 0 < x < 4:
            ax.plot([x - 1 + 0.28, x - 0.28], [base, base], color=t["muted"], lw=0.8, ls=":", zorder=2)
    ax.axhline(0, color=t["baseline"], lw=0.8)
    ax.set_xticks(range(5)); ax.set_xticklabels(labels, color=t["ink_secondary"], fontsize=8.5)
    ax.set_xlim(-0.6, 4.6)
    ax.set_ylim(min(level) - 120, 160)
    titles(ax, t, "Cost and slippage are what the book loses",
           "B0 over 18 walk-forward quarters; the delay helps, because the five-day horizon reverses rather than trends.")
    finish(fig, t, "rr-execution-haircut", mode)


# ----------------------------------------------------------------------------- 3
def regime_map(mode):
    t = THEMES[mode]
    g = rd("04_regime_grid_with_test")
    g = g[g["cut"] == "rolling"].set_index(["volume", "sigma"])
    order = ["low", "mid", "high"]
    Z = np.array([[g.loc[(v, s), "signal_weighted_bp"] for v in order] for s in order[::-1]])
    vmax = np.nanmax(np.abs(Z))
    fig, ax = plt.subplots(figsize=(5.6, 4.4), facecolor=t["surface"])
    ax.set_facecolor(t["surface"])
    ax.imshow(Z, cmap=diverging(t), vmin=-vmax, vmax=vmax, aspect="auto")
    for i, s in enumerate(order[::-1]):
        for j, v in enumerate(order):
            r = g.loc[(v, s)]
            strong = r.signal_weighted_bp > 0.45 * vmax          # a dark fill: box text takes the surface colour
            main, sub = (t["surface"], t["surface"]) if strong else (t["ink"], t["ink_secondary"])
            ax.text(j, i - 0.12, f"{r.signal_weighted_bp:+.1f} bp", ha="center", va="center", color=main, fontsize=9.5, fontweight="600")
            ax.text(j, i + 0.16, f"t {r.t:+.2f}\n{int(r.dates)} dates, {int(r.asset_days):,} asset-days",
                    ha="center", va="center", color=sub, fontsize=7)
    for (v, s) in (("high", "low"), ("low", "high")):
        j, i = order.index(v), order[::-1].index(s)
        ax.add_patch(Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False, ec=t["accent"], lw=2.0))
    ax.set_xticks(range(3)); ax.set_xticklabels(order); ax.set_yticks(range(3)); ax.set_yticklabels(order[::-1])
    ax.tick_params(colors=t["muted"], length=0, labelsize=8.5)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_xlabel(r"Volume tercile: rank of $V_{s,t}$ against the asset's own trailing year", color=t["muted"], fontsize=8.5, labelpad=7)
    ax.set_ylabel(r"Volatility tercile: rank of $\sigma_{s,t}$", color=t["ink_secondary"], fontsize=9, labelpad=8)
    roll = rd("04_regime_by_period_with_test")
    rr = roll[(roll.cut == "rolling") & (roll.period == "WF 2022Q1-2026Q2")].iloc[0]
    titles(ax, t, "No high-volume, low-volatility advantage",
           f"Momentum's signal-weighted forward return per 5 days, rolling cut, 18 quarters. "
           f"Ringed corners, paired by date: {rr.diff_bp:+.1f} bp (t {rr.t:+.2f}).")
    finish(fig, t, "rr-regime-map", mode)


# ----------------------------------------------------------------------------- 4
def rebuild_scorecard(mode):
    t = THEMES[mode]
    sc = rd("06_scorecard").set_index(["book", "sample"])
    bt = rd("08_robustness_rebuild_bootstrap").set_index(["sample", "mean_block"])
    samples = [("WF", "18 quarters"), ("Test", "Test, 4 quarters")]
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.6), facecolor=t["surface"])
    specs = [("d_sharpe_vs_B0", "d_sharpe", "B1 minus B0, annualised Sharpe", 1.0, "{:+.2f}"),
             ("d_turnover_pct_vs_B0", "d_turnover_pct", "B1 vs B0, turnover per unit gross (%)", 100.0, "{:+.1f}%")]
    for ax, (pcol, bcol, ylabel, k, fmt) in zip(axes, specs):
        style_axes(ax, t, ylabel=ylabel, xlabel="Sample")
        for x, (s, lab) in enumerate(samples):
            pt = sc.loc[("B1", s), pcol] * k
            lo21, hi21 = bt.loc[(s, 21), f"{bcol}_90_lo"] * k, bt.loc[(s, 21), f"{bcol}_90_hi"] * k
            lo, hi = bt.loc[s][f"{bcol}_90_lo"].min() * k, bt.loc[s][f"{bcol}_90_hi"].max() * k
            ax.plot([x, x], [lo, hi], color=t["ramp"][3], lw=1.0, zorder=2)
            ax.plot([x, x], [lo21, hi21], color=t["ramp"][5], lw=3.2, solid_capstyle="round", zorder=3)
            ax.plot([x], [pt], "o", color=t["surface"], mec=t["ramp"][5], mew=1.6, ms=7, zorder=4)
            ax.text(x + 0.11, pt, fmt.format(pt), color=t["ink"], fontsize=8.5, va="center", bbox=backing(t), zorder=5,
                    gid=f"label-{pcol}-{s}")
        ax.axhline(0, color=t["baseline"], lw=0.9, zorder=1)
        lo_lim, hi_lim = ax.get_ylim()
        for txt in [x for x in ax.texts if (x.get_gid() or "").startswith("label-")]:
            y = txt.get_position()[1]                   # a value label must not sit on the zero line
            if abs(y) < 0.06 * (hi_lim - lo_lim):
                txt.set_y(y + np.sign(y or -1.0) * 0.06 * (hi_lim - lo_lim))
        ax.set_xticks(range(len(samples))); ax.set_xticklabels([lab for _, lab in samples], color=t["ink_secondary"], fontsize=8.5)
        ax.set_xlim(-0.5, len(samples) - 0.3)
    axes[1].axhline(-14, color=t["accent"], lw=1.2, ls="--", zorder=1)
    axes[1].text(len(samples) - 0.32, -13.2, "resume: -14%", color=t["accent"], fontsize=8, ha="right", va="bottom",
                 bbox=backing(t), zorder=5)
    lo_y = min(axes[1].get_ylim()[0], -16); axes[1].set_ylim(lo_y, axes[1].get_ylim()[1])
    axes[0].set_ylim(axes[0].get_ylim()[0], max(axes[0].get_ylim()[1], 1.75))   # headroom for the note
    axes[0].set_yticks([y for y in np.arange(-1.5, 1.01, 0.5) if y >= axes[0].get_ylim()[0]])  # no gridline under it
    axes[0].text(0.02, 0.98, "B0's own Sharpe CI includes 0, so\na percentage change is undefined", transform=axes[0].transAxes,
                 color=t["muted"], fontsize=7.5, va="top", bbox=backing(t), zorder=5)
    titles(axes[0], t, "The rebuild trades a little less and earns no better",
           "Point estimate; thick bar: 90% paired bootstrap CI, mean block 21 days; thin bar: widest over blocks 5 to 63.")
    fig.subplots_adjust(wspace=0.38)
    finish(fig, t, "rr-rebuild-scorecard", mode)


# ----------------------------------------------------------------------------- 5
def macd_heatmap(mode):
    t = THEMES[mode]
    g = rd("01_macd_grid")
    g = g[(g["rule"] == "proportional") & (g["sample"] == "WF 2022Q1-2025Q2")]
    fast, slow = [1, 5, 10, 21], [5, 10, 21, 63]
    Z = np.full((len(slow), len(fast)), np.nan)
    for i, ns in enumerate(slow):
        for j, nf in enumerate(fast):
            r = g[(g.nf == nf) & (g.ns == ns)]
            if len(r):
                Z[i, j] = r["t"].iloc[0]
    ref = g[(g.nf == 12) & (g.ns == 26)]["t"].iloc[0]
    vmax = 2.0
    fig, ax = plt.subplots(figsize=(5.4, 4.2), facecolor=t["surface"])
    ax.set_facecolor(t["surface"])
    ax.imshow(np.ma.masked_invalid(Z), cmap=diverging(t), vmin=-vmax, vmax=vmax, origin="lower", aspect="auto")
    for i in range(len(slow)):
        for j in range(len(fast)):
            if np.isfinite(Z[i, j]):
                ax.text(j, i, f"t {Z[i, j]:+.2f}", ha="center", va="center", color=t["ink"], fontsize=8.5)
            else:
                ax.text(j, i, "n_f >= n_s", ha="center", va="center", color=t["muted"], fontsize=7)
    ax.set_xticks(range(len(fast))); ax.set_xticklabels(fast); ax.set_yticks(range(len(slow))); ax.set_yticklabels(slow)
    ax.tick_params(colors=t["muted"], length=0, labelsize=8.5)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_xlabel(r"Fast EMA span $n_f$ (trading days)", color=t["muted"], fontsize=8.5, labelpad=7)
    ax.set_ylabel(r"Slow EMA span $n_s$ (trading days)", color=t["ink_secondary"], fontsize=9, labelpad=8)
    titles(ax, t, "No warm band anywhere in the MACD grid",
           f"t of the G5 - G1 spread, proportional rule, 2022Q1 to 2025Q2. Conventional 12/26: t {ref:+.2f}.")
    finish(fig, t, "rr-macd-heatmap", mode)


# ============================================================================= Round 2
def r2_equity_curves(mode):
    t = THEMES[mode]
    d = rd("22_daily_excess")
    d["date"] = pd.to_datetime(d["date"]); d = d.set_index("date")
    m3 = [c for c in d.columns if c.startswith("T3")][0]
    cum = d[["T0 naive_1", "T0", "T1", m3]].cumsum()
    fig, ax = plt.subplots(figsize=(7.2, 3.9), facecolor=t["surface"])
    style_axes(ax, t, ylabel="Cumulative excess return per $1", xlabel="Date (2021-02 to 2026-06)")
    for blk, label in (("OV", "OV"), ("Test", "Test")):
        idx = d.index[d["block"] == blk]
        ax.axvspan(idx.min(), idx.max(), color=t["grid"], alpha=0.55, zorder=0, lw=0)
        ax.text(idx.min() + (idx.max() - idx.min()) / 2, 0.985, label, transform=ax.get_xaxis_transform(),
                ha="center", va="top", color=t["muted"], fontsize=8)
    lines = [("T0 naive_1", "T0, no cost", t["ramp"][5], "--", 1.2), ("T0", "T0, paper", t["ramp"][5], "-", 1.8),
             ("T1", "T1, 10% vol target", t["accent"], "-", 2.0), (m3, "T3, daily leverage", t["ramp"][3], "-", 1.2)]
    for col, _, color, ls, lw in lines:
        ax.plot(cum.index, cum[col], color=color, ls=ls, lw=lw, zorder=3)
    ends = sorted([(cum[c].iloc[-1], lab, colr) for c, lab, colr, _, _ in lines])
    span = cum.max().max() - cum.min().min()
    ypos = [e[0] for e in ends]
    for i in range(1, len(ypos)):
        ypos[i] = max(ypos[i], ypos[i - 1] + 0.09 * span)
    ypos = off_grid(ypos, 0.1, span)
    for (y, lab, colr), yy in zip(ends, ypos):
        ax.text(cum.index[-1] + pd.Timedelta(days=20), yy, f"{lab}  {y:+.2f}", color=colr, fontsize=8, va="center",
                bbox=backing(t), zorder=5)
    ax.axhline(0, color=t["baseline"], lw=0.8, zorder=2)
    ax.set_xlim(cum.index[0], cum.index[-1] + pd.Timedelta(days=330))
    years = [pd.Timestamp(f"{y}-01-01") for y in range(2022, 2027)]
    ax.set_xticks(years); ax.set_xticklabels([str(y.year) for y in years])
    ax.set_yticks([v for v in ax.get_yticks() if abs(v - round(v, 1)) < 1e-9])
    titles(ax, t, "Trend following at the paper's horizon pays, and costs barely dent it",
           "12-month look-back, 1-month hold, 40% / sigma per asset; T1 scales the book to 10% volatility and halves the drawdown.")
    finish(fig, t, "rr2-equity-curves", mode)


def r2_regime_bars(mode):
    t = THEMES[mode]
    r = rd("21_regime_returns")
    r = r[(r["cut"] == "D rolling") & (r["sample"] == "full 2021-02..2026-06") & r["book"].isin(["T0", "T1"])]
    order = ["low", "mid", "high"]
    fig, ax = plt.subplots(figsize=(6.4, 3.8), facecolor=t["surface"])
    style_axes(ax, t, ylabel="Annual excess return (%)", xlabel="VIX state: tercile of its rank against the trailing year",
               grid=False)                                          # every bar carries its value
    vals = r["ann_excess"].to_numpy() * 100
    ax.set_ylim(min(vals.min(), 0) - 12, max(vals.max(), 0) + 14)   # hand-built bars do not autoscale
    for k, (book, color) in enumerate((("T0", t["ramp"][5]), ("T1", t["accent"]))):
        sub = r[r.book == book].set_index("state")
        for j, st in enumerate(order):
            v = sub.loc[st, "ann_excess"] * 100
            x = j + (k - 0.5) * 0.34
            rounded_bar(ax, x, v, width=0.30, color=color)
            ax.text(x, v + (2.2 if v >= 0 else -2.2), f"{v:+.0f}%\nSR {sub.loc[st, 'sharpe']:+.2f}", ha="center",
                    va="bottom" if v >= 0 else "top", color=t["ink"], fontsize=7.5)
    for j, st in enumerate(order):
        days = int(r[(r.book == "T0") & (r.state == st)]["days"].iloc[0])
        ax.text(j, -0.13, f"{days} days", transform=ax.get_xaxis_transform(), ha="center", va="top", color=t["muted"], fontsize=7.5)
    ax.axhline(0, color=t["baseline"], lw=0.9)
    ax.set_xticks(range(3)); ax.set_xticklabels(order, color=t["ink_secondary"], fontsize=8.5)
    ax.set_xlim(-0.6, 2.6)
    ax.text(0.99, 0.97, "T0, the paper", transform=ax.transAxes, ha="right", va="top", color=t["ramp"][5], fontsize=8)
    ax.text(0.99, 0.89, "T1, 10% vol target", transform=ax.transAxes, ha="right", va="top", color=t["accent"], fontsize=8)
    titles(ax, t, "Trend following loses when VIX is high",
           "2021-02 to 2026-06, after costs, in excess of bills; the same pattern holds on Test alone.")
    finish(fig, t, "rr2-regime-bars", mode)


def r2_leverage_path(mode):
    t = THEMES[mode]
    d = rd("22_daily_excess")
    d["date"] = pd.to_datetime(d["date"]); d = d.set_index("date")
    fig, ax = plt.subplots(figsize=(7.2, 3.6), facecolor=t["surface"])
    style_axes(ax, t, ylabel="Gross exposure (multiple of capital)", xlabel="Date (2021-02 to 2026-06)")
    high = d["vix_state_D"] == 2
    runs = (high != high.shift()).cumsum()
    for _, seg in d[high].groupby(runs[high]):
        ax.axvspan(seg.index.min(), seg.index.max(), color=t["grid"], alpha=0.8, lw=0, zorder=0)
    ax.plot(d.index, d["T0_gross"], color=t["ramp"][5], lw=1.2, zorder=3)
    ax.plot(d.index, d["T1_gross"], color=t["accent"], lw=1.6, zorder=3)
    y0, y1 = off_grid([d["T0_gross"].iloc[-1], d["T1_gross"].iloc[-1]], 0.5, 3.6, margin=0.03)
    ax.text(d.index[-1] + pd.Timedelta(days=12), y0, "T0", color=t["ramp"][5], fontsize=8, va="center", bbox=backing(t))
    ax.text(d.index[-1] + pd.Timedelta(days=12), y1, "T1", color=t["accent"], fontsize=8, va="center", bbox=backing(t))
    ax.set_xlim(d.index[0], d.index[-1] + pd.Timedelta(days=90))
    years = [pd.Timestamp(f"{y}-01-01") for y in range(2022, 2027)]
    ax.set_xticks(years); ax.set_xticklabels([str(y.year) for y in years])
    ax.set_ylim(0, 3.6)
    titles(ax, t, "Volatility targeting cuts leverage when the tape gets loud",
           "Grey: days with VIX in the top tercile of its trailing year. T0 sits near its 3x cap; T1 moves with ex-ante risk.")
    finish(fig, t, "rr2-leverage-path", mode)


def r2_tsmom_grid(mode):
    t = THEMES[mode]
    g = rd("21_tsmom_grid")
    g = g[g["sample"] == "full 2021-02..2026-06"]
    ks, hs = sorted(g.k_months.unique()), sorted(g.h_months.unique())
    Z = np.array([[g[(g.k_months == k) & (g.h_months == h)]["sharpe"].iloc[0] for h in hs] for k in ks])
    vmax = np.nanmax(np.abs(Z))
    fig, ax = plt.subplots(figsize=(4.8, 4.2), facecolor=t["surface"])
    ax.set_facecolor(t["surface"])
    ax.imshow(Z, cmap=diverging(t), vmin=-vmax, vmax=vmax, origin="lower", aspect="auto")
    for i, k in enumerate(ks):
        for j, h in enumerate(hs):
            strong = Z[i, j] > 0.45 * vmax
            ax.text(j, i, f"{Z[i, j]:+.2f}", ha="center", va="center", color=t["surface"] if strong else t["ink"], fontsize=9)
    i, j = ks.index(12), hs.index(1)
    ax.add_patch(Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False, ec=t["accent"], lw=2.0))
    ax.set_xticks(range(len(hs))); ax.set_xticklabels(hs); ax.set_yticks(range(len(ks))); ax.set_yticklabels(ks)
    ax.tick_params(colors=t["muted"], length=0, labelsize=8.5)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_xlabel("Holding period h (months)", color=t["muted"], fontsize=8.5, labelpad=7)
    ax.set_ylabel("Look-back k (months)", color=t["ink_secondary"], fontsize=9, labelpad=8)
    titles(ax, t, "Longer look-backs carry the trend",
           "Annualised Sharpe after costs, 2021-02 to 2026-06; ringed: the paper's k = 12, h = 1.")
    finish(fig, t, "rr2-tsmom-grid", mode)


def r2_haircut(mode):
    t = THEMES[mode]
    h = rd("21_haircut_T0").set_index("sample").loc["full 2021-02..2026-06"]
    level = [h.naive_0_ann_bp]
    for k in ("delay_bp", "cost_bp", "slip_bp"):
        level.append(level[-1] + h[k])
    fig, ax = plt.subplots(figsize=(7.2, 3.7), facecolor=t["surface"])
    style_axes(ax, t, ylabel="T0 annual return (bp per year)", xlabel="Execution assumption added, in order")
    labels = ["Same close,\nno cost", "+ one-day\ndelay", "+ 5 bp\ncost", "+ 2 bp\nslippage", "Realistic"]
    bars = [(0, level[0], t["ramp"][5])]
    for i in range(1, 4):
        ch = level[i] - level[i - 1]
        bars.append((level[i - 1], ch, t["ramp"][3] if ch > 0 else t["accent"]))
    bars.append((0, level[-1], t["ramp"][5]))
    for x, (base, hgt, c) in enumerate(bars):
        rounded_bar(ax, x, hgt, base=base, width=0.56, color=c)
        top = base + hgt
        if x in (0, 4):                                 # totals: label inside the bar, clear of the gridlines
            ax.text(x, top - 18, f"{hgt:+.0f}", ha="center", va="top", color=t["surface"], fontsize=8.5, fontweight="600")
        else:
            ax.text(x, top + (14 if hgt >= 0 else -14), f"{hgt:+.0f}", ha="center", va="bottom" if hgt >= 0 else "top",
                    color=t["ink"], fontsize=8.5)
        if 0 < x < 4:
            ax.plot([x - 1 + 0.28, x - 0.28], [base, base], color=t["muted"], lw=0.8, ls=":", zorder=2)
    ax.axhline(0, color=t["baseline"], lw=0.8)
    ax.set_xticks(range(5)); ax.set_xticklabels(labels, color=t["ink_secondary"], fontsize=8.5)
    ax.set_xlim(-0.6, 4.6); ax.set_ylim(0, max(level) * 1.18)
    titles(ax, t, f"Execution takes {100 * h.H_0:.0f}% of the same-close return, {100 * h.H_1:.0f}% of the next-close one",
           "T0 over 2021-02 to 2026-06; monthly trading keeps the friction small.")
    finish(fig, t, "rr2-haircut", mode)


FIGURES = (equity_curves, execution_haircut, regime_map, rebuild_scorecard, macd_heatmap,
           r2_equity_curves, r2_regime_bars, r2_leverage_path, r2_tsmom_grid, r2_haircut)


def main():
    (HERE / "figures").mkdir(exist_ok=True)
    for f in FIGURES:
        for mode in ("light", "dark"):
            f(mode)
    print(sorted(p.name for p in (HERE / "figures").glob("rr-*.png")))


if __name__ == "__main__":
    main()
