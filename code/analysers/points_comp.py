import numpy as np
import pandas as pd
import seaborn as sns
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

# Read each players.csv file and add a 'Race' column
for folder in race_folders:
    file_path = os.path.join(processed_dir, folder, 'players.csv')
    df = pd.read_csv(file_path)
    df['Race'] = folder
    dfs.append(df)

# Combine all dataframes
combined_df = pd.concat(dfs, ignore_index=True)
combined_df['RaceNumber'] = combined_df['Race'].str.extract(r'R(\d+)').astype(int)

# Group by player Team and sum the points
total_points_df = combined_df.groupby('Team', sort=False)['Points'].sum().reset_index()

# Sort by total points descending and keep top 10
total_points_df = total_points_df.sort_values('Points', ascending=False)
top_n = min(10, len(total_points_df))
top_teams_df = total_points_df.head(top_n)
selected_teams = top_teams_df['Team'].tolist()

# Filter race data to top teams only
race_points_df = (
    combined_df[combined_df['Team'].isin(selected_teams)]
    .groupby(['RaceNumber', 'Race', 'Team'], sort=False)['Points']
    .sum()
    .reset_index()
)

# Make sure all top teams have a row for each race
race_numbers = sorted(race_points_df['RaceNumber'].unique())
full_index = pd.MultiIndex.from_product([race_numbers, selected_teams], names=['RaceNumber', 'Team'])
race_points_df = race_points_df.set_index(['RaceNumber', 'Team']).reindex(full_index, fill_value=0).reset_index()

# Ensure analysis folder exists
analysis_dir = os.path.join(PROJECT_ROOT, 'analysis')
os.makedirs(analysis_dir, exist_ok=True)

# Create the bar plot for ALL teams sorted by total points
all_teams_sorted = total_points_df.sort_values('Points', ascending=False)
plt.figure(figsize=(12, max(8, len(all_teams_sorted) * 0.25)))
sns.barplot(data=all_teams_sorted, x='Points', y='Team', palette='viridis')
plt.title(f'Total Points Scored by All Teams ({race_folders[0]}-{race_folders[-1]})', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Total Points', fontsize=12, fontweight='bold')
plt.ylabel('Team', fontsize=12, fontweight='bold')
plt.tight_layout()
all_teams_bar_path = os.path.join(analysis_dir, 'all_teams_total_points_horizontal_bargraph.png')
plt.savefig(all_teams_bar_path, dpi=300, bbox_inches='tight')
plt.close()

# Create the cumulative points line plot for top 10 teams
plt.style.use('default')
# Use a custom palette with distinct colors (replacing gray with purple)
custom_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf', '#652C97', '#3141EE', '#DD00C7', '#00B2B2', '#652C97', '#00DA00', '#DB8708', '#d21111', '#AC9500', '#3141EE']
color_map = dict(zip(selected_teams, custom_colors[:top_n]))

# Add race 0 with 0 points for all teams
race_0_data = pd.DataFrame({
    'RaceNumber': [0] * top_n,
    'Race': ['R0'] * top_n,
    'Team': selected_teams,
    'Points': [0] * top_n
})
cumulative_base_df = pd.concat([race_0_data, race_points_df], ignore_index=True)

cumulative_df = cumulative_base_df.sort_values(['Team', 'RaceNumber'])
cumulative_df['CumulativePoints'] = cumulative_df.groupby('Team')['Points'].cumsum()

fig, ax = plt.subplots(figsize=(13, 8))
for team in selected_teams:
    team_data = cumulative_df[cumulative_df['Team'] == team]
    ax.plot(
        team_data['RaceNumber'],
        team_data['CumulativePoints'],
        marker='o',
        color=color_map[team],
        linewidth=1.8,
        label=team
    )

ax.set_title(f'Cumulative Points by Race for Top {top_n} Teams ({race_folders[0]}-{race_folders[-1]})', fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('Race Number', fontsize=12, fontweight='bold')
ax.set_ylabel('Cumulative Points', fontsize=12, fontweight='bold')
ax.set_xticks(sorted([0] + race_numbers))
ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)

# Annotate team names and total points outside the graph with full height spacing
last_race = max(race_numbers)
text_x = last_race + 0.15
y_min = cumulative_df['CumulativePoints'].min()
y_max = cumulative_df['CumulativePoints'].max()
label_y_positions = np.linspace(y_max, y_min, top_n)

final_totals = cumulative_df.groupby('Team')['CumulativePoints'].last().sort_values(ascending=False)
for idx, (team, total_points) in enumerate(final_totals.items()):
    ax.text(
        text_x,
        label_y_positions[idx],
        f'{team} ({int(total_points)})',
        color=color_map[team],
        fontsize=10,
        va='center',
        fontweight='bold'
    )

ax.set_xlim(0, last_race + 1.3)
plt.tight_layout()
line_output_path = os.path.join(analysis_dir, 'top10_cumulative_points_lineplot.png')
plt.savefig(line_output_path, dpi=300, bbox_inches='tight')
plt.close()