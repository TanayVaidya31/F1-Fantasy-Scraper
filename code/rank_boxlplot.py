import glob
import os
import re

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
ANALYSIS_DIR = os.path.join(PROJECT_ROOT, "analysis")
os.makedirs(ANALYSIS_DIR, exist_ok=True)

round_files = sorted(
    glob.glob(os.path.join(PROCESSED_DIR, "R*", "players.csv")),
    key=lambda path: int(re.search(r"R(\d+)", path, re.IGNORECASE).group(1)) if re.search(r"R(\d+)", path, re.IGNORECASE) else 0,
)

history_frames = []
for path in round_files:
    round_name = os.path.basename(os.path.dirname(path))
    if round_name.upper() == "R0":
        continue

    df = pd.read_csv(path)
    if "Name" not in df.columns or "Team" not in df.columns or "Rank" not in df.columns:
        continue

    df = df.loc[:, ["Name", "Team", "Rank"]].copy()
    df["Round"] = round_name
    df = df.dropna(subset=["Team"])
    df["Rank"] = pd.to_numeric(df["Rank"], errors="coerce")
    history_frames.append(df)

if not history_frames:
    raise FileNotFoundError("No processed round players.csv files found.")

history = pd.concat(history_frames, ignore_index=True)
history = history.dropna(subset=["Rank"])

player_order = (
    history.groupby("Team")
    ["Rank"]
    .mean()
    .sort_values()
    .index
    .tolist()
)

# Create labels: for each team, use the name of the player with the best (lowest) average rank
label_dict = {}
for team in player_order:
    team_data = history[history["Team"] == team]
    best_player = (
        team_data.groupby("Name")["Rank"]
        .mean()
        .sort_values()
        .index[0]
    )
    label_dict[team] = best_player

labels = [label_dict[team] for team in player_order]

# sns.set_style("whitegrid")
fig, ax = plt.subplots(figsize=(14, 8))

sns.boxplot(
    data=history,
    x="Team",
    y="Rank",
    order=player_order,
    ax=ax,
    palette='PRGn',
    width=0.6,
    fliersize=3,
    linewidth=1
)

ax.set_title("All Players: Rank Distribution Across All Races", fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel("Player", fontsize=12, fontweight='bold')
ax.set_ylabel("Rank", fontsize=12, fontweight='bold')
ax.set_xticklabels(labels, rotation=45, ha="right")
ax.set_ylim(0, history["Rank"].max()+1)
ax.invert_yaxis()
ax.grid(True, axis="y", linestyle="--", alpha=0.5)
fig.tight_layout()

output_path = os.path.join(ANALYSIS_DIR, "rank_box_all.png")
fig.savefig(output_path, dpi=180, bbox_inches="tight")
plt.close(fig)

print(f"Saved all-players rank box plot to: {output_path}")
