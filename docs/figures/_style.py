"""Shared design tokens and drawing primitives for the docs/ figures.

Every chapter's ``make_*.py`` imports from here, so the figures stay one visual
system: single-hue marks, rounded data-ends squared at the baseline, hairline
recessive gridlines, labels in ink tokens (never the series colour), and
light/dark variants stepped for their own surface rather than colour-flipped.

Change a token here and every chapter's figures move together. That is the point
of this module -- do not re-declare colours inside a chapter script.
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyBboxPatch, PathPatch
from matplotlib.path import Path as MplPath

# Where the PNGs land. Each chapter's figures live beside their generator in
# figures/<NN>_figures/, so a chapter script announces its own directory with
# set_out(Path(__file__).resolve().parent) before it draws anything.
OUT = Path(__file__).resolve().parent
DATA = Path(__file__).resolve().parents[2] / "CTA_data"


def set_out(path):
    """Point save() at this chapter's figure directory."""
    global OUT
    OUT = Path(path).resolve()

# ---------------------------------------------------------------- design tokens
THEMES = {
    "light": dict(
        surface="#fcfcfb",
        ink="#0b0b0b",
        ink_secondary="#52514e",
        muted="#898781",
        grid="#e1e0d9",
        baseline="#c3c2b7",
        series="#2a78d6",
        wash="#2a78d6",
        accent="#6d28d9",       # violet: the crux, what the strategy hinges on
        validation="#1f8f63",   # green: what only measures the strategy
        # sequential blue ramp, steps 100 -> 700; lightest = near zero
        ramp=["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"],
    ),
    "dark": dict(
        surface="#1a1a19",
        ink="#ffffff",
        ink_secondary="#c3c2b7",
        muted="#898781",
        grid="#2c2c2a",
        baseline="#383835",
        series="#3987e5",
        wash="#3987e5",
        accent="#8b5cf6",       # violet for a dark surface: the crux
        validation="#35a37a",   # green for a dark surface
        # on a dark surface "near zero" must recede toward the surface, so the
        # same single hue runs dark -> light instead of light -> dark
        ramp=["#0d366b", "#184f95", "#256abf", "#3987e5", "#6da7ec", "#9ec5f4", "#cde2fb"],
    ),
}

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
    "mathtext.fontset": "dejavusans",
    "axes.linewidth": 0.8,
    "figure.dpi": 200,
    "savefig.dpi": 200,
})


# ------------------------------------------------------------------- primitives
def rounded_bar(ax, x, height, base=0.0, width=0.30, color="#2a78d6", zorder=3):
    """A column with a rounded data-end and a square baseline end.

    bar() gives square corners and FancyBboxPatch rounds all four, so the path is
    built by hand: straight at the baseline, arced at the tip.
    """
    x0, x1 = x - width / 2, x + width / 2
    tip = base + height
    s = 1.0 if height >= 0 else -1.0
    r = min(abs(height) * 0.22, width * 0.30) * s
    k = width * 0.30

    verts = [(x0, base), (x0, tip - r),
             (x0, tip), (x0 + k, tip),
             (x1 - k, tip),
             (x1, tip), (x1, tip - r),
             (x1, base), (x0, base)]
    codes = [MplPath.MOVETO, MplPath.LINETO,
             MplPath.CURVE3, MplPath.CURVE3,
             MplPath.LINETO,
             MplPath.CURVE3, MplPath.CURVE3,
             MplPath.LINETO, MplPath.CLOSEPOLY]
    ax.add_patch(PathPatch(MplPath(verts, codes), facecolor=color,
                           edgecolor="none", zorder=zorder))


def style_axes(ax, t, ylabel=None, xlabel=None, grid=True):
    ax.set_facecolor(t["surface"])
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(t["baseline"])
    ax.tick_params(colors=t["muted"], length=0, labelsize=8.5)
    if grid:
        ax.yaxis.grid(True, color=t["grid"], linewidth=0.8, linestyle="-", zorder=0)
    ax.set_axisbelow(True)
    if ylabel:
        ax.set_ylabel(ylabel, color=t["ink_secondary"], fontsize=9, labelpad=8)
    if xlabel:
        ax.set_xlabel(xlabel, color=t["muted"], fontsize=8.5, labelpad=7)


def titles(ax, t, title, subtitle):
    """Title and subtitle as stacked axes-space text, so they never collide."""
    ax.text(0, 1.145, title, transform=ax.transAxes,
            color=t["ink"], fontsize=11.5, fontweight="600", va="bottom")
    ax.text(0, 1.045, subtitle, transform=ax.transAxes,
            color=t["ink_secondary"], fontsize=8.8, va="bottom")


def save(fig, t, name):
    fig.savefig(OUT / name, facecolor=t["surface"], bbox_inches="tight", pad_inches=0.28)
    plt.close(fig)
