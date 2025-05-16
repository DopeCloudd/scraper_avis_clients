import datetime
import os

from core.config import LOGS_DIR, LOGS_FILE

# 📁 Dossier log + fichier
os.makedirs(LOGS_DIR, exist_ok=True)


def log(message: str):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    full_msg = f"[{timestamp}] {message}"

    # Terminal
    print(full_msg)

    # Fichier
    with open(LOGS_FILE, "a", encoding="utf-8") as f:
        f.write(full_msg + "\n")
