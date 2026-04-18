import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

CURRENT_DIR = os.path.abspath(__file__)
PROJECT_ROOT = CURRENT_DIR
for _ in range(3):  # go up 3 levels
    PROJECT_ROOT = os.path.dirname(PROJECT_ROOT)
processed_dir = os.path.join(PROJECT_ROOT, "data", "processed")
analysis_dir = os.path.join(PROJECT_ROOT, "analysis")
confidential_dir = os.path.join(PROJECT_ROOT, "analysis" ,"confidential_analysis")
os.makedirs(confidential_dir, exist_ok=True)
os.makedirs(analysis_dir, exist_ok=True)

# Find the latest round folder (highest R number)
race_folders = sorted(
    [f for f in os.listdir(processed_dir) if f.startswith("R")],
    key=lambda x: int(x.lstrip("R")),
)

if not race_folders:
    print("No race folders found.")
    exit()

latest_folder = race_folders[-1]
file_path = os.path.join(processed_dir, latest_folder, "playerinfo.csv")

if not os.path.exists(file_path):
    print(f"playerinfo.csv not found in {latest_folder}")
    exit()

df = pd.read_csv(file_path)

# Rename columns to remove underscores in legends
df = df.rename(columns={'Total_Points': 'Total Points', 'Total_Cost_Cap': 'Total Cost Cap'})

# Set seaborn style
sns.set_style("whitegrid")

# Scatter plot: Total Cost Cap on x-axis, Total Points on y-axis
plt.figure(figsize=(12, 8))
scatter = sns.scatterplot(x='Total Cost Cap', y='Total Points', data=df, 
                          hue='Total Points', palette='viridis_r', alpha=0.7, s=100, size='Total Cost Cap', sizes=(50, 200))

# Annotate each point with team name
for i, row in df.iterrows():
    plt.annotate(row['Team'], (row['Total Cost Cap'], row['Total Points']), 
                 textcoords="offset points", xytext=(5,5), ha='left', fontsize=8)

plt.xlabel('Total Cost Cap', fontweight='bold')
plt.ylabel('Total Points',  fontweight='bold')
plt.title(f'Points vs Cost Cap - {latest_folder}', fontsize=16, fontweight='bold', pad=20)

output_path1 = os.path.join(confidential_dir, "costcap_scatter.png")
plt.savefig(output_path1, bbox_inches='tight')
print(f"Scatter plot saved to {output_path1}")

plt.xticks([])  # Set x-ticks to blank to hide them in the public version
plt.legend([], [])  # Hide legend for public version
output_path2 = os.path.join(analysis_dir, "costcap_scatter.png")
plt.savefig(output_path2, bbox_inches='tight')
print(f"Scatter plot saved to {output_path2}")