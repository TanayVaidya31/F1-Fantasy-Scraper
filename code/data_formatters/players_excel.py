import os
import pandas as pd
import seaborn as sns

CURRENT_DIR = os.path.abspath(__file__)
PROJECT_ROOT = CURRENT_DIR
for _ in range(3):  # go up 3 levels
    PROJECT_ROOT = os.path.dirname(PROJECT_ROOT)
processed_dir = os.path.join(PROJECT_ROOT, "data", "processed")
confidential_dir = os.path.join(PROJECT_ROOT, "analysis", "confidential_analysis")
os.makedirs(confidential_dir, exist_ok=True)

# Find all round folders excluding R0
race_folders = sorted(
    [f for f in os.listdir(processed_dir) if f.startswith("R") and f != "R0"],
    key=lambda x: int(x.lstrip("R")),
    reverse=True,
)

output_path = os.path.join(confidential_dir, "racewise_players_report.xlsx")

with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
    workbook = writer.book

    # Formatting styles
    header_format = workbook.add_format(
        {"bold": True, "bg_color": "#333333", "font_color": "#FFFFFF", "align": "center"}
    )
    rank_format = workbook.add_format({"align": "center", "bg_color": "#F2F2F2"})
    team_name_format = workbook.add_format({"bg_color": "#CBCBCB", "align": "center"})
    points_format = workbook.add_format({"num_format": "0", "bg_color": "#E2EFDA", "align": "center"})
    rem_cost_cap_format = workbook.add_format({"num_format": "0.0", "bg_color": "#DDEBF7", "align": "center"})
    dri1_format = workbook.add_format({"bg_color": "#E9CFEE", "align": "center"})
    drirest_format = workbook.add_format({"bg_color": "#D2EFD8", "align": "center"})
    con_format = workbook.add_format({"bg_color": "#D4E3ED", "align": "center"})
    lim_chip_format = workbook.add_format({"bg_color": "#6278DE", "align": "center"})
    threex_chip_format = workbook.add_format({"bg_color": "#62E16C", "align": "center"})
    noneg_chip_format = workbook.add_format({"bg_color": "#A261DC", "align": "center"})
    wild_chip_format = workbook.add_format({"bg_color": "#DE6060", "align": "center"})
    auto_chip_format = workbook.add_format({"bg_color": "#5EDACD", "align": "center"})
    final_chip_format = workbook.add_format({"bg_color": "#DCAB62", "align": "center"})

    for folder in race_folders:
        file_path = os.path.join(processed_dir, folder, "players.csv")
        if not os.path.exists(file_path):
            continue

        df = pd.read_csv(file_path)
        # df.insert(0, "Overall Rank", range(1, len(df) + 1))

        df = df.rename(columns={
            'Rank': 'Race Rank',
            'Points': 'Points Scored',
            'Remaining_Cost_Cap': 'Remaining Cost Cap',
            'Dri1': 'Lead Driver (2x)',
            'Dri2': 'Driver #2',
            'Dri3': 'Driver #3',
            'Dri4': 'Driver #4',
            'Dri5': 'Driver #5',
            'Con1': 'Constructor #1',
            'Con2': 'Constructor #2',
            'Chips': 'Chips Used'
        })

        sheet_name = f"Race {int(folder.lstrip('R'))}"
        df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=1, header=False)
        worksheet = writer.sheets[sheet_name]

        # Write headers with formatting
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)

        # Set column widths
        worksheet.set_column(0, 0, 12)  # Rank
        worksheet.set_column(1, 1, 30)  # Team
        worksheet.set_column(2, 2, 20)  # Name
        worksheet.set_column(3, 3, 14)  # Points
        worksheet.set_column(4, 4, 18)  # Rem Cost Cap
        worksheet.set_column(5, 5, 14)  # Lead Driver
        worksheet.set_column(6, 10, 12)  # Other Drivers
        worksheet.set_column(11, 12, 14)  # Constructors
        worksheet.set_column(12, 12, 12)  # Chips

        # Apply formatting row by row
        for row_idx in range(len(df)):
            worksheet.write(row_idx + 1, 0, df.at[row_idx, "Race Rank"], rank_format)
            worksheet.write(row_idx + 1, 1, df.at[row_idx, "Team"], team_name_format)
            worksheet.write(row_idx + 1, 2, df.at[row_idx, "Name"], team_name_format)

            total_points = df.at[row_idx, "Points Scored"]
            if pd.notna(total_points):
                worksheet.write_number(row_idx + 1, 3, total_points, points_format)
            else:
                worksheet.write(row_idx + 1, 3, "", points_format)

            cost_cap = df.at[row_idx, "Remaining Cost Cap"]
            if pd.notna(cost_cap):
                worksheet.write_number(row_idx + 1, 4, cost_cap, rem_cost_cap_format)
            else:
                worksheet.write(row_idx + 1, 4, "", rem_cost_cap_format)

            lead_driver = df.at[row_idx, "Lead Driver (2x)"]
            if pd.notna(lead_driver) and str(lead_driver).strip():
                worksheet.write(row_idx + 1, 5, lead_driver, dri1_format)
            else:
                worksheet.write(row_idx + 1, 5, "", dri1_format)

            for i in range(2, 6):
                driver_col = f"Driver #{i}"
                if driver_col in df.columns:
                    driver = df.at[row_idx, driver_col]
                    if pd.notna(driver) and str(driver).strip():
                        worksheet.write(row_idx + 1, df.columns.get_loc(driver_col), driver, drirest_format)
                    else:
                        worksheet.write(row_idx + 1, df.columns.get_loc(driver_col), "", drirest_format)

            for con_col in ["Constructor #1", "Constructor #2"]:
                if con_col in df.columns:
                    constructor = df.at[row_idx, con_col]
                    if pd.notna(constructor) and str(constructor).strip():
                        worksheet.write(row_idx + 1, df.columns.get_loc(con_col), constructor, con_format)
                    else:
                        worksheet.write(row_idx + 1, df.columns.get_loc(con_col), "", con_format)

            chip_used = df.at[row_idx, "Chips Used"]
            if pd.notna(chip_used) and str(chip_used).strip():
                if "Limitless" in chip_used:
                    worksheet.write(row_idx + 1, df.columns.get_loc("Chips Used"), chip_used, lim_chip_format)
                elif "x3 Boost" in chip_used:
                    worksheet.write(row_idx + 1, df.columns.get_loc("Chips Used"), chip_used, threex_chip_format)
                elif "No Negative" in chip_used:
                    worksheet.write(row_idx + 1, df.columns.get_loc("Chips Used"), chip_used, noneg_chip_format)
                elif "Wildcard" in chip_used:
                    worksheet.write(row_idx + 1, df.columns.get_loc("Chips Used"), chip_used, wild_chip_format)
                elif "Auto Pilot" in chip_used:
                    worksheet.write(row_idx + 1, df.columns.get_loc("Chips Used"), chip_used, auto_chip_format)
                elif "Final Fix" in chip_used:
                    worksheet.write(row_idx + 1, df.columns.get_loc("Chips Used"), chip_used, final_chip_format)
                else:
                    worksheet.write(row_idx + 1, df.columns.get_loc("Chips Used"), chip_used)

        # Conditional formatting for points using a seaborn green continuous palette
        viridis_colors = sns.color_palette("Blues", 3).as_hex()
        worksheet.conditional_format(
            1,
            3,
            len(df),
            3,
            {
                "type": "3_color_scale",
                "min_color": viridis_colors[0],
                "mid_color": viridis_colors[1],
                "max_color": viridis_colors[2],
            },
        )

        worksheet.conditional_format(
            1,
            4,
            len(df),
            4,
            {
                "type": "3_color_scale",
                "min_color": "#fee9e9",
                "mid_color": "#e29e9e",
                "max_color": "#d35151",
            },
        )

        worksheet.conditional_format(
            1,
            6,
            len(df),
            6,
            {"type": "2_color_scale", "min_color": "#FFEB9C", "max_color": "#C6EFCE"},
        )
