"""Figures for docs/00_pipeline.tex.

Run from anywhere:

    python docs/figures/make_00_pipeline.py

Writes light- and dark-mode PNGs into docs/figures/. The chapter references
them through a <picture> element so GitHub serves the variant matching the
reader's theme.

Figures produced
----------------
    execution-haircut   what each execution assumption removes from the naive return
    regime-map          where the edge lives, on a volume x volatility grid
    rebuild-scorecard   baseline against rebuild, on Sharpe and on turnover
    build-order         the eight build stages, and the loop back to the signal

All are schematics drawn from illustrative values. The three story figures show
the *shape* of the project's result -- the erosion, the corner the edge lives
in, the direction the rebuild moved -- not its measured numbers, which live in
the prototype notes.

Formulas stay in the markdown as LaTeX rather than being rendered here: text in
an image is neither selectable nor searchable.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # figures/, for _style

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch
from _style import THEMES, rounded_bar, save, set_out, style_axes, titles

set_out(Path(__file__).resolve().parent)


def _relative_luminance(hex_colour):
    """WCAG relative luminance of a #rrggbb string."""
    channels = []
    for i in (1, 3, 5):
        c = int(hex_colour[i:i + 2], 16) / 255
        channels.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    r, g, b = channels
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _cell_ink(fill, t):
    """Whichever of the theme's two ink tokens reads better on this fill.

    Only the ramp needs this: it runs light to dark inside one theme, so a
    single ink token would go unreadable at one end. Solid brand fills use the
    surface token directly, as the rest of the figures do.
    """
    lf = _relative_luminance(fill)
    def contrast(other):
        lo, hi = sorted((lf, _relative_luminance(other)))
        return (hi + 0.05) / (lo + 0.05)
    return max((t["ink"], t["surface"]), key=contrast)


# ------------------------------------ fig: what execution takes off the top
def execution_haircut(mode):
    """00 s1.3 -- the naive return, and the three assumptions that eat it.

    Schematic waterfall. The naive backtest is indexed to 100; transaction
    costs, slippage and a one-day execution delay are each subtracted in turn,
    leaving the return the strategy would actually have banked. The split
    between the three is illustrative; the total -- over a quarter of the naive
    return -- is the project's measured finding.
    """
    t = THEMES[mode]

    steps = [-11.0, -7.0, -8.0]                       # costs, slippage, delay
    naive = 100.0
    traded = naive + sum(steps)

    labels = ["naive\nbacktest", "transaction\ncosts", "slippage",
              "execution\ndelay", "as\ntraded"]

    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    fig.patch.set_facecolor(t["surface"])

    # end bars sit on the floor; the three deductions float between them
    rounded_bar(ax, 0, naive, base=0.0, width=0.52, color=t["ramp"][5])
    base = naive
    for i, step in enumerate(steps, start=1):
        rounded_bar(ax, i, step, base=base, width=0.52, color=t["ramp"][3])
        ax.text(i, base + step - 4.0, f"{step:+.0f}", ha="center", va="top",
                color=t["ink_secondary"], fontsize=8.6, fontweight="600")
        base += step
    rounded_bar(ax, 4, traded, base=0.0, width=0.52, color=t["accent"])

    # dashed connectors carry each running level across to the next bar
    level = naive
    for i, step in enumerate(steps):
        ax.plot([i + 0.26, i + 1.26], [level] * 2, color=t["baseline"],
                linewidth=0.9, linestyle=(0, (3, 2)), zorder=2)
        level += step
    ax.plot([3.26, 4.26], [traded] * 2, color=t["baseline"],
            linewidth=0.9, linestyle=(0, (3, 2)), zorder=2)

    for x, v in ((0, naive), (4, traded)):
        ax.text(x, v + 3.5, f"{v:.0f}", ha="center", va="bottom",
                color=t["ink"], fontsize=9.4, fontweight="600")

    # the bracket that is the headline: everything between the two end bars
    bx = 4.45
    ax.plot([bx - 0.06, bx, bx, bx - 0.06], [traded, traded, naive, naive],
            color=t["accent"], linewidth=1.1, solid_joinstyle="miter", zorder=4)
    ax.text(bx + 0.12, (naive + traded) / 2,
            "over a quarter of\nthe naive return,\ngone before a\nsingle judgement\nabout the market",
            ha="left", va="center", color=t["accent"], fontsize=8.2,
            fontweight="600", linespacing=1.45)

    style_axes(ax, t, ylabel="cumulative return over the sample,\nnaive backtest = 100",
               xlabel="the naive result, and what each execution assumption removes")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=8.4)
    ax.set_xlim(-0.6, 6.0)
    ax.set_ylim(0, 118)
    ax.set_yticks([0, 25, 50, 75, 100])

    titles(ax, t, "Execution is not a rounding error",
           "illustrative split; the total erosion is the project's measured result")
    fig.tight_layout(rect=(0, 0, 1, 0.87))
    save(fig, t, f"execution-haircut-{mode}.png")


# ------------------------------------------- fig: where the edge actually lives
def regime_map(mode):
    """00 s1.4 -- the same signal, sorted by how liquid and how violent the tape is.

    Schematic. Each cell is the top-minus-bottom bucket spread the momentum
    signal delivered inside that regime, in basis points. The edge is not
    spread evenly over the sample: it concentrates in the high-volume,
    low-volatility corner and is close to nothing in the opposite one. An
    unconditional backtest averages the whole grid into a single number.
    """
    t = THEMES[mode]

    rows = ["high\n$\\sigma_{s,t}$", "mid\n$\\sigma_{s,t}$", "low\n$\\sigma_{s,t}$"]
    cols = ["low $V_{s,t}$", "mid $V_{s,t}$", "high $V_{s,t}$"]
    cells = np.array([
        [+2, +5, +9],        # high volatility -- whipsaw, nothing survives
        [+8, +14, +21],      # mid
        [+13, +26, +38],     # low volatility, heavy volume -- the corner
    ], dtype=float)

    lo, hi = cells.min(), cells.max()
    ramp = t["ramp"]

    fig, ax = plt.subplots(figsize=(6.6, 4.2))
    fig.patch.set_facecolor(t["surface"])
    ax.set_facecolor(t["surface"])

    for i in range(cells.shape[0]):
        for j in range(cells.shape[1]):
            score = (cells[i, j] - lo) / (hi - lo)
            shade = ramp[int(round(score * (len(ramp) - 1)))]
            ax.add_patch(plt.Rectangle((j, i), 1, 1, facecolor=shade,
                                       edgecolor=t["surface"], linewidth=1.8, zorder=2))
            ax.text(j + 0.5, i + 0.5, f"{cells[i, j]:+.0f}", ha="center", va="center",
                    color=_cell_ink(shade, t), fontsize=10.0, fontweight="600", zorder=4)

    # ring the corner the rebuild was aimed at
    ax.add_patch(plt.Rectangle((2.04, 2.04), 0.92, 0.92, facecolor="none",
                               edgecolor=t["accent"], linewidth=1.8, zorder=5))
    ax.annotate("", xy=(2.98, 2.5), xytext=(3.52, 2.5),
                arrowprops=dict(arrowstyle="-|>", color=t["accent"],
                                linewidth=1.1, shrinkA=0, shrinkB=0), zorder=5)
    ax.text(3.60, 2.5, "liquid and calm:\nwhere the signal\nkept working",
            ha="left", va="center", color=t["accent"], fontsize=8.2,
            fontweight="600", linespacing=1.45)
    ax.text(3.60, 0.5, "violent and thin:\nthe backtest was\nbeing paid for\nrisk it could\nnot repeat",
            ha="left", va="center", color=t["ink_secondary"], fontsize=8.2,
            linespacing=1.45)

    ax.set_xlim(0, 6.5)
    ax.set_ylim(0, 3)
    ax.set_xticks(np.arange(len(cols)) + 0.5)
    ax.set_yticks(np.arange(len(rows)) + 0.5)
    ax.set_xticklabels(cols, fontsize=9)
    ax.set_yticklabels(rows, fontsize=8.8)
    ax.tick_params(colors=t["muted"], length=0)
    for side in ax.spines.values():
        side.set_visible(False)
    ax.set_xlabel("rolling 21-day volume $V_{s,t}$, in terciles",
                  color=t["ink_secondary"], fontsize=9.2, labelpad=8)
    ax.set_ylabel("rolling 21-day realized\nvolatility $\\sigma_{s,t}$, in terciles",
                  color=t["ink_secondary"], fontsize=9.2, labelpad=8)

    titles(ax, t, "The edge has an address",
           "illustrative — top-minus-bottom bucket spread in basis points, per regime cell")
    fig.tight_layout(rect=(0, 0, 1, 0.89))
    save(fig, t, f"regime-map-{mode}.png")


# ------------------------------------------- fig: what the rebuild bought
def rebuild_scorecard(mode):
    """00 s1.5 -- the rebuild moved two numbers, in opposite directions.

    Schematic. Left: out-of-sample Sharpe, which the rebuild raised. Right:
    annual turnover, which it cut. Both panels are drawn at illustrative
    levels; the percentage changes between the pairs are the project's measured
    result, and the point of showing them together is that neither is worth
    reading alone.
    """
    t = THEMES[mode]

    panels = [
        ("out-of-sample Sharpe ratio", (0.38, 0.41), "{:.2f}", 0.62, "+8%"),
        ("annual turnover, multiples of book", (5.2, 4.5), "{:.1f}", 7.6, "-14%"),
    ]

    fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.6))
    fig.patch.set_facecolor(t["surface"])

    for ax, (ylabel, (before, after), fmt, top, delta) in zip(axes, panels):
        for x, v, colour in ((0, before, t["ramp"][4]), (1, after, t["accent"])):
            rounded_bar(ax, x, v, base=0.0, width=0.44, color=colour)
            ax.text(x, v + top * 0.035, fmt.format(v), ha="center", va="bottom",
                    color=t["ink"], fontsize=9.6, fontweight="600")

        ax.annotate("", xy=(1, top * 0.86), xytext=(0, top * 0.86),
                    arrowprops=dict(arrowstyle="-|>", color=t["accent"],
                                    linewidth=1.1, shrinkA=0, shrinkB=0))
        ax.text(0.5, top * 0.885, delta, ha="center", va="bottom",
                color=t["accent"], fontsize=9.6, fontweight="600")

        style_axes(ax, t, ylabel=ylabel, xlabel="strategy version")
        ax.set_xticks([0, 1])
        ax.set_xticklabels(["baseline", "rebuilt"], fontsize=8.8)
        ax.set_xlim(-0.6, 1.6)
        ax.set_ylim(0, top)

    titles(axes[0], t, "What the rebuild bought, and what it cost",
           "illustrative levels; the changes between each pair are the project's measured result")
    fig.tight_layout(rect=(0, 0, 1, 0.86))
    save(fig, t, f"rebuild-scorecard-{mode}.png")


# ------------------------------------------------- fig: the merged build order
def build_order(mode):
    """00 s3 -- the eight build stages, each gated by the question it asks.

    Schematic. One column, read downward: every stage does one thing, answers
    one question, and hands a named object to the next. The right column is
    what actually judges the stage. The violet return on the left is the second
    lap -- the diagnosis from stage 5 re-enters at stage 1 as a better signal,
    which is the shape of this project rather than an optional extra.
    """
    t = THEMES[mode]

    W, H = 5.4, 0.60            # stage card
    CX = 5.0                    # card centre x
    GS = 0.92                   # vertical gap between card centres
    TOP = 7.20                  # top card centre y
    GATE_X = 8.05               # left edge of the "what judges it" column
    LOOP_X = 1.35               # the return path's rail

    names = [
        "0 · Validate the data",
        "1 · Compute a signal",
        "2 · Size the positions",
        "3 · Simulate under execution",
        "4 · Evaluate",
        "5 · Attack the result",
        "6 · Rebuild against the diagnosis",
        "7 · Try a model",
    ]
    questions = [
        "Can I trust a single number in this dataset?",
        "Is a higher signal followed by a higher forward return?",
        "How much do I bet, and is the exposure what I think it is?",
        "How much of it survives costs, slippage and delay?",
        "Is it any good, and where exactly does it fail?",
        "How much is edge, and how much is search?",
        "Does the edge improve where the diagnosis said it would?",
        "Does a learned prediction beat the rule?",
    ]
    gates = [
        "continuity, split adjustment,\nan alignment checked by hand",
        "bucket monotonicity, the G5 − G1 spread\nagainst its error bars, turnover",
        "gross and net exposure, turnover",
        "cost and delay drag, and no\nimplausibly smooth equity curve",
        "Sharpe, maximum drawdown,\nhit rate, read beside the curve",
        "regime-conditional spread,\nout-of-sample and deflated Sharpe",
        "out-of-sample Sharpe and turnover,\nagainst the same baseline",
        "test IC, and its mean over\nits own standard deviation",
    ]
    handoffs = [
        "trusted data", "edge confirmed", "sized book", "honest PnL",
        "verdict", "a diagnosis", "a better signal",
    ]

    fig, ax = plt.subplots(figsize=(10.0, 6.7))
    fig.patch.set_facecolor(t["surface"])
    ax.set_facecolor(t["surface"])
    ax.set_xlim(0, 11.9)
    ax.set_ylim(-0.62, 7.83)
    ax.axis("off")

    ys = [TOP - i * GS for i in range(len(names))]

    # blue builds it, green measures it, violet is the signal and the lap back to it
    fills = [t["ramp"][5], t["accent"], t["ramp"][5],
             t["validation"], t["validation"], t["validation"],
             t["accent"], t["ramp"][4]]

    ax.text(CX - W / 2, ys[0] + H / 2 + 0.30, "the stage, and the question it must answer",
            ha="left", va="center", color=t["muted"], fontsize=8.2, fontstyle="italic")
    ax.text(GATE_X, ys[0] + H / 2 + 0.30, "what judges it",
            ha="left", va="center", color=t["muted"], fontsize=8.2, fontstyle="italic")

    for name, question, gate, y, fill in zip(names, questions, gates, ys, fills):
        ax.add_patch(FancyBboxPatch(
            (CX - W / 2, y - H / 2), W, H,
            boxstyle="round,pad=0.02,rounding_size=0.14", zorder=3,
            facecolor=fill, edgecolor="none"))
        ax.text(CX, y + 0.115, name, ha="center", va="center",
                color=t["surface"], fontsize=9.4, fontweight="600", zorder=4)
        ax.text(CX, y - 0.135, question, ha="center", va="center",
                color=t["surface"], fontsize=7.3, alpha=0.88, zorder=4)
        ax.text(GATE_X, y, gate, ha="left", va="center",
                color=t["ink_secondary"], fontsize=7.4, linespacing=1.45)

    # handoff arrows, with the object named on the arrow itself
    for i in range(len(ys) - 1):
        y0, y1 = ys[i] - H / 2, ys[i + 1] + H / 2
        ax.annotate("", xy=(CX, y1 - 0.01), xytext=(CX, y0 + 0.01),
                    arrowprops=dict(arrowstyle="-|>", color=t["baseline"],
                                    linewidth=1.1, shrinkA=0, shrinkB=0))
        ax.text(CX, (y0 + y1) / 2, handoffs[i], ha="center", va="center",
                color=t["ink_secondary"], fontsize=7.2, zorder=5,
                bbox=dict(boxstyle="round,pad=0.18", facecolor=t["surface"],
                          edgecolor="none"))

    # the second lap: the diagnosis re-enters at the signal
    x_edge = CX - W / 2
    ax.plot([x_edge, LOOP_X, LOOP_X], [ys[6], ys[6], ys[1]],
            color=t["accent"], linewidth=1.2, solid_joinstyle="round", zorder=2)
    ax.annotate("", xy=(x_edge - 0.02, ys[1]), xytext=(LOOP_X, ys[1]),
                arrowprops=dict(arrowstyle="-|>", color=t["accent"],
                                linewidth=1.2, shrinkA=0, shrinkB=0))
    ax.text(LOOP_X - 0.22, (ys[1] + ys[6]) / 2,
            "the second lap — regime-aware features,\nvolatility scaling, turnover control",
            ha="center", va="center", rotation=90, color=t["accent"],
            fontsize=8.0, fontweight="600", linespacing=1.5)

    # colour key
    key = [
        (1.25, t["ramp"][5], "build the strategy · 0–2"),
        (3.95, t["validation"], "measure it · 3–5"),
        (6.05, t["accent"], "the crux, and the lap back · 1, 6"),
        (9.40, t["ramp"][4], "optional extension · 7"),
    ]
    ky = -0.36
    for kx, colour, label in key:
        ax.add_patch(FancyBboxPatch((kx, ky - 0.12), 0.62, 0.24,
                     boxstyle="round,pad=0.02,rounding_size=0.07", zorder=3,
                     facecolor=colour, edgecolor="none"))
        ax.text(kx + 0.76, ky, label, ha="left", va="center",
                color=t["ink_secondary"], fontsize=7.6)

    titles(ax, t, "How this strategy was built",
           "eight stages, each gated by one question — and the return path that made it a rebuild")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    save(fig, t, f"build-order-{mode}.png")


FIGURES = (execution_haircut, regime_map, rebuild_scorecard, build_order)

if __name__ == "__main__":
    for mode in ("light", "dark"):
        for fn in FIGURES:
            fn(mode)
    print(f"wrote {2 * len(FIGURES)} figures for 00_pipeline")
