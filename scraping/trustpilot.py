import json
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from core.logger import log
from core.result_collector import compare_results
from scraping.driver import get_stealth_driver


def get_trustpilot_sites():
    with open("data/listing.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("sites", [])


def scrape_trustpilot(mode: str = "check") -> dict:
    sites = get_trustpilot_sites()
    all_avis = {}
    driver = get_stealth_driver(headless=False)

    try:
        for site in sites:
            domain = site.replace("www.", "").strip()
            url = f"https://fr.trustpilot.com/review/{domain}"
            log(f"[TRUSTPILOT] Scraping {url}")

            try:
                driver.get(url)
                time.sleep(4)

                avis_list = []
                current_page = 1
                max_pages = 10

                while current_page <= max_pages:
                    try:
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

                                titre = el.find_element(
                                    By.CSS_SELECTOR, '[data-service-review-title-typography="true"]'
                                ).text.strip() or ""

                                contenu = el.find_element(
                                    By.CSS_SELECTOR, '[data-service-review-text-typography="true"]'
                                ).text.strip() or ""

                                avis_list.append({
                                    "auteur": auteur,
                                    "note": note,
                                    "date": date,
                                    "titre": titre,
                                    "contenu": contenu,
                                })
                            except Exception as e:
                                log(f"[TRUSTPILOT] Erreur dans un avis : {e}")

                        # pagination
                        try:
                            next_btn = driver.find_element(
                                By.CSS_SELECTOR, 'a[data-pagination-button-next-link="true"]'
                            )
                            next_url = next_btn.get_attribute("href")
                            if next_url:
                                driver.get(next_url)
                                current_page += 1
                                time.sleep(2)
                            else:
                                break
                        except Exception:
                            break

                    except Exception as e:
                        log(f"[TRUSTPILOT] Erreur chargement page {current_page} : {e}")
                        break

                log(f"[TRUSTPILOT] ✅ {len(avis_list)} avis pour {site}")
                all_avis[site] = avis_list

            except Exception as e:
                log(f"[TRUSTPILOT] ❌ Erreur sur {site} : {e}")
                all_avis[site] = []

    finally:
        driver.quit()

    return compare_results("trustpilot", all_avis, mode)
