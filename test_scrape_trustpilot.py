import os
import sys

from scraping.trustpilot import scrape_all_trustpilot_sites

sys.path.append(os.path.abspath("."))

if __name__ == "__main__":
    scrape_all_trustpilot_sites()
