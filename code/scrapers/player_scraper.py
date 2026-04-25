import selenium
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import os
import csv
from dotenv import load_dotenv
    
load_dotenv()
CURRENT_DIR = os.path.abspath(__file__)
PROJECT_ROOT = CURRENT_DIR
for _ in range(3):  # go up 3 levels
    PROJECT_ROOT = os.path.dirname(PROJECT_ROOT)
EMAIL = os.getenv("F1_FANTASY_EMAIL")
PASSWORD = os.getenv("F1_FANTASY_PASSWORD")
PRIVATE_LEAGUE_URL = os.getenv("F1_FANTASY_PRIVATE_LEAGUE_URL")
MAIN_LINK = 'https://fantasy.formula1.com/en/'
    
def scrape(link):
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    options.add_argument('--disable-blink-features=AutomationControlled')
    prefs = {
        "download.default_directory": "/tmp",
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True,
        "download.directory_upgrade": True,
    }
    options.add_experimental_option('prefs', prefs)
    #driver = uc.Chrome(options=options)
    driver = uc.Chrome(options=options, version_main=146)
    driver.maximize_window()
    driver.get(link)
    #print("test")
    time.sleep(5)

    wait = WebDriverWait(driver, 10)  # Wait up to 10 seconds

    try:
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe[@title='SP Consent Message']")))
        #print("Found and switched to iframe")
        cookies_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Essential only cookies']")))
        #print("Found cookies button")
        cookies_button.click()
        #print("Clicked cookies button")
        driver.switch_to.default_content()
        #print("Switched back to main content")
        time.sleep(2)
    except Exception as e:
        print(f"Cookies button not found or clickable: {e}")

    try:
        signin_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='SIGN IN']")))
        #print("Found sign in button")
        signin_button.click()
        #print("Clicked sign in button")
        time.sleep(2)
    except Exception as e:
        print(f"Sign in button not found or clickable: {e}")

    try:
        email_input = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "txtLogin")))
        #print("Found email input")
        password_input = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "txtPassword")))
        #print("Found password input")
        email_input.send_keys(EMAIL)
        #print("Entered email")
        time.sleep(1)
        password_input.send_keys(PASSWORD)
        #print("Entered password")
        time.sleep(1)
        unhide_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[@class='eyeIcon eyeHide']")))
        #print("Found unhide password button")
        unhide_button.click()
        #print("Clicked unhide password button")
        time.sleep(1)
        mainsignin_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Sign In']")))
        #print("Found main sign in button")
        mainsignin_button.click()
        #print("Clicked main sign in button")
        time.sleep(3)

    except Exception as e:
        print(f"Email or password input not found: {e}")

    try:
        driver.get(PRIVATE_LEAGUE_URL)
        # print("Navigated to league")
        time.sleep(1)

    except Exception as e:
        print(f"Login failed: {e}")

    try:
        overall_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Overall']")))
        # print("Found overall button")
        overall_button.click()
        # print("Clicked overall button")
        time.sleep(1)

    except Exception as e:
        print(f"Overall button not found or clicked: {e}")

    try:            
        gp_buttons = wait.until(EC.element_to_be_clickable((By.XPATH, "//li[@class='si-select__option ']")))
        gp_buttons = driver.find_elements(By.XPATH, "//li[@class='si-select__option ']")
        gp_count = len(gp_buttons)
        # print(f"Found {gp_count} grand prix buttons")
        for i in range(gp_count):
            gp_buttons = driver.find_elements(By.XPATH, "//li[@class='si-select__option ']")
            driver.execute_script("arguments[0].click();", gp_buttons[i])
            # print(f"Clicked grand prix button {i}")
            time.sleep(3)

            # OLDER CODE FOR DEBUGGING
            # test = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='si-miniCard__name']")))
            # player_teams = driver.find_elements(By.XPATH, "//div[@class='si-miniCard__name']")
            # print(f"Found player teams for grand prix {i}: {[team.text for team in player_teams]}")
            # teams = [team.text for team in player_teams]
            # print(f"Found player teams for grand prix {i}: {teams}")

            # player_names = driver.find_elements(By.XPATH, "//div[@class='si-miniCard__team']")
            # print(f"Found player names for grand prix {i}: {[name.text for name in player_names]}")
            # names = [name.text for name in player_names]
            # print(f"Found player names for grand prix {i}: {names}")

            # player_points = driver.find_elements(By.XPATH, "//td[@class='si-tbl si-tbl--points']")
            # print(f"Found player points for grand prix {i}: {[point.text for point in player_points]}")
            # points = [point.text for point in player_points]
            # print(f"Found player points for grand prix {i}: {points}")

            # # Save to players.csv
            # race_dir = os.path.join(PROJECT_ROOT, "data", "processed", f"R{i+1}")
            # os.makedirs(race_dir, exist_ok=True)
            # csv_path = os.path.join(race_dir, "players.csv")
            # print(f"Saving players data to {csv_path}")
            # with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            #     writer = csv.writer(f)
            #     writer.writerow(["Team", "Name", "Points"])
            #     for team, name, pts in zip(teams, names, points):
            #         writer.writerow([team, name, pts])
            # print(f"Saved players data to {csv_path}")

            player_main_rows = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//tr[@role='button']")))
            player_main_row_count = len(player_main_rows)
            # print(f"Found player main rows for grand prix {i}: {player_main_row_count} rows")

            all_players_data = []

            for j in range(player_main_row_count):
                current_row = player_main_rows[j]
                player_rank = current_row.find_element(By.CLASS_NAME, "si-user__rank").text
                player_team = current_row.find_element(By.CLASS_NAME, "si-miniCard__name").text
                player_name = current_row.find_element(By.CLASS_NAME, "si-miniCard__team").text
                player_points = current_row.find_element(By.CLASS_NAME, "si-tbl.si-tbl--points").text
                # print(f"\nPlayer {j} for grand prix {i}: Rank={player_rank}, Team={player_team}, Name={player_name}, Points={player_points}")

                driver.execute_script("arguments[0].click();", current_row)
                # print(f"Clicked player {j} for grand prix {i}")
                time.sleep(2)
                player_team_card_container = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "si-oppositeTeamView__summary-container")))
                
                player_team_card_container_nametest = player_team_card_container.find_element(By.CLASS_NAME, "si-oppositeTeamView__summary-teamName").text
                # print(f"Team name from card container for player {j}: {player_team_card_container_nametest}")
                if player_team_card_container_nametest != player_team:
                    # print(f"Team name mismatch for player {j} in grand prix {i}: expected {player_team}, found {player_team_card_container_nametest}")
                    time.sleep(2)
                    player_team_card_container_nametest = player_team_card_container.find_element(By.CLASS_NAME, "si-oppositeTeamView__summary-teamName").text
                    # print(f"Rechecked team name for player {j} in grand prix {i}: found {player_team_card_container_nametest}")

                player_team_remaining_costcap = player_team_card_container.find_element(By.CLASS_NAME, "si-oppositeTeamView__summary-value").text
                # Remove first and last character and convert to float
                costcap_cleaned = player_team_remaining_costcap[1:-1] if len(player_team_remaining_costcap) > 2 else player_team_remaining_costcap
                # print(f"Remaining cost cap for player {j} in grand prix {i}: {costcap_cleaned}")
                
                player_team_driver_names = player_team_card_container.find_elements(By.CLASS_NAME, "si-oppositeTeamView__roster-name-last")
                driver_names = [driver_name.text[:3] for driver_name in player_team_driver_names]
                # print(f"Driver names for player {j}: {driver_names}")
                
                player_team_constructor_names = player_team_card_container.find_elements(By.XPATH, "//div[@class='si-oppositeTeamView__roster-name si-oppositeTeamView__roster-name--constructor']")
                constructor_names = [cons.text[:3] for cons in player_team_constructor_names]
                constructor_names = [
                    "RBR" if name == "Red" else "RBs" if name == "Rac" else name
                    for name in constructor_names
                ]
                # print(f"Constructor names for player {j}: {constructor_names}")

                # Use find_elements to quickly check if element exists (returns empty list instead of exception)
                chip_elements = player_team_card_container.find_elements(By.CLASS_NAME, "si-booster__box-text")
                player_team_chips = chip_elements[0].text if chip_elements else ""
                # print(f"Chip for player {j}: {player_team_chips}")

                # Pad driver and constructor lists to required length
                while len(driver_names) < 5:
                    driver_names.append("")
                while len(constructor_names) < 2:
                    constructor_names.append("")

                # Create row data: Rank,Team,Name,Points,Remaining_Cost_Cap,Dri1,Dri2,Dri3,Dri4,Dri5,Con1,Con2,Chips
                row_data = [
                    player_rank,
                    player_team,
                    player_name,
                    player_points,
                    costcap_cleaned,
                    driver_names[0],
                    driver_names[1],
                    driver_names[2],
                    driver_names[3],
                    driver_names[4],
                    constructor_names[0],
                    constructor_names[1],
                    player_team_chips
                ]
                all_players_data.append(row_data)

            # Save all players data to CSV for this grand prix
            race_dir = os.path.join(PROJECT_ROOT, "data", "processed", f"R{i+1}")
            os.makedirs(race_dir, exist_ok=True)
            csv_path = os.path.join(race_dir, "players.csv")
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Rank", "Team", "Name", "Points", "Remaining_Cost_Cap", "Dri1", "Dri2", "Dri3", "Dri4", "Dri5", "Con1", "Con2", "Chips"])
                writer.writerows(all_players_data)
            # print(f"Saved {len(all_players_data)} players to {csv_path}")

            if i == 0:
                r0_data = []
                for row in all_players_data:
                    r0_data.append([
                        "0",
                        row[1],
                        row[2],
                        "0",
                        "100.0",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        ""
                    ])
                r0_dir = os.path.join(PROJECT_ROOT, "data", "processed", "R0")
                os.makedirs(r0_dir, exist_ok=True)
                r0_path = os.path.join(r0_dir, "players.csv")
                with open(r0_path, 'w', newline='', encoding='utf-8') as f0:
                    writer0 = csv.writer(f0)
                    writer0.writerow(["Rank", "Team", "Name", "Points", "Remaining_Cost_Cap", "Dri1", "Dri2", "Dri3", "Dri4", "Dri5", "Con1", "Con2", "Chips"])
                    writer0.writerows(r0_data)

            driver.execute_script("arguments[0].click();", overall_button)
            # print(f"Clicked overall button for grand prix {i}")
            time.sleep(3)

        # print("Clicked all grand prix button")
        time.sleep(5)

    except Exception as e:
        print(f"Grand prix button not found or error while scraping data (look with head mode if player cards are not updating upon clicking): {e}")

    time.sleep(2)

scrape(MAIN_LINK)