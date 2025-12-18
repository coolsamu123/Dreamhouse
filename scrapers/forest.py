"""
Scrapers for real estate agencies in Forest (1190).
"""

import logging

from bs4 import BeautifulSoup

from .base_scraper import BaseScraper

logger = logging.getLogger('dreamhouse.forest')


class MyImmoAltitudeScraper(BaseScraper):
    """Scraper for MYIMMO Altitude - https://www.myimmo.be"""

    name = "MYIMMO Altitude"
    base_url = "https://www.myimmo.be"
    commune = "Forest"

    def get_listings_url(self) -> str:
        return f"{self.base_url}/fr/biens-a-vendre.php"

    def parse_listing_cards(self, soup: BeautifulSoup) -> list[dict]:
        listings = []
        cards = soup.select('.property-card, .bien-item, .listing, article, .property, .item')

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

                text = card.get_text()
                listing['surface'] = self._extract_surface(text)
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


class ImmobiliereGeorgesScraper(BaseScraper):
    """Scraper for Immobilière Georges - https://www.immobilieregeorges.be"""

    name = "Immobilière Georges"
    base_url = "https://www.immobilieregeorges.be"
    commune = "Forest"

    def get_listings_url(self) -> str:
        return f"{self.base_url}/fr/ventes"

    def parse_listing_cards(self, soup: BeautifulSoup) -> list[dict]:
        listings = []
        cards = soup.select('.property, .bien, article, .listing-item, .property-card')

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


class AbriEuropeScraper(BaseScraper):
    """Scraper for Abri-Europe - https://www.abrieurope.be"""

    name = "Abri-Europe"
    base_url = "https://www.abrieurope.be"
    commune = "Forest"

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


class Century21AZScraper(BaseScraper):
    """Scraper for Century 21 A à Z - https://www.century21.be"""

    name = "Century 21 A à Z"
    base_url = "https://www.century21.be"
    commune = "Forest"

    def get_listings_url(self) -> str:
        return f"{self.base_url}/fr/agence/century-21-a-a-z-immobilier"

    def parse_listing_cards(self, soup: BeautifulSoup) -> list[dict]:
        listings = []
        cards = soup.select('.property-card, .property, .bien, article, .listing')

        for card in cards:
            try:
                listing = {}

                link = card.select_one('a[href*="bien"], a[href*="property"], a[href]')
                if link:
                    listing['url'] = link.get('href', '')

                title_elem = card.select_one('h2, h3, .title, .property-title')
                if title_elem:
                    listing['title'] = title_elem.get_text(strip=True)

                price_elem = card.select_one('.price, .prix, [class*="price"]')
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


# List of all Forest scrapers
FOREST_SCRAPERS = [
    MyImmoAltitudeScraper,
    ImmobiliereGeorgesScraper,
    AbriEuropeScraper,
    Century21AZScraper,
]


def scrape_all_forest() -> list[dict]:
    """Run all Forest scrapers and return combined listings."""
    all_listings = []

    for scraper_class in FOREST_SCRAPERS:
        try:
            scraper = scraper_class()
            listings = scraper.run()
            all_listings.extend(listings)
        except Exception as e:
            logger.error(f"Failed to run {scraper_class.name}: {e}")

    return all_listings
