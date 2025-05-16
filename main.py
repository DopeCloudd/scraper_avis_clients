import sys

from core.logger import log
from core.mailer import send_global_report
from scraping.scamdoc import scrape_scamdoc
from scraping.scamtel import scrape_scamtel
from scraping.trustpilot import scrape_trustpilot


def main():
    if len(sys.argv) < 2:
        print("Usage : python main.py [init|check]")
        return

    mode = sys.argv[1]
    assert mode in ["init", "check"]

    log(f"▶️ Mode sélectionné : {mode}")

    reports = []
    reports.append(scrape_trustpilot(mode))
    reports.append(scrape_scamdoc(mode))
    reports.append(scrape_scamtel(mode))

    if mode == "check":
        send_global_report(reports)


if __name__ == "__main__":
    main()
