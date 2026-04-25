import csv
import json
import os
import re

CURRENT_DIR = os.path.abspath(__file__)
PROJECT_ROOT = CURRENT_DIR
for _ in range(3):  # go up 3 levels
    PROJECT_ROOT = os.path.dirname(PROJECT_ROOT)
RAW_PATH = os.path.join(PROJECT_ROOT, "data", "raw")
PROCESSED_PATH = os.path.join(PROJECT_ROOT, "data", "processed")

RACE_FILE_RE = re.compile(r"^race_(\d+)\.json$")


def find_raw_files():
    if not os.path.isdir(RAW_PATH):
        raise FileNotFoundError(f"Raw path not found: {RAW_PATH}")

    files = []
    for name in os.listdir(RAW_PATH):
        match = RACE_FILE_RE.match(name)
        if match:
            files.append((int(match.group(1)), name))
    return sorted(files, key=lambda x: x[0])


def build_row_with_empty_price(item):
    # Build row with empty price column for initial processing
    points = item.get("ProjectedGamedayPoints", "0")
    try:
        points = str(int(float(points)))
    except ValueError:
        points = "0"
    return [
        item.get("DriverTLA", ""),
        points,
        "",  # Empty price to be filled later
    ]


def write_csv(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Name", "Points", "Price"])
        for row in rows:
            writer.writerow(row)


def process_race_for_points(race_num, all_races):
    # Write name and points data for a race to RN folder, but skip price (price will be added in the next pass)
    if race_num not in all_races:
        return
    
    values = all_races[race_num]
    driver_rows = []
    constructor_rows = []

    for item in values:
        position = str(item.get("PositionName", "")).upper()
        row = build_row_with_empty_price(item)
        if position == "DRIVER":
            driver_rows.append(row)
        elif position == "CONSTRUCTOR":
            constructor_rows.append(row)

    race_dir = os.path.join(PROCESSED_PATH, f"R{race_num}")
    os.makedirs(race_dir, exist_ok=True)

    write_csv(os.path.join(race_dir, "drivers.csv"), driver_rows)
    write_csv(os.path.join(race_dir, "constructors.csv"), constructor_rows)

    print(f"Processed R{race_num}: {len(driver_rows)} drivers, {len(constructor_rows)} constructors (points from race {race_num})")


def write_price_csv(csv_path, price_map):
    # Write a CSV file with zero points and price values from price_map (used for pre-race folders that are missing the initial points+price CSVs) 
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Points", "Price"])
        for name, price in price_map.items():
            writer.writerow([name, "0", price])


def update_csv_with_prices(csv_path, price_map):
    # Update a CSV file by adding prices in the price column based on the price_map (used for updating existing CSVs with price data from the next race) 
    if not os.path.exists(csv_path):
        return
    
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)
    
    # Update price column (index 2) based on price_map
    for row in rows:
        if row and row[0]:  # Ensure row has name
            name = row[0]
            if name in price_map:
                row[2] = price_map[name]
    
    # Write back
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for row in rows:
            writer.writerow(row)


def update_race_with_price(folder_num, race_num, all_races):
    # Update R(folder_num) with price data from race_num
    if race_num not in all_races:
        return
    
    values = all_races[race_num]
    
    # Build price map: name -> price
    driver_price_map = {}
    constructor_price_map = {}
    
    for item in values:
        position = str(item.get("PositionName", "")).upper()
        name = item.get("DriverTLA", "")
        price = item.get("Value", "")
        
        if name:
            if position == "DRIVER":
                driver_price_map[name] = price
            elif position == "CONSTRUCTOR":
                constructor_price_map[name] = price
    
    race_dir = os.path.join(PROCESSED_PATH, f"R{folder_num}")
    os.makedirs(race_dir, exist_ok=True)
    
    # Ensure pre-race folder has initial zero-point CSVs if missing
    drivers_csv = os.path.join(race_dir, "drivers.csv")
    if not os.path.exists(drivers_csv):
        write_price_csv(drivers_csv, driver_price_map)
    else:
        update_csv_with_prices(drivers_csv, driver_price_map)

    constructors_csv = os.path.join(race_dir, "constructors.csv")
    if not os.path.exists(constructors_csv):
        write_price_csv(constructors_csv, constructor_price_map)
    else:
        update_csv_with_prices(constructors_csv, constructor_price_map)


def format_all():
    os.makedirs(PROCESSED_PATH, exist_ok=True)
    raw_files = find_raw_files()
    if not raw_files:
        print(f"No raw JSON files found in {RAW_PATH}")
        return

    # Load all race data into memory
    all_races = {}
    for race_num, filename in raw_files:
        raw_path = os.path.join(RAW_PATH, filename)
        with open(raw_path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        all_races[race_num] = payload.get("Data", {}).get("Value", [])

    last_race_num = max(all_races.keys())
    
    # First pass: write name+points for all races except the last one
    # (processed race folder is one behind raw, so skip latest race points)
    for race_num in sorted(all_races.keys()):
        if race_num == last_race_num:
            break  # Skip last race's points
        process_race_for_points(race_num, all_races)

    # Second pass: update each folder with price from the next race
    # race_N price -> R(N-1), so: R(N-1) gets price from race_N
    for i, (race_num, _) in enumerate(raw_files):
        folder_num = race_num - 1  # race_1 price -> R0
        update_race_with_price(folder_num, race_num, all_races)
        print(f"Updated R{folder_num} with price from race {race_num}")


if __name__ == "__main__":
    format_all()
