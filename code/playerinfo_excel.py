import os
import pandas as pd
import seaborn as sns

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
processed_dir = os.path.join(PROJECT_ROOT, "data", "processed")
analysis_dir = os.path.join(PROJECT_ROOT, "analysis")
os.makedirs(analysis_dir, exist_ok=True)

# Find all round folders excluding R0
race_folders = sorted(
    [f for f in os.listdir(processed_dir) if f.startswith("R") and f != "R0"],
    key=lambda x: int(x.lstrip("R")),
    reverse=True,
)

output_path = os.path.join(analysis_dir, "racewise_playerinfo_report.xlsx")

with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
    workbook = writer.book

    # Formatting styles
    header_format = workbook.add_format(
        {"bold": True, "bg_color": "#333333", "font_color": "#FFFFFF", "align": "center"}
    )
    rank_format = workbook.add_format({"align": "center", "bg_color": "#F2F2F2"})
    points_format = workbook.add_format({"num_format": "0", "bg_color": "#E2EFDA", "align": "center"})
    cost_cap_format = workbook.add_format({"num_format": "0.0", "bg_color": "#DDEBF7", "align": "center"})
    swaps_used_format = workbook.add_format({"bg_color": "#FFC7CE", "align": "right"})
    swaps_left_format = workbook.add_format({"bg_color": "#C6EFCE", "align": "center"})
    team_name_format = workbook.add_format({"bg_color": "#CBCBCB", "align": "center"})
    chip_formats = {
        "Limitless": workbook.add_format({"bg_color": "#6278DE", "align": "center"}),
        "3x Boost": workbook.add_format({"bg_color": "#62E16C", "align": "center"}),
        "No Negative": workbook.add_format({"bg_color": "#A261DC", "align": "center"}),
        "Wildcard": workbook.add_format({"bg_color": "#DE6060", "align": "center"}),
        "Auto Pilot": workbook.add_format({"bg_color": "#5EDACD", "align": "center"}),
        "Final Fix": workbook.add_format({"bg_color": "#DCAB62", "align": "center"}),
    }

    for folder in race_folders:
        file_path = os.path.join(processed_dir, folder, "playerinfo.csv")
        if not os.path.exists(file_path):
            continue

        df = pd.read_csv(file_path)
        df.insert(0, "Overall Rank", range(1, len(df) + 1))

        df = df.rename(columns={
            'Total_Points': 'Total Points',
            'Total_Cost_Cap': 'Total Cost Cap',
            'Swaps_Made': 'Transfers Made',
            'Swaps_Rem': 'Transfers Left',
            'LL': 'Limitless',
            '3X': '3x Boost',
            'NN': 'No Negative',
            'WC': 'Wildcard',
            'AP': 'Auto Pilot',
            'FF': 'Final Fix',
        })

        sheet_name = f"Race {int(folder.lstrip('R'))}"
        df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=1, header=False)
        worksheet = writer.sheets[sheet_name]

        # Write headers with formatting
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)

        # Set column widths
        worksheet.set_column(0, 0, 12)  # Overall Rank
        worksheet.set_column(1, 1, 30)  # Team
        worksheet.set_column(2, 2, 20)  # Name
        worksheet.set_column(3, 3, 14)  # Total Points
        worksheet.set_column(4, 4, 16)  # Total Cost Cap
        worksheet.set_column(5, 5, 14)  # Transfers Made
        worksheet.set_column(6, 6, 14)  # Transfers Remaining
        worksheet.set_column(7, 12, 12)  # Chips

        # Apply formatting row by row
        for row_idx in range(len(df)):
            worksheet.write(row_idx + 1, 0, df.at[row_idx, "Overall Rank"], rank_format)
            worksheet.write(row_idx + 1, 1, df.at[row_idx, "Team"], team_name_format)
            worksheet.write(row_idx + 1, 2, df.at[row_idx, "Name"], team_name_format)

            total_points = df.at[row_idx, "Total Points"]
            if pd.notna(total_points):
                worksheet.write_number(row_idx + 1, 3, total_points, points_format)
            else:
                worksheet.write(row_idx + 1, 3, "", points_format)

            cost_cap = df.at[row_idx, "Total Cost Cap"]
            if pd.notna(cost_cap):
                worksheet.write_number(row_idx + 1, 4, cost_cap, cost_cap_format)
            else:
                worksheet.write(row_idx + 1, 4, "", cost_cap_format)

            swaps_made = df.at[row_idx, "Transfers Made"]
            if pd.notna(swaps_made):
                worksheet.write_number(row_idx + 1, 5, swaps_made, swaps_used_format)
            else:
                worksheet.write(row_idx + 1, 5, "", swaps_used_format)

            swaps_rem = df.at[row_idx, "Transfers Left"]
            if pd.notna(swaps_rem):
                worksheet.write_number(row_idx + 1, 6, swaps_rem, swaps_left_format)
            else:
                worksheet.write(row_idx + 1, 6, "", swaps_left_format)

            for chip_col, fmt in chip_formats.items():
                if chip_col in df.columns:
                    value = df.at[row_idx, chip_col]
                    if pd.notna(value) and str(value).strip():
                        worksheet.write(row_idx + 1, df.columns.get_loc(chip_col), value, fmt)
                    else:
                        worksheet.write(row_idx + 1, df.columns.get_loc(chip_col), "")

        # Conditional formatting for points using a seaborn purple to green continuous palette
        viridis_colors = sns.color_palette("PRGn", 3).as_hex()[::-1]
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
                "min_color": "#deebf7",
                "mid_color": "#9ecae1",
                "max_color": "#3182bd",
            },
        )

        # Add a simple bar visualization to swaps made only
        worksheet.conditional_format(
            1, 5, len(df), 5, {"type": "data_bar", "bar_color": "#FF8080"}
        )
        worksheet.conditional_format(
            1,
            6,
            len(df),
            6,
            {"type": "2_color_scale", "min_color": "#FFEB9C", "max_color": "#C6EFCE"},
        )
