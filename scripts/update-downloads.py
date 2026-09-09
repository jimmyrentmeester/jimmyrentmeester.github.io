#!/usr/bin/env python3
"""
Werkt het downloadaantal op de homepages bij met cijfers uit de App Store
Connect API (Sales and Trends Reports).

Zelfde principe als update-ratings.py: de bezoeker doet nul externe
requests. Wij halen het cijfer hier op, schrijven het statisch in de HTML,
en committen het resultaat.

Waarom dit een apart script is en niet in update-ratings.py zit: ratings
komen uit Apple's publieke lookup-API (geen sleutel nodig). Downloadaantallen
zitten daar niet in — die vragen de App Store Connect API, en die vereist
een privésleutel (JWT-auth met een .p8-bestand). Dat is een heel ander
soort geheim dan "geen geheim", dus bewust gescheiden: als deze sleutel ooit
verloopt of ingetrokken wordt, blijven de ratings gewoon doorlopen.

Vereist drie GitHub Secrets (of lokaal env-vars voor handmatig testen):
  ASC_KEY_ID       — Key ID van de API-sleutel (ASC → Users and Access →
                      Integrations → App Store Connect API)
  ASC_ISSUER_ID    — Issuer ID, staat op dezelfde pagina
  ASC_PRIVATE_KEY  — de volledige inhoud van het .p8-bestand (incl.
                      -----BEGIN PRIVATE KEY----- regels)

De sleutel heeft genoeg aan de "Sales and Reports"-rol (App Manager niet
nodig). Zonder deze env-vars stopt het script stil (exit 0, geen wijziging)
— dat is bewust zodat de dagelijkse workflow niet rood kleurt zolang de
secrets nog niet zijn toegevoegd.

Onder een instelbare drempel tonen we geen downloadcijfer — zie ook de
MIN_RATINGS_TO_SHOW-afweging in update-ratings.py: een paar honderd
downloads naast een claim over "vier apps die ik zelf bouw" oogt eerder
kwetsbaar dan overtuigend.

Aanroepen:  python3 scripts/update-downloads.py [--check]
            --check schrijft niets en geeft exit 1 als er iets zou wijzigen.

Bron: App Store Connect API "Sales and Trends Reports" endpoint
(GET /v1/salesReports), reportType=SALES, frequency=DAILY. Elke daily
report bevat rijen per app/product/land; "Units" opgeteld over alle rijen
met Product Type Identifier "1"/"1F"/"1T" (app-installs, geen updates/
herdownloads dubbel tellen we bewust niet uit — zie NOTE hieronder) geeft
het aantal nieuwe downloads voor die dag. We tellen decemaal de laatste N
dagen op tot een cumulatief totaal-sinds-launch per app, gecachet in
downloads-cache.json zodat we niet elke keer de volledige historie
opnieuw hoeven op te vragen.
"""

import base64
import csv
import datetime as dt
import gzip
import io
import json
import os
import pathlib
import re
import sys
import time
import urllib.error
import urllib.request

try:
    import jwt  # PyJWT — geïnstalleerd door de workflow (pip install pyjwt)
except ImportError:
    jwt = None

MIN_DOWNLOADS_TO_SHOW = 50

# app_id (App Store Connect "Apple ID", hetzelfde nummer als in de
# rating-marker) -> Vendor Number is NIET hetzelfde als de App Store id.
# ASC_VENDOR_NUMBER moet je één keer opzoeken: App Store Connect →
# Business → "Vendor number" bovenaan, geldt voor je hele account (alle
# apps), dus dit is geen per-app-secret.
APPS = {
    "6783058581": "BabyBeam",
    "6779888720": "GRID_BREAKER",
    "6792535679": "WristVault",
}

# Startdatum voor de allereerste run (lege cache): ruim vóór de vroegste
# app-lancering, zodat downloads sinds launch worden meegeteld i.p.v.
# alleen vanaf "gisteren" (GRID_BREAKER ~begin juni, WristVault eind juli,
# BabyBeam 04-07). Een paar weken te vroeg beginnen levert gewoon 404's op
# die worden overgeslagen (misses-teller reset zodra er weer data is), dus
# geen risico op vastlopen.
BACKFILL_START = dt.date(2026, 6, 1)

# Per taal: decimaalscheiding (duizendtal) en tekst als er nog niets te tonen is.
LOCALES = {
    "index.html":    {"thousands": ",", "none": ""},
    "nl/index.html": {"thousands": ".", "none": ""},
}

MARKER = re.compile(r"(<!--downloads:(\d+)-->)(.*?)(<!--/downloads-->)", re.S)

ASC_API = "https://api.appstoreconnect.apple.com/v1/salesReports"
CACHE_PATH = pathlib.Path(__file__).resolve().parent.parent / "downloads-cache.json"


def make_jwt():
    key_id = os.environ.get("ASC_KEY_ID")
    issuer_id = os.environ.get("ASC_ISSUER_ID")
    private_key = os.environ.get("ASC_PRIVATE_KEY")
    if not (key_id and issuer_id and private_key):
        return None
    if jwt is None:
        print("PyJWT niet geïnstalleerd — 'pip install pyjwt cryptography'", file=sys.stderr)
        return None
    now = int(time.time())
    payload = {
        "iss": issuer_id,
        "iat": now,
        "exp": now + 19 * 60,  # max 20 min, marge houden
        "aud": "appstoreconnect-v1",
    }
    headers = {"alg": "ES256", "kid": key_id, "typ": "JWT"}
    return jwt.encode(payload, private_key, algorithm="ES256", headers=headers)


def fetch_daily_report(token, report_date, vendor_number):
    """Eén dag Sales Report ophalen. Geeft de rauwe (gzipped) TSV-bytes terug,
    of None als er voor die dag nog geen rapport is (weekend/te vroeg/te laat)."""
    params = {
        "filter[reportDate]": report_date.isoformat(),
        "filter[reportType]": "SALES",
        "filter[reportSubType]": "SUMMARY",
        "filter[frequency]": "DAILY",
        "filter[vendorNumber]": vendor_number,
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    req = urllib.request.Request(
        f"{ASC_API}?{query}",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/a-gzip"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None  # nog geen rapport voor die dag (normaal, kom later terug)
        raise


def units_by_app(gz_bytes):
    """TSV uitpakken en Units optellen per SKU/Apple Identifier."""
    raw = gzip.decompress(gz_bytes).decode("utf-8", errors="replace")
    reader = csv.DictReader(io.StringIO(raw), delimiter="\t")
    totals = {}
    for row in reader:
        # "1"=app, "1F"=in-app purchase, "1T"=update — alleen "1" telt als
        # nieuwe download. Updates/herdownloads bewust niet meegeteld,
        # anders loopt het cijfer sneller op dan de App Store zelf toont.
        if row.get("Product Type Identifier") != "1":
            continue
        app_id = row.get("Apple Identifier", "").strip()
        try:
            units = int(row.get("Units", "0") or "0")
        except ValueError:
            units = 0
        totals[app_id] = totals.get(app_id, 0) + units
    return totals


def load_cache():
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    return {"last_date": None, "totals": {}}


def save_cache(cache):
    CACHE_PATH.write_text(json.dumps(cache, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def update_totals(token, vendor_number):
    """Haalt alle nog-niet-verwerkte dagen op sinds de cache en telt ze bij
    het cumulatieve totaal per app op. Rapporten verschijnen met ~2-3 dagen
    vertraging, dus we stoppen zodra we twee 404's op rij tegenkomen."""
    cache = load_cache()
    start = (
        dt.date.fromisoformat(cache["last_date"]) + dt.timedelta(days=1)
        if cache["last_date"]
        else BACKFILL_START  # zonder cache: backfillen vanaf vóór de eerste app-launch
    )
    today = dt.date.today()
    d = start
    misses = 0
    # Bij backfill (potentieel maanden aan dagen) mogen losse dagen zonder
    # rapport (misses) niet de hele run afkappen zoals bij de normale
    # dagelijkse catch-up van 1-2 dagen. We tellen alleen na het inlopen
    # van de achterstand (d dicht bij vandaag) de 2-misses-stop, zodat een
    # paar ontbrekende dagen uit het verleden de backfill niet vroegtijdig
    # stoppen terwijl recentere dagen nog niet zijn opgehaald.
    catching_up = (today - start).days > 7
    while d < today:
        report = fetch_daily_report(token, d, vendor_number)
        if report is None:
            misses += 1
            if not catching_up and misses >= 2:
                break
            d += dt.timedelta(days=1)
            continue
        misses = 0
        for app_id, units in units_by_app(report).items():
            cache["totals"][app_id] = cache["totals"].get(app_id, 0) + units
        cache["last_date"] = d.isoformat()
        d += dt.timedelta(days=1)
        # Zodra we binnen 7 dagen van vandaag zijn, gedraagt de rest van de
        # loop zich weer als normale dagelijkse catch-up.
        catching_up = (today - d).days > 7
    save_cache(cache)
    return cache["totals"]


def render(loc, total):
    if total is None or total < MIN_DOWNLOADS_TO_SHOW:
        return ""
    # Duizendtallen met de juiste scheiding per taal, geen decimalen.
    text = f"{total:,}".replace(",", "\0").replace(".", loc["thousands"]).replace("\0", loc["thousands"])
    return f' · <span class="dl"><span class="n">{text}</span> downloads</span>'


def main():
    check = "--check" in sys.argv
    root = pathlib.Path(__file__).resolve().parent.parent

    token = make_jwt()
    vendor_number = os.environ.get("ASC_VENDOR_NUMBER")
    if not token or not vendor_number:
        print("ASC_KEY_ID/ASC_ISSUER_ID/ASC_PRIVATE_KEY/ASC_VENDOR_NUMBER nog niet gezet — "
              "downloads-script slaat over (dit is geen fout).")
        return

    totals_by_appstore_id = update_totals(token, vendor_number)
    # De Sales Report indexeert op "Apple Identifier", wat hetzelfde nummer
    # is als de App Store id die we al in de rating-markers gebruiken.
    changed = False

    for rel, loc in LOCALES.items():
        path = root / rel
        src = path.read_text(encoding="utf-8")

        def replace(m):
            app_id = m.group(2)
            total = totals_by_appstore_id.get(app_id)
            return m.group(1) + render(loc, total) + m.group(4)

        out = MARKER.sub(replace, src)
        if out != src:
            changed = True
            print(f"bijgewerkt: {rel}")
            if not check:
                path.write_text(out, encoding="utf-8")

    if not changed:
        print("geen wijzigingen in de downloadcijfers")
    if check and changed:
        sys.exit(1)


if __name__ == "__main__":
    main()
