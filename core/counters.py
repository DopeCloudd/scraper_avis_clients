import json
import os


def load_counts(scraper_name: str) -> dict:
    path = f"data/{scraper_name}_counts.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_counts(scraper_name: str, counts: dict):
    path = f"data/{scraper_name}_counts.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(counts, f, indent=2, ensure_ascii=False)
