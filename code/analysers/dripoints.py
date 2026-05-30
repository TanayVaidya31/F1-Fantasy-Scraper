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

def dripoints_perrace_lineplot():
    # ------------------ LOAD DATA ------------------
    race_folders = [f for f in os.listdir(processed_dir) if f.startswith('R') and f != 'R0']
    race_folders.sort()

    dfs = []

    for folder in race_folders:
        file_path = os.path.join(processed_dir, folder, 'drivers.csv')
        df = pd.read_csv(file_path)

        df['Race'] = folder
        dfs.append(df)

    combined_df = pd.concat(dfs, ignore_index=True)

    # Extract numeric race number
    combined_df['RaceNumber'] = combined_df['Race'].str.extract(r'R(\d+)').astype(int)

    # ------------------ PER-RACE POINTS ------------------
    race_points_df = (
        combined_df
        .groupby(['RaceNumber', 'Name'], sort=False)['Points']
        .sum()
        .reset_index()
    )

    # Ensure all names appear in all races (fill missing with 0)
    race_numbers = sorted(race_points_df['RaceNumber'].unique())
    all_names = race_points_df['Name'].unique()

    full_index = pd.MultiIndex.from_product(
        [race_numbers, all_names],
        names=['RaceNumber', 'Name']
    )

    race_points_df = (
        race_points_df
        .set_index(['RaceNumber', 'Name'])
        .reindex(full_index, fill_value=0)
        .reset_index()
    )

    # ------------------ OUTPUT DIR ------------------
    analysis_dir = os.path.join(PROJECT_ROOT, 'analysis')
    os.makedirs(analysis_dir, exist_ok=True)

    # ------------------ PLOT ------------------
    plt.figure(figsize=(14, 9))

    custom_colors = ["#18d4af", '#ff7f0e', '#272ad6', "#da1111", "#bd39b5", "#30587d", "#288D28", "#6a6a6a", "#bcbcbc", "#89a6ee", "#1E1E1E"]
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
    sns.lineplot(
        data=race_points_df,
        x='RaceNumber',
        y='Points',
        hue='Name',
        style='Name',                # enables line styles
        dashes=driver_style,
        palette=color_map,
        marker='o'
    )

    plt.title(f'Driver Points Per Race', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Race Number', fontsize=12, fontweight='bold')
    plt.ylabel('Points per Race', fontsize=12, fontweight='bold')
    plt.xticks(race_numbers)

    # Improve readability of small changes
    plt.gca().yaxis.set_major_formatter(lambda x, _: f'{x:.0f}')  # show 0 decimal places

    # Add markers values (optional but VERY helpful)
    for line in plt.gca().lines:
        for x, y in zip(line.get_xdata(), line.get_ydata()):
            if not np.isnan(y):
                plt.annotate(
                    f'{y:.0f}',
                    (x, y),
                    textcoords="offset points",
                    xytext=(0, 3),   # move 5 pixels up
                    ha='center',
                    fontsize=7
                )

    plt.grid(True, alpha=0.3)

    plt.legend(title='Name', bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.tight_layout()

    output_path = os.path.join(analysis_dir, 'dripoints_perrace_lineplot.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Driver points per race line plot saved to: {output_path}")

if __name__ == "__main__":
    dripoints_perrace_lineplot()