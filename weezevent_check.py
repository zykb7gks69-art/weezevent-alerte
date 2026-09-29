name: Surveillance billetterie Weezevent

on:
  schedule:
    - cron: "*/5 * * * *"   # toutes les 5 minutes (minimum autorisé par GitHub)
  workflow_dispatch:         # permet de le lancer à la main pour tester

jobs:
  check:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Installer les dépendances
        run: |
          pip install playwright requests
          playwright install --with-deps chromium

      - name: Vérifier la billetterie
        env:
          NTFY_TOPIC: ${{ secrets.NTFY_TOPIC }}
        run: python weezevent_check.py
