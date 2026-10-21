# Bureau Sproet – statische website

Statische, responsive herbouw van www.bureausproet.nl (voorheen Joomla).
Geen database, geen PHP, geen cookies, geen externe scripts of lettertypes.

## Lokaal bekijken

```
python build.py --serve
```

Open daarna http://localhost:8000/. Je hebt alleen Python 3.8+ nodig.

## Teksten aanpassen

- Paginateksten staan als HTML-fragmenten in `content/` (bv. `content/wat/beeldredactie.html`).
- Menu's, paginatitels, de tekst in de rode balk en de illustraties staan bovenin `build.py`.
- Stijl: `static/assets/css/site.css`. Afbeeldingen: `static/assets/img/`.
- Draai daarna `python build.py`; het resultaat staat in `public/`.

In de content kun je `{{mail:anita}}` gebruiken voor een (tegen spambots verborgen) e-mailadres
en `{{root}}` aan het begin van interne links (`<a href="{{root}}contact/">`).

## Publiceren

**GitHub Pages:** push naar `main` in een GitHub-repository en zet onder
*Settings → Pages → Source* de optie op **GitHub Actions**. De workflow in
`.github/workflows/pages.yml` bouwt en publiceert de site automatisch.

**Elke andere webserver (Synology, Greenhost, Codeberg, …):** draai `python build.py`
en kopieer de inhoud van `public/` naar de webmap.

Oude Joomla-adressen (`/index.php/...`) verwijzen automatisch door naar de nieuwe adressen.
