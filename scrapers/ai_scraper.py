"""
AI-powered scraper using DeepSeek API.
Extracts listings from any real estate website using LLM.
"""

import json
import logging
import os
import re
import time
from typing import Optional

import requests
from bs4 import BeautifulSoup

from .base_scraper import BaseScraper
from .utils import generate_listing_id, SEARCH_CRITERIA

logger = logging.getLogger('dreamhouse.ai_scraper')

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

EXTRACTION_PROMPT = """Tu es un assistant qui extrait des annonces immobilières d'une page HTML.

CRITÈRES DE RECHERCHE:
- Type: Appartement à VENDRE (pas location)
- Communes: Saint-Gilles (1060), Forest (1190), Ixelles (1050) uniquement
- Prix maximum: 500.000 €
- Surface minimum: 80 m²

Extrais TOUTES les annonces qui correspondent à ces critères. Pour chaque annonce, retourne un objet JSON avec:
- url: lien vers l'annonce (relatif ou absolu) - OBLIGATOIRE
- title: titre de l'annonce
- price: prix en nombre entier (ex: 350000, pas "350.000 €")
- surface: surface en m² (nombre entier)
- bedrooms: nombre de chambres (nombre entier)
- address: adresse complète ou localisation

IMPORTANT:
- Retourne UNIQUEMENT un tableau JSON valide, sans texte avant ou après
- Si aucune annonce ne correspond, retourne []
- Ignore les annonces de location
- Ignore les annonces hors des communes ciblées
- Ignore les annonces > 500.000 € ou < 80 m²

Exemple de réponse valide:
[{"url": "/bien/123", "title": "Appartement 2ch Saint-Gilles", "price": 350000, "surface": 85, "bedrooms": 2, "address": "Rue de la Victoire 12, 1060 Saint-Gilles"}]

HTML de la page:
"""


def call_deepseek_api(prompt: str, api_key: str) -> Optional[str]:
    """Call DeepSeek API and return response content."""
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
                        "content": prompt
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 4000
            },
            timeout=90
        )
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        logger.error(f"DeepSeek API call failed: {e}")
        return None


def extract_with_ai(html: str, base_url: str, site_name: str = "") -> list[dict]:
    """Use DeepSeek to extract listings from HTML."""
    api_key = os.environ.get('DEEPSEEK_API_KEY')

    if not api_key:
        logger.warning("DEEPSEEK_API_KEY not configured")
        return []

    # Clean HTML - remove scripts, styles, keep only body
    soup = BeautifulSoup(html, 'lxml')

    # Remove unwanted elements
    for tag in soup.find_all(['script', 'style', 'nav', 'footer', 'header', 'noscript', 'svg', 'iframe']):
        tag.decompose()

    # Get text content with some structure
    body = soup.find('body')
    if body:
        clean_html = str(body)[:20000]  # Limit to ~20k chars
    else:
        clean_html = str(soup)[:20000]

    # Add site context to prompt
    full_prompt = EXTRACTION_PROMPT
    if site_name:
        full_prompt = f"Site: {site_name}\n\n" + full_prompt
    full_prompt += clean_html

    content = call_deepseek_api(full_prompt, api_key)
    if not content:
        return []

    try:
        # Parse JSON from response
        json_match = re.search(r'\[[\s\S]*\]', content)
        if json_match:
            listings = json.loads(json_match.group())

            valid_listings = []
            for listing in listings:
                url = listing.get('url', '')
                if not url:
                    continue

                # Normalize URL
                if not url.startswith('http'):
                    if url.startswith('/'):
                        listing['url'] = f"{base_url.rstrip('/')}{url}"
                    else:
                        listing['url'] = f"{base_url.rstrip('/')}/{url}"

                # Generate ID
                listing['id'] = generate_listing_id(listing['url'])

                # Validate criteria
                price = listing.get('price')
                surface = listing.get('surface')

                # Filter by criteria
                if price and price > SEARCH_CRITERIA['prix_max']:
                    continue
                if surface and surface < SEARCH_CRITERIA['surface_min']:
                    continue

                valid_listings.append(listing)

            return valid_listings

        return []

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse AI response as JSON: {e}")
        logger.debug(f"Response was: {content[:500]}")
        return []
    except Exception as e:
        logger.error(f"AI extraction failed: {e}")
        return []


class UniversalAIScraper(BaseScraper):
    """
    Universal scraper that uses AI to extract listings from any website.
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
        listings = extract_with_ai(html, self.base_url, self.name)

        # Add source and commune to all listings
        for listing in listings:
            listing['source'] = self.name
            if not listing.get('commune'):
                listing['commune'] = self.commune

        return listings


# ============================================================
# COMPLETE LIST OF ALL AGENCIES TO SCRAPE WITH AI
# ============================================================

AI_SCRAPER_CONFIGS = [
    # -------------------- SAINT-GILLES (1060) --------------------
    {
        "name": "JAM Properties",
        "base_url": "https://www.jamproperties.be",
        "listing_url": "https://www.jamproperties.be/fr/a-vendre",
        "commune": "Saint-Gilles"
    },
    {
        "name": "Everest Properties",
        "base_url": "https://www.everestproperties.be",
        "listing_url": "https://www.everestproperties.be/fr/ventes",
        "commune": "Saint-Gilles"
    },
    {
        "name": "Viabilis",
        "base_url": "https://www.viabilis.be",
        "listing_url": "https://www.viabilis.be/fr/a-vendre",
        "commune": "Saint-Gilles"
    },
    {
        "name": "Nesting Realty",
        "base_url": "https://www.nesting-realty.be",
        "listing_url": "https://www.nesting-realty.be/fr/biens-a-vendre",
        "commune": "Saint-Gilles"
    },
    {
        "name": "Inside Properties",
        "base_url": "https://www.inside-properties.be",
        "listing_url": "https://www.inside-properties.be/fr/properties?transaction=sale",
        "commune": "Saint-Gilles"
    },
    {
        "name": "Fredimmo",
        "base_url": "https://www.fredimmo.be",
        "listing_url": "https://www.fredimmo.be/fr/a-vendre",
        "commune": "Saint-Gilles"
    },
    {
        "name": "Modifa",
        "base_url": "https://www.modifa.be",
        "listing_url": "https://www.modifa.be/biens?type=vente",
        "commune": "Saint-Gilles"
    },

    # -------------------- FOREST (1190) --------------------
    {
        "name": "MYIMMO Altitude",
        "base_url": "https://www.myimmo.be",
        "listing_url": "https://www.myimmo.be/fr/biens-a-vendre.php",
        "commune": "Forest"
    },
    {
        "name": "Immobilière Georges",
        "base_url": "https://www.immobilieregeorges.be",
        "listing_url": "https://www.immobilieregeorges.be/fr/ventes",
        "commune": "Forest"
    },
    {
        "name": "Abri-Europe",
        "base_url": "https://www.abrieurope.be",
        "listing_url": "https://www.abrieurope.be/fr/a-vendre",
        "commune": "Forest"
    },
    {
        "name": "Century 21 Forest",
        "base_url": "https://www.century21.be",
        "listing_url": "https://www.century21.be/fr/agence/century-21-a-a-z-immobilier/a-vendre",
        "commune": "Forest"
    },

    # -------------------- IXELLES (1050) --------------------
    {
        "name": "Lecobel Vaneau",
        "base_url": "https://www.lecobel-vaneau.be",
        "listing_url": "https://www.lecobel-vaneau.be/fr/biens-a-vendre",
        "commune": "Ixelles"
    },
    {
        "name": "Oralis Real Estate",
        "base_url": "https://www.oralis.be",
        "listing_url": "https://www.oralis.be/fr/a-vendre",
        "commune": "Ixelles"
    },
    {
        "name": "Tribel Immo",
        "base_url": "https://www.tribel-immo.be",
        "listing_url": "https://www.tribel-immo.be/fr/a-vendre",
        "commune": "Ixelles"
    },
    {
        "name": "ERA Châtelain",
        "base_url": "https://www.era.be",
        "listing_url": "https://www.era.be/fr/era-chatelain/a-vendre",
        "commune": "Ixelles"
    },
    {
        "name": "By the Way",
        "base_url": "https://www.bytheway.immo",
        "listing_url": "https://www.bytheway.immo/fr/ventes",
        "commune": "Ixelles"
    },
    {
        "name": "Fierce Immo",
        "base_url": "https://fierceimmo.com",
        "listing_url": "https://fierceimmo.com/fr/ventes",
        "commune": "Ixelles"
    },
    {
        "name": "Address Real Estate",
        "base_url": "https://www.address-re.be",
        "listing_url": "https://www.address-re.be/fr/a-vendre",
        "commune": "Ixelles"
    },
    {
        "name": "Immo Clairière",
        "base_url": "https://www.immoclairiere.be",
        "listing_url": "https://www.immoclairiere.be/fr/a-vendre",
        "commune": "Ixelles"
    },
    {
        "name": "De Maurissens",
        "base_url": "https://www.demaurissens.be",
        "listing_url": "https://www.demaurissens.be/fr/ventes",
        "commune": "Ixelles"
    },
    {
        "name": "Engel & Völkers",
        "base_url": "https://www.engelvoelkers.com",
        "listing_url": "https://www.engelvoelkers.com/fr-be/bruxelles/acheter-appartement",
        "commune": "Ixelles"
    },
    {
        "name": "Trevi Ixelles",
        "base_url": "https://www.trevi.be",
        "listing_url": "https://www.trevi.be/fr/trevi-brussels-ixelles/a-vendre",
        "commune": "Ixelles"
    },

    # -------------------- PORTAILS MAJEURS --------------------
    {
        "name": "Immoweb Saint-Gilles",
        "base_url": "https://www.immoweb.be",
        "listing_url": "https://www.immoweb.be/fr/recherche/appartement/a-vendre/saint-gilles/1060?maxPrice=500000&minSurface=80",
        "commune": "Saint-Gilles"
    },
    {
        "name": "Immoweb Forest",
        "base_url": "https://www.immoweb.be",
        "listing_url": "https://www.immoweb.be/fr/recherche/appartement/a-vendre/forest/1190?maxPrice=500000&minSurface=80",
        "commune": "Forest"
    },
    {
        "name": "Immoweb Ixelles",
        "base_url": "https://www.immoweb.be",
        "listing_url": "https://www.immoweb.be/fr/recherche/appartement/a-vendre/ixelles/1050?maxPrice=500000&minSurface=80",
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
    total = len(scrapers)

    logger.info(f"[AI] Starting AI scraping for {total} sites...")

    for i, scraper in enumerate(scrapers, 1):
        try:
            logger.info(f"[AI] ({i}/{total}) Scraping {scraper.name}...")
            listings = scraper.run()
            all_listings.extend(listings)
            logger.info(f"[AI] Found {len(listings)} listings from {scraper.name}")

            # Rate limiting - wait between requests
            if i < total:
                time.sleep(1)  # 1 second between API calls

        except Exception as e:
            logger.error(f"[AI] Failed to scrape {scraper.name}: {e}")

    logger.info(f"[AI] Total: {len(all_listings)} listings from AI scrapers")
    return all_listings
