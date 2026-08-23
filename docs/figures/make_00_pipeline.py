"""Figures for docs/00-pipeline.md.

Run from anywhere:

    python docs/figures/make_00_pipeline.py

Writes light- and dark-mode PNGs into docs/figures/. The chapter references
them through a <picture> element so GitHub serves the variant matching the
reader's theme.

Figures produced
----------------
    strategy-pipeline  the seven-stage build order, each stage gated by a question

All are schematics drawn from illustrative values.

Formulas stay in the markdown as LaTeX rather than being rendered here: text in
an image is neither selectable nor searchable.
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from _style import THEMES, save, titles


# ------------------------------------------------- fig: the strategy pipeline
def strategy_pipeline(mode):
    """00-pipeline -- the build order, seven stages, each gated by a question.

    Schematic. The point is the order and the gate: each stage does one thing,
    asks one question, and only hands on when the answer is yes. The label on
    each arrow is the object handed to the next stage.
    """
    t = THEMES[mode]
    W, H = 4.9, 0.64              # box size
    CX = 3.6                      # centre x of the chain
    GS = 0.92                     # vertical gap between box centres
    TOP = 6.3                     # centre y of the top box

    names = [
        "0 · Validate the data",
        "1 · State a hypothesis, compute a signal",
        "2 · Size the positions",
        "3 · Simulate",
        "4 · Evaluate",
        "5 · Attack the result",
        "6 · Try a model",
    ]
    questions = [
        "Can I trust a single number in this dataset?",
        "Is higher signal followed by higher forward return?",
        "How much should I bet, and is the exposure what I think it is?",
        "Does any of it survive reality?",
        "Is the strategy any good, and where does it fail?",
        "How much is real edge, and how much is search?",
        "Does a learned prediction beat the rule?",
    ]
    handoffs = [
        "trusted data", "edge confirmed", "sized book",
        "honest PnL", "verdict", "surviving baseline",
    ]

    fig, ax = plt.subplots(figsize=(9.2, 7.2))
    fig.patch.set_facecolor(t["surface"])
    ax.set_facecolor(t["surface"])
    ax.set_xlim(0, 9.6)
    ax.set_ylim(-0.5, 6.9)
    ax.axis("off")

    ys = [TOP - i * GS for i in range(len(names))]
    for name, question, y in zip(names, questions, ys):
        ax.add_patch(FancyBboxPatch(
            (CX - W / 2, y - H / 2), W, H,
            boxstyle="round,pad=0.02,rounding_size=0.15", zorder=3,
            facecolor=t["ramp"][5], edgecolor="none"))
        ax.text(CX, y + 0.10, name, ha="center", va="center",
                color=t["surface"], fontsize=9.6, fontweight="600", zorder=4)
        ax.text(CX, y - 0.145, question, ha="center", va="center",
                color=t["surface"], fontsize=7.5, alpha=0.85, zorder=4)

    for i in range(len(ys) - 1):
        y0, y1 = ys[i] - H / 2, ys[i + 1] + H / 2
        ax.annotate("", xy=(CX, y1 - 0.02), xytext=(CX, y0 + 0.02),
                    arrowprops=dict(arrowstyle="-|>", color=t["baseline"],
                                    linewidth=1.1, shrinkA=0, shrinkB=0))
        ax.plot([CX, CX + W / 2 + 0.10], [(y0 + y1) / 2] * 2,
                color=t["baseline"], linewidth=0.7, zorder=4)
        ax.text(CX + W / 2 + 0.14, (y0 + y1) / 2, handoffs[i],
                ha="left", va="center", color=t["ink_secondary"], fontsize=7.6,
                bbox=dict(boxstyle="round,pad=0.18", facecolor=t["surface"],
                          edgecolor="none"), zorder=5)

    titles(ax, t, "The build order: each stage is gated by its question",
           "seven stages in a forced order; the label on each arrow is what the stage hands on")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    save(fig, t, f"strategy-pipeline-{mode}.png")

FIGURES = (strategy_pipeline,)

if __name__ == "__main__":
    for mode in ("light", "dark"):
        for fn in FIGURES:
            fn(mode)
    print(f"wrote {2 * len(FIGURES)} figures for 00-pipeline.md")
