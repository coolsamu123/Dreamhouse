#!/usr/bin/env python3
"""
Dreamhouse - Real Estate Scraping System for Brussels

Main entry point - AI-powered scraping only.
"""

import argparse
import logging
import sys
from datetime import datetime

from scrapers.ai_scraper import scrape_with_ai, AI_SCRAPER_CONFIGS
from scrapers.utils import (
    load_listings,
    save_listings,
    load_history,
    save_history,
    merge_listings,
    notify_new_listings,
    save_json,
    DATA_DIR,
    DOCS_DIR,
    logger,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)


def run_all_scrapers() -> list[dict]:
    """Run AI scrapers for all sites."""
    logger.info("=" * 60)
    logger.info("🏠 Dreamhouse - AI Scraping")
    logger.info(f"Time: {datetime.utcnow().isoformat()}Z")
    logger.info(f"Sites to scrape: {len(AI_SCRAPER_CONFIGS)}")
    logger.info("=" * 60)

    # AI-powered scrapers (DeepSeek)
    listings = scrape_with_ai()

    logger.info("\n" + "=" * 60)
    logger.info(f"Total listings found: {len(listings)}")
    logger.info("=" * 60)

    return listings


def process_listings(new_scraped: list[dict]) -> list[dict]:
    """
    Process newly scraped listings:
    - Merge with existing listings
    - Identify truly new listings
    - Update history
    - Save all data

    Returns list of truly new listings (for notifications).
    """
    # Load existing data
    existing_listings = load_listings()
    if not isinstance(existing_listings, dict):
        existing_listings = {}

    history = load_history()
    if not isinstance(history, dict):
        history = {'seen_ids': []}

    # Merge listings
    updated_listings, truly_new = merge_listings(existing_listings, new_scraped)

    # Update history
    for listing in truly_new:
        if listing['id'] not in history.get('seen_ids', []):
            history.setdefault('seen_ids', []).append(listing['id'])

    history['last_updated'] = datetime.utcnow().isoformat() + 'Z'

    # Save data
    save_listings(updated_listings)
    save_history(history)

    # Save new listings separately
    save_json(DATA_DIR / 'new_listings.json', truly_new)

    # Prepare listings for frontend (as list, sorted by first_seen)
    listings_list = list(updated_listings.values())
    listings_list.sort(key=lambda x: x.get('first_seen', ''), reverse=True)

    # Save for frontend
    frontend_data = {
        'listings': listings_list,
        'last_updated': datetime.utcnow().isoformat() + 'Z',
        'total_count': len(listings_list),
        'new_count': len(truly_new),
    }
    save_json(DOCS_DIR / 'listings.json', frontend_data)

    logger.info(f"\n🆕 Truly new listings: {len(truly_new)}")

    return truly_new


def list_scrapers():
    """List all AI scrapers."""
    print("\n🏠 Dreamhouse - AI Scrapers\n")

    print("📍 Saint-Gilles (1060):")
    for c in AI_SCRAPER_CONFIGS:
        if c['commune'] == 'Saint-Gilles':
            print(f"   - {c['name']}")

    print("\n📍 Forest (1190):")
    for c in AI_SCRAPER_CONFIGS:
        if c['commune'] == 'Forest':
            print(f"   - {c['name']}")

    print("\n📍 Ixelles (1050):")
    for c in AI_SCRAPER_CONFIGS:
        if c['commune'] == 'Ixelles':
            print(f"   - {c['name']}")

    print(f"\nTotal: {len(AI_SCRAPER_CONFIGS)} sites")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Dreamhouse - AI-powered Real Estate Scraping for Brussels'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all AI scrapers'
    )
    parser.add_argument(
        '--no-notify',
        action='store_true',
        help='Disable Telegram notifications'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run scrapers but do not save or notify'
    )

    args = parser.parse_args()

    if args.list:
        list_scrapers()
        return

    # Run AI scrapers
    listings = run_all_scrapers()

    if args.dry_run:
        logger.info("\n[DRY RUN] Would have processed the following listings:")
        for listing in listings[:10]:
            logger.info(f"  - {listing.get('title', 'No title')} | {listing.get('price')}€ | {listing.get('source')}")
        if len(listings) > 10:
            logger.info(f"  ... and {len(listings) - 10} more")
        return

    # Process and save listings
    truly_new = process_listings(listings)

    # Send notifications for new listings
    if truly_new and not args.no_notify:
        logger.info("\n📱 Sending Telegram notifications...")
        notify_new_listings(truly_new)
    elif not truly_new:
        logger.info("\nNo new listings to notify about.")

    logger.info("\n✅ Scraping run complete!")


if __name__ == '__main__':
    main()
