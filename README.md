# F1 Fantasy Lab

A data pipeline and analysis toolkit for **F1 Fantasy**.  
This project pulls official F1 Fantasy data, optionally scrapes private league data, structures everything into clean datasets, and generates reports and visualizations for analysis.

Designed to be modular and extensible — you can run individual components (scraping, processing, analysis) independently.

---

## Features

- 📥 Automated ingestion of official F1 Fantasy data (JSON feeds)
- 🔐 Optional scraping of **private league data** (Selenium-based)
- 🧹 Structured data pipeline (raw → processed)
- 📊 Multiple analysis modules (Visualisations):
  - Player Performance trends & strategy insights
  - Driver & Constructor Points & Price comparisons
  - Player Budget & Cost Cap analysis
  - Private League Rank, Transfers used and chips distribution trends
  - Export-ready Excel reports

---

## Project Structure

F1-Fantasy-Scraper/
│
├── code/
│   ├── scrapers/              # Data ingestion (JSON + league scraping)
│   ├── data_formatters/       # Data cleaning & transformation
│   └── analysers/             # Visualizations & analysis
│
├── data/
│   ├── raw/                   # Raw JSON data
│   └── processed/             # Structured per-race datasets (R0, R1, ...)
│
├── analysis/                  # Generated plots
│   └── confidential_analysis/ # League-specific outputs
│
├── .env.example               # Environment template
├── requirements.txt
└── README.md

---

## Pipeline Overview

Scrapers -> Raw JSON → Formatter → Processed CSVs → Player Aggregation → Analysis → Visuals / Reports

---

## Data Model

### 📊 Race Folders (`R1`, `R2`, ...)
Each round contains:

- `drivers.csv` / `constructors.csv`  
  → Price + points per race  

- `players.csv`  
  → Team composition, rank, chips, budget  

- `playerinfo.csv`  
  → Aggregated metrics:
  - Total points
  - Cost cap progression
  - Transfers used
  - Chip usage history  

---

### Baseline (`R0`)
A synthetic pre-season state:
- Uses pre race pricing
- Initializes players with appropriate points and cost caps
- Ensures consistent pipeline behavior

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/f1-fantasy-scraper.git
cd f1-fantasy-scraper
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a .env file:
```bash
F1_FANTASY_EMAIL=your_email
F1_FANTASY_PASSWORD=your_password
F1_FANTASY_PRIVATE_LEAGUE_URL=your_league_url
```

---

## Usage

Run the pipeline step-by-step:

```bash
python code/scrapers/raw_json_scraper.py
python code/data_formatters/raw_json_formatter.py
python code/scrapers/player_scraper.py
python code/data_formatters/playerinfo_formatter.py
python code/data_formatters/players_excel.py
python code/data_formatters/playerinfo_excel.py
```

---

## Analysis Modules

- Drivers, Constructors and Players Points Performance Analysis
- League Rank distribution trends
- Transfer usage patterns
<!-- - Limitless and 3x Boost chips usage timing and impact -->
- Team evolution tracking
- Cost Cap Growth Analysis
- Constructor Combinations Analysis
- Price trends across races
- Points consistency
- Tabular Reports
- Excel exports for sharing and reporting

---

## Future Improvements

- 🔮 Predictive Modeling:
  - Points and price prediction models
  - Optimal team selection algorithms

- 🧠 Strategy Optimization:
  - Chip usage strategy modeling
  - Risk-reward simulations

- 📊 Advanced Analytics:
  - Limitless and 3x Boost chips usage timing and impact
  - Player clustering (strategy archetypes)
  - Meta trend detection across leagues

- 🌐 Application Layer
  - Web dashboard for interactive analysis
  - Web-based league comparison tools
  - API layer for querying processed data

- ⚙️ Engineering Enhancements
  - Migrate from CSV → SQL (SQLite/PostgreSQL)
  - Scheduled scraping (cron jobs)
  - Config-driven pipeline execution
  - Dockerization for reproducibility

---

## Disclaimer

This project is for educational and analytical purposes.
Scraping and automated login may violate F1 Fantasy terms of service.
Use responsibly and avoid sharing sensitive credentials.

---

## Notes

Scraper selectors may break if the F1 Fantasy UI changes
Chrome version mismatches can affect Selenium
Raw data is preserved to allow reprocessing without re-scraping

---

## Contributing

Contributions are welcome.
If you find bugs or have ideas for improvements, feel free to open an issue or submit a pull request.
