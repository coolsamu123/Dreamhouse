"""
Utility functions for Dreamhouse scrapers.
"""

import hashlib
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('dreamhouse')

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
DOCS_DIR = BASE_DIR / 'docs'


def generate_listing_id(url: str) -> str:
    """Generate a unique ID for a listing based on its URL."""
    return hashlib.md5(url.encode()).hexdigest()[:12]


def load_json(filepath: Path) -> dict | list:
    """Load JSON file, return empty dict/list if not exists."""
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_json(filepath: Path, data: dict | list) -> None:
    """Save data to JSON file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_listings() -> dict:
    """Load current listings."""
    return load_json(DATA_DIR / 'listings.json')


def save_listings(listings: dict) -> None:
    """Save listings to file."""
    save_json(DATA_DIR / 'listings.json', listings)


def load_history() -> dict:
    """Load history of seen listings."""
    return load_json(DATA_DIR / 'history.json')


def save_history(history: dict) -> None:
    """Save history to file."""
    save_json(DATA_DIR / 'history.json', history)


def send_telegram(message: str) -> bool:
    """
    Send a message via Telegram bot.

    Requires environment variables:
    - TELEGRAM_BOT_TOKEN
    - TELEGRAM_CHAT_ID
    """
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')

    if not token or not chat_id:
        logger.warning("Telegram credentials not configured")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown',
        'disable_web_page_preview': False
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        logger.info("Telegram message sent successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to send Telegram message: {e}")
        return False


def format_telegram_message(listing: dict) -> str:
    """Format a listing for Telegram notification."""
    commune = listing.get('commune', 'Bruxelles')
    address = listing.get('address', 'Adresse non disponible')
    price = listing.get('price', 'N/A')
    bedrooms = listing.get('bedrooms', '?')
    surface = listing.get('surface', '?')
    source = listing.get('source', 'Unknown')
    url = listing.get('source_url', '#')

    if isinstance(price, (int, float)):
        price_str = f"{price:,.0f}".replace(',', '.')
    else:
        price_str = str(price)

    message = f"""🏠 *Nouvelle annonce !*

📍 *{commune}* - {address}
💰 {price_str} €
🛏️ {bedrooms} chambre(s) | 📐 {surface} m²

🏢 Source: {source}

🔗 [Voir l'annonce]({url})"""

    return message


def notify_new_listings(new_listings: list[dict]) -> None:
    """Send Telegram notifications for new listings."""
    for listing in new_listings:
        message = format_telegram_message(listing)
        send_telegram(message)
        time.sleep(0.5)  # Avoid rate limiting


def is_listing_new(listing: dict, hours: int = 24) -> bool:
    """Check if a listing is considered new (within last N hours)."""
    first_seen = listing.get('first_seen')
    if not first_seen:
        return True

    try:
        seen_time = datetime.fromisoformat(first_seen.replace('Z', '+00:00'))
        now = datetime.now(seen_time.tzinfo)
        diff = now - seen_time
        return diff.total_seconds() < hours * 3600
    except Exception:
        return False


def merge_listings(existing: dict, new_listings: list[dict]) -> tuple[dict, list[dict]]:
    """
    Merge new listings with existing ones.

    Returns:
        Tuple of (updated listings dict, list of truly new listings)
    """
    now = datetime.utcnow().isoformat() + 'Z'
    truly_new = []

    for listing in new_listings:
        listing_id = listing.get('id') or generate_listing_id(listing.get('source_url', ''))
        listing['id'] = listing_id

        if listing_id in existing:
            # Update last_seen
            existing[listing_id]['last_seen'] = now
            existing[listing_id]['is_new'] = False
        else:
            # New listing
            listing['first_seen'] = now
            listing['last_seen'] = now
            listing['is_new'] = True
            existing[listing_id] = listing
            truly_new.append(listing)

    return existing, truly_new


# Search criteria configuration
SEARCH_CRITERIA = {
    "type": "appartement",
    "transaction": "vente",  # achat
    "communes": ["Saint-Gilles", "Forest", "Ixelles"],
    "prix_max": 500000,
    "prix_min": 0,
    "chambres_min": 1,
    "surface_min": 80,
}


def matches_criteria(listing: dict) -> bool:
    """Check if a listing matches the search criteria."""
    price = listing.get('price')
    if price:
        if isinstance(price, str):
            try:
                price = float(price.replace('.', '').replace(',', '.').replace('€', '').strip())
            except ValueError:
                price = None

        if price:
            if price > SEARCH_CRITERIA['prix_max'] or price < SEARCH_CRITERIA['prix_min']:
                return False

    surface = listing.get('surface')
    if surface and isinstance(surface, (int, float)):
        if surface < SEARCH_CRITERIA['surface_min']:
            return False

    commune = listing.get('commune', '').lower()
    valid_communes = [c.lower() for c in SEARCH_CRITERIA['communes']]
    if commune and not any(vc in commune for vc in valid_communes):
        return False

    return True
