import csv
import json
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
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


def build_row(item):
    points = item.get("ProjectedGamedayPoints", "0")
    try:
        points = str(int(float(points)))
    except ValueError:
        points = "0"
    return [
        item.get("DriverTLA", ""),
        points,
        item.get("Value", ""),
    ]


def write_csv(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Name", "Points", "Price"])
        for row in rows:
            writer.writerow(row)


def process_race_file(race_num, filename):
    raw_path = os.path.join(RAW_PATH, filename)
    with open(raw_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    values = payload.get("Data", {}).get("Value", [])
    driver_rows = []
    constructor_rows = []

    for item in values:
        position = str(item.get("PositionName", "")).upper()
        row = build_row(item)
        if position == "DRIVER":
            driver_rows.append(row)
        elif position == "CONSTRUCTOR":
            constructor_rows.append(row)

    race_dir = os.path.join(PROCESSED_PATH, f"R{race_num}")
    os.makedirs(race_dir, exist_ok=True)

    write_csv(os.path.join(race_dir, "drivers.csv"), driver_rows)
    write_csv(os.path.join(race_dir, "constructors.csv"), constructor_rows)

    print(f"Processed race {race_num}: {len(driver_rows)} drivers, {len(constructor_rows)} constructors")


def format_all():
    os.makedirs(PROCESSED_PATH, exist_ok=True)
    raw_files = find_raw_files()
    if not raw_files:
        print(f"No raw JSON files found in {RAW_PATH}")
        return

    for race_num, filename in raw_files:
        process_race_file(race_num, filename)


if __name__ == "__main__":
    format_all()
