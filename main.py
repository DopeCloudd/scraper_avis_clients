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

    # Trustpilot
    try:
        reports.append(scrape_trustpilot(mode))
    except Exception as e:
        log(f"[TRUSTPILOT] ❌ Erreur critique : {e}")
        reports.append({"scraper": "trustpilot", "new": False, "count": 0, "targets": [], "error": True})

    # Scamdoc
    try:
        reports.append(scrape_scamdoc(mode))
    except Exception as e:
        log(f"[SCAMDOC] ❌ Erreur critique : {e}")
        reports.append({"scraper": "scamdoc", "new": False, "count": 0, "targets": [], "error": True})

    # Scamtel
    try:
        reports.append(scrape_scamtel(mode))
    except Exception as e:
        log(f"[SCAMTEL] ❌ Erreur critique : {e}")
        reports.append({"scraper": "scamtel", "new": False, "count": 0, "targets": [], "error": True})

    # Envoi du rapport si mode = check
    if mode == "check":
        send_global_report(reports)


if __name__ == "__main__":
    main()
