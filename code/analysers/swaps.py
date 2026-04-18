import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

CURRENT_DIR = os.path.abspath(__file__)
PROJECT_ROOT = CURRENT_DIR
for _ in range(3):  # go up 3 levels
    PROJECT_ROOT = os.path.dirname(PROJECT_ROOT)

# Dynamically find race folders (excluding R0)
processed_dir = os.path.join(PROJECT_ROOT, 'data', 'processed')
race_folders = [f for f in os.listdir(processed_dir) if f.startswith('R') and f != 'R0']
race_folders.sort()  # Ensure they are in order R1, R2, etc.

# List to hold dataframes
dfs = []

# Read each playerinfo.csv file
for folder in race_folders:
    file_path = os.path.join(processed_dir, folder, 'playerinfo.csv')
    df = pd.read_csv(file_path)
    df['Race'] = folder
    dfs.append(df)

# Combine all dataframes
combined_df = pd.concat(dfs, ignore_index=True)

# Group by team and aggregate swaps
swaps_data = []
for team in combined_df['Team'].unique():
    team_data = combined_df[combined_df['Team'] == team]
    
    # Count swaps for each type
    regular_swaps = 0
    limitless_swaps = 0
    wildcard_swaps = 0
    
    for _, row in team_data.iterrows():
        swaps_made = row['Swaps_Made']
        race = row['Race']  # Get the current race for this row
        ll_chip = row['LL']
        wc_chip = row['WC']
        
        # Check if Limitless chip was used in THIS specific round
        if pd.notna(ll_chip) and str(ll_chip).strip() == race:
            limitless_swaps += swaps_made
        # Check if Wildcard chip was used in THIS specific round
        elif pd.notna(wc_chip) and str(wc_chip).strip() == race:
            wildcard_swaps += swaps_made
        else:  # Regular swaps (no chip used in this round)
            regular_swaps += swaps_made
    
    total_swaps = regular_swaps + limitless_swaps + wildcard_swaps
    swaps_data.append({
        'Team': team,
        'Regular': regular_swaps,
        'Limitless': limitless_swaps,
        'Wildcard': wildcard_swaps,
        'Total': total_swaps
    })

swaps_df = pd.DataFrame(swaps_data)

# Sort by total swaps descending
swaps_df = swaps_df.sort_values('Total', ascending=True)  # True for horizontal bar (reversed for top-to-bottom)

# Ensure analysis folder exists
analysis_dir = os.path.join(PROJECT_ROOT, 'analysis')
os.makedirs(analysis_dir, exist_ok=True)

# Identify teams with non-zero swaps and apply viridis gradient only to them
non_zero_teams = swaps_df[swaps_df['Total'] > 0].copy()
n_non_zero = len(non_zero_teams)

# Map viridis colors to non-zero teams in descending order (most swaps = yellow at index 0, least = purple)
import matplotlib.cm as cm
viridis = cm.get_cmap('viridis')
color_map = {}
for idx, (_, row) in enumerate(non_zero_teams.iterrows()):
    team = row['Team']
    # Map in reverse: highest swaps to index 0 (yellow in reversed viridis), lowest to index n-1 (purple)
    color_idx = idx / (n_non_zero - 1) if n_non_zero > 1 else 0
    color_map[team] = viridis(1 - color_idx)  # Reverse: 1-1=0 (purple) to 1-0=1 (yellow)

# Assign light gray to zero-swap teams
for _, row in swaps_df[swaps_df['Total'] == 0].iterrows():
    team = row['Team']
    color_map[team] = '#CCCCCC'

colors_gradient = [color_map[team] for team in swaps_df['Team']]

# Create stacked horizontal bar chart
plt.style.use('default')
fig, ax = plt.subplots(figsize=(12, max(8, len(swaps_df) * 0.35)))

# Plot stacked bars
x_pos = np.arange(len(swaps_df))
ax.barh(x_pos, swaps_df['Regular'], color=colors_gradient, height=0.7)
ax.barh(x_pos, swaps_df['Limitless'], left=swaps_df['Regular'], label='Limitless Transfers', color="#001BCE", height=0.7)
ax.barh(
    x_pos,
    swaps_df['Wildcard'],
    left=swaps_df['Regular'] + swaps_df['Limitless'],
    label='Wildcard Transfers',
    color="#D20000",
    height=0.7
)

ax.set_yticks(x_pos)
ax.set_yticklabels(swaps_df['Team'], fontsize=10)
ax.set_xlabel('Total Transfers Made', fontsize=12, fontweight='bold')
ax.set_ylabel('Team', fontsize=12, fontweight='bold')
ax.set_title(f'Total Transfers by Team ({race_folders[0]}-{race_folders[-1]})', fontsize=14, fontweight='bold', pad=20)
ax.legend(loc='lower right', fontsize=10)
ax.grid(axis='x', alpha=0.3, linestyle='-', linewidth=0.5)
ax.set_ylim(-0.5, len(swaps_df) - 0.5)

plt.tight_layout()
output_path = os.path.join(analysis_dir, 'team_swaps_horizontal_bargraph.png')
plt.savefig(output_path, dpi=300, bbox_inches='tight')
plt.close()
