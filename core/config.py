import os
from pathlib import Path

from dotenv import load_dotenv

# Charger les variables d’environnement
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
HISTORIQUE_FILE = DATA_DIR / "historique.json"
SOURCE_FILE = DATA_DIR / "sources.csv"

EMAIL_TO = os.getenv("EMAIL_TO")
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_PWD = os.getenv("EMAIL_PWD")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
