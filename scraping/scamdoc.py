import json
import os
import smtplib
import time
from email.mime.text import MIMEText
from typing import List

from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from scraping.driver import get_stealth_driver

load_dotenv()


def load_targets(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("emails", []) + data.get("sites", [])


def accept_cookies_if_present(driver):
    try:
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button//span[text()=\"J'ACCEPTE\"]")
            )
        ).click()
        print("[SCAMDOC] ✅ Consentement cookies accepté.")
        time.sleep(1)
    except Exception:
        print("[SCAMDOC] Aucun popup de cookie détecté.")


def search_scandoc(driver, query: str):
    driver.get("https://fr.scamdoc.com/")
    time.sleep(5)  # Cloudflare protection
    accept_cookies_if_present(driver)

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "search_input")))
    input_field = driver.find_element(By.ID, "search_input")
    input_field.clear()
    input_field.send_keys(query)

    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "search-load")))
    search_button = driver.find_element(By.ID, "search-load")
    search_button.click()

    # Attendre que le formulaire d’avis soit visible (présent même sans avis)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "comment-add-form"))
    )
    time.sleep(1)


def extract_reviews(driver) -> List[str]:
    reviews = []

    avis_elements = driver.find_elements(By.CSS_SELECTOR, ".comment-list-item")
    if not avis_elements:
        print("[SCAMDOC] Aucun avis pour ce résultat.")
        return reviews

    while True:
        avis_elements = driver.find_elements(By.CSS_SELECTOR, ".comment-list-item")
        for el in avis_elements:
            try:
                texte = el.find_element(By.CSS_SELECTOR, ".comment-text").text.strip()
                info = el.find_element(By.CSS_SELECTOR, ".comment-info").text.strip()
                reviews.append(f"{info} | {texte}")
            except Exception as e:
                print(f"[SCAMDOC] Erreur extraction avis : {e}")

        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "a.page-link[rel='next']")
            next_url = next_button.get_attribute("href")
            if not next_url:
                break
            driver.get(next_url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "comment-add-form"))
            )
            time.sleep(2)
        except Exception:
            break

    return reviews


def send_scamdoc_email(new_items: list[str]):
    if not new_items:
        return

    sender = os.getenv("EMAIL_SENDER")
    password = os.getenv("EMAIL_PASSWORD")
    recipient = os.getenv("EMAIL_RECIPIENT")

    subject = "🆕 Nouveaux avis détectés sur Scamdoc"
    body_lines = [
        "Bonjour,\n\nDes nouveaux avis ont été détectés sur Scamdoc pour les éléments suivants :\n"
    ]

    for item in new_items:
        link = f"https://fr.scamdoc.com/search?search={item}"
        body_lines.append(f"- {item} → {link}")

    body_lines.append("\nCordialement,\nVotre robot de veille Scamdoc")
    body = "\n".join(body_lines)

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())
        print("📧 Email Scamdoc envoyé.")
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi de l'email Scamdoc : {e}")


def scrape_scandoc_all(mode: str = "check"):
    assert mode in ["init", "check"], "Mode invalide (init | check)"

    targets = load_targets("data/listing.json")
    output_path = "data/scamdoc_avis.json"
    count_path = "data/scamdoc_counts.json"

    if os.path.exists(count_path):
        with open(count_path, "r", encoding="utf-8") as f:
            old_counts = json.load(f)
    else:
        old_counts = {}

    results = {}
    new_counts = {}
    nouveaux = []

    driver = get_stealth_driver(headless=False)

    try:
        for target in targets:
            print(f"[SCAMDOC] Recherche de : {target}")
            try:
                search_scandoc(driver, target)
                avis = extract_reviews(driver)
                results[target] = avis
                new_counts[target] = len(avis)
                print(f"[SCAMDOC] ✅ {len(avis)} avis trouvés pour {target}")

                if mode == "check" and len(avis) > old_counts.get(target, 0):
                    nouveaux.append(target)

            except Exception as e:
                print(f"[SCAMDOC] ❌ Erreur pour {target} : {e}")
                results[target] = []
                new_counts[target] = old_counts.get(target, 0)

    finally:
        driver.quit()

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    with open(count_path, "w", encoding="utf-8") as f:
        json.dump(new_counts, f, indent=2, ensure_ascii=False)

    print("[SCAMDOC] Données sauvegardées.")

    if mode == "check":
        if nouveaux:
            print("\n🆕 Nouveaux avis détectés pour :")
            for n in nouveaux:
                print(f" - {n} → https://fr.scamdoc.com/search?search={n}")
            send_scamdoc_email(nouveaux)
        else:
            print("\n✅ Aucun nouvel avis détecté.")
