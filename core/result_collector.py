from core.counters import load_counts, save_counts


def compare_results(scraper_name: str, new_data: dict, mode: str = "check") -> dict:
    """
    Compare les nouveaux résultats avec les anciens compteurs.

    Retourne un dict :
    {
        "scraper": "trustpilot",
        "nouveaux": {"site1.fr": 2},
        "total": {"site1.fr": 5, "site2.fr": 3}
    }
    """
    assert mode in ["init", "check"]
    old_counts = load_counts(scraper_name)
    new_counts = {k: len(v) for k, v in new_data.items()}
    nouveaux = {}

    if mode == "check":
        for k, new_val in new_counts.items():
            if new_val > old_counts.get(k, 0):
                nouveaux[k] = new_val - old_counts.get(k, 0)

    save_counts(scraper_name, new_counts)

    return {
        "scraper": scraper_name,
        "nouveaux": nouveaux,
        "total": new_counts,
    }
