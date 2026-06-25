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
import re

load_dotenv()
CURRENT_DIR = os.path.abspath(__file__)
PROJECT_ROOT = CURRENT_DIR
for _ in range(3):  # go up 3 levels
    PROJECT_ROOT = os.path.dirname(PROJECT_ROOT)
PATH = os.path.join(PROJECT_ROOT, "data", "processed")
EMAIL = os.getenv("F1_FANTASY_EMAIL")
PASSWORD = os.getenv("F1_FANTASY_PASSWORD")
PRIVATE_LEAGUE_URL = os.getenv("F1_FANTASY_PRIVATE_LEAGUE_URL")
MAIN_LINK = 'https://fantasy.formula1.com/en/'

def get_chrome_version_main():
    """Get the main version of the installed Chrome browser."""
    try:
        driver_path = ChromeDriverManager().install()
        #print("driver_path=",driver_path)
        version = re.search(r"(\d+)\.", driver_path)
        if version:
            return int(version.group(1))  # Return the main version (e.g., integer 145)
    except Exception as e:
        print(f"Error getting Chrome version: {e}")
        return None

def init_driver():
    # Get the main version of Chrome
    version_main_value = get_chrome_version_main()
    if not version_main_value:
        raise Exception("Could not determine Chrome version.")

    options = uc.ChromeOptions()
    # options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument('--disable-blink-features=AutomationControlled')
    driver = uc.Chrome(options=options, version_main=version_main_value, use_subprocess=True)
    return driver

def click_cookies(driver, wait):
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

def login(wait):
    try:
        signin_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='SIGN IN']")))
        #print("Found sign in button")
        signin_button.click()
        #print("Clicked sign in button")
        time.sleep(2)
    except Exception as e:
        print(f"Sign in button not found or clickable: {e}")

def enter_credentials(wait):
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

def overall_button(wait):
    try:
        overall_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='si-select__field si-select__field--button']//button")))
        # print("Found overall button")
        overall_button.click()
        # print("Clicked overall button")
        time.sleep(1)

    except Exception as e:
        print(f"Overall button not found or clicked: {e}")

def player_card_check(player_team, player_team_card_container, j, i, count):
    player_team_card_container_nametest = player_team_card_container.find_element(By.CLASS_NAME, "si-oppositeTeamView__summary-teamName").text
    # print(f"Team name from card container for player {j}: {player_team_card_container_nametest}")
    if count and player_team_card_container_nametest != player_team:
        # print(f"Team name mismatch for player {j} in grand prix {i}: expected {player_team}, found {player_team_card_container_nametest}")
        time.sleep(1)
        player_card_check(player_team, player_team_card_container, j, i, count-1)  # Recursive call to check again after waiting
        # print(f"Rechecked team name for player {j} in grand prix {i}: found {player_team_card_container_nametest}")

def scrape_players_data(driver, wait, update):
    try:    
        overall_button(wait)
        gp_buttons = wait.until(EC.element_to_be_clickable((By.XPATH, "//li[@class='si-select__option ']")))
        gp_buttons = driver.find_elements(By.XPATH, "//li[@class='si-select__option ']")
        
        if(update):
            try:            
                # Find existing max_saved
                folders = [
                    f for f in os.listdir(PATH)
                    if f.startswith("R") and f[1:].isdigit()
                ]

                valid_races = []

                for folder in folders:
                    race_num = int(folder[1:])
                    playerinfo_path = os.path.join(PATH, folder, "players.csv")

                    if os.path.exists(playerinfo_path):
                        valid_races.append(race_num)

                max_saved = max(valid_races, default=0)
            
            except Exception as e:
                print(f"Error determining max saved race: {e}")
        else:
            max_saved = 0
        print(f"Max saved race: {max_saved}")

        gp_count = len(gp_buttons)
        print(f"Found {gp_count} grand prix buttons")
        for i in range(max_saved, gp_count):
            gp_buttons = wait.until(EC.element_to_be_clickable((By.XPATH, "//li[@class='si-select__option ']")))
            gp_buttons = driver.find_elements(By.XPATH, "//li[@class='si-select__option ']")
            driver.execute_script("arguments[0].click();", gp_buttons[i])
            print(f"Clicked grand prix button {i}")
            time.sleep(3)

            player_main_rows = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//tr[@role='button']")))
            player_main_row_count = len(player_main_rows)
            # print(f"Found player main rows for grand prix {i}: {player_main_row_count} rows")

            all_players_data = []

            for j in range(player_main_row_count):
                current_row = player_main_rows[j]
                player_rank = current_row.find_element(By.CLASS_NAME, "si-user__rank").text
                player_team = current_row.find_element(By.CLASS_NAME, "si-miniCard__name").text

                if player_team == "ferrari don't fumble":
                    # print(f"\nBugged for player {j} in grand prix {i} before clicking, skipping this player")
                    continue

                player_name = current_row.find_element(By.CLASS_NAME, "si-miniCard__team").text
                player_points = current_row.find_element(By.CLASS_NAME, "si-tbl.si-tbl--points").text
                # print(f"\nPlayer {j} for grand prix {i}: Rank={player_rank}, Team={player_team}, Name={player_name}, Points={player_points}")

                driver.execute_script("arguments[0].click();", current_row)
                # print(f"Clicked player {j} for grand prix {i}")
                time.sleep(1)

                player_team_card_container = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "si-oppositeTeamView__summary-container")))
                player_card_check(player_team, player_team_card_container, j, i, 3)

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

                if(player_team_chips == 'Final Fix'):
                    # print(f"\nPlayer {j} in grand prix {i} has Final Fix chip, different flow to find replaced driver")
                    replaced_driver_parent_element = player_team_card_container.find_element(By.XPATH, "//i[@class='f1i-final-fix']/ancestor::div[@class='si-oppositeTeamView__roster-item  ']")
                    player_team_driver_names = replaced_driver_parent_element.find_elements(By.CLASS_NAME, "si-oppositeTeamView__roster-name-last")
                    replacedwith_driver_name = player_team_driver_names[0].text[:3]
                    print(f"Replaced driver with Final Fix for player {j}: {replacedwith_driver_name}")
                    driver_names[5] += f" <- {replacedwith_driver_name}"  # Add replaced driver as 6th driver in the list (DriFixedOut)
                    print(f"Updated 6th driver name for player {j} in grand prix {i}: {driver_names[5]}")

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
                    player_team_chips,
                    driver_names[5] if len(driver_names) > 5 else ""
                ]
                all_players_data.append(row_data)

            # Save all players data to CSV for this grand prix
            race_dir = os.path.join(PROJECT_ROOT, "data", "processed", f"R{i+1}")
            os.makedirs(race_dir, exist_ok=True)
            csv_path = os.path.join(race_dir, "players.csv")
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Rank", "Team", "Name", "Points", "Remaining_Cost_Cap", "Dri1", "Dri2", "Dri3", "Dri4", "Dri5", "Con1", "Con2", "Chips", "DriFixedOut"])
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
                        "",
                        ""
                    ])
                r0_dir = os.path.join(PROJECT_ROOT, "data", "processed", "R0")
                os.makedirs(r0_dir, exist_ok=True)
                r0_path = os.path.join(r0_dir, "players.csv")
                with open(r0_path, 'w', newline='', encoding='utf-8') as f0:
                    writer0 = csv.writer(f0)
                    writer0.writerow(["Rank", "Team", "Name", "Points", "Remaining_Cost_Cap", "Dri1", "Dri2", "Dri3", "Dri4", "Dri5", "Con1", "Con2", "Chips", "DriFixedOut"])
                    writer0.writerows(r0_data)

            overall_button(wait)
            # print(f"Clicked overall button for grand prix {i}")
            time.sleep(3)

        # print("Clicked all grand prix button")
        time.sleep(5)

    except Exception as e:
        print(f"Grand prix button not found or error while scraping data (look with head mode if player cards are not updating upon clicking): {e}")

    time.sleep(2)

def player_scrape_main(update):
    driver = init_driver()
    driver.get(MAIN_LINK)
    wait = WebDriverWait(driver, 10)
    driver.maximize_window()
    time.sleep(5)
    click_cookies(driver, wait)
    try:
        login(wait)
    except Exception as e:
        print(f"Login process failed: {e}")
        click_cookies(driver, wait)  # Try clicking cookies again if login fails
        try:
            login(wait)
        except Exception as e:
            print(f"Second login attempt failed: {e}")
            driver.quit()
            return    
    enter_credentials(wait)
    driver.get(PRIVATE_LEAGUE_URL)
    # print("Navigated to league")
    time.sleep(1)
    scrape_players_data(driver, wait, update)
    driver.quit()

if __name__ == "__main__":
    player_scrape_main(update=False)  # Set update=True to only scrape new grand prix data, or False to scrape all data from the beginning