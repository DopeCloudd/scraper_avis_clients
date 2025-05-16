import smtplib
from email.mime.text import MIMEText

from core.config import EMAIL_FROM, EMAIL_PWD, EMAIL_TO


def send_global_report(reports: list[dict]):

    has_updates = any(r["nouveaux"] for r in reports)

    if has_updates:
        subject = "🆕 Nouveaux avis détectés"
        body = ["Bonjour,\n\nVoici les nouveaux avis détectés aujourd'hui :\n"]

        for report in reports:
            if report["nouveaux"]:
                body.append(f"🗂️ {report['scraper'].upper()}")
                for cible, nb in report["nouveaux"].items():
                    if report["scraper"] == "trustpilot":
                        url = f"https://fr.trustpilot.com/review/{cible.replace('www.', '')}"
                    elif report["scraper"] == "scamdoc":
                        url = f"https://fr.scamdoc.com/search?search={cible}"
                    elif report["scraper"] == "scamtel":
                        url = f"https://fr.scamtel.com/search?search={cible}"
                    else:
                        url = cible
                    body.append(f"- {cible} → {url} (+{nb} avis)")
                body.append("")  # ligne vide
        body.append("Cordialement,\nVotre robot de veille.")
    else:
        subject = "✅ Aucun nouvel avis détecté"
        body = [
            "Bonjour,\n\n",
            "La vérification automatique s’est bien déroulée.\n",
            "Aucun nouvel avis détecté aujourd’hui.\n\n",
            "Cordialement,\nLe robot de veille."
        ]

    message = MIMEText("\n".join(body))
    message["Subject"] = subject
    message["From"] = EMAIL_FROM
    message["To"] = EMAIL_TO

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_FROM, EMAIL_PWD)
            server.sendmail(EMAIL_FROM, EMAIL_TO, message.as_string())
        print("📧 Email récapitulatif envoyé.")
    except Exception as e:
        print(f"❌ Erreur lors de l’envoi de l’e-mail : {e}")
