import json
import os
import smtplib
import time
from email.mime.text import MIMEText
from typing import List

from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from scraping.driver import get_stealth_driver

load_dotenv()


def load_phones(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("phones", []) or data.get("telephones", [])


def search_scamtel(driver, phone: str):
    driver.get("https://fr.scamtel.com/")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "search")))

    input_field = driver.find_element(By.NAME, "search")
    input_field.clear()
    input_field.send_keys(phone)
    input_field.send_keys(Keys.RETURN)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".comment-list-item, .no-comments")
        )
    )
    time.sleep(2)


def extract_reviews(driver) -> List[str]:
    reviews = []
    while True:
        avis_elements = driver.find_elements(By.CSS_SELECTOR, ".comment-list-item")
        for el in avis_elements:
            try:
                texte = el.find_element(By.CSS_SELECTOR, ".comment-text").text.strip()
                info = el.find_element(By.CSS_SELECTOR, ".comment-info").text.strip()
                reviews.append(f"{info} | {texte}")
            except Exception as e:
                print(f"[SCAMTEL] Erreur extraction avis : {e}")

        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "a.page-link[rel='next']")
            next_url = next_button.get_attribute("href")
            if not next_url:
                break
            driver.get(next_url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".comment-list-item"))
            )
            time.sleep(2)
        except Exception:
            break

    return reviews


def send_scamtel_email(new_numbers: list[str]):
    if not new_numbers:
        return

    sender = os.getenv("EMAIL_SENDER")
    password = os.getenv("EMAIL_PASSWORD")
    recipient = os.getenv("EMAIL_RECIPIENT")

    subject = "🆕 Nouveaux avis détectés sur Scamtel"
    lines = ["Bonjour,\n\nDes nouveaux avis ont été publiés sur les numéros suivants :\n"]

    for number in new_numbers:
        lines.append(f"- {number} → https://fr.scamtel.com/search?search={number}")

    lines.append("\nCordialement,\nVotre robot de veille Scamtel")
    body = "\n".join(lines)

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())
        print("📧 Email Scamtel envoyé.")
    except Exception as e:
        print(f"❌ Erreur envoi email Scamtel : {e}")


def scrape_scamtel(mode: str = "check"):
    assert mode in ["init", "check"], "Mode invalide (init | check)"

    phones = load_phones("data/listing.json")
    count_path = "data/scamtel_counts.json"
    avis_path = "data/scamtel_avis.json"

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
        for phone in phones:
            print(f"[SCAMTEL] Recherche : {phone}")
            try:
                search_scamtel(driver, phone)
                avis = extract_reviews(driver)
                results[phone] = avis
                new_counts[phone] = len(avis)
                print(f"[SCAMTEL] ✅ {len(avis)} avis pour {phone}")

                if mode == "check" and len(avis) > old_counts.get(phone, 0):
                    nouveaux.append(phone)

            except Exception as e:
                print(f"[SCAMTEL] ❌ Erreur pour {phone} : {e}")
                results[phone] = []
                new_counts[phone] = old_counts.get(phone, 0)

    finally:
        driver.quit()

    with open(avis_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    with open(count_path, "w", encoding="utf-8") as f:
        json.dump(new_counts, f, indent=2, ensure_ascii=False)

    print("[SCAMTEL] Données sauvegardées.")

    if mode == "check":
        if nouveaux:
            print("\n🆕 Nouveaux avis détectés pour :")
            for n in nouveaux:
                print(f" - {n}")
            send_scamtel_email(nouveaux)
        else:
            print("\n✅ Aucun nouvel avis détecté.")