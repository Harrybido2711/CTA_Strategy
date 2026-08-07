"""Figures for docs/00-pipeline.md.

Run from anywhere:

    python docs/figures/make_00_pipeline.py

Writes light- and dark-mode PNGs into docs/figures/. The chapter references
them through a <picture> element so GitHub serves the variant matching the
reader's theme.

Figures produced
----------------
    strategy-pipeline  which stages are the strategy and which only measure it

All are schematics drawn from illustrative values.

Formulas stay in the markdown as LaTeX rather than being rendered here: text in
an image is neither selectable nor searchable.
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from _style import THEMES, save, titles


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

FIGURES = (strategy_pipeline,)

if __name__ == "__main__":
    for mode in ("light", "dark"):
        for fn in FIGURES:
            fn(mode)
    print(f"wrote {2 * len(FIGURES)} figures for 00-pipeline.md")
