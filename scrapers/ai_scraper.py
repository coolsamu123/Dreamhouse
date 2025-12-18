"""
AI-powered scraper using DeepSeek API.
Extracts listings from any real estate website using LLM.
"""

import json
import logging
import os
import re
from typing import Optional

import requests
from bs4 import BeautifulSoup

from .base_scraper import BaseScraper
from .utils import generate_listing_id

logger = logging.getLogger('dreamhouse.ai_scraper')

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

EXTRACTION_PROMPT = """Tu es un assistant qui extrait des annonces immobilières d'une page HTML.

Extrais TOUTES les annonces de vente d'appartements de cette page. Pour chaque annonce, retourne un objet JSON avec:
- url: lien vers l'annonce (relatif ou absolu)
- title: titre de l'annonce
- price: prix en nombre (juste le chiffre, sans € ni espaces)
- surface: surface en m² (juste le nombre)
- bedrooms: nombre de chambres (juste le nombre)
- address: adresse ou localisation

Retourne UNIQUEMENT un tableau JSON valide, sans explication. Si aucune annonce, retourne [].

Exemple de réponse:
[{"url": "/bien/123", "title": "Appartement 2ch", "price": 350000, "surface": 85, "bedrooms": 2, "address": "Rue de la Paix, 1060"}]

HTML de la page:
"""


def extract_with_ai(html: str, base_url: str) -> list[dict]:
    """Use DeepSeek to extract listings from HTML."""
    api_key = os.environ.get('DEEPSEEK_API_KEY')

    if not api_key:
        logger.warning("DEEPSEEK_API_KEY not configured")
        return []

    # Clean HTML - remove scripts, styles, keep only body
    soup = BeautifulSoup(html, 'lxml')

    # Remove unwanted elements
    for tag in soup.find_all(['script', 'style', 'nav', 'footer', 'header', 'noscript']):
        tag.decompose()

    # Get text content with some structure
    body = soup.find('body')
    if body:
        clean_html = str(body)[:15000]  # Limit to ~15k chars to save tokens
    else:
        clean_html = str(soup)[:15000]

    try:
        response = requests.post(
            DEEPSEEK_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "user",
                        "content": EXTRACTION_PROMPT + clean_html
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 4000
            },
            timeout=60
        )
        response.raise_for_status()

        result = response.json()
        content = result['choices'][0]['message']['content']

        # Parse JSON from response
        # Try to find JSON array in the response
        json_match = re.search(r'\[[\s\S]*\]', content)
        if json_match:
            listings = json.loads(json_match.group())

            # Normalize URLs
            for listing in listings:
                url = listing.get('url', '')
                if url and not url.startswith('http'):
                    listing['url'] = f"{base_url.rstrip('/')}/{url.lstrip('/')}"

                # Generate ID
                if listing.get('url'):
                    listing['id'] = generate_listing_id(listing['url'])

            return listings

        return []

    except Exception as e:
        logger.error(f"AI extraction failed: {e}")
        return []


class AIScraperMixin:
    """Mixin to add AI extraction capability to any scraper."""

    def parse_with_ai(self, html: str) -> list[dict]:
        """Parse HTML using AI when CSS selectors fail."""
        return extract_with_ai(html, self.base_url)


class UniversalAIScraper(BaseScraper, AIScraperMixin):
    """
    Universal scraper that uses AI to extract listings from any website.
    Falls back to AI when CSS selectors don't find anything.
    """

    name = "Universal AI"
    base_url = ""
    commune = ""
    listing_url = ""

    def __init__(self, name: str, base_url: str, listing_url: str, commune: str):
        super().__init__()
        self.name = name
        self.base_url = base_url
        self.listing_url = listing_url
        self.commune = commune

    def get_listings_url(self) -> str:
        return self.listing_url

    def parse_listing_cards(self, soup: BeautifulSoup) -> list[dict]:
        # Use AI to extract listings
        html = str(soup)
        listings = self.parse_with_ai(html)

        # Add commune to all listings
        for listing in listings:
            if not listing.get('commune'):
                listing['commune'] = self.commune

        return listings


# Pre-configured AI scrapers for problematic sites
AI_SCRAPER_CONFIGS = [
    {
        "name": "JAM Properties (AI)",
        "base_url": "https://www.jamproperties.be",
        "listing_url": "https://www.jamproperties.be/fr/a-vendre",
        "commune": "Saint-Gilles"
    },
    {
        "name": "Lecobel Vaneau (AI)",
        "base_url": "https://www.lecobel-vaneau.be",
        "listing_url": "https://www.lecobel-vaneau.be/fr/biens-a-vendre",
        "commune": "Ixelles"
    },
    {
        "name": "ERA Châtelain (AI)",
        "base_url": "https://www.era.be",
        "listing_url": "https://www.era.be/fr/era-chatelain/a-vendre",
        "commune": "Ixelles"
    },
]


def create_ai_scrapers() -> list[UniversalAIScraper]:
    """Create AI scraper instances from config."""
    return [
        UniversalAIScraper(**config)
        for config in AI_SCRAPER_CONFIGS
    ]


def scrape_with_ai() -> list[dict]:
    """Run all AI scrapers and return combined listings."""
    api_key = os.environ.get('DEEPSEEK_API_KEY')
    if not api_key:
        logger.info("DEEPSEEK_API_KEY not set, skipping AI scrapers")
        return []

    all_listings = []
    scrapers = create_ai_scrapers()

    for scraper in scrapers:
        try:
            logger.info(f"[AI] Scraping {scraper.name}...")
            listings = scraper.run()
            all_listings.extend(listings)
            logger.info(f"[AI] Found {len(listings)} listings from {scraper.name}")
        except Exception as e:
            logger.error(f"[AI] Failed to scrape {scraper.name}: {e}")

    return all_listings
