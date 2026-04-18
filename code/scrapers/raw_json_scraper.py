import requests
import json
import os

BASE_URL = "https://fantasy.formula1.com/feeds/drivers/{}_en.json"
FILENAME = "race_{}.json"

# Determine the project root and raw data path
CURRENT_DIR = os.path.abspath(__file__)
PROJECT_ROOT = CURRENT_DIR
for _ in range(3):  # go up 3 levels
    PROJECT_ROOT = os.path.dirname(PROJECT_ROOT)
PATH = os.path.join(PROJECT_ROOT, "data", "raw")

# Ensure the output directory exists
os.makedirs(PATH, exist_ok=True)
print(f"Output directory: {PATH}")

def scrape_all():
    """Scrape all race data from scratch."""
    # Find the maximum race number with data (up to 30)
    max_race = 0
    for i in range(1, 31):
        url = BASE_URL.format(i)
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data:  # Check if data is not empty
                    max_race = i
                else:
                    break
            else:
                break
        except Exception as e:
            print(f"Error fetching race {i}: {e}")
            break

    # Scrape and save data in same order
    for i in range(1, max_race + 1):
        url = BASE_URL.format(i)
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data:
                    filename = FILENAME.format(i)
                    filepath = os.path.join(PATH, filename)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=4)
                    print(f"Saved {filename}")
        except Exception as e:
            print(f"Error saving race {i}: {e}")

def update():
    """Update by fetching only new race data and renumbering existing files."""
    # Find existing max_saved
    files = [f for f in os.listdir(PATH) if f.startswith("race_") and f.endswith(".json")]
    max_saved = max((int(f.split('_')[1].split('.')[0]) for f in files), default=0)

    # Find new max_race
    max_race = 0
    for i in range(1, 31):
        url = BASE_URL.format(i)
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data:
                    max_race = i
                else:
                    break
            else:
                break
        except Exception as e:
            print(f"Error fetching race {i}: {e}")
            break

    if max_race <= max_saved:
        print("No new data to update.")
        return

    # Fetch new races
    new_races = {}
    for i in range(max_saved + 1, max_race + 1):
        url = BASE_URL.format(i)
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data:
                    new_races[i] = data
        except Exception as e:
            print(f"Error fetching race {i}: {e}")

    # Save new races with their race numbers
    for race_num, data in new_races.items():
        filename = f"race_{race_num}.json"
        filepath = os.path.join(PATH, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print(f"Saved {filename}")

# Run update by default for optimization
if __name__ == "__main__":
    #scrape_all()  # Use this to scrape from scratch
    update()
