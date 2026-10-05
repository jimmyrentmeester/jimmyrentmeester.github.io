#!/usr/bin/env python3
"""
Maakt de cv-pdf's (NL en EN) die op /nl/cv/ en /cv/ te downloaden zijn.

De inhoud staat hieronder in DATA en moet gelijk blijven aan de cv-pagina's
(nl/cv/index.html en cv/index.html). Verander je daar iets, pas het hier ook
aan en draai dit script opnieuw.

Gebruik (Node + Playwright nodig voor de laatste stap):
    python3 scripts/cv-pdf/build.py          # schrijft .build/cv-nl.html en cv-en.html
    node scripts/cv-pdf/render.js            # maakt de twee pdf's

Lettertypes: Inter en Source Serif 4 (SIL Open Font License), alleen in de
pdf ingebed; de website zelf laadt geen webfonts.
"""
import base64
import html
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / ".build"
ROOT = HERE.parent.parent

MAIL = "jimmy.rentmeester@gmail.com"
LINKEDIN = "linkedin.com/in/jimmyrentmeester"

DATA = {
    "nl": {
        "out": "nl/cv/jimmy-rentmeester-cv.pdf",
        "compact": True,
        "site": "jimmyrentmeester.github.io/nl",
        "role": "Lead Productmanager · Coolblue",
        "place": "Tilburg",
        "labels": {"profile": "Profiel", "experience": "Ervaring", "glance": "In het kort",
                   "skills": "Vaardigheden", "education": "Opleiding",
                   "languages": "Talen", "now": "heden"},
        "profile": "Ik ben Lead Productmanager bij Coolblue en verantwoordelijk voor het commerciële resultaat en de online klantreis van de categorieën Gaming en Printers & Kantoor in Nederland, België en Duitsland. Ik maak keuzes op basis van klantinzicht en data, en breng daarbij de belangen van commercie, marketing, inkoop en development bij elkaar. Waar ik goed in ben: prioriteren, afspraken maken met stakeholders, en structuur aanbrengen als veel dingen van elkaar afhangen. Daarnaast breng ik eigen iOS-apps uit, waarin ik de productrichting en keuzes bepaal.",
        "glance": [("Team", "9 mensen: 3 commercieel productmanagers, 3 product journey managers, 3 productredacteuren"),
                   ("Werkgebied", "Nederland, België, Duitsland"),
                   ("E-commerce", "Sinds 2016"),
                   ("Leidinggevend", "Sinds 2022")],
        "skills": [("Strategisch productmanagement", "visie, roadmap, prioritering"),
                   ("Data-analyse en procesoptimalisatie", "Looker, Tableau, Google Workspace, funnelanalyse, experimenten"),
                   ("Stakeholdermanagement", "business reviews op managementniveau, cross-functionele afstemming"),
                   ("Customer experience", "NPS, klantreis, retour- en reviewanalyse"),
                   ("Technologie", "AI-agents aansturen met Claude en Gemini, App Store-releases"),
                   ("AI-ambassadeur", "Power user van Glean bij Coolblue; collega's begeleiden bij gebruik en adoptie")],
        "education": [("Bachelor Communication & Media Studies", "Fontys Academy for the Creative Economy", "2012 – 2016"),
                      ("ICT Media & Design, propedeuse", "Fontys Hogeschool Eindhoven", "2011 – 2012"),
                      ("Netwerkbeheerder, mbo niveau 4", "Koning Willem I College", "2008 – 2011")],
        "languages": "Nederlands, Engels",
        "jobs": [
            ("Aug 2022 – heden", "Lead Productmanager", "Coolblue · Gaming, Printers & Kantoor",
             "Verantwoordelijk voor het commerciële resultaat en de online klantreis van de categorieën Gaming en Printers & Kantoor in Nederland, België en Duitsland. Ik geef direct leiding aan negen mensen en coach ze op hun werk en ontwikkeling.",
             ["Visies en roadmaps opstellen en uitrollen voor meerdere categorieteams, vertaald naar kwartaalmijlpalen.",
              "Strategie vertalen naar projectplannen, geprioriteerd op klant- en businesswaarde.",
              "Multidisciplinaire projectteams leiden: afstemming, voortgang en prioritering.",
              "Afspraken maken met stakeholders zoals inkoop, marketing en development over resultaat en voortgang.",
              "Met developmentteams van andere domeinen nieuwe features op hun roadmap krijgen.",
              "De LEGO-categorie bij Coolblue opgezet en er eindverantwoordelijk voor, ook commercieel."]),
            ("Apr 2026 – heden", "Productontwikkeling eigen iOS-apps", "Buiten werktijd · backlog, user stories, App Store-releases",
             "AI schrijft de code; ik bepaal het probleem, de scope, de prioriteiten en wat live gaat.",
             [("BabyBeam.", "Videobabyfoon met twee iPhones, zonder account. Live sinds juli 2026."),
              ("WristVault.", "Horlogecollectie bijhouden, eenmalige aankoop. Live sinds juli 2026."),
              ("GRID_BREAKER.", "Reflexspel zonder advertenties. Live sinds juni 2026.")],
             ("Projectnotities zoals de backlog en een story met acceptatiecriterium staan op ", "jimmyrentmeester.github.io/nl", "https://jimmyrentmeester.github.io/nl/", ".")),
            ("2020 – 2022", "Productmanager Gaming", "Coolblue",
             "Eindverantwoordelijk voor het commerciële resultaat en de klantreis van de Gaming-categorie. Bij de lancering van de PlayStation 5 in 2020 (weinig voorraad, veel vraag) werkte ik tegelijk met development, het app-team, marketing, klantenservice en logistiek. Daarna richtte ik een vast proces in voor nieuwe leveringen.",
             ["Groei en klantreizen verbeteren op basis van gedrags-, retour- en reviewdata.",
              "Collega-productmanagers coachen op data, experimenten en het vak."]),
            ("2019 – 2020", "SEO Specialist", "BigSpark B.V. · Nijmegen",
             "Technische en inhoudelijke SEO om organisch verkeer te laten groeien, op basis van data-analyse.", []),
            ("2018 – 2019", "Online Marketeer SEO & CRO", "Coolblue",
             "Customer journey voor Gaming & IT-accessoires. Landingspagina's en navigatie verbeterd op basis van klantgedrag.", []),
            ("2017 – 2018", "Product Support Specialist", "Coolblue",
             "NPS, retourredenen en klantfeedback analyseren voor productverbeteringen.", []),
            ("2016 – 2017", "Productredacteur", "Coolblue",
             "Content voor Virtual Reality en Tablets, en verbeteringen binnen het contentteam.", []),
            ("2014 – 2016", "Software Research & Concept Development", "U-Approach · Eindhoven",
             "Concepten met Bluetooth-beacons voor onder meer GLOW en VisitBrabant, samen met design en IT. Onderzoek naar hoe mensen mobiele apps gebruiken en wat dat gedrag beïnvloedt.", []),
        ],
        "foot": "Adres en telefoonnummer op aanvraag per e-mail.",
    },
    "en": {
        "out": "cv/jimmy-rentmeester-cv-en.pdf",
        "compact": True,  # Engelse tekst is langer; zo blijft het op twee pagina's
        "site": "jimmyrentmeester.github.io",
        "role": "Lead Product Manager · Coolblue",
        "place": "Tilburg, Netherlands",
        "labels": {"profile": "Profile", "experience": "Experience", "glance": "At a glance",
                   "skills": "Skills", "education": "Education",
                   "languages": "Languages", "now": "present"},
        "profile": "I'm Lead Product Manager at Coolblue, responsible for the commercial results and the online customer journey of the Gaming and Printers & Office categories in the Netherlands, Belgium and Germany. I make decisions based on customer insight and data, and bring the interests of commercial, marketing, purchasing and development together along the way. What I'm good at: prioritising, making agreements with stakeholders, and bringing structure when a lot of things depend on each other. Alongside that I ship my own iOS apps, where I set the product direction and make the decisions.",
        "glance": [("Team", "9 people: 3 commercial product managers, 3 product journey managers, 3 product editors"),
                   ("Market", "Netherlands, Belgium, Germany"),
                   ("E-commerce", "Since 2016"),
                   ("Leading a team", "Since 2022")],
        "skills": [("Strategic product management", "vision, roadmap, prioritisation"),
                   ("Data analysis and process optimisation", "Looker, Tableau, Google Workspace, funnel analysis, experiments"),
                   ("Stakeholder management", "management-level business reviews, cross-functional alignment"),
                   ("Customer experience", "NPS, customer journey, returns and review analysis"),
                   ("Technology", "directing AI agents with Claude and Gemini, App Store releases"),
                   ("AI ambassador", "Power user of Glean at Coolblue; helping colleagues use and adopt it")],
        "education": [("BA Communication & Media Studies", "Fontys Academy for the Creative Economy", "2012 – 2016"),
                      ("ICT Media & Design, foundation year", "Fontys University of Applied Sciences, Eindhoven", "2011 – 2012"),
                      ("Network Engineer, vocational level 4", "Koning Willem I College", "2008 – 2011")],
        "languages": "Dutch, English",
        "jobs": [
            ("Aug 2022 – present", "Lead Product Manager", "Coolblue · Gaming, Printers & Office",
             "Responsible for the commercial results and the online customer journey of the Gaming and Printers & Office categories in the Netherlands, Belgium and Germany. I directly lead nine people and coach them on their work and development.",
             ["Setting and rolling out vision and roadmaps across several category teams, broken down into quarterly milestones.",
              "Turning strategy into project plans, prioritised on customer and business value.",
              "Leading multidisciplinary project teams: alignment, progress and prioritisation.",
              "Making agreements with stakeholders such as purchasing, marketing and development on results and progress.",
              "Getting new features onto the roadmaps of development teams in other domains.",
              "Set up the LEGO category at Coolblue and owned it end to end, commercial results included."]),
            ("Apr 2026 – present", "Product development, own iOS apps", "Outside work · backlog, user stories, App Store releases",
             "AI writes the code; I decide the problem, the scope, the priorities and what goes live.",
             [("BabyBeam.", "Video baby monitor using two iPhones, no account. Live since July 2026."),
              ("WristVault.", "Watch collection tracker, one-time purchase. Live since July 2026."),
              ("GRID_BREAKER.", "Reflex game without ads. Live since June 2026.")],
             ("Working notes such as the backlog and a story with an acceptance criterion are on ", "jimmyrentmeester.github.io", "https://jimmyrentmeester.github.io/", ".")),
            ("2020 – 2022", "Product Manager, Gaming", "Coolblue",
             "End-to-end owner of the commercial performance and customer journey of the Gaming category. For the PlayStation 5 launch in 2020 (little stock, a lot of demand) I worked with development, the app team, marketing, customer service and logistics at the same time. Afterwards I set up a fixed process for new deliveries.",
             ["Improving growth and customer journeys using behavioural, returns and review data.",
              "Coaching fellow product managers on data, experimentation and the craft."]),
            ("2019 – 2020", "SEO Specialist", "BigSpark B.V. · Nijmegen",
             "Technical and editorial SEO to grow organic traffic, based on data analysis.", []),
            ("2018 – 2019", "Online Marketeer, SEO & CRO", "Coolblue",
             "Customer journey for Gaming & IT accessories. Improved landing pages and navigation based on customer behaviour.", []),
            ("2017 – 2018", "Product Support Specialist", "Coolblue",
             "Analysing NPS, return reasons and customer feedback to drive product improvements.", []),
            ("2016 – 2017", "Product Editor", "Coolblue",
             "Content for Virtual Reality and Tablets, and improvements within the content team.", []),
            ("2014 – 2016", "Software Research & Concept Development", "U-Approach · Eindhoven",
             "Concepts around Bluetooth beacons for clients including GLOW and VisitBrabant, working with design and IT. Research into how people use mobile apps and what shifts that behaviour.", []),
        ],
        "foot": "Address and phone number available on request by email.",
    },
}


def font_face():
    faces = [("Inter", 400, "normal", "inter-latin-400-normal"), ("Inter", 500, "normal", "inter-latin-500-normal"),
             ("Inter", 600, "normal", "inter-latin-600-normal"), ("Inter", 700, "normal", "inter-latin-700-normal"),
             ("Source Serif", 400, "normal", "source-serif-4-latin-400-normal"),
             ("Source Serif", 600, "normal", "source-serif-4-latin-600-normal"),
             ("Source Serif", 400, "italic", "source-serif-4-latin-400-italic")]
    out = []
    for fam, w, st, f in faces:
        b64 = base64.b64encode((HERE / "fonts" / f"{f}.woff2").read_bytes()).decode()
        out.append(f"@font-face{{font-family:'{fam}';font-weight:{w};font-style:{st};"
                   f"src:url(data:font/woff2;base64,{b64}) format('woff2');}}")
    return "\n".join(out)


CSS = """
@page { size: A4; margin: 15mm 15mm 14mm; }
:root { --ink:#14161c; --muted:#555c69; --faint:#8a909c; --line:#e3e1dc; --accent:#4d5dfb; }
* { box-sizing: border-box; }
html, body { margin: 0; }
body { font-family: 'Inter', sans-serif; font-size: 8.9pt; line-height: 1.5; color: var(--ink);
       -webkit-print-color-adjust: exact; print-color-adjust: exact; font-feature-settings: "ss01", "cv11"; }
a { color: inherit; text-decoration: none; }

header { display: grid; grid-template-columns: 1fr auto; gap: 8mm; align-items: center;
         padding-bottom: 6mm; border-bottom: 1.5pt solid var(--ink); margin-bottom: 6mm; }
h1 { font-family: 'Source Serif', serif; font-weight: 600; font-size: 27pt; line-height: 1;
     letter-spacing: -.02em; margin: 0 0 2.2mm; }
.role { font-size: 10.5pt; font-weight: 500; color: var(--accent); margin: 0 0 3.2mm; }
.contact { display: flex; flex-wrap: wrap; gap: 1mm 4.5mm; margin: 0; color: var(--muted); font-size: 8.3pt; }
.contact span::before { content: ""; display: inline-block; width: 1.3mm; height: 1.3mm; border-radius: 50%;
                        background: var(--accent); margin: 0 1.6mm .45mm 0; vertical-align: middle; }
.photo { width: 27mm; height: 27mm; border-radius: 50%; object-fit: cover; display: block; }

.grid { display: grid; grid-template-columns: 1fr 55mm; gap: 0 8mm; }
.side { border-left: .6pt solid var(--line); padding-left: 6mm; }

h2 { font-size: 7.2pt; font-weight: 700; letter-spacing: .16em; text-transform: uppercase;
     color: var(--accent); margin: 0 0 2.6mm; }
section { margin-bottom: 6mm; }
.side section { break-inside: avoid; }
.profile p { margin: 0; font-family: 'Source Serif', serif; font-size: 10.6pt; line-height: 1.5; color: var(--ink); }

.job { display: grid; grid-template-columns: 24mm 1fr; gap: 0 4mm; padding: 2.6mm 0 3mm;
       border-top: .6pt solid var(--line); break-inside: avoid; }
.job:first-of-type { border-top: 0; padding-top: 0; }
.when { font-size: 7.6pt; color: var(--faint); font-weight: 500; padding-top: .5mm; font-variant-numeric: tabular-nums; }
.job h3 { font-size: 9.6pt; font-weight: 600; margin: 0; line-height: 1.3; }
.job .org { font-size: 8.2pt; color: var(--muted); margin: .3mm 0 1.4mm; }
.job p { margin: 0; color: #2c313a; }
.job ul { margin: 1.4mm 0 0; padding-left: 3.6mm; color: #2c313a; }
.job li { margin: 0 0 .7mm; }
.job li::marker { color: var(--accent); }
.job li b { font-weight: 600; color: var(--ink); }
.job .note { margin: 1.4mm 0 0; color: var(--muted); font-size: 8.2pt; }
.job .note a { color: var(--accent); }

.side dl { margin: 0; }
.side dt { font-size: 7.4pt; color: var(--faint); font-weight: 500; }
.side dd { margin: 0 0 2.2mm; }
.item { margin: 0 0 2.4mm; break-inside: avoid; }
.item b { font-weight: 600; display: block; }
.item span { color: var(--muted); display: block; font-size: 8.2pt; }
.item i { font-style: normal; color: var(--faint); font-size: 7.6pt; }

/* Compacte variant (EN): iets kleinere maten, zelfde ontwerp. */
body.compact { font-size: 8.6pt; line-height: 1.45; }
.compact header { padding-bottom: 5mm; margin-bottom: 5mm; }
.compact .photo { width: 25mm; height: 25mm; }
.compact section { margin-bottom: 5mm; }
.compact .profile p { font-size: 10.2pt; line-height: 1.45; }
.compact .job { padding: 2.2mm 0 2.4mm; }
.compact .job li { margin-bottom: .5mm; }
.compact .side dd { margin-bottom: 1.8mm; }
.compact .item { margin-bottom: 2mm; }

footer { margin-top: 2mm; padding-top: 2.4mm; border-top: .6pt solid var(--line);
         display: flex; justify-content: space-between; color: var(--faint); font-size: 7.4pt; }
"""


def esc(s):
    return html.escape(s, quote=False)


def page(code, d):
    L = d["labels"]
    jobs = []
    for job in d["jobs"]:
        when, title, org, text, bullets = job[:5]
        note = job[5] if len(job) > 5 else None
        def li(b):
            return f"<li><b>{esc(b[0])}</b> {esc(b[1])}</li>" if isinstance(b, tuple) else f"<li>{esc(b)}</li>"
        ul = ("<ul>" + "".join(li(b) for b in bullets) + "</ul>") if bullets else ""
        if note:
            ul += f'<p class="note">{esc(note[0])}<a href="{note[2]}">{esc(note[1])}</a>{esc(note[3])}</p>'
        jobs.append(f'<div class="job"><div class="when">{esc(when)}</div><div><h3>{esc(title)}</h3>'
                    f'<p class="org">{esc(org)}</p><p>{esc(text)}</p>{ul}</div></div>')
    glance = "".join(f"<dt>{esc(a)}</dt><dd>{esc(b)}</dd>" for a, b in d["glance"])
    skills = "".join(f'<div class="item"><b>{esc(a)}</b><span>{esc(b)}</span></div>' for a, b in d["skills"])
    edu = "".join(f'<div class="item"><b>{esc(a)}</b><span>{esc(b)}</span><i>{esc(c)}</i></div>' for a, b, c in d["education"])
    photo = base64.b64encode((HERE / "photo.jpg").read_bytes()).decode()
    return f"""<!doctype html>
<html lang="{code}"><head><meta charset="utf-8"><meta name="robots" content="noindex">
<title>Jimmy Rentmeester — CV</title><style>{font_face()}{CSS}</style></head>
<body{' class="compact"' if d.get("compact") else ''}>
<header>
  <div>
    <h1>Jimmy Rentmeester</h1>
    <p class="role">{esc(d["role"])}</p>
    <p class="contact"><span><a href="mailto:{MAIL}">{MAIL}</a></span><span><a href="https://www.{LINKEDIN}">{LINKEDIN}</a></span><span><a href="https://{d["site"]}/">{d["site"]}</a></span><span>{esc(d["place"])}</span></p>
  </div>
  <img class="photo" src="data:image/jpeg;base64,{photo}" alt="">
</header>
<div class="grid">
  <main>
    <section class="profile"><h2>{L["profile"]}</h2><p>{esc(d["profile"])}</p></section>
    <section><h2>{L["experience"]}</h2>{"".join(jobs)}</section>
  </main>
  <aside class="side">
    <section><h2>{L["glance"]}</h2><dl>{glance}</dl></section>
    <section><h2>{L["skills"]}</h2>{skills}</section>
    <section><h2>{L["education"]}</h2>{edu}</section>
    <section><h2>{L["languages"]}</h2><p style="margin:0">{esc(d["languages"])}</p></section>
  </aside>
</div>
<footer><span>{esc(d["foot"])}</span><span>{MAIL}</span></footer>
</body></html>"""


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for code, d in DATA.items():
        (OUT / f"cv-{code}.html").write_text(page(code, d), encoding="utf-8")
        print("geschreven:", OUT / f"cv-{code}.html", "→", d["out"])
