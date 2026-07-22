#!/usr/bin/env python3
"""
Werkt de ratingregels op de homepages bij met de actuele App Store-cijfers.

Waarom zo: de bezoeker mag geen enkele externe request doen — dat is de belofte
in de colophon. Dus halen we de cijfers hier op, schrijven ze in de HTML, en
committen het resultaat. Wat de browser krijgt blijft statische tekst.

De cijfers komen uit Apple's publieke lookup-API; daar is geen sleutel voor
nodig. Downloadaantallen zitten daar niet in — die vragen de App Store Connect
API met een privésleutel, en dat is bewust nog niet ingebouwd.

Aanroepen:  python3 scripts/update-ratings.py [--check]
            --check schrijft niets en geeft exit 1 als er iets zou wijzigen.
"""

import json
import pathlib
import re
import sys
import urllib.request

LOOKUP = "https://itunes.apple.com/lookup?id={}&country=nl"

# Per taal: decimaalteken en de tekst als er nog geen ratings zijn.
LOCALES = {
    "index.html":    {"dec": ".", "none": "No ratings yet"},
    "nl/index.html": {"dec": ",", "none": "Nog geen ratings"},
}

MARKER = re.compile(r"(<!--rating:(\d+)-->)(.*?)(<!--/rating-->)", re.S)


def fetch(app_id):
    """(gemiddelde, aantal) voor een app-id, of (None, 0) als er nog niets is."""
    req = urllib.request.Request(
        LOOKUP.format(app_id), headers={"User-Agent": "jimmyrentmeester.github.io"}
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.load(r)
    if not data.get("resultCount"):
        raise SystemExit(f"App {app_id} niet gevonden in de lookup-API")
    app = data["results"][0]
    count = int(app.get("userRatingCount") or 0)
    if count == 0:
        return None, 0
    return float(app.get("averageUserRating") or 0), count


def render(loc, score, count):
    if count == 0:
        return f'<span class="none">{loc["none"]}</span>'
    text = f"{score:.1f}".replace(".", loc["dec"])
    word = "rating" if count == 1 else "ratings"
    return f'<span class="score">{text}</span> ★ · {count} {word}'


def main():
    check = "--check" in sys.argv
    root = pathlib.Path(__file__).resolve().parent.parent
    cache, changed = {}, False

    for rel, loc in LOCALES.items():
        path = root / rel
        src = path.read_text(encoding="utf-8")

        def replace(m):
            app_id = m.group(2)
            if app_id not in cache:
                cache[app_id] = fetch(app_id)
            score, count = cache[app_id]
            return m.group(1) + render(loc, score, count) + m.group(4)

        out = MARKER.sub(replace, src)
        if out != src:
            changed = True
            print(f"bijgewerkt: {rel}")
            if not check:
                path.write_text(out, encoding="utf-8")

    if not changed:
        print("geen wijzigingen")
    if check and changed:
        sys.exit(1)


if __name__ == "__main__":
    main()
