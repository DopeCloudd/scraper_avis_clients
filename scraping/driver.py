from selenium.webdriver.chrome.service import Service
from undetected_chromedriver import Chrome, ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager

from core.user_agent import get_random_user_agent


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
    options.add_argument("--lang=fr-FR")

    # 🎯 User-agent aléatoire
    ua = get_random_user_agent()
    options.add_argument(f"--user-agent={ua}")

    print(f"[DRIVER] 🎭 User-Agent utilisé : {ua}")

    driver = Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.set_page_load_timeout(30)
    return driver
