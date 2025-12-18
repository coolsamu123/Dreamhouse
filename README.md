# Dreamhouse

Automated real estate scraping system for Brussels apartments in Saint-Gilles, Forest, and Ixelles.

## Features

- Scrapes 20+ real estate agencies in Brussels
- Detects new listings automatically
- Web interface with filters and map view
- Telegram notifications for new listings
- Runs every 2 hours via GitHub Actions

## Project Structure

```
Dreamhouse/
├── .github/workflows/scrape.yml  # Automated scraping
├── scrapers/
│   ├── base_scraper.py           # Base scraper class
│   ├── saint_gilles.py           # Saint-Gilles agencies
│   ├── forest.py                 # Forest agencies
│   ├── ixelles.py                # Ixelles agencies
│   └── utils.py                  # Utilities
├── data/
│   ├── listings.json             # All listings
│   ├── history.json              # Seen listings
│   └── new_listings.json         # New listings
├── docs/                         # GitHub Pages
│   ├── index.html
│   ├── style.css
│   ├── app.js
│   └── listings.json
├── main.py                       # Entry point
└── requirements.txt
```

## Agencies Covered

### Saint-Gilles (1060)
- JAM Properties
- Everest Properties
- Viabilis
- Nesting Realty
- Inside Properties
- Fredimmo
- Modifa

### Forest (1190)
- MYIMMO Altitude
- Immobiliere Georges
- Abri-Europe
- Century 21 A a Z

### Ixelles (1050)
- Lecobel Vaneau
- Oralis Real Estate
- Tribel Immo
- ERA Chatelain
- By the Way
- Fierce Immo
- MyImmo Ixelles
- Address Real Estate
- Immo Clairiere
- Immobiliere de Maurissens
- Engel & Volkers
- Trevi Louise

## Usage

### Run locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run all scrapers
python main.py

# Run a specific scraper
python main.py --scraper "JAM Properties"

# List available scrapers
python main.py --list

# Dry run (no saving)
python main.py --dry-run
```

### Test frontend locally

```bash
cd docs && python -m http.server 8000
```

## Configuration

### Telegram Notifications

1. Create a bot via @BotFather
2. Get the bot token
3. Create a group/channel and get the chat_id
4. Add as GitHub secrets:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`

### Search Criteria

Edit `scrapers/utils.py`:

```python
SEARCH_CRITERIA = {
    "type": "appartement",
    "transaction": "location",
    "communes": ["Saint-Gilles", "Forest", "Ixelles"],
    "prix_max": 1500,
    "prix_min": 800,
    "chambres_min": 1,
    "surface_min": 50,
}
```

## GitHub Pages

The frontend is served at: `https://coolsamu123.github.io/Dreamhouse/`

To enable:
1. Go to repository Settings > Pages
2. Set source to "Deploy from a branch"
3. Select `main` branch and `/docs` folder

## License

MIT
