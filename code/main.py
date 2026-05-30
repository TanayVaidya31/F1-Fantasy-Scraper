from scrapers.player_scraper_updated import player_scrape_main
from scrapers.raw_json_scraper import scrape_all_raw, update_raw

from data_formatters.raw_json_formatter import format_all_raw
from data_formatters.playerinfo_formatter import player_formatter
from data_formatters.playerinfo_excel import playerinfo_excel_report
from data_formatters.players_excel import player_excel_report

from analysers.concombo_heatmap import constructor_combo_heatmap
from analysers.conspoints import conpoints_perrace_lineplot
from analysers.consprice import consprice_perrace_lineplot
from analysers.costcap_analysis import costcap_analysis
from analysers.dripoints import dripoints_perrace_lineplot
from analysers.driprice import driprice_perrace_lineplot
from analysers.plottable_experi_public import plottable_experi_public
from analysers.plottable_experi import plottable_experi
from analysers.points_comp import points_comparison_lineplot
from analysers.rank_boxlplot import rank_boxplot_all
from analysers.swaps import team_swaps_horizontal_bargraph



if __name__ == "__main__":
    # Step 1: Scrape raw JSON data (only new data if update=True)
    scrape_all_raw()  # Use this to scrape from scratch, or update_raw() to only fetch new data
    # update_raw()  # Use this to only fetch new data since last scrape  

    # Step 2: Scrape player data (only new data if update=True)
    # player_scrape_main(update=False)  # Set update=True to only scrape new grand prix data, or False to scrape all data from the beginning
    player_scrape_main(update=True)  # Set update=True to only scrape new grand prix data, or False to scrape all data from the beginning

    # Step 3: Format raw JSON into processed CSVs
    format_all_raw() 

    # Step 4: Format playerinfo CSVs for Excel output
    player_formatter()

    # Step 5: Format players CSVs for Excel output
    player_excel_report()  # Generate the players Excel report after formatting
    playerinfo_excel_report()  # Generate the playerinfo Excel report after formatting

    # Step 6: Run analysers to generate visualizations
    constructor_combo_heatmap()
    conpoints_perrace_lineplot()
    consprice_perrace_lineplot()
    costcap_analysis()
    dripoints_perrace_lineplot()
    driprice_perrace_lineplot()
    plottable_experi_public()
    plottable_experi()
    points_comparison_lineplot()
    rank_boxplot_all()
    team_swaps_horizontal_bargraph()