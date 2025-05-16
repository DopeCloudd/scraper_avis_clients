import gc
import json
import random
import time
from typing import List

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from core.logger import log
from core.result_collector import compare_results
from scraping.driver import get_stealth_driver


def load_targets(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("emails", []) + data.get("sites", [])


def accept_cookies_if_present(driver):
    try:
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button//span[text()=\"J'ACCEPTE\"]"))
        ).click()
        log("[SCAMDOC] ✅ Consentement cookies accepté.")
        time.sleep(random.uniform(0.5, 1.5))
    except Exception:
        log("[SCAMDOC] Aucun popup cookies détecté.")


def search_scamdoc(driver, query: str):
    driver.get("https://fr.scamdoc.com/")
    time.sleep(random.uniform(4, 6))  # pause initiale

    accept_cookies_if_present(driver)

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "search_input")))
    input_field = driver.find_element(By.ID, "search_input")
    input_field.clear()
    input_field.send_keys(query)

    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "search-load")))
    driver.find_element(By.ID, "search-load").click()

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "comment-add-form")))
    time.sleep(random.uniform(1.5, 3))  # pause après chargement


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
                log(f"[SCAMDOC] Erreur extraction avis : {e}")

        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "a.page-link[rel='next']")
            next_url = next_button.get_attribute("href")
            if not next_url:
                break

            time.sleep(random.uniform(2, 4))  # pause avant pagination
            driver.get(next_url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "comment-add-form")))

        except Exception:
            break

    return reviews


def scrape_scamdoc(mode: str = "check") -> dict:
    targets = load_targets("data/listing.json")
    all_avis = {}

    driver = get_stealth_driver(headless=False)

    try:
        for target in targets:
            log(f"[SCAMDOC] Recherche de : {target}")
            try:
                search_scamdoc(driver, target)
                avis = extract_reviews(driver)
                all_avis[target] = avis
                log(f"[SCAMDOC] ✅ {len(avis)} avis pour {target}")
            except Exception as e:
                log(f"[SCAMDOC] ❌ Erreur pour {target} : {e}")
                all_avis[target] = []

            time.sleep(random.uniform(3, 6))  # pause entre cibles

    finally:
        driver.quit()
        del driver
        gc.collect()

    return compare_results("scamdoc", all_avis, mode)
