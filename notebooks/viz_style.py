"""
viz_style.py - shared chart styling for the Retail Shop Analysis project.

Every notebook imports this module so that all charts use the same
colours, fonts and layout. Keeping style in one place makes the
project look consistent and keeps the notebook code focused on analysis.
"""
import os
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# ---------------------------------------------------------------
# Colour palette (colour-blind-safe; validated categorical order)
# ---------------------------------------------------------------
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
MAGENTA, GREEN, VIOLET, RED = "#e87ba4", "#008300", "#6250d6", "#e34948"
GRAY = "#9a9994"            # neutral / "other"
TEXT, TEXT_2 = "#0b0b0b", "#52514e"
GRID = "#e4e3df"
SURFACE = "#fcfcfb"

# Fixed colour per product category (colour follows the entity, never its rank)
CATEGORY_COLORS = {"Technology": BLUE, "Furniture": ORANGE, "Office Supplies": AQUA}
# Diverging pair for profit (positive) vs loss (negative)
POS, NEG = BLUE, RED
# Sequential blue ramp for heatmaps (light -> dark)
SEQ_CMAP = "Blues"

# Where exported charts are saved (relative to the notebooks/ folder)
VIS_DIR = os.path.join("..", "visualizations")
os.makedirs(VIS_DIR, exist_ok=True)


def apply_style():
    """Apply a clean, report-friendly matplotlib style."""
    plt.rcParams.update({
        "figure.figsize": (10, 5.2),
        "figure.dpi": 110,
        "savefig.dpi": 160,
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "axes.edgecolor": GRID,
        "axes.labelcolor": TEXT_2,
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "axes.titlecolor": TEXT,
        "axes.titlelocation": "left",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": GRID,
        "grid.linewidth": 0.8,
        "xtick.color": TEXT_2,
        "ytick.color": TEXT_2,
        "font.size": 10,
        "legend.frameon": False,
        "lines.linewidth": 2,
    })


def money_axis(ax, axis="y"):
    """Format an axis as currency ($1.2M / $350K)."""
    def fmt(x, _):
        sign = "-" if x < 0 else ""
        x = abs(x)
        if x >= 1e6:
            return f"{sign}${x/1e6:.1f}M"
        if x >= 1e3:
            return f"{sign}${x/1e3:.0f}K"
        return f"{sign}${x:.0f}"
    target = ax.yaxis if axis == "y" else ax.xaxis
    target.set_major_formatter(mtick.FuncFormatter(fmt))


def save(fig, name):
    """Save a figure into visualizations/ and return its path."""
    path = os.path.join(VIS_DIR, name)
    fig.savefig(path, bbox_inches="tight", facecolor=SURFACE)
    return path
