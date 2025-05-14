import os
import sys

from dotenv import load_dotenv

from scraping.scamdoc import scrape_scandoc_all
from scraping.scamtel import scrape_scamtel
from scraping.trustpilot import scrape_all_trustpilot_sites

sys.path.append(os.path.abspath("."))
load_dotenv()


def main():
    if len(sys.argv) < 2:
        print("Usage : python main.py [init|check]")
        return

    mode = sys.argv[1]
    assert mode in ["init", "check"], "Mode invalide : utilisez init ou check"

    print(f"▶️ Mode sélectionné : {mode}\n")

    # Lancer tous les scrapers
    scrape_all_trustpilot_sites(mode)
    scrape_scandoc_all(mode)
    scrape_scamtel(mode)


if __name__ == "__main__":
    main()
