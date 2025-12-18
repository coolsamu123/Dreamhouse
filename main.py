#!/usr/bin/env python3
"""
Dreamhouse - Real Estate Scraping System for Brussels

Main entry point for running all scrapers and processing listings.
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

from scrapers.saint_gilles import scrape_all_saint_gilles, SAINT_GILLES_SCRAPERS
from scrapers.forest import scrape_all_forest, FOREST_SCRAPERS
from scrapers.ixelles import scrape_all_ixelles, IXELLES_SCRAPERS
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
    """Run all scrapers and return combined listings."""
    all_listings = []

    logger.info("=" * 60)
    logger.info("Starting Dreamhouse scraping run")
    logger.info(f"Time: {datetime.utcnow().isoformat()}Z")
    logger.info("=" * 60)

    # Saint-Gilles
    logger.info("\n📍 Scraping Saint-Gilles (1060)...")
    saint_gilles_listings = scrape_all_saint_gilles()
    all_listings.extend(saint_gilles_listings)
    logger.info(f"Found {len(saint_gilles_listings)} listings in Saint-Gilles")

    # Forest
    logger.info("\n📍 Scraping Forest (1190)...")
    forest_listings = scrape_all_forest()
    all_listings.extend(forest_listings)
    logger.info(f"Found {len(forest_listings)} listings in Forest")

    # Ixelles
    logger.info("\n📍 Scraping Ixelles (1050)...")
    ixelles_listings = scrape_all_ixelles()
    all_listings.extend(ixelles_listings)
    logger.info(f"Found {len(ixelles_listings)} listings in Ixelles")

    logger.info("\n" + "=" * 60)
    logger.info(f"Total listings found: {len(all_listings)}")
    logger.info("=" * 60)

    return all_listings


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


def run_single_scraper(scraper_name: str) -> list[dict]:
    """Run a single scraper by name."""
    all_scrapers = {
        **{s.name: s for s in SAINT_GILLES_SCRAPERS},
        **{s.name: s for s in FOREST_SCRAPERS},
        **{s.name: s for s in IXELLES_SCRAPERS},
    }

    if scraper_name not in all_scrapers:
        logger.error(f"Unknown scraper: {scraper_name}")
        logger.info(f"Available scrapers: {', '.join(all_scrapers.keys())}")
        return []

    scraper_class = all_scrapers[scraper_name]
    scraper = scraper_class()
    return scraper.run()


def list_scrapers():
    """List all available scrapers."""
    print("\n🏠 Dreamhouse - Available Scrapers\n")

    print("📍 Saint-Gilles (1060):")
    for s in SAINT_GILLES_SCRAPERS:
        print(f"   - {s.name}")

    print("\n📍 Forest (1190):")
    for s in FOREST_SCRAPERS:
        print(f"   - {s.name}")

    print("\n📍 Ixelles (1050):")
    for s in IXELLES_SCRAPERS:
        print(f"   - {s.name}")

    total = len(SAINT_GILLES_SCRAPERS) + len(FOREST_SCRAPERS) + len(IXELLES_SCRAPERS)
    print(f"\nTotal: {total} scrapers")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Dreamhouse - Real Estate Scraping System for Brussels'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all available scrapers'
    )
    parser.add_argument(
        '--scraper',
        type=str,
        help='Run a specific scraper by name'
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

    # Run scrapers
    if args.scraper:
        logger.info(f"Running single scraper: {args.scraper}")
        listings = run_single_scraper(args.scraper)
    else:
        listings = run_all_scrapers()

    if args.dry_run:
        logger.info("\n[DRY RUN] Would have processed the following listings:")
        for listing in listings[:5]:
            logger.info(f"  - {listing.get('title', 'No title')} ({listing.get('source')})")
        if len(listings) > 5:
            logger.info(f"  ... and {len(listings) - 5} more")
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
