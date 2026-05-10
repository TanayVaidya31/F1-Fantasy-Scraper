import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import os

sns.set_theme(style="whitegrid")

# =========================================================
# PATH SETUP
# =========================================================
CURRENT_DIR = os.path.abspath(__file__)
PROJECT_ROOT = CURRENT_DIR

for _ in range(3):
    PROJECT_ROOT = os.path.dirname(PROJECT_ROOT)

processed_dir = os.path.join(
    PROJECT_ROOT,
    'data',
    'processed'
)

# =========================================================
# LOAD DATA
# =========================================================
race_folders = [
    f for f in os.listdir(processed_dir)
    if f.startswith('R')
]

race_folders.sort(
    key=lambda x: int(x[1:])
)

players_dfs = {}
combined_dfs = []

for folder in race_folders:

    players_path = os.path.join(
        processed_dir,
        folder,
        'players.csv'
    )

    players_df = pd.read_csv(players_path)

    players_df['Race'] = folder
    players_df['RaceNumber'] = int(folder[1:])

    players_df['UsedLimitless'] = (
        players_df['Chips']
        .fillna('')
        .str.strip()
        .str.lower()
        .eq('limitless')
    )

    players_dfs[folder] = players_df
    combined_dfs.append(players_df)

combined_df = pd.concat(
    combined_dfs,
    ignore_index=True
)

# =========================================================
# DYNAMIC COLOUR HELPERS
# =========================================================
race_list = sorted(
    combined_df['Race'].unique(),
    key=lambda x: int(x[1:])
)

player_list = sorted(
    combined_df['Team'].unique()
)

race_palette = dict(zip(
    race_list,
    sns.color_palette(
        "husl",
        len(race_list)
    )
))

player_palette = dict(zip(
    player_list,
    sns.color_palette(
        "tab20",
        max(len(player_list), 1)
    )
))

# =========================================================
# HELPER FUNCTIONS
# =========================================================
def create_score_map(df, key_col='Name'):

    score_map = {}

    for _, row in df.iterrows():

        name = str(
            row[key_col]
        ).strip().upper()

        score_map[name] = row['Points']

    return score_map


def calculate_base_team_score(
    previous_team_row,
    current_driver_scores,
    current_constructor_scores
):

    total = 0

    # ------------------ DRIVERS ------------------
    for i in range(1, 6):

        driver = str(
            previous_team_row[f'Dri{i}']
        ).strip().upper()

        driver_score = current_driver_scores.get(
            driver,
            0
        )

        # Dri1 = turbo/captain
        if i == 1:
            driver_score *= 2

        total += driver_score

    # ------------------ CONSTRUCTORS ------------------
    for i in range(1, 3):

        constructor = str(
            previous_team_row[f'Con{i}']
        ).strip().upper()

        constructor_score = current_constructor_scores.get(
            constructor,
            0
        )

        total += constructor_score

    return total

# =========================================================
# ANALYSIS
# =========================================================
limitless_vs_next = []
limitless_vs_avg = []
scatter_data = []

for race_folder in race_folders:

    race_num = int(race_folder[1:])

    # Need previous race for base simulation
    if race_num == 1:
        continue

    race_df = players_dfs[race_folder]

    ll_users = race_df[
        race_df['UsedLimitless']
    ]

    # Includes ALL non-limitless teams,
    # including other chips
    non_ll = race_df[
        ~race_df['UsedLimitless']
    ]

    if ll_users.empty or non_ll.empty:
        continue

    # =====================================================
    # FIELD BENCHMARKS
    # =====================================================
    avg_score = non_ll['Points'].mean()

    top_10_avg = (
        non_ll
        .sort_values(
            'Points',
            ascending=False
        )
        .head(10)['Points']
        .mean()
    )

    next_highest = non_ll['Points'].max()

    # =====================================================
    # CURRENT RACE ASSET SCORES
    # =====================================================
    drivers_path = os.path.join(
        processed_dir,
        race_folder,
        'drivers.csv'
    )

    constructors_path = os.path.join(
        processed_dir,
        race_folder,
        'constructors.csv'
    )

    drivers_df = pd.read_csv(drivers_path)

    constructors_df = pd.read_csv(
        constructors_path
    )

    current_driver_scores = create_score_map(
        drivers_df
    )

    current_constructor_scores = create_score_map(
        constructors_df
    )

    # =====================================================
    # PREVIOUS PLAYER DATA
    # =====================================================
    previous_race_folder = f'R{race_num - 1}'

    previous_df = players_dfs[
        previous_race_folder
    ]

    # =====================================================
    # LOOP THROUGH LL USERS
    # =====================================================
    for _, row in ll_users.iterrows():

        player = row['Team']

        ll_score = row['Points']

        # -------------------------------------------------
        # GRAPH 1 DATA
        # Uses FULL non-LL average
        # -------------------------------------------------
        limitless_vs_next.append({
            'Player': player,
            'Race': race_folder,
            'Limitless': ll_score,
            'Comparison': next_highest,
            'Difference': ll_score - next_highest
        })

        limitless_vs_avg.append({
            'Player': player,
            'Race': race_folder,
            'Limitless': ll_score,
            'Comparison': avg_score,
            'Difference': ll_score - top_10_avg
        })

        # -------------------------------------------------
        # PREVIOUS TEAM
        # -------------------------------------------------
        previous_player = previous_df[
            previous_df['Team'] == player
        ]

        if previous_player.empty:
            continue

        previous_team_row = previous_player.iloc[0]

        # -------------------------------------------------
        # SIMULATED BASE TEAM SCORE
        # -------------------------------------------------
        base_team_score = calculate_base_team_score(
            previous_team_row,
            current_driver_scores,
            current_constructor_scores
        )

        base_delta = ll_score - base_team_score

        top10_delta = ll_score - top_10_avg

        # -------------------------------------------------
        # SCATTER DATA
        # -------------------------------------------------
        scatter_data.append({
            'Player': player,
            'Race': race_folder,
            'BaseDelta': base_delta,
            'Top10Delta': top10_delta
        })

# =========================================================
# DATAFRAMES
# =========================================================
df_next = pd.DataFrame(limitless_vs_next)

df_avg = pd.DataFrame(limitless_vs_avg)

df_scatter = pd.DataFrame(scatter_data)

# =========================================================
# LABELS
# =========================================================
for df in [df_next, df_avg]:

    df['Label'] = (
        df['Player']
        + "\n("
        + df['Race']
        + ")"
    )

# =========================================================
# COMBINED COMPARISON DATA
# =========================================================
comparison_df = df_next[
    ['Label', 'Limitless']
].copy()

comparison_df['Highest Non-LL'] = (
    df_next['Comparison']
)

comparison_df['Avg Non-LL'] = (
    df_avg['Comparison']
)

comparison_df = comparison_df.melt(
    id_vars=['Label'],
    value_vars=[
        'Limitless',
        'Highest Non-LL',
        'Avg Non-LL'
    ],
    var_name='Type',
    value_name='Points'
)

# =========================================================
# DELTA DATA
# =========================================================
delta_df = pd.concat([
    df_next.assign(Type='Vs Next'),
    df_avg.assign(Type='Vs Top 10 Avg')
])

# =========================================================
# PLOTTING
# =========================================================
fig, axes = plt.subplots(
    2,
    2,
    figsize=(18, 14)
)

# =========================================================
# 1️⃣ GROUPED COMPARISON CHART
# =========================================================
comparison_palette = {
    'Limitless': '#3049D8',
    'Highest Non-LL': '#EC1919',
    'Avg Non-LL': '#D9D206'
}

sns.barplot(
    data=comparison_df,
    x='Label',
    y='Points',
    hue='Type',
    ax=axes[0, 0],
    palette=comparison_palette
)

axes[0, 0].set_title(
    "Limitless vs Field"
)

for container in axes[0, 0].containers:

    axes[0, 0].bar_label(
        container,
        fmt='%.0f',
        padding=3,
        fontsize=9
    )

# =========================================================
# 2️⃣ DELTA CHART
# =========================================================
delta_palette = {
    'Vs Next': '#CE6414',
    'Vs Top 10 Avg': '#12C318'
}

sns.barplot(
    data=delta_df,
    x='Label',
    y='Difference',
    hue='Type',
    ax=axes[0, 1],
    palette=delta_palette
)

axes[0, 1].axhline(
    0,
    linestyle='--',
    color='grey'
)

axes[0, 1].set_title(
    "Limitless Advantage"
)

for container in axes[0, 1].containers:

    axes[0, 1].bar_label(
        container,
        fmt='%.0f',
        padding=3,
        fontsize=9
    )

# =========================================================
# 3️⃣ BOXPLOT DISTRIBUTION
# =========================================================
ll_races = sorted(
    combined_df.loc[
        combined_df['UsedLimitless'],
        'Race'
    ].unique(),
    key=lambda x: int(x[1:])
)

boxplot_df = combined_df[
    combined_df['Race'].isin(ll_races)
]

sns.boxplot(
    data=boxplot_df,
    x='Race',
    y='Points',
    ax=axes[1, 0],
    color='#D9D9D9'
)

# Overlay LL users
ll_points = combined_df[
    combined_df['UsedLimitless']
]

sns.scatterplot(
    data=ll_points,
    x='Race',
    y='Points',
    hue='Team',
    palette=player_palette,
    s=140,
    ax=axes[1, 0]
)

axes[1, 0].set_title(
    "Race Score Distribution with Limitless Users"
)

axes[1, 0].set_xlabel(
    "Race"
)

# =========================================================
# 4️⃣ LL VALUE SCATTER
# =========================================================
sns.scatterplot(
    data=df_scatter,
    x='Top10Delta',
    y='BaseDelta',
    hue='Race',
    palette=race_palette,
    s=180,
    ax=axes[1, 1]
)

# Labels
for _, row in df_scatter.iterrows():

    axes[1, 1].text(
        row['Top10Delta'],
        row['BaseDelta'] + 5,
        row['Player'],
        fontsize=9
    )

# Reference lines
axes[1, 1].axhline(
    0,
    linestyle='--',
    color='grey'
)

axes[1, 1].axvline(
    0,
    linestyle='--',
    color='grey'
)

axes[1, 1].set_title(
    "Limitless Value Analysis"
)

axes[1, 1].set_xlabel(
    "Delta vs Top 10 Non-LL Average"
)

axes[1, 1].set_ylabel(
    "Delta vs Simulated Base Team"
)

# =========================================================
# FINAL TOUCH
# =========================================================
for ax in axes.flat:

    ax.tick_params(
        axis='x',
        rotation=0
    )

axes[0, 0].set_xlabel("")
axes[0, 1].set_xlabel("")

axes[0, 0].set_ylabel("Points")
axes[0, 1].set_ylabel("Point Difference")
axes[1, 0].set_ylabel("Points")

plt.tight_layout()

output_path = os.path.join(
    PROJECT_ROOT,
    'analysis',
    'limitless_analysis.png'
)

plt.savefig(
    output_path,
    dpi=300,
    bbox_inches='tight'
)

plt.show()

# OG LIMITLESS CODE FOR REFERENCE IDK

# import pandas as pd
# import seaborn as sns
# import matplotlib.pyplot as plt
# import numpy as np
# import os

# sns.set_theme(style="whitegrid")

# # ------------------ PATH SETUP ------------------
# CURRENT_DIR = os.path.abspath(__file__)
# PROJECT_ROOT = CURRENT_DIR
# for _ in range(3):
#     PROJECT_ROOT = os.path.dirname(PROJECT_ROOT)

# processed_dir = os.path.join(PROJECT_ROOT, 'data', 'processed')

# # ------------------ LOAD DATA ------------------
# race_folders = [f for f in os.listdir(processed_dir) if f.startswith('R')]
# race_folders.sort()

# dfs = []

# for folder in race_folders:
#     file_path = os.path.join(processed_dir, folder, 'players.csv')
#     df = pd.read_csv(file_path)

#     df['Race'] = folder
#     dfs.append(df)

# combined_df = pd.concat(dfs, ignore_index=True)

# # ------------------ CLEAN DATA ------------------
# combined_df['UsedLimitless'] = (
#     combined_df['Chips']
#     .fillna('')
#     .str.strip()
#     .str.lower()
#     .eq('limitless')
# )

# # Extract race number (R1 → 1)
# combined_df['RaceNumber'] = combined_df['Race'].str.extract(r'R(\d+)').astype(int)

# # ------------------ ANALYSIS ------------------
# limitless_vs_next = []
# limitless_vs_avg = []

# for race, race_df in combined_df.groupby('RaceNumber'):

#     ll_users = race_df[race_df['UsedLimitless']]
#     non_ll = race_df[~race_df['UsedLimitless']]

#     if len(non_ll) == 0:
#         continue

#     next_highest = non_ll['Points'].max()
#     avg_score = non_ll['Points'].mean()

#     for _, row in ll_users.iterrows():
#         player = row['Team']
#         ll_score = row['Points']

#         limitless_vs_next.append({
#             'Player': player,
#             'Race': f'R{race}',
#             'Limitless': ll_score,
#             'Comparison': next_highest,
#             'Difference': ll_score - next_highest
#         })

#         limitless_vs_avg.append({
#             'Player': player,
#             'Race': f'R{race}',
#             'Limitless': ll_score,
#             'Comparison': avg_score,
#             'Difference': ll_score - avg_score
#         })

# df_next = pd.DataFrame(limitless_vs_next)
# df_avg = pd.DataFrame(limitless_vs_avg)

# # Labels
# df_next['Label'] = df_next['Player'] + "\n(" + df_next['Race'] + ")"
# df_avg['Label'] = df_avg['Player'] + "\n(" + df_avg['Race'] + ")"

# # ------------------ PLOTTING ------------------
# fig, axes = plt.subplots(2, 2, figsize=(18, 14))

# # 1️⃣ Limitless vs Next Highest
# sns.barplot(
#     data=df_next.melt(id_vars=['Label'],
#                       value_vars=['Limitless', 'Comparison'],
#                       var_name='Type',
#                       value_name='Points'),
#     x='Label', y='Points', hue='Type',
#     ax=axes[0, 0],
#     palette=['#3049D8', '#EC1919']
# )
# axes[0, 0].set_title("Limitless vs Highest Non-Limitless")
# for container in axes[0, 0].containers:
#     axes[0, 0].bar_label(container, fmt='%.0f', padding=3, fontsize=9)
# # 2️⃣ Limitless vs Average
# sns.barplot(
#     data=df_avg.melt(id_vars=['Label'],
#                      value_vars=['Limitless', 'Comparison'],
#                      var_name='Type',
#                      value_name='Points'),
#     x='Label', y='Points', hue='Type',
#     ax=axes[0, 1],
#     palette=['#3049D8', '#D9D206']
# )
# axes[0, 1].set_title("Limitless vs Average")
# for container in axes[0, 1].containers:
#     axes[0, 1].bar_label(container, fmt='%.0f', padding=3, fontsize=9)
# # 3️⃣ Delta comparison
# delta_df = pd.concat([
#     df_next.assign(Type='Vs Next'),
#     df_avg.assign(Type='Vs Avg')
# ])

# sns.barplot(
#     data=delta_df,
#     x='Label', y='Difference', hue='Type',
#     ax=axes[1, 0],
#     palette=['#CE6414', '#12C318']
# )
# axes[1, 0].axhline(0, linestyle='--', color='black')
# axes[1, 0].set_title("Limitless Advantage")
# for container in axes[1, 0].containers:
#     axes[1, 0].bar_label(
#         container,
#         fmt='%.1f',
#         padding=3,
#         fontsize=9
#     )
# # 4️⃣ Scatter
# sns.scatterplot(
#     data=df_avg,
#     x='Comparison',
#     y='Limitless',
#     hue='Race',
#     s=120,
#     ax=axes[1, 1]
# )

# # Diagonal line
# min_val = min(df_avg['Comparison'].min(), df_avg['Limitless'].min())
# max_val = max(df_avg['Comparison'].max(), df_avg['Limitless'].max())
# axes[1, 1].plot([min_val, max_val], [min_val, max_val], linestyle='--')

# # Labels
# for _, row in df_avg.iterrows():
#     axes[1, 1].text(row['Comparison'], row['Limitless'], row['Player'], fontsize=9)

# axes[1, 1].set_title("Limitless Scatter")

# # ------------------ FINAL TOUCH ------------------
# for ax in axes.flat:
#     ax.tick_params(axis='x', rotation=0)
#     ax.set_xlabel("")
#     ax.set_ylabel("Points")

# plt.tight_layout()

# output_path = os.path.join(PROJECT_ROOT, 'analysis', 'limitless_analysis.png')
# plt.savefig(output_path, dpi=300, bbox_inches='tight')
# plt.show()