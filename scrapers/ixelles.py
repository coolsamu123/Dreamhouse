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
        import re

        # Try multiple selectors for Tribel Immo's structure
        cards = soup.select('.property-item, .bien-item, .listing-item, .properties-list-item, tr[class*="property"], div[class*="property"], article')

        if not cards:
            # Fallback: find all links to property details
            cards = soup.select('a[href*="view=detail"], a[href*="id="]')
            if cards:
                # Wrap links in their parent containers
                cards = [link.parent for link in cards if link.parent]

        for card in cards:
            try:
                listing = {}

                # URL - look for detail links
                link = card.select_one('a[href*="view=detail"], a[href*="id="], a[href]')
                if link:
                    href = link.get('href', '')
                    if href and 'id=' in href:
                        listing['url'] = href if href.startswith('http') else f"{self.base_url}{href}"

                # Title
                title_elem = card.select_one('h2, h3, h4, .title, .property-title, strong, b')
                if title_elem:
                    listing['title'] = title_elem.get_text(strip=True)

                # Price - look for € symbol in text
                text = card.get_text()
                price_match = re.search(r'(\d[\d\s.,]*)\s*€', text)
                if price_match:
                    price_str = price_match.group(1).replace(' ', '').replace('.', '').replace(',', '.')
                    try:
                        listing['price'] = float(price_str)
                    except:
                        pass

                # Also try specific price elements
                if not listing.get('price'):
                    price_elem = card.select_one('.price, .prix, [class*="price"], [class*="prix"], span.amount')
                    if price_elem:
                        listing['price'] = self._extract_price(price_elem.get_text())

                # Surface and bedrooms
                listing['surface'] = self._extract_surface(text)
                listing['bedrooms'] = self._extract_bedrooms(text)

                # Image
                img = card.select_one('img[src]:not([src*="pix.gif"]):not([src*="blank"])')
                if img:
                    src = img.get('src') or img.get('data-src', '')
                    if src and not src.endswith('pix.gif'):
                        listing['images'] = [src if src.startswith('http') else f"{self.base_url}/{src.lstrip('/')}"]

                if listing.get('url'):
                    listings.append(listing)

            except Exception as e:
                logger.warning(f"Failed to parse Tribel card: {e}")

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
