# F1 Fantasy Scraper

A small scraper project for Formula 1 Fantasy data. This repository collects raw race JSON data from the official F1 Fantasy API and can also scrape private league player teams using a logged-in account.

## Project Structure

- `code/`
  - `raw_json_scraper.py` - fetches live race driver JSON feeds and stores them in `data/raw/`.
  - `player_scraper.py` - uses Selenium / undetected-chromedriver to log into F1 Fantasy, navigate to a private league, and scrape player team data.
- `data/`
  - `raw/` - raw JSON race files like `race_1.json`, `race_2.json`, etc.
  - `processed/` - prepared CSV files organized by race (example output folders `R1/`, `R2/`, ...).
- `.env.example` - example environment variables used for private league scraping.

## Requirements

- Python 3.10+ (or compatible)
- `requests`
- `selenium`
- `undetected-chromedriver`
- `webdriver-manager`
- `python-dotenv`

Install dependencies with:

```bash
pip install requests selenium undetected-chromedriver webdriver-manager python-dotenv
```

## Usage

### Raw JSON scraping

To fetch official F1 Fantasy race feeds and save them under `data/raw/`:

```bash
python code/raw_json_scraper.py
```

### Private league player scraping

This tool requires valid F1 Fantasy login credentials plus a private league URL. Create a `.env` file in the repository root with:

```env
F1_FANTASY_EMAIL="your-email@example.com"
F1_FANTASY_PASSWORD="your-password"
F1_FANTASY_PRIVATE_LEAGUE_URL="https://fantasy.formula1.com/en/leagues/leaderboard/private/your-league-id"
```

Then run the scraper:

```bash
python code/player_scraper.py
```

## Notes

- The `player_scraper.py` workflow is built around the current F1 Fantasy website layout, so selectors may need updates if the site changes.
- This project is a work in progress.
- Handling for new drivers, teams, and evolving F1 Fantasy page structure will be added in the future.

## Disclaimer

Use this project responsibly and follow all applicable terms of service for the F1 Fantasy site.
