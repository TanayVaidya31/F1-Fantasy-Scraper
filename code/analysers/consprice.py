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
    file_path = os.path.join(processed_dir, folder, 'constructors.csv')
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
    'MER': '#00D2BE',
    'RBR': '#0600EF',
    'FER': '#DC0000',
    'MCL': '#FF8700',
    'AST': "#006F21",
    'ALP': '#bd39b5',
    'AUD': '#bcbcbc',
    'CAD': '#1E1E1E',
    'HAA': '#6a6a6a',
    'WIL': '#30587d',
    'RBS': '#89a6ee',
}

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
        palette=color_map,
        marker='o'
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
                    xytext=(0, 3),   # move 5 pixels up
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
    'Premium Constructors (≥ 18.5M$)',
    'prem_constructors.png'
)

plot_graph(
    low_df,
    'Non-Premium Constructors (< 18.5M$)',
    'nonprem_constructors.png'
)