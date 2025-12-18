"""
Scrapers for real estate agencies in Ixelles (1050).
"""

import logging

from bs4 import BeautifulSoup

from .base_scraper import BaseScraper

logger = logging.getLogger('dreamhouse.ixelles')


class LecobelVaneauScraper(BaseScraper):
    """Scraper for Lecobel Vaneau - https://www.lecobel-vaneau.be"""

    name = "Lecobel Vaneau"
    base_url = "https://www.lecobel-vaneau.be"
    commune = "Ixelles"

    def get_listings_url(self) -> str:
        return f"{self.base_url}/fr/biens-a-vendre"

    def parse_listing_cards(self, soup: BeautifulSoup) -> list[dict]:
        listings = []
        cards = soup.select('.property-card, .property, .bien, article, .listing-item')

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


class OralisScraper(BaseScraper):
    """Scraper for Oralis Real Estate - https://www.oralis.be"""

    name = "Oralis Real Estate"
    base_url = "https://www.oralis.be"
    commune = "Ixelles"

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


class TribelImmoScraper(BaseScraper):
    """Scraper for Tribel Immo - https://www.tribel-immo.be"""

    name = "Tribel Immo"
    base_url = "https://www.tribel-immo.be"
    commune = "Ixelles"

    def get_listings_url(self) -> str:
        return f"{self.base_url}/fr/a-vendre"

    def parse_listing_cards(self, soup: BeautifulSoup) -> list[dict]:
        listings = []
        cards = soup.select('.property, .bien, article, .listing, .property-card')

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


class EraChatelainScraper(BaseScraper):
    """Scraper for ERA Châtelain - https://www.era.be"""

    name = "ERA Châtelain"
    base_url = "https://www.era.be"
    commune = "Ixelles"

    def get_listings_url(self) -> str:
        return f"{self.base_url}/fr/era-chatelain/a-louer"

    def parse_listing_cards(self, soup: BeautifulSoup) -> list[dict]:
        listings = []
        cards = soup.select('.property-card, .property, .bien, article, .listing')

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


class ByTheWayScraper(BaseScraper):
    """Scraper for By the Way - https://www.bytheway.immo"""

    name = "By the Way"
    base_url = "https://www.bytheway.immo"
    commune = "Ixelles"

    def get_listings_url(self) -> str:
        return f"{self.base_url}/fr/ventes"

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


class FierceImmoScraper(BaseScraper):
    """Scraper for Fierce Immo - https://fierceimmo.com"""

    name = "Fierce Immo"
    base_url = "https://fierceimmo.com"
    commune = "Ixelles"

    def get_listings_url(self) -> str:
        return f"{self.base_url}/fr/ventes"

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


class MyImmoIxellesScraper(BaseScraper):
    """Scraper for MyImmo Ixelles - https://www.myimmo.be"""

    name = "MyImmo Ixelles"
    base_url = "https://www.myimmo.be"
    commune = "Ixelles"

    def get_listings_url(self) -> str:
        return f"{self.base_url}/fr/biens-a-vendre.php"

    def parse_listing_cards(self, soup: BeautifulSoup) -> list[dict]:
        listings = []
        cards = soup.select('.property, .bien, article, .listing, .item')

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


class AddressRealEstateScraper(BaseScraper):
    """Scraper for Address Real Estate - https://www.address-re.be"""

    name = "Address Real Estate"
    base_url = "https://www.address-re.be"
    commune = "Ixelles"

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


class ImmoClairiereScraper(BaseScraper):
    """Scraper for Immo Clairière - https://www.immoclairiere.be"""

    name = "Immo Clairière"
    base_url = "https://www.immoclairiere.be"
    commune = "Ixelles"

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


class DeMaurissensScraper(BaseScraper):
    """Scraper for Immobilière de Maurissens - https://www.demaurissens.be"""

    name = "Immobilière de Maurissens"
    base_url = "https://www.demaurissens.be"
    commune = "Ixelles"

    def get_listings_url(self) -> str:
        return f"{self.base_url}/fr/ventes"

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


class EngelVolkersScraper(BaseScraper):
    """Scraper for Engel & Völkers - https://www.engelvoelkers.com"""

    name = "Engel & Völkers"
    base_url = "https://www.engelvoelkers.com"
    commune = "Ixelles"

    def get_listings_url(self) -> str:
        return f"{self.base_url}/fr-be/bruxelles/louer"

    def parse_listing_cards(self, soup: BeautifulSoup) -> list[dict]:
        listings = []
        cards = soup.select('.property-card, .property, .ev-property, article, .listing')

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


class TreviLouiseScraper(BaseScraper):
    """Scraper for Trevi Louise - https://www.trevi.be"""

    name = "Trevi Louise"
    base_url = "https://www.trevi.be"
    commune = "Ixelles"

    def get_listings_url(self) -> str:
        return f"{self.base_url}/fr/trevi-brussels-ixelles/a-louer"

    def parse_listing_cards(self, soup: BeautifulSoup) -> list[dict]:
        listings = []
        cards = soup.select('.property-card, .property, .bien, article, .listing')

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


# List of all Ixelles scrapers
IXELLES_SCRAPERS = [
    LecobelVaneauScraper,
    OralisScraper,
    TribelImmoScraper,
    EraChatelainScraper,
    ByTheWayScraper,
    FierceImmoScraper,
    MyImmoIxellesScraper,
    AddressRealEstateScraper,
    ImmoClairiereScraper,
    DeMaurissensScraper,
    EngelVolkersScraper,
    TreviLouiseScraper,
]


def scrape_all_ixelles() -> list[dict]:
    """Run all Ixelles scrapers and return combined listings."""
    all_listings = []

    for scraper_class in IXELLES_SCRAPERS:
        try:
            scraper = scraper_class()
            listings = scraper.run()
            all_listings.extend(listings)
        except Exception as e:
            logger.error(f"Failed to run {scraper_class.name}: {e}")

    return all_listings
