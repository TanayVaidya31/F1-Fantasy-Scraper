import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from plottable import Table, ColumnDefinition
from plottable.cmap import normed_cmap
from matplotlib.colors import LinearSegmentedColormap

CURRENT_DIR = os.path.abspath(__file__)
PROJECT_ROOT = CURRENT_DIR
for _ in range(3):
    PROJECT_ROOT = os.path.dirname(PROJECT_ROOT)

processed_dir = os.path.join(PROJECT_ROOT, "data", "processed")
output_dir = os.path.join(PROJECT_ROOT, "analysis", "confidential_analysis", "plottable_imgs_exp")
os.makedirs(output_dir, exist_ok=True)

race_folders = sorted(
    [f for f in os.listdir(processed_dir) if f.startswith("R") and f != "R0"],
    key=lambda x: int(x.lstrip("R")),
    reverse=True,
)

COLUMNS = ["Overall Rank", "Team", "Name", "Total Points", "Total Cost Cap", "Transfers Left"]

# ── Colour palette ─────────────────────────────────────────────────────────────
BG_COLOR     = "#0f1117"
HEADER_BG    = "#1a1d2e"
ODD_ROW      = "#13161f"
EVEN_ROW     = "#181b27"
BORDER_COLOR = "#2a2d3e"
TEXT_PRIMARY = "#e8eaf6"
TEXT_DIM     = "#8890b5"
ACCENT       = "#7c4dff"

# Colour scales: low → high
POINTS_CMAP = LinearSegmentedColormap.from_list(
    "points", ["#C8B32C", "#c4c424", "#2DB026", "#7630c2", "#7d30b5"],
)
COST_CMAP = LinearSegmentedColormap.from_list(
    "cost", ["#1a1d2e", "#2d4a7a", "#1565c0", "#42a5f5", "#80d8ff"],
)


def build_column_defs(df: pd.DataFrame) -> list:
    pts_cmap  = normed_cmap(df["Total Points"],   cmap=POINTS_CMAP, num_stds=2.5)
    cost_cmap = normed_cmap(df["Total Cost Cap"], cmap=COST_CMAP,   num_stds=2.5)

    return [
        ColumnDefinition(
            name="Team",
            width=1.8,
            textprops={"ha": "left", "color": TEXT_DIM, "fontsize": 9},
        ),
        ColumnDefinition(
            name="Name",
            width=2.0,
            textprops={"ha": "left", "color": TEXT_PRIMARY, "fontsize": 9, "fontweight": "bold"},
        ),
        ColumnDefinition(
            name="Total Points",
            width=1.4,
            textprops={"ha": "center", "color": TEXT_PRIMARY, "fontsize": 9, "fontweight": "bold"},
            cmap=pts_cmap,
        ),
        ColumnDefinition(
            name="Total Cost Cap",
            width=1.4,
            textprops={"ha": "center", "color": TEXT_PRIMARY, "fontsize": 9, "fontweight": "bold"},
            cmap=cost_cmap,
            formatter=lambda v: f"{v:.1f}",
        ),
        ColumnDefinition(
            name="Transfers Left",
            width=1.3,
            textprops={"ha": "center", "color": TEXT_DIM, "fontsize": 9},
        ),
    ]


for folder in race_folders:
    file_path = os.path.join(processed_dir, folder, "playerinfo.csv")
    if not os.path.exists(file_path):
        continue

    df = pd.read_csv(file_path)
    df.insert(0, "Overall Rank", range(1, len(df) + 1))
    df = df.rename(columns={
        "Total_Points":   "Total Points",
        "Total_Cost_Cap": "Total Cost Cap",
        "Swaps_Rem":      "Transfers Left",
    })
    df = df[COLUMNS].copy()
    df["Total Points"]   = df["Total Points"].round(0).astype("Int64")
    df["Total Cost Cap"] = df["Total Cost Cap"].round(1)
    df = df.set_index("Overall Rank")

    n_rows = len(df)
    fig_h  = max(5, n_rows * 0.42 + 2.5)
    fig, ax = plt.subplots(figsize=(15, fig_h))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.axis("off")

    # ── Table ──────────────────────────────────────────────────────────────────
    # Header cell styling is done via col_label_cell_kw (background) and
    # textprops (global text defaults). Per-column text is set in ColumnDefinition.
    tab = Table(
        df,
        ax=ax,
        column_definitions=build_column_defs(df),
        row_dividers=True,
        col_label_divider=True,
        footer_divider=False,
        odd_row_color=ODD_ROW,
        even_row_color=EVEN_ROW,
        # Global text defaults (headers inherit these unless overridden)
        textprops={"color": TEXT_PRIMARY, "fontsize": 9},
        # Style the header row background + text globally
        col_label_cell_kw={"facecolor": HEADER_BG},
        row_divider_kw={"linewidth": 0.4, "linestyle": "-", "color": BORDER_COLOR},
        col_label_divider_kw={"linewidth": 1.2, "linestyle": "-", "color": ACCENT},
    )

    # ── Post-render: style data cells via tab.columns / tab.rows ───────────────
    # Accent colour + bold for the rank column data cells
    tab.columns["Overall Rank"].set_fontcolor(ACCENT)

    # Bold + bright for header labels (column label row is row index 0 in plottable)
    # Use tab.rows to set font on all data rows uniformly if needed
    # Style individual column header texts via the col_label cells directly
    for col_name in df.reset_index().columns:
        if col_name in tab.columns:
            # Make header text bold and sized correctly
            col_obj = tab.columns[col_name]
            # col_label_cell is the first cell (index 0) in the column sequence
            if hasattr(col_obj, 'column_label'):
                col_obj.column_label.set_text_props(fontweight="bold", fontsize=9.5)

    # ── Title block ────────────────────────────────────────────────────────────
    race_num = int(folder.lstrip("R"))

    fig.text(
        0.5, 0.97, f"RACE  {race_num}",
        ha="center", va="top",
        fontsize=22, fontweight="bold",
        color=TEXT_PRIMARY, fontfamily="monospace",
        transform=fig.transFigure,
    )
    fig.text(
        0.5, 0.93, "PLAYER  STANDINGS",
        ha="center", va="top",
        fontsize=9.5, color=TEXT_DIM, fontfamily="monospace",
        transform=fig.transFigure,
    )
    fig.add_artist(plt.Line2D(
        [0.12, 0.88], [0.915, 0.915],
        transform=fig.transFigure,
        color=ACCENT, linewidth=1.2, alpha=0.7,
    ))

    # ── Colour-scale legend strips ─────────────────────────────────────────────
    for x_pos, cmap, label in [
        (0.565, POINTS_CMAP, "Points scale →"),
        (0.72,  COST_CMAP,   "Cost scale →"),
    ]:
        lax = fig.add_axes([x_pos, 0.005, 0.135, 0.016])
        lax.imshow(np.linspace(0, 1, 256).reshape(1, -1), aspect="auto", cmap=cmap)
        lax.set_yticks([])
        lax.set_xticks([])
        for spine in lax.spines.values():
            spine.set_visible(False)
        lax.set_title(label, color=TEXT_DIM, fontsize=6.5, pad=2)

    # ── Save ───────────────────────────────────────────────────────────────────
    out_path = os.path.join(output_dir, f"race_{race_num}_playerinfo.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=BG_COLOR)
    plt.close()
    print(f"Saved: {out_path}")