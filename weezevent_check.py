import os
import sys

import requests
from playwright.sync_api import sync_playwright

URL = "https://my.weezevent.com/la-nuit-du-droit-au-conseil-detat-2026"

# Messages qui indiquent que la billetterie est complete
MOTS_COMPLET = [
    "victime de son succès",
    "revenir plus tard",
    "plus de places",
    "aucune place",
    "billetterie fermée",
]
# Elements presents quand le module de billetterie est bien charge
MOTS_WIDGET = ["panier", "coordonnées"]


def main():
    topic = os.environ.get("NTFY_TOPIC")
    if not topic:
        sys.exit("Variable NTFY_TOPIC manquante")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(locale="fr-FR")
        page.goto(URL, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(4000)
        morceaux = []
        for frame in page.frames:
            try:
                morceaux.append(frame.inner_text("body"))
            except Exception:
                pass
        browser.close()

    texte = "\n".join(morceaux).lower()
    complet = any(m in texte for m in MOTS_COMPLET)
    widget_charge = all(m in texte for m in MOTS_WIDGET)

    print("----- TEXTE VU -----")
    print(texte[-1500:])
    print(f"---- complet={complet} widget_charge={widget_charge} ----")

    if widget_charge and not complet:
        requests.post(
            f"https://ntfy.sh/{topic}",
            data="Une place semble disponible à la Nuit du Droit !".encode("utf-8"),
            headers={"Title": "Place dispo !", "Priority": "urgent",
                     "Tags": "ticket", "Click": URL},
            timeout=15,
        )
        print("Notification envoyée")
    else:
        print("Toujours complet (ou module non charge)")


if __name__ == "__main__":
    main()
