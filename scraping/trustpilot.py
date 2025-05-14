import json
import os
import smtplib
import time
from email.mime.text import MIMEText

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from scraping.driver import get_stealth_driver


def scrape_trustpilot(url: str, max_pages: int = 10) -> list[dict]:
    driver = get_stealth_driver(headless=False)
    avis_list = []
    current_page = 1

    try:
        driver.get(url)
        time.sleep(5)

        while current_page <= max_pages:
            print(f"[TRUSTPILOT] Scraping page {current_page}")

            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "article[data-service-review-card-paper='true']")
                )
            )

            review_elements = driver.find_elements(
                By.CSS_SELECTOR,
                "section.styles_reviewListContainer__2bg_p article[data-service-review-card-paper='true']",
            )

            for el in review_elements:
                try:
                    auteur = el.find_element(
                        By.CSS_SELECTOR, '[data-consumer-name-typography="true"]'
                    ).text.strip()
                    date = (
                        el.find_element(By.TAG_NAME, "time")
                        .get_attribute("datetime")
                        .split("T")[0]
                    )

                    try:
                        note_img = el.find_element(
                            By.CSS_SELECTOR, "[data-service-review-rating] img"
                        )
                        note = note_img.get_attribute("alt").split()[1]
                    except Exception:
                        note = "N/A"

                    try:
                        titre = el.find_element(
                            By.CSS_SELECTOR,
                            '[data-service-review-title-typography="true"]',
                        ).text.strip()
                    except Exception:
                        titre = ""

                    try:
                        contenu = el.find_element(
                            By.CSS_SELECTOR,
                            '[data-service-review-text-typography="true"]',
                        ).text.strip()
                    except Exception:
                        contenu = ""

                    avis_list.append(
                        {
                            "auteur": auteur,
                            "note": note,
                            "date": date,
                            "titre": titre,
                            "contenu": contenu,
                        }
                    )

                except Exception as e:
                    print(f"[TRUSTPILOT] Erreur dans un avis : {e}")

            # Pagination
            try:
                next_btn = driver.find_element(
                    By.CSS_SELECTOR, 'a[data-pagination-button-next-link="true"]'
                )
                next_url = next_btn.get_attribute("href")

                if next_url:
                    driver.get(next_url)
                    current_page += 1
                    time.sleep(3)
                else:
                    break
            except Exception:
                print("[TRUSTPILOT] Fin de la pagination ou bouton introuvable.")
                break

    finally:
        driver.quit()

    return avis_list


def scrape_all_trustpilot_sites(mode: str = "check"):
    assert mode in ["init", "check"], "Mode invalide (init | check)"

    listing_path = "data/listing.json"
    count_path = "data/trustpilot_counts.json"
    output_path = "data/trustpilot_avis.json"

    if not os.path.exists(listing_path):
        print(f"[TRUSTPILOT] Fichier introuvable : {listing_path}")
        return

    with open(listing_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    sites = data.get("sites", [])

    if mode == "check" and os.path.exists(count_path):
        with open(count_path, "r", encoding="utf-8") as f:
            old_counts = json.load(f)
    else:
        old_counts = {}

    results = {}
    new_counts = {}
    nouveaux_sites = []

    for site in sites:
        domain = site.replace("www.", "").strip()
        url = f"https://fr.trustpilot.com/review/{domain}"
        print(f"[TRUSTPILOT] Scraping pour {site} → {url}")

        try:
            avis = scrape_trustpilot(url)
            results[site] = avis
            new_counts[site] = len(avis)
            print(f"[TRUSTPILOT] ✅ {len(avis)} avis récupérés pour {site}\n")

            if mode == "check" and old_counts.get(site, 0) < len(avis):
                nouveaux_sites.append(site)

        except Exception as e:
            print(f"[TRUSTPILOT] ❌ Erreur pour {site} : {e}")
            results[site] = []
            new_counts[site] = old_counts.get(site, 0)

    # Enregistre les avis et les nouveaux comptes
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    with open(count_path, "w", encoding="utf-8") as f:
        json.dump(new_counts, f, indent=2, ensure_ascii=False)

    print(f"[TRUSTPILOT] Données enregistrées dans {output_path} et {count_path}")

    # Envoie email uniquement en mode check
    if mode == "check":
        send_notification_email(nouveaux_sites)


def send_notification_email(nouveaux_sites: list[str]):
    if not nouveaux_sites:
        return

    sender = os.getenv("EMAIL_SENDER")  # depuis .env
    password = os.getenv("EMAIL_PASSWORD")
    recipient = os.getenv("EMAIL_RECIPIENT")

    subject = "🆕 Nouveaux avis détectés sur Trustpilot"
    body_lines = [
        "Bonjour,\n\nDes nouveaux avis ont été détectés sur les sites suivants :\n"
    ]

    for site in nouveaux_sites:
        url = f"https://fr.trustpilot.com/review/{site.replace('www.', '')}"
        body_lines.append(f"- {site} → {url}")

    body_lines.append("\nCordialement,\nVotre robot de veille Trustpilot")
    body = "\n".join(body_lines)

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())
        print("📧 Email de notification envoyé.")
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi de l'email : {e}")