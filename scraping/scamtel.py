import gc
import json
import random
import time
from typing import List

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from core.logger import log
from core.result_collector import compare_results
from scraping.driver import get_stealth_driver


def load_phones(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("telephones", [])


def search_scamtel(driver, phone: str):
    driver.get("https://fr.scamtel.com/")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "search")))

    input_field = driver.find_element(By.NAME, "search")
    input_field.clear()
    input_field.send_keys(phone)
    input_field.send_keys(Keys.RETURN)

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "comment-add-form")))
    time.sleep(random.uniform(1.5, 3))  # délai naturel après recherche


def extract_reviews(driver) -> List[str]:
    reviews = []

    avis_elements = driver.find_elements(By.CSS_SELECTOR, ".comment-list-item")
    if not avis_elements:
        return []

    while True:
        avis_elements = driver.find_elements(By.CSS_SELECTOR, ".comment-list-item")
        for el in avis_elements:
            try:
                texte = el.find_element(By.CSS_SELECTOR, ".comment-text").text.strip()
                info = el.find_element(By.CSS_SELECTOR, ".comment-info").text.strip()
                reviews.append(f"{info} | {texte}")
            except Exception as e:
                log(f"[SCAMTEL] Erreur extraction avis : {e}")

        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "a.page-link[rel='next']")
            next_url = next_button.get_attribute("href")
            if not next_url:
                break

            time.sleep(random.uniform(2, 4))  # délai avant pagination
            driver.get(next_url)

            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "comment-add-form")))
        except Exception:
            break

    return reviews


def scrape_scamtel(mode: str = "check") -> dict:
    phones = load_phones("data/listing.json")
    all_avis = {}

    driver = get_stealth_driver(headless=False)

    try:
        for phone in phones:
            log(f"[SCAMTEL] Recherche de : {phone}")
            try:
                search_scamtel(driver, phone)
                avis = extract_reviews(driver)
                all_avis[phone] = avis
                log(f"[SCAMTEL] ✅ {len(avis)} avis pour {phone}")
            except Exception as e:
                log(f"[SCAMTEL] ❌ Erreur pour {phone} : {e}")
                all_avis[phone] = []

            # délai aléatoire entre les numéros
            time.sleep(random.uniform(3.5, 6))

    finally:
        driver.quit()
        del driver
        gc.collect()

    return compare_results("scamtel", all_avis, mode)
