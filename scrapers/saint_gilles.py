"""
Scrapers for real estate agencies in Saint-Gilles (1060).
"""

import logging
import re
from typing import Optional

from bs4 import BeautifulSoup

from .base_scraper import BaseScraper

logger = logging.getLogger('dreamhouse.saint_gilles')


class JamPropertiesScraper(BaseScraper):
    """Scraper for JAM Properties - https://www.jamproperties.be"""

    name = "JAM Properties"
    base_url = "https://www.jamproperties.be"
    commune = "Saint-Gilles"

    def get_listings_url(self) -> str:
        return f"{self.base_url}/fr/a-vendre"

    def parse_listing_cards(self, soup: BeautifulSoup) -> list[dict]:
        listings = []
        cards = soup.select('.property-card, .bien-item, article.property, .listing-item, [class*="property"]')

        if not cards:
            # Try alternative selectors
            cards = soup.select('.card, article, .item')

        for card in cards:
            try:
                listing = {}

                # URL
                link = card.select_one('a[href*="bien"], a[href*="property"], a[href]')
                if link:
                    listing['url'] = link.get('href', '')

                # Title
                title_elem = card.select_one('h2, h3, .title, .property-title, [class*="title"]')
                if title_elem:
                    listing['title'] = title_elem.get_text(strip=True)

                # Price
                price_elem = card.select_one('.price, .prix, [class*="price"], [class*="prix"]')
                if price_elem:
                    listing['price'] = self._extract_price(price_elem.get_text())

                # Surface
                surface_elem = card.select_one('[class*="surface"], [class*="area"], .m2')
                if surface_elem:
                    listing['surface'] = self._extract_surface(surface_elem.get_text())

                # Bedrooms
                rooms_elem = card.select_one('[class*="room"], [class*="chambre"], [class*="bedroom"]')
                if rooms_elem:
                    listing['bedrooms'] = self._extract_bedrooms(rooms_elem.get_text())

                # Address
                address_elem = card.select_one('.address, .adresse, [class*="location"], [class*="address"]')
                if address_elem:
                    listing['address'] = address_elem.get_text(strip=True)

                # Image
                img = card.select_one('img[src], img[data-src]')
                if img:
                    listing['images'] = [img.get('src') or img.get('data-src', '')]

                if listing.get('url'):
                    listings.append(listing)

            except Exception as e:
                logger.warning(f"Failed to parse card: {e}")

        return listings


class EverestPropertiesScraper(BaseScraper):
    """Scraper for Everest Properties - https://www.everestproperties.be"""

    name = "Everest Properties"
    base_url = "https://www.everestproperties.be"
    commune = "Saint-Gilles"

    def get_listings_url(self) -> str:
        return f"{self.base_url}/fr/ventes"

    def parse_listing_cards(self, soup: BeautifulSoup) -> list[dict]:
        listings = []
        cards = soup.select('.property-item, .listing-card, .bien, article, .property')

        for card in cards:
            try:
                listing = {}

                link = card.select_one('a[href]')
                if link:
                    listing['url'] = link.get('href', '')

                title_elem = card.select_one('h2, h3, .title, .property-title')
                if title_elem:
                    listing['title'] = title_elem.get_text(strip=True)

                price_elem = card.select_one('.price, .prix, [class*="price"]')
                if price_elem:
                    listing['price'] = self._extract_price(price_elem.get_text())

                # Look for details in text content
                text = card.get_text()
                if not listing.get('surface'):
                    listing['surface'] = self._extract_surface(text)
                if not listing.get('bedrooms'):
                    listing['bedrooms'] = self._extract_bedrooms(text)

                address_elem = card.select_one('.address, .location, [class*="address"]')
                if address_elem:
                    listing['address'] = address_elem.get_text(strip=True)

                img = card.select_one('img')
                if img:
                    listing['images'] = [img.get('src') or img.get('data-src', '')]

                if listing.get('url'):
                    listings.append(listing)

            except Exception as e:
                logger.warning(f"Failed to parse card: {e}")

        return listings


class ViabilisScraper(BaseScraper):
    """Scraper for Viabilis - https://www.viabilis.be"""

    name = "Viabilis"
    base_url = "https://www.viabilis.be"
    commune = "Saint-Gilles"

    def get_listings_url(self) -> str:
        return f"{self.base_url}/fr/a-vendre"

    def parse_listing_cards(self, soup: BeautifulSoup) -> list[dict]:
        listings = []
        cards = soup.select('.property, .bien, .listing, article')

        for card in cards:
            try:
                listing = {}

                link = card.select_one('a[href]')
                if link:
                    listing['url'] = link.get('href', '')

                title_elem = card.select_one('h2, h3, .title')
                if title_elem:
                    listing['title'] = title_elem.get_text(strip=True)

                price_elem = card.select_one('.price, .prix')
                if price_elem:
                    listing['price'] = self._extract_price(price_elem.get_text())

                text = card.get_text()
                listing['surface'] = self._extract_surface(text)
                listing['bedrooms'] = self._extract_bedrooms(text)

                img = card.select_one('img')
                if img:
                    listing['images'] = [img.get('src') or img.get('data-src', '')]

                if listing.get('url'):
                    listings.append(listing)

            except Exception as e:
                logger.warning(f"Failed to parse card: {e}")

        return listings


class NestingRealtyScraper(BaseScraper):
    """Scraper for Nesting Realty - https://www.nesting-realty.be"""

    name = "Nesting Realty"
    base_url = "https://www.nesting-realty.be"
    commune = "Saint-Gilles"

    def get_listings_url(self) -> str:
        return f"{self.base_url}/fr/biens-a-vendre"

    def parse_listing_cards(self, soup: BeautifulSoup) -> list[dict]:
        listings = []
        cards = soup.select('.property-card, .bien, .listing, article, .property-item')

        for card in cards:
            try:
                listing = {}

                link = card.select_one('a[href]')
                if link:
                    listing['url'] = link.get('href', '')

                title_elem = card.select_one('h2, h3, .title, .property-title')
                if title_elem:
                    listing['title'] = title_elem.get_text(strip=True)

                price_elem = card.select_one('.price, .prix')
                if price_elem:
                    listing['price'] = self._extract_price(price_elem.get_text())

                text = card.get_text()
                listing['surface'] = self._extract_surface(text)
                listing['bedrooms'] = self._extract_bedrooms(text)

                address_elem = card.select_one('.address, .location')
                if address_elem:
                    listing['address'] = address_elem.get_text(strip=True)

                img = card.select_one('img')
                if img:
                    listing['images'] = [img.get('src') or img.get('data-src', '')]

                if listing.get('url'):
                    listings.append(listing)

            except Exception as e:
                logger.warning(f"Failed to parse card: {e}")

        return listings


class InsidePropertiesScraper(BaseScraper):
    """Scraper for Inside Properties - https://www.inside-properties.be"""

    name = "Inside Properties"
    base_url = "https://www.inside-properties.be"
    commune = "Saint-Gilles"

    def get_listings_url(self) -> str:
        return f"{self.base_url}/fr/properties"

    def parse_listing_cards(self, soup: BeautifulSoup) -> list[dict]:
        listings = []
        cards = soup.select('.property, .bien, article, .listing-item')

        for card in cards:
            try:
                listing = {}

                link = card.select_one('a[href]')
                if link:
                    listing['url'] = link.get('href', '')

                title_elem = card.select_one('h2, h3, .title')
                if title_elem:
                    listing['title'] = title_elem.get_text(strip=True)

                price_elem = card.select_one('.price, .prix')
                if price_elem:
                    listing['price'] = self._extract_price(price_elem.get_text())

                text = card.get_text()
                listing['surface'] = self._extract_surface(text)
                listing['bedrooms'] = self._extract_bedrooms(text)

                img = card.select_one('img')
                if img:
                    listing['images'] = [img.get('src') or img.get('data-src', '')]

                if listing.get('url'):
                    listings.append(listing)

            except Exception as e:
                logger.warning(f"Failed to parse card: {e}")

        return listings


class FredimmoScraper(BaseScraper):
    """Scraper for Fredimmo - https://www.fredimmo.be"""

    name = "Fredimmo"
    base_url = "https://www.fredimmo.be"
    commune = "Saint-Gilles"

    def get_listings_url(self) -> str:
        return f"{self.base_url}/fr/a-vendre"

    def parse_listing_cards(self, soup: BeautifulSoup) -> list[dict]:
        listings = []
        cards = soup.select('.property, .bien, article, .listing')

        for card in cards:
            try:
                listing = {}

                link = card.select_one('a[href]')
                if link:
                    listing['url'] = link.get('href', '')

                title_elem = card.select_one('h2, h3, .title')
                if title_elem:
                    listing['title'] = title_elem.get_text(strip=True)

                price_elem = card.select_one('.price, .prix')
                if price_elem:
                    listing['price'] = self._extract_price(price_elem.get_text())

                text = card.get_text()
                listing['surface'] = self._extract_surface(text)
                listing['bedrooms'] = self._extract_bedrooms(text)

                img = card.select_one('img')
                if img:
                    listing['images'] = [img.get('src') or img.get('data-src', '')]

                if listing.get('url'):
                    listings.append(listing)

            except Exception as e:
                logger.warning(f"Failed to parse card: {e}")

        return listings


class ModifaScraper(BaseScraper):
    """Scraper for Modifa - https://www.modifa.be"""

    name = "Modifa"
    base_url = "https://www.modifa.be"
    commune = "Saint-Gilles"

    def get_listings_url(self) -> str:
        return f"{self.base_url}/biens?type=vente"

    def parse_listing_cards(self, soup: BeautifulSoup) -> list[dict]:
        listings = []
        cards = soup.select('.property, .bien, article, .listing, .card')

        for card in cards:
            try:
                listing = {}

                link = card.select_one('a[href]')
                if link:
                    listing['url'] = link.get('href', '')

                title_elem = card.select_one('h2, h3, .title')
                if title_elem:
                    listing['title'] = title_elem.get_text(strip=True)

                price_elem = card.select_one('.price, .prix')
                if price_elem:
                    listing['price'] = self._extract_price(price_elem.get_text())

                text = card.get_text()
                listing['surface'] = self._extract_surface(text)
                listing['bedrooms'] = self._extract_bedrooms(text)

                img = card.select_one('img')
                if img:
                    listing['images'] = [img.get('src') or img.get('data-src', '')]

                if listing.get('url'):
                    listings.append(listing)

            except Exception as e:
                logger.warning(f"Failed to parse card: {e}")

        return listings


# List of all Saint-Gilles scrapers
SAINT_GILLES_SCRAPERS = [
    JamPropertiesScraper,
    EverestPropertiesScraper,
    ViabilisScraper,
    NestingRealtyScraper,
    InsidePropertiesScraper,
    FredimmoScraper,
    ModifaScraper,
]


def scrape_all_saint_gilles() -> list[dict]:
    """Run all Saint-Gilles scrapers and return combined listings."""
    all_listings = []

    for scraper_class in SAINT_GILLES_SCRAPERS:
        try:
            scraper = scraper_class()
            listings = scraper.run()
            all_listings.extend(listings)
        except Exception as e:
            logger.error(f"Failed to run {scraper_class.name}: {e}")

    return all_listings
