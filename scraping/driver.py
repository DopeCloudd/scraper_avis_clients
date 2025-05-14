from selenium.webdriver.chrome.service import Service
from undetected_chromedriver import Chrome, ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager


def get_stealth_driver(headless: bool = False) -> Chrome:
    options = ChromeOptions()

    if headless:
        options.add_argument("--headless=new")

    # Options classiques pour éviter la détection
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")

    # Ces deux options POSENT PROBLÈME — on les supprime :
    # options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # options.add_experimental_option("useAutomationExtension", False)

    # Démarrage du navigateur
    driver = Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.set_page_load_timeout(30)
    return driver
