from django.test import TestCase
from .scraper import scrape_amazon

class ScraperTests(TestCase):

    def test_scrape_amazon_single_page(self):
        # Test scraping a single page
        df = scrape_amazon('mens+red+hat', 1)
        assert len(df) > 0  # Check if we got some results
        assert 'Name' in df.columns  # Check if 'Name' column exists
        assert 'Price' in df.columns  # Check if 'Price' column exists

    def test_scrape_amazon_multiple_pages(self):
        # Test scraping multiple pages
        df = scrape_amazon('mens+red+hat', 3)
        assert len(df) > 0  # Check if we got some results
        assert 'Name' in df.columns  # Check if 'Name' column exists
        assert 'Price' in df.columns  # Check if 'Price' column exists