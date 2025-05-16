import os
from pathlib import Path

from dotenv import load_dotenv

# Charger les variables d’environnement
load_dotenv()

# 📁 Répertoires
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
LOGS_FILE = LOGS_DIR / "scraper.log"

# 📄 Fichiers (exemple si tu veux centraliser certains chemins)
HISTORIQUE_FILE = DATA_DIR / "historique.json"
SOURCE_FILE = DATA_DIR / "sources.csv"

# 📧 Email
EMAIL_TO = os.getenv("EMAIL_RECIPIENT")
EMAIL_FROM = os.getenv("EMAIL_SENDER")
EMAIL_PWD = os.getenv("EMAIL_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
