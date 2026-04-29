import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# ------------------ PATH SETUP ------------------
CURRENT_DIR = os.path.abspath(__file__)
PROJECT_ROOT = CURRENT_DIR
for _ in range(3):
    PROJECT_ROOT = os.path.dirname(PROJECT_ROOT)

processed_dir = os.path.join(PROJECT_ROOT, 'data', 'processed')

# ------------------ LOAD DATA ------------------
race_folders = [f for f in os.listdir(processed_dir) if f.startswith('R')]
race_folders.sort()

dfs = []

for folder in race_folders:
    file_path = os.path.join(processed_dir, folder, 'drivers.csv')
    df = pd.read_csv(file_path)
    df['Race'] = folder
    dfs.append(df)

combined_df = pd.concat(dfs, ignore_index=True)

combined_df['RaceNumber'] = combined_df['Race'].str.extract(r'R(\d+)').astype(int)

# ------------------ PER-RACE PRICE ------------------
race_points_df = (
    combined_df
    .groupby(['RaceNumber', 'Name'], sort=False)['Price']
    .sum()
    .reset_index()
)

# Ensure all names appear in all races
race_numbers = sorted(race_points_df['RaceNumber'].unique())
all_names = race_points_df['Name'].unique()

full_index = pd.MultiIndex.from_product(
    [race_numbers, all_names],
    names=['RaceNumber', 'Name']
)

race_points_df = (
    race_points_df
    .set_index(['RaceNumber', 'Name'])
    .reindex(full_index, fill_value=np.nan)   # use NaN instead of 0 (important)
    .reset_index()
)

# ------------------ SPLIT BY PRICE ------------------
# Get latest race prices
latest_race = max(race_numbers)

latest_prices = (
    race_points_df[race_points_df['RaceNumber'] == latest_race]
    [['Name', 'Price']]
)

high_value_names = latest_prices[latest_prices['Price'] >= 18.5]['Name'].tolist()
low_value_names  = latest_prices[latest_prices['Price'] < 18.5]['Name'].tolist()

high_df = race_points_df[race_points_df['Name'].isin(high_value_names)]
low_df  = race_points_df[race_points_df['Name'].isin(low_value_names)]

# ------------------ COLORS ------------------
color_map = {
    'RUS': '#00D2BE',   # Mercedes teal
    'VER': '#0600EF',   # Red Bull blue
    'LEC': '#DC0000',   # Ferrari red
    'NOR': '#FF8700',   # McLaren orange
    'ALO': "#006F21",   # Aston Martin green
    'GAS': '#bd39b5',   # Alpine magenta
    'HUL': '#bcbcbc',   # Audi light gray
    'PER': '#1E1E1E',   # Cadillac dark gray
    'BEA': '#6a6a6a',   # Haas gray
    'SAI': '#30587d',   # Williams blue
    'LAW': '#89a6ee',   # Racing Bulls light blue

    'ANT': '#00D2BE',   # Mercedes teal
    'HAD': '#0600EF',   # Red Bull blue
    'HAM': '#DC0000',   # Ferrari red
    'PIA': '#FF8700',   # McLaren orange
    'STR': "#006F21",   # Aston Martin green
    'COL': '#bd39b5',   # Alpine magenta
    'BOR': '#bcbcbc',   # Audi light gray
    'BOT': '#1E1E1E',   # Cadillac dark gray
    'OCO': '#6a6a6a',   # Haas gray
    'ALB': '#30587d',   # Williams blue
    'LIN': '#89a6ee',   # Racing Bulls light blue
}
driver_style = {
    'RUS': '',        'ANT': (4, 2),
    'VER': '',        'HAD': (4, 2),
    'LEC': '',        'HAM': (4, 2),
    'NOR': '',        'PIA': (4, 2),
    'ALO': '',        'STR': (4, 2),
    'GAS': '',        'COL': (4, 2),
    'HUL': '',        'BOR': (4, 2),
    'PER': '',        'BOT': (4, 2),
    'BEA': '',        'OCO': (4, 2),
    'SAI': '',        'ALB': (4, 2),
    'LAW': '',        'LIN': (4, 2),
}
set(race_points_df['Name']).issubset(driver_style.keys())

analysis_dir = os.path.join(PROJECT_ROOT, 'analysis')
os.makedirs(analysis_dir, exist_ok=True)

# ------------------ FUNCTION TO PLOT ------------------
def plot_graph(data, title, filename):
    plt.figure(figsize=(12, 7))

    sns.lineplot(
        data=data,
        x='RaceNumber',
        y='Price',
        hue='Name',
        style='Name',                # enables line styles
        dashes=driver_style,
        palette=color_map
        # marker='o'
    )

    ax = plt.gca()
    for name, group in data.groupby('Name'):
        group = group.sort_values('RaceNumber')

        x = group['RaceNumber'].values
        y = group['Price'].values

        for i in range(len(y)):

            if i == len(y) - 1:
                marker = 'o'
                facecolor = color_map[name]  # default color for last point
            else:
                if y[i+1] > y[i]:
                    marker = '^'
                    facecolor = "#11d100" # green for increase
                elif y[i+1] < y[i]:
                    marker = 'v'
                    facecolor = "#d41c00" # red for decrease
                else:
                    marker = 'o'
                    facecolor = color_map[name]

            ax.scatter(
                x[i],
                y[i],
                color=color_map[name],
                marker=marker,
                facecolors=facecolor,   # use facecolors instead of facecolor (more reliable)
                edgecolors="white",   # use edgecolors for the marker outline
                zorder=3,
                linewidth=0.3
            )

    plt.title(title, fontsize=15, fontweight='bold')
    plt.xlabel('Race Number')
    plt.ylabel('Constructor Price (Millions $)')

    plt.xticks(race_numbers)

    # Improve readability of small changes
    plt.gca().yaxis.set_major_formatter(lambda x, _: f'{x:.1f}')  # show 1 decimal places

    # Add markers values (optional but VERY helpful)
    for line in plt.gca().lines:
        for x, y in zip(line.get_xdata(), line.get_ydata()):
            if not np.isnan(y):
                plt.annotate(
                    f'{y:.1f}',
                    (x, y),
                    textcoords="offset points",
                    xytext=(0, 4),   # move 5 pixels up
                    ha='center',
                    fontsize=7
                )

    plt.grid(True, alpha=0.3)

    plt.legend(title='Constructor', bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.tight_layout()
    plt.savefig(os.path.join(analysis_dir, filename), dpi=300, bbox_inches='tight')
    plt.close()

# ------------------ PLOT BOTH ------------------
plot_graph(
    high_df,
    'Premium Drivers (≥ 18.5M$)',
    'prem_drivers.png'
)

plot_graph(
    low_df,
    'Non-Premium Drivers (< 18.5M$)',
    'nonprem_drivers.png'
)