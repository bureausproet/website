#!/usr/bin/env python3
"""Bouwt de statische website van Bureau Sproet.

Gebruik:
    python build.py            # bouwt de site in ./public
    python build.py --serve    # bouwt en start een lokale webserver op http://localhost:8000

Er zijn geen externe pakketten nodig; alleen Python 3.8+.

Teksten aanpassen: bewerk de HTML-fragmenten in ./content en draai dit script opnieuw.
Menu's, paginatitels, illustraties en de tekst in de rode balk onderaan staan in PAGES hieronder.

Speciale codes in de content:
    {{root}}          relatief pad naar de hoofdmap van de site (voor interne links)
    {{mail:naam}}     e-mailadres naam@bureausproet.nl, licht verborgen voor spambots
"""
import html
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
STATIC = ROOT / "static"
OUT = ROOT / "public"

SITE_URL = "https://www.bureausproet.nl"
SITE_NAME = "Bureau Sproet"
MAIL_DOMAIN = "bureausproet.nl"
MAIL_SUBJECT = "Informatie via de website"

# Hoofdmenu: (sectie, label, pad)
MAIN_MENU = [
    ("home", "Home", ""),
    ("wie", "Wie", "wie/"),
    ("wat", "Wat", "wat/"),
    ("waarom", "Waarom", "waarom/"),
    ("voor-wie", "Voor wie", "voor-wie/"),
    ("contact", "Contact", "contact/"),
]

# Submenu's in de zijbalk: sectie -> (kop, [(label, pad)])
SUB_MENUS = {
    "wie": ("Wie zijn wij", [
        ("Drie Sproeten", "wie/"),
        ("Anita ter Hofte", "wie/anita-ter-hofte/"),
        ("Mariët Bosschers", "wie/mariet-bosschers/"),
        ("Hannebeth Haffmans", "wie/hannebeth-haffmans/"),
    ]),
    "wat": ("Onze diensten", [
        ("Inleiding", "wat/"),
        ("Tekst- en bureauredactie", "wat/tekst-en-bureauredactie/"),
        ("Beeldredactie", "wat/beeldredactie/"),
        ("Webredactie", "wat/webredactie/"),
        ("Redactie in een content management systeem", "wat/redactie-in-een-cms/"),
        ("Onderwijskundige redactie", "wat/onderwijskundige-redactie/"),
        ("Schrijven van educatieve en informatieve tekst", "wat/schrijven-van-educatieve-en-informatieve-tekst/"),
        ("Projectleiding en auteursmanagement", "wat/projectleiding-en-auteursmanagement/"),
    ]),
}

# Illustraties onderaan de pagina: naam -> (bestand, breedte, hoogte, uitlijning)
ILLUSTRATIONS = {
    "wie": ("wie-zijn-wij.jpg", 663, 363, "left"),
    "anita": ("anita-ter-hofte.jpg", 663, 363, "left"),
    "mariet": ("mariet-bosschers.jpg", 664, 359, "left"),
    "hannebeth": ("hannebeth-haffmans.jpg", 669, 362, "left"),
    "wat": ("wat-doen-wij.jpg", 891, 270, "full"),
    "waarom": ("waarom-doen-wij-dat.jpg", 302, 233, "right"),
    "contact": ("contact_bg.jpg", 281, 219, "right"),
}

# Pagina's: pad, sectie, titel, tekst in de rode balk, illustratie, omschrijving (meta description)
PAGES = [
    dict(path="wie/", section="wie", title="Wie vormen Bureau Sproet?", tagline="Flexibel en betrokken", illu="wie",
         description="Bureau Sproet bestaat uit drie redacteuren: Mariët, Hannebeth en Anita."),
    dict(path="wie/anita-ter-hofte/", section="wie", title="Anita ter Hofte", tagline="Bureau Sproet - Anita ter Hofte", illu="anita"),
    dict(path="wie/mariet-bosschers/", section="wie", title="Mariët Bosschers", tagline="Bureau Sproet - Mariët Bosschers", illu="mariet"),
    dict(path="wie/hannebeth-haffmans/", section="wie", title="Hannebeth Haffmans", tagline="Bureau Sproet - Hannebeth Haffmans", illu="hannebeth"),
    dict(path="wat/", section="wat", title="Wat doet Bureau Sproet?", tagline="Aan het werk!", illu="wat",
         description="Tekst en beeld bewerken voor allerlei doelgroepen, dat is de specialiteit van Bureau Sproet."),
    dict(path="wat/tekst-en-bureauredactie/", section="wat", title="Tekst- en bureauredactie", tagline="Tekst- en bureauredactie", illu="wat"),
    dict(path="wat/beeldredactie/", section="wat", title="Beeldredactie", tagline="Beeldredactie", illu="wat"),
    dict(path="wat/webredactie/", section="wat", title="Webredactie", tagline="Webredactie", illu="wat"),
    dict(path="wat/redactie-in-een-cms/", section="wat", title="Redactie in een content management systeem", tagline="Redactie in een Content Management Systeem", illu="wat"),
    dict(path="wat/onderwijskundige-redactie/", section="wat", title="Onderwijskundige redactie", tagline="Onderwijskundige redactie", illu="wat"),
    dict(path="wat/schrijven-van-educatieve-en-informatieve-tekst/", section="wat", title="Schrijven van educatieve en informatieve tekst", tagline="Schrijven van educatieve en informatieve tekst", illu="wat"),
    dict(path="wat/projectleiding-en-auteursmanagement/", section="wat", title="Projectleiding en auteursmanagement", tagline="Projectleiding en auteursmanagement", illu="wat"),
    dict(path="waarom/", section="waarom", title="Waarom Bureau Sproet?", tagline="Flexibel en betrokken", illu="waarom"),
    dict(path="voor-wie/", section="voor-wie", title="Opdrachtgevers", tagline="Bureau Sproet werkt samen met ...", illu="wat"),
    dict(path="contact/", section="contact", title="Contact", tagline="Bellen en mailen met Bureau Sproet", illu="contact",
         description="Bureau Sproet, Jansbuitensingel 7, 6811 AA Arnhem."),
    dict(path="privacyverklaring/", section="contact", title="Privacyverklaring", tagline="Privacyverklaring Bureau Sproet", illu="contact"),
]

HOME = dict(path="", section="home", title="Bureau Sproet - Redactiebureau voor uitgeefprojecten",
            tagline="Bureau Sproet - Redactiebureau voor uitgeefprojecten",
            description="Bureau Sproet is een redactiebureau voor uitgeefprojecten: tekst- en beeldredactie, webredactie en onderwijskundige redactie.")

# Oude Joomla-adressen -> nieuwe adressen (voor bestaande links en zoekmachines)
REDIRECTS = {
    "index.php/": "",
    "index.php/wie/": "wie/",
    "index.php/wie-inleiding/": "wie/",
    "index.php/g-anita-ter-hofte/": "wie/anita-ter-hofte/",
    "index.php/g-mariet-bosschers/": "wie/mariet-bosschers/",
    "index.php/g-hannebeth-haffmans/": "wie/hannebeth-haffmans/",
    "index.php/wat/": "wat/",
    "index.php/g-inleiding/": "wat/",
    "index.php/g-tekst-en-bureauredactie/": "wat/tekst-en-bureauredactie/",
    "index.php/g-beeldredactie/": "wat/beeldredactie/",
    "index.php/g-webredactie/": "wat/webredactie/",
    "index.php/g-werken-in-content-management-systeem/": "wat/redactie-in-een-cms/",
    "index.php/g-onderwijskundige-redactie/": "wat/onderwijskundige-redactie/",
    "index.php/g-schrijven-van-educatieve-en-informatieve-tekst/": "wat/schrijven-van-educatieve-en-informatieve-tekst/",
    "index.php/g-projectleiding-en-auteursmanagement/": "wat/projectleiding-en-auteursmanagement/",
    "index.php/waarom/": "waarom/",
    "index.php/voor-wie/": "voor-wie/",
    "index.php/contact/": "contact/",
}

e = html.escape


def rel_root(path):
    """Relatief pad van een pagina terug naar de hoofdmap, bv. 'wat/beeldredactie/' -> '../../'."""
    return "../" * path.count("/")


def mail_link(user):
    # Het adres staat niet letterlijk in de HTML; site.js maakt er een klikbare link van.
    return (f'<a class="mail" href="#" data-u="{e(user)}" data-d="{e(MAIL_DOMAIN)}" '
            f'data-s="{e(MAIL_SUBJECT)}">{e(user)} [at] {e(MAIL_DOMAIN)}</a>')


def render_content(text, root):
    out = text.replace("{{root}}", root)
    while "{{mail:" in out:
        start = out.index("{{mail:")
        end = out.index("}}", start)
        out = out[:start] + mail_link(out[start + 7:end]) + out[end + 2:]
    return out


def head(page, root, extra=""):
    title = page["title"] if page["section"] == "home" else f'{page["title"]} | {SITE_NAME}'
    desc = page.get("description") or f'{page["title"]} - {SITE_NAME}, redactiebureau voor uitgeefprojecten.'
    return f"""<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; img-src 'self' data:; script-src 'self'; style-src 'self'; base-uri 'none'; form-action 'none'">
<meta name="referrer" content="strict-origin-when-cross-origin">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{SITE_URL}/{page['path']}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:title" content="{e(page['title'])}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{SITE_URL}/{page['path']}">
<meta property="og:image" content="{SITE_URL}/assets/img/home_logo.png">
<meta name="theme-color" content="#E2001A">
<link rel="icon" href="{root}assets/img/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{root}assets/img/home_logo.png">
<link rel="stylesheet" href="{root}assets/css/site.css">
<script src="{root}assets/js/site.js" defer></script>
{extra}</head>"""


def header(page, root):
    items = []
    for section, label, path in MAIN_MENU:
        current = ' aria-current="page"' if page["section"] == section and page["path"] == path else (
            ' class="active"' if page["section"] == section else "")
        items.append(f'<li><a href="{root}{path}"{current}>{e(label)}</a></li>')
    brand = "" if page["section"] == "home" else (
        f'<a class="brand" href="{root}"><img src="{root}assets/img/logo.png" width="103" height="65" '
        f'alt="Bureau Sproet - naar de homepage"></a>')
    return f"""<a class="skip" href="#inhoud">Naar de inhoud</a>
<header class="site-header">
  {brand}
  <nav class="mainnav" aria-label="Hoofdmenu">
    <ul>
      {"".join(items)}
    </ul>
  </nav>
</header>"""


def subnav(page, root):
    if page["section"] not in SUB_MENUS:
        return ""
    heading, entries = SUB_MENUS[page["section"]]
    items = []
    for label, path in entries:
        current = ' aria-current="page"' if path == page["path"] else ""
        items.append(f'<li><a href="{root}{path}"{current}>{e(label)}</a></li>')
    return f"""<nav class="subnav" aria-label="{e(heading)}">
      <h2>{e(heading)}</h2>
      <ul>
        {"".join(items)}
      </ul>
    </nav>"""


def illustration(page, root):
    name = page.get("illu")
    if not name:
        return ""
    file, w, h, align = ILLUSTRATIONS[name]
    return (f'<div class="illu illu-{align}"><img src="{root}assets/img/{file}" width="{w}" height="{h}" '
            f'alt="" loading="lazy"></div>')


def footer(page, root):
    tag = "h1" if page["section"] == "home" else "p"
    return f"""<footer class="site-footer">
  <{tag} class="tagline">{e(page["tagline"])}</{tag}>
  <p class="colofon">Bureau Sproet &middot; Jansbuitensingel 7, 6811 AA Arnhem &middot; KvK 08174607 &middot;
    <a href="{root}privacyverklaring/">Privacyverklaring</a></p>
</footer>"""


def render_page(page):
    root = rel_root(page["path"])
    body = render_content((CONTENT / (page["path"].rstrip("/") + ".html")).read_text(encoding="utf-8"), root)
    has_sub = page["section"] in SUB_MENUS
    return f"""{head(page, root)}
<body>
{header(page, root)}
<main id="inhoud" class="panel">
  <div class="cols{' has-sub' if has_sub else ''}">
    <article class="content">
{body}
    </article>
    {subnav(page, root)}
  </div>
  {illustration(page, root)}
</main>
{footer(page, root)}
</body>
</html>
"""


def render_home():
    root = ""
    tiles = "\n    ".join(
        f'<img src="assets/img/home_bg{i}.jpg" width="445" height="260" alt="">' for i in range(1, 5))
    return f"""{head(HOME, root)}
<body class="home">
{header(HOME, root)}
<main id="inhoud" class="panel">
  <div class="mosaic">
    {tiles}
    <img class="mosaic-logo" src="assets/img/home_logo.png" width="191" height="127" alt="Bureau Sproet">
  </div>
</main>
{footer(HOME, root)}
</body>
</html>
"""


def render_redirect(old, new):
    root = rel_root(old)
    return f"""<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<title>Doorverwijzing | {SITE_NAME}</title>
<meta name="robots" content="noindex">
<link rel="canonical" href="{SITE_URL}/{new}">
<meta http-equiv="refresh" content="0; url={root}{new}">
</head>
<body>
<p>Deze pagina is verhuisd naar <a href="{root}{new}">{SITE_URL}/{new}</a>.</p>
</body>
</html>
"""


def render_404():
    # Een 404-pagina kan op elk adres verschijnen, daarom absolute paden.
    page = dict(path="404.html", section="", title="Pagina niet gevonden", tagline="Pagina niet gevonden")
    content = """<h1>Pagina niet gevonden</h1>
<p>Deze pagina bestaat niet (meer). Ga naar de <a href="/">homepage</a> of bekijk
<a href="/wat/">wat Bureau Sproet doet</a>.</p>"""
    html_out = render_page_from(page, content, root="/")
    return html_out.replace('<link rel="canonical" href="https://www.bureausproet.nl/404.html">',
                            '<meta name="robots" content="noindex">')


def render_page_from(page, content, root):
    return f"""{head(page, root)}
<body>
{header(page, root)}
<main id="inhoud" class="panel">
  <div class="cols">
    <article class="content">
{content}
    </article>
  </div>
</main>
{footer(page, root)}
</body>
</html>
"""


def write(rel, text):
    target = OUT / rel
    if rel == "" or rel.endswith("/"):
        target = target / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8", newline="\n")


def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(STATIC, OUT)

    write("", render_home())
    for page in PAGES:
        write(page["path"], render_page(page))
    for old, new in REDIRECTS.items():
        write(old, render_redirect(old, new))
    write("404.html", render_404())

    urls = [""] + [p["path"] for p in PAGES]
    sitemap = "\n".join(f"  <url><loc>{SITE_URL}/{u}</loc></url>" for u in urls)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n'
                         f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sitemap}\n</urlset>\n')
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
    write(".nojekyll", "")

    count = sum(1 for _ in OUT.rglob("*.html"))
    print(f"Klaar: {count} HTML-bestanden in {OUT}")


def serve(port=8000):
    import functools
    import http.server

    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(OUT))
    with http.server.ThreadingHTTPServer(("127.0.0.1", port), handler) as httpd:
        print(f"Bekijk de site op http://localhost:{port}/  (stoppen met Ctrl+C)")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    os.chdir(ROOT)
    build()
    if "--serve" in sys.argv:
        serve()
