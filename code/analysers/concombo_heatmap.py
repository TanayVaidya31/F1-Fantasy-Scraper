import os
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# 1. SETUP PATHS
CURRENT_DIR = os.path.abspath(__file__)
PROJECT_ROOT = CURRENT_DIR
for _ in range(3):  # go up 3 levels to reach the root project folder
    PROJECT_ROOT = os.path.dirname(PROJECT_ROOT)

processed_dir = os.path.join(PROJECT_ROOT, 'data', 'processed')
concombo_dir = os.path.join(PROJECT_ROOT, 'analysis', 'confidential_analysis', 'constructor_combos')

# Ensure the analysis directory exists
os.makedirs(concombo_dir, exist_ok=True)

# Find all race folders and filter out R0
race_folders = [f for f in os.listdir(processed_dir) if f.startswith('R') and f != 'R0']
race_folders.sort(key=lambda x: int(x[1:]))
latest_round = race_folders[-1]

# 2. AGGREGATE CUMULATIVE CONSTRUCTOR POINTS (R1 to Latest)
cumulative_pts = {}
for folder in race_folders:
    con_file = os.path.join(processed_dir, folder, 'constructors.csv')
    if os.path.exists(con_file):
        df_con = pd.read_csv(con_file)
        for _, row in df_con.iterrows():
            name = str(row['Name']).upper()
            pts = row['Points']
            cumulative_pts[name] = cumulative_pts.get(name, 0) + pts

# Get Latest Round points specifically for the first heatmap
latest_con_df = pd.read_csv(os.path.join(processed_dir, latest_round, 'constructors.csv'))
latest_con_df['Name'] = latest_con_df['Name'].str.upper()
latest_pts_map = dict(zip(latest_con_df['Name'], latest_con_df['Points']))

# 3. PROCESS PLAYER PICKS (From the Latest Round)
players = pd.read_csv(os.path.join(processed_dir, latest_round, 'players.csv'))
players['Con1'] = players['Con1'].str.upper()
players['Con2'] = players['Con2'].str.upper()
total_players = len(players)

# Identify unique picked combos and active constructors
all_picked = [tuple(sorted([r['Con1'], r['Con2']])) for _, r in players.iterrows()]
counts = pd.Series(all_picked).value_counts()
active_cons = sorted(list(set([c for combo in counts.index for c in combo])))

# 4. PREPARE MATRICES
n = len(active_cons)
# Latest Round Matrices
latest_data = np.zeros((n, n))
latest_labels = np.empty((n, n), dtype=object)
# Cumulative Matrices
cumul_data = np.zeros((n, n))
cumul_labels = np.empty((n, n), dtype=object)

for i, con1 in enumerate(active_cons):
    for j, con2 in enumerate(active_cons):
        combo = tuple(sorted([con1, con2]))
        pick_count = counts.get(combo, 0)
        pct = (pick_count / total_players) * 100
        
        # BLOCK DIAGONAL (Same Constructor combos are impossible)
        if i == j:
            latest_data[i, j] = np.nan  # NaN excludes it from the color scale calculation
            cumul_data[i, j] = np.nan
            latest_labels[i, j] = "N/A"
            cumul_labels[i, j] = "N/A"
            continue
            
        # LATEST POINTS
        l_pts = latest_pts_map.get(con1, 0) + latest_pts_map.get(con2, 0)
        latest_data[i, j] = l_pts
        latest_labels[i, j] = f"{con1}/{con2}\n{l_pts} pts\n{pct:.1f}%"
        
        # CUMULATIVE POINTS
        c_pts = cumulative_pts.get(con1, 0) + cumulative_pts.get(con2, 0)
        cumul_data[i, j] = c_pts
        cumul_labels[i, j] = f"{con1}/{con2}\n{c_pts} pts\n{pct:.1f}%"

# 5. VISUALIZE AND SAVE
if f'{latest_round}' == 'R1':
    plot_configs = [
        (latest_data, latest_labels, f"Latest Race ({latest_round})", f"constructor_heatmap_latest_{latest_round}.png"),
        (cumul_data, cumul_labels, "Cumulative (R1)", f"constructor_heatmap_cumulative_{latest_round}.png")
    ]
else:
    plot_configs = [
        (latest_data, latest_labels, f"Latest Race ({latest_round})", f"constructor_heatmap_latest_{latest_round}.png"),
        (cumul_data, cumul_labels, f"Cumulative (R1-{latest_round})", f"constructor_heatmap_cumulative_{latest_round}.png")
    ]

for data, labels, title_type, filename in plot_configs:
    fig, ax = plt.subplots(figsize=(14, 12))
    
    # 1. Set the background color of the axes to black
    # This will show through in any cells where the data is np.nan (the diagonal)
    ax.set_facecolor('lightgrey')
    
    sns.heatmap(
        data, 
        annot=labels, 
        fmt="", 
        cmap="viridis_r", 
        xticklabels=active_cons, 
        yticklabels=active_cons,
        linewidths=1,
        linecolor='black', # This creates the grid lines
        cbar_kws={'label': f'Total {title_type} Points'},
        ax=ax # Ensure we use the axes we just styled
    )
    
    # Note: Seaborn does not draw annotations for NaN values. This is perfect for "blocking out" the diagonal, as it remains solid black.
    
    plt.title(f"Combined Constructor Points and Pick Rate: {title_type}\nPoints (Color) and Popularity (%)", 
              fontsize=18, pad=20, fontweight='bold')
    plt.xlabel("Constructor A", fontsize=14, fontweight='bold')
    plt.ylabel("Constructor B", fontsize=14, fontweight='bold')
    plt.xticks(rotation=0)
    plt.yticks(rotation=0)
    
    plt.tight_layout()
    save_path = os.path.join(concombo_dir, filename)
    plt.savefig(save_path, dpi=300, bbox_inches='tight', pad_inches=0.05)
    plt.close()

print(f"Heatmaps successfully saved to: {concombo_dir}")