from __future__ import annotations

from contextlib import contextmanager

from selenium.webdriver.chrome.service import Service
from undetected_chromedriver import Chrome, ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager

from core.logger import log
from core.user_agent import get_random_user_agent

try:
    from selenium_stealth import stealth
except Exception:
    stealth = None


def get_stealth_driver(headless: bool = False) -> Chrome:
    options = ChromeOptions()

    if headless:
        options.add_argument("--headless=new")
    else:
        options.add_argument("--start-maximized")

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-notifications")
    options.add_argument("--lang=fr-FR")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # 🎯 User-agent aléatoire
    ua = get_random_user_agent()
    options.add_argument(f"--user-agent={ua}")

    log(f"[DRIVER] 🎭 User-Agent utilisé : {ua}")

    driver = Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.set_page_load_timeout(30)

    if stealth is not None:
        stealth(
            driver,
            languages=["fr-FR", "fr"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )
    else:
        log("[DRIVER] ⚠️ selenium-stealth non installé, stealth partiel.")

    return driver


def close_driver(driver: Chrome | None) -> None:
    if driver is None:
        return

    try:
        driver.quit()
    except Exception as e:
        log(f"[DRIVER] ⚠️ Erreur fermeture driver : {e}")

    try:
        service = getattr(driver, "service", None)
        if service is not None:
            service.stop()
    except Exception as e:
        log(f"[DRIVER] ⚠️ Erreur arrêt service driver : {e}")


@contextmanager
def managed_driver(headless: bool = False) -> Chrome:
    driver = get_stealth_driver(headless=headless)
    try:
        yield driver
    finally:
        close_driver(driver)
