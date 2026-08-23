"""Figures for docs/00-pipeline.md.

Run from anywhere:

    python docs/figures/make_00_pipeline.py

Writes light- and dark-mode PNGs into docs/figures/. The chapter references
them through a <picture> element so GitHub serves the variant matching the
reader's theme.

Figures produced
----------------
    build-order  the seven build stages with the two ways a signal gets made

All are schematics drawn from illustrative values.

Formulas stay in the markdown as LaTeX rather than being rendered here: text in
an image is neither selectable nor searchable.
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from _style import THEMES, save, titles


# ------------------------------------------------- fig: the merged build order
def build_order(mode):
    """00-pipeline -- the seven build stages with the two ways a signal gets made.

    Schematic, drawn as one figure with two coupled views. Left: the build
    order -- seven stages, each gated by the question it asks, handing a
    labelled object to the next; the brackets mark what is the strategy and
    what is only its validation. Right: the signal's two sources -- a rule
    (momentum, MACD) or a learned model (prediction) -- converge on the same
    signal, and stage 6's learned prediction feeds back to replace the rule.
    """
    t = THEMES[mode]

    # ---- chain geometry
    W, H = 4.5, 0.62            # stage panel
    CX = 3.7                    # chain centre x
    GS = 1.02                   # vertical gap between stage centres
    TOP = 8.0                   # top stage centre y

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

    fig, ax = plt.subplots(figsize=(11.0, 8.0))
    fig.patch.set_facecolor(t["surface"])
    ax.set_facecolor(t["surface"])
    ax.set_xlim(0, 13.2)
    ax.set_ylim(-0.4, 8.8)
    ax.axis("off")

    ys = [TOP - i * GS for i in range(len(names))]

    # ---- left rail: what is the strategy, what is its validation
    ax.plot([1.15, 1.02, 1.02, 1.15], [ys[0] + H / 2, ys[0] + H / 2,
                                       ys[2] - H / 2, ys[2] - H / 2],
            color=t["ramp"][5], linewidth=1.1, solid_joinstyle="miter", zorder=3)
    ax.text(0.60, (ys[0] + ys[2]) / 2, "the strategy", ha="center", va="center",
            rotation=90, color=t["ramp"][5], fontsize=8.8, fontweight="600")
    ax.plot([1.15, 1.02, 1.02, 1.15], [ys[3] + H / 2, ys[3] + H / 2,
                                       ys[5] - H / 2, ys[5] - H / 2],
            color=t["validation"], linewidth=1.1, solid_joinstyle="miter", zorder=3)
    ax.text(0.60, (ys[3] + ys[5]) / 2, "validation", ha="center", va="center",
            rotation=90, color=t["validation"], fontsize=8.8, fontweight="600")

    # ---- the seven stages: blue = strategy, green = validation, violet = the crux
    fills = [t["ramp"][5], t["accent"], t["ramp"][5],
             t["validation"], t["validation"], t["validation"], t["ramp"][4]]
    for name, question, y, fill in zip(names, questions, ys, fills):
        ax.add_patch(FancyBboxPatch(
            (CX - W / 2, y - H / 2), W, H,
            boxstyle="round,pad=0.02,rounding_size=0.15", zorder=3,
            facecolor=fill, edgecolor="none"))
        ax.text(CX, y + 0.10, name, ha="center", va="center",
                color=t["surface"], fontsize=9.6, fontweight="600", zorder=4)
        ax.text(CX, y - 0.145, question, ha="center", va="center",
                color=t["surface"], fontsize=7.4, alpha=0.85, zorder=4)

    # ---- handoff arrows + labels between stages
    for i in range(len(ys) - 1):
        y0, y1 = ys[i] - H / 2, ys[i + 1] + H / 2
        ax.annotate("", xy=(CX, y1 - 0.02), xytext=(CX, y0 + 0.02),
                    arrowprops=dict(arrowstyle="-|>", color=t["baseline"],
                                    linewidth=1.1, shrinkA=0, shrinkB=0))
        ax.plot([CX, CX + W / 2 + 0.12], [(y0 + y1) / 2] * 2,
                color=t["baseline"], linewidth=0.7, zorder=4)
        ax.text(CX + W / 2 + 0.16, (y0 + y1) / 2, handoffs[i],
                ha="left", va="center", color=t["ink_secondary"], fontsize=7.5,
                bbox=dict(boxstyle="round,pad=0.16", facecolor=t["surface"],
                          edgecolor="none"), zorder=5)

    # ---- inset: the signal's two sources, aligned with stage 1
    iy = ys[1]                          # stage 1 centre y
    ax.text(7.1, iy + 1.14, "the signal's two sources", ha="left", va="center",
            color=t["ink_secondary"], fontsize=8.2, fontstyle="italic")
    # rule box
    rb = (8.1, iy + 0.42)
    ax.add_patch(FancyBboxPatch((rb[0] - 1.15, rb[1] - 0.26), 2.3, 0.52,
                 boxstyle="round,pad=0.02,rounding_size=0.12", zorder=3,
                 facecolor=t["ramp"][3], edgecolor="none"))
    ax.text(rb[0], rb[1] + 0.07, "rule", ha="center", va="center",
            color=t["surface"], fontsize=8.4, fontweight="600", zorder=4)
    ax.text(rb[0], rb[1] - 0.13, "momentum · MACD", ha="center", va="center",
            color=t["surface"], fontsize=7.0, alpha=0.9, zorder=4)
    # model box
    mb = (8.1, iy - 0.42)
    ax.add_patch(FancyBboxPatch((mb[0] - 1.15, mb[1] - 0.26), 2.3, 0.52,
                 boxstyle="round,pad=0.02,rounding_size=0.12", zorder=3,
                 facecolor=t["ramp"][3], edgecolor="none"))
    ax.text(mb[0], mb[1] + 0.07, "ML model", ha="center", va="center",
            color=t["surface"], fontsize=8.4, fontweight="600", zorder=4)
    ax.text(mb[0], mb[1] - 0.13, r"$\rightarrow$ prediction", ha="center", va="center",
            color=t["surface"], fontsize=7.0, alpha=0.9, zorder=4)
    # signal node
    sn = (10.0, iy)
    ax.add_patch(FancyBboxPatch((sn[0] - 0.55, sn[1] - 0.26), 1.1, 0.52,
                 boxstyle="round,pad=0.02,rounding_size=0.12", zorder=3,
                 facecolor=t["accent"], edgecolor="none"))
    ax.text(sn[0], sn[1], "signal", ha="center", va="center",
            color=t["surface"], fontsize=8.4, fontweight="600", zorder=4)
    # converging arrows into the signal node
    for bx in (rb, mb):
        ax.annotate("", xy=(sn[0] - 0.58, sn[1]), xytext=(bx[0] + 1.18, bx[1]),
                    arrowprops=dict(arrowstyle="-|>", color=t["baseline"],
                                    linewidth=1.0, shrinkA=0, shrinkB=0))
    # dashed tie to stage 1
    ax.plot([CX + W / 2, 6.95], [iy, iy], color=t["muted"], linewidth=0.9,
            linestyle=(0, (3, 2)), zorder=2)
    ax.text((CX + W / 2 + 6.95) / 2, iy + 0.24, "stage 1 builds the signal",
            ha="center", va="center", color=t["muted"], fontsize=7.2,
            fontstyle="italic")

    # ---- feedback: stage 6's learned prediction replaces the rule
    fx = 11.2                              # right rail x
    ax.plot([CX + W / 2, fx], [ys[6], ys[6]], color=t["ramp"][4], linewidth=1.0, zorder=2)
    ax.plot([fx, fx], [ys[6], mb[1]], color=t["ramp"][4], linewidth=1.0, zorder=2)
    ax.annotate("", xy=(mb[0] + 1.18, mb[1]), xytext=(fx, mb[1]),
                arrowprops=dict(arrowstyle="-|>", color=t["ramp"][4], linewidth=1.0,
                                shrinkA=0, shrinkB=0))
    ax.text(fx + 0.12, (ys[6] + mb[1]) / 2, "a learned prediction\nreplaces the rule",
            ha="left", va="center", color=t["ramp"][4], fontsize=7.8,
            fontweight="600", linespacing=1.35)

    # ---- colour key
    key = [
        (t["ramp"][5], "the strategy · stages 0–2"),
        (t["validation"], "validation · stages 3–5"),
        (t["accent"], "the signal — the crux · stage 1"),
    ]
    kx0, ky = 1.8, 0.35
    for i, (color, label) in enumerate(key):
        x0 = kx0 + i * 3.6
        ax.add_patch(FancyBboxPatch((x0, ky - 0.13), 0.8, 0.26,
                     boxstyle="round,pad=0.02,rounding_size=0.08", zorder=3,
                     facecolor=color, edgecolor="none"))
        ax.text(x0 + 0.95, ky, label, ha="left", va="center",
                color=t["ink_secondary"], fontsize=7.6)

    titles(ax, t, "How a CTA strategy is built",
           "seven stages, each gated by its question; blue = strategy, teal = validation, amber = the signal, the crux")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    save(fig, t, f"build-order-{mode}.png")


FIGURES = (build_order,)

if __name__ == "__main__":
    for mode in ("light", "dark"):
        for fn in FIGURES:
            fn(mode)
    print(f"wrote {2 * len(FIGURES)} figures for 00-pipeline.md")
