"""
Scrapers for major real estate portals in Belgium.
"""

import json
import logging
import re
from typing import Optional

from bs4 import BeautifulSoup

from .base_scraper import BaseScraper

logger = logging.getLogger('dreamhouse.portals')


class ImmowebScraper(BaseScraper):
    """
    Scraper for Immoweb - https://www.immoweb.be
    The largest real estate portal in Belgium.
    """

    name = "Immoweb"
    base_url = "https://www.immoweb.be"
    commune = "Bruxelles"

    def get_listings_url(self) -> str:
        # Search for apartments for sale in target communes
        params = [
            "countries=BE",
            "maxPrice=500000",
            "minSurface=80",
            "propertyTypes=APARTMENT",
            "provinces=BRUSSELS",
            "postalCodes=BE-1050,BE-1060,BE-1190",  # Ixelles, Saint-Gilles, Forest
            "orderBy=newest",
        ]
        return f"{self.base_url}/fr/recherche/appartement/a-vendre?{'&'.join(params)}"

    def parse_listing_cards(self, soup: BeautifulSoup) -> list[dict]:
        listings = []

        # Immoweb uses iw-search cards
        cards = soup.select('article.card, article[class*="card"], .search-results__item, .result-item')

        if not cards:
            # Try to find script tag with JSON data
            script_tags = soup.find_all('script', type='application/json')
            for script in script_tags:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and 'results' in data:
                        return self._parse_json_results(data['results'])
                except:
                    pass

            # Alternative selectors
            cards = soup.select('[class*="search-result"], [class*="property-card"], .card--result')

        for card in cards:
            try:
                listing = self._parse_card(card)
                if listing.get('url'):
                    listings.append(listing)
            except Exception as e:
                logger.warning(f"Failed to parse Immoweb card: {e}")

        return listings

    def _parse_card(self, card) -> dict:
        """Parse a single Immoweb card."""
        listing = {}

        # URL
        link = card.select_one('a[href*="/annonce/"], a[href*="/classified/"], a.card__title-link')
        if link:
            href = link.get('href', '')
            listing['url'] = href if href.startswith('http') else f"{self.base_url}{href}"

        # Title
        title_elem = card.select_one('.card__title, .card-title, h2, h3')
        if title_elem:
            listing['title'] = title_elem.get_text(strip=True)

        # Price
        price_elem = card.select_one('.card__price, .card-price, [class*="price"], .sr-price')
        if price_elem:
            listing['price'] = self._extract_price(price_elem.get_text())

        # Location/Address
        location_elem = card.select_one('.card__information--locality, .card-locality, [class*="locality"], .card__information--property')
        if location_elem:
            location_text = location_elem.get_text(strip=True)
            listing['address'] = location_text

            # Extract commune from location
            location_lower = location_text.lower()
            if 'saint-gilles' in location_lower or '1060' in location_text:
                listing['commune'] = 'Saint-Gilles'
            elif 'forest' in location_lower or '1190' in location_text:
                listing['commune'] = 'Forest'
            elif 'ixelles' in location_lower or '1050' in location_text:
                listing['commune'] = 'Ixelles'

        # Surface and bedrooms from details
        details = card.select('.card__information, [class*="detail"], [class*="info"]')
        for detail in details:
            text = detail.get_text()
            if not listing.get('surface'):
                listing['surface'] = self._extract_surface(text)
            if not listing.get('bedrooms'):
                listing['bedrooms'] = self._extract_bedrooms(text)

        # Also check full card text
        card_text = card.get_text()
        if not listing.get('surface'):
            listing['surface'] = self._extract_surface(card_text)
        if not listing.get('bedrooms'):
            listing['bedrooms'] = self._extract_bedrooms(card_text)

        # Image
        img = card.select_one('img[src], img[data-src], img[data-lazy-src]')
        if img:
            img_url = img.get('src') or img.get('data-src') or img.get('data-lazy-src', '')
            if img_url and not img_url.startswith('data:'):
                listing['images'] = [img_url]

        return listing

    def _parse_json_results(self, results: list) -> list[dict]:
        """Parse results from Immoweb JSON data."""
        listings = []
        for item in results:
            try:
                listing = {
                    'url': f"{self.base_url}/fr/annonce/{item.get('id', '')}",
                    'title': item.get('title', ''),
                    'price': item.get('price', {}).get('mainValue') if isinstance(item.get('price'), dict) else item.get('price'),
                    'surface': item.get('surface', {}).get('liveable') if isinstance(item.get('surface'), dict) else item.get('surface'),
                    'bedrooms': item.get('bedroomCount'),
                    'address': f"{item.get('property', {}).get('location', {}).get('street', '')} {item.get('property', {}).get('location', {}).get('locality', '')}".strip(),
                }

                # Determine commune
                locality = str(item.get('property', {}).get('location', {}).get('locality', '')).lower()
                postal = str(item.get('property', {}).get('location', {}).get('postalCode', ''))
                if 'saint-gilles' in locality or postal == '1060':
                    listing['commune'] = 'Saint-Gilles'
                elif 'forest' in locality or postal == '1190':
                    listing['commune'] = 'Forest'
                elif 'ixelles' in locality or postal == '1050':
                    listing['commune'] = 'Ixelles'

                # Images
                media = item.get('media', {}).get('pictures', [])
                if media:
                    listing['images'] = [p.get('smallUrl') or p.get('mediumUrl') for p in media[:3] if p.get('smallUrl') or p.get('mediumUrl')]

                if listing['url']:
                    listings.append(listing)
            except Exception as e:
                logger.warning(f"Failed to parse Immoweb JSON item: {e}")

        return listings


class ZimmoScraper(BaseScraper):
    """Scraper for Zimmo - https://www.zimmo.be"""

    name = "Zimmo"
    base_url = "https://www.zimmo.be"
    commune = "Bruxelles"

    def get_listings_url(self) -> str:
        return f"{self.base_url}/fr/chercher/?search=eyJmaWx0ZXIiOnsic3RhdHVzIjp7ImluIjpbIkZPUl9TQUxFIl19fX0&ptype=app&price=0-500000&sort=date_desc"

    def parse_listing_cards(self, soup: BeautifulSoup) -> list[dict]:
        listings = []
        cards = soup.select('.property-item, .search-result-item, article.property, .result-card')

        for card in cards:
            try:
                listing = {}

                link = card.select_one('a[href*="/fr/"], a[href*="annonce"], a.property-link')
                if link:
                    listing['url'] = link.get('href', '')

                title_elem = card.select_one('.property-title, h2, h3, .title')
                if title_elem:
                    listing['title'] = title_elem.get_text(strip=True)

                price_elem = card.select_one('.property-price, .price, [class*="price"]')
                if price_elem:
                    listing['price'] = self._extract_price(price_elem.get_text())

                text = card.get_text()
                listing['surface'] = self._extract_surface(text)
                listing['bedrooms'] = self._extract_bedrooms(text)

                location_elem = card.select_one('.property-location, .location, [class*="location"]')
                if location_elem:
                    listing['address'] = location_elem.get_text(strip=True)

                img = card.select_one('img')
                if img:
                    listing['images'] = [img.get('src') or img.get('data-src', '')]

                if listing.get('url'):
                    listings.append(listing)

            except Exception as e:
                logger.warning(f"Failed to parse Zimmo card: {e}")

        return listings


# List of all portal scrapers
PORTAL_SCRAPERS = [
    ImmowebScraper,
    ZimmoScraper,
]


def scrape_all_portals() -> list[dict]:
    """Run all portal scrapers and return combined listings."""
    all_listings = []

    for scraper_class in PORTAL_SCRAPERS:
        try:
            scraper = scraper_class()
            listings = scraper.run()
            all_listings.extend(listings)
        except Exception as e:
            logger.error(f"Failed to run {scraper_class.name}: {e}")

    return all_listings
