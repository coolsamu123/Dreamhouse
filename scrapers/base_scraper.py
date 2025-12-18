"""
Base scraper class for real estate websites.
"""

import logging
import random
import time
from abc import ABC, abstractmethod
from typing import Optional

import requests
from bs4 import BeautifulSoup

from .utils import generate_listing_id, matches_criteria

logger = logging.getLogger('dreamhouse.scraper')

# Realistic user agents
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
]


class BaseScraper(ABC):
    """Base class for all real estate scrapers."""

    name: str = "Base Scraper"
    base_url: str = ""
    commune: str = ""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr-BE,fr;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        self.delay_min = 1.0
        self.delay_max = 2.5
        self.max_retries = 3

    def _delay(self) -> None:
        """Random delay between requests."""
        time.sleep(random.uniform(self.delay_min, self.delay_max))

    def _get(self, url: str, **kwargs) -> Optional[requests.Response]:
        """Make a GET request with retry logic."""
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, timeout=30, **kwargs)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                logger.warning(f"[{self.name}] Request failed (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"[{self.name}] All retries failed for {url}")
                    return None
        return None

    def _parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML content."""
        return BeautifulSoup(html, 'lxml')

    def _extract_price(self, text: str) -> Optional[float]:
        """Extract price from text."""
        if not text:
            return None
        import re
        # Remove common patterns and extract number
        text = text.replace('\xa0', ' ').replace(' ', '').replace('.', '')
        text = text.replace('€', '').replace('/mois', '').replace('/m', '')
        match = re.search(r'(\d+)', text)
        if match:
            return float(match.group(1))
        return None

    def _extract_surface(self, text: str) -> Optional[float]:
        """Extract surface area from text."""
        if not text:
            return None
        import re
        text = text.replace('\xa0', ' ').replace(',', '.')
        match = re.search(r'(\d+(?:\.\d+)?)\s*m[²2]?', text, re.IGNORECASE)
        if match:
            return float(match.group(1))
        return None

    def _extract_bedrooms(self, text: str) -> Optional[int]:
        """Extract number of bedrooms from text."""
        if not text:
            return None
        import re
        # Look for patterns like "2 ch", "2 chambres", "2 slaapkamers"
        match = re.search(r'(\d+)\s*(?:ch(?:ambre)?s?|slaapkamers?|bedroom?s?)', text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        # Just a number
        match = re.search(r'(\d+)', text)
        if match:
            return int(match.group(1))
        return None

    def _make_absolute_url(self, url: str) -> str:
        """Convert relative URL to absolute."""
        if not url:
            return ""
        if url.startswith('http'):
            return url
        if url.startswith('//'):
            return 'https:' + url
        if url.startswith('/'):
            from urllib.parse import urljoin
            return urljoin(self.base_url, url)
        return self.base_url.rstrip('/') + '/' + url

    @abstractmethod
    def get_listings_url(self) -> str:
        """Return the URL to scrape listings from."""
        pass

    @abstractmethod
    def parse_listing_cards(self, soup: BeautifulSoup) -> list[dict]:
        """Parse listing cards from the page and return list of raw listing data."""
        pass

    def scrape(self) -> list[dict]:
        """Main scraping method."""
        logger.info(f"[{self.name}] Starting scrape...")

        url = self.get_listings_url()
        response = self._get(url)

        if not response:
            logger.error(f"[{self.name}] Failed to fetch listings page")
            return []

        soup = self._parse_html(response.text)
        raw_listings = self.parse_listing_cards(soup)

        listings = []
        for raw in raw_listings:
            try:
                listing = self._normalize_listing(raw)
                if listing and matches_criteria(listing):
                    listings.append(listing)
            except Exception as e:
                logger.warning(f"[{self.name}] Failed to normalize listing: {e}")

        logger.info(f"[{self.name}] Found {len(listings)} matching listings")
        return listings

    def _normalize_listing(self, raw: dict) -> Optional[dict]:
        """Normalize a raw listing to standard format."""
        source_url = raw.get('url', '')
        if not source_url:
            return None

        listing = {
            'id': generate_listing_id(source_url),
            'source': self.name,
            'source_url': self._make_absolute_url(source_url),
            'title': raw.get('title', '').strip(),
            'price': raw.get('price'),
            'surface': raw.get('surface'),
            'bedrooms': raw.get('bedrooms'),
            'address': raw.get('address', '').strip(),
            'commune': raw.get('commune', self.commune),
            'description': raw.get('description', '').strip(),
            'images': raw.get('images', []),
        }

        # Clean up images
        listing['images'] = [self._make_absolute_url(img) for img in listing['images'] if img]

        return listing

    def run(self) -> list[dict]:
        """Run the scraper and return listings."""
        try:
            return self.scrape()
        except Exception as e:
            logger.error(f"[{self.name}] Scraper failed: {e}")
            return []
