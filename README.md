# Monitoring — Actieplan Managementletter 2025

Online statusdashboard voor de opvolging van de bevindingen uit de
managementletter 2025 van **Concern voor Werk**. Bedoeld om derden inzicht te
geven in de voortgang van de verschillende acties/projecten.

## 🔗 Online bekijken

Na publicatie staat het dashboard op:

> https://dgoudbeek-cmyk.github.io/managementletter-monitor-2025/

Publiceren gebeurt automatisch via GitHub Pages bij elke push naar de
publicatiebranch (zie [`.github/workflows/deploy-pages.yml`](.github/workflows/deploy-pages.yml)).

## 📁 Structuur

| Bestand | Doel |
|---------|------|
| `index.html` | Het dashboard (HTML/CSS/JS, geen afhankelijkheden, geen build nodig). |
| `data.js` | **De gedeelde bron van waarheid**: alle acties met status, notities en metadata. |
| `.github/workflows/deploy-pages.yml` | Publiceert automatisch naar GitHub Pages. |

De status die bezoekers zien komt **uitsluitend** uit `data.js`. Wijzigingen zijn
dus voor iedereen gelijk en versiebeheerd — niet per browser.

## ✏️ Status bijwerken

Er zijn twee manieren. **Manier 1 is de makkelijkste.**

### 1. Via de bewerkmodus in het dashboard (aanbevolen)

1. Open het dashboard en klik rechtsboven in de werkbalk op **“Bewerken”**.
2. Pas per actie de status aan (Niet gestart / Opgestart / Afgerond) en vul een
   **voortgangsnotitie** in. De datum “laatst bijgewerkt” wordt automatisch gezet.
3. Klik op **“Exporteer data.js”** — er wordt een nieuw `data.js` gedownload.
4. Vervang het `data.js` in deze repo door de download en **commit** het.
   Bij de push publiceert GitHub Pages automatisch de nieuwe stand.

> Wijzigingen in de bewerkmodus staan lokaal in jouw browser tot je ze
> exporteert en commit. Een knop “Wijzigingen wissen” zet alles terug naar de
> gepubliceerde stand.

### 2. Handmatig in `data.js`

Pas per actie de velden `status`, `notitie` en `bijgewerkt` aan en commit.

## 🧱 Datamodel (`data.js`)

Elke actie is een object met deze velden:

| Veld | Betekenis |
|------|-----------|
| `id` | Uniek nummer, bv. `P01`. |
| `thema` | Korte titel van de actie. |
| `entiteit` | `NV`, `Gemeente`, `GR`, `GR / NV` of `Keten`. |
| `prioriteit` | `Hoog`, `Middel` of `Laag`. |
| `bron` | Verwijzing naar de bevinding in de managementletter. |
| `owner` | Verantwoordelijke(n). |
| `deadline` | `JJJJ-MM-DD` of vrije tekst (bv. `Direct (doorlopend)`). |
| `status` | `Open` (= Niet gestart), `Opgestart` of `Afgerond`. |
| `bijgewerkt` | Datum laatste statuswijziging (`JJJJ-MM-DD`). |
| `notitie` | Voortgangsnotitie (zichtbaar bij ‘Toon details’). |
| `bevinding` / `risico` / `actie` / `eersteStap` / `kpi` | Inhoudelijke toelichting. |

`window.MONITOR_CONFIG` bovenin `data.js` bevat titel, subtitel, peildatum en
accentkleur van het dashboard.

## 💻 Lokaal bekijken

Omdat `index.html` `data.js` via een `<script>` laadt, open je het via een
mini-webserver (niet rechtstreeks als bestand):

```bash
python3 -m http.server 8000
# open http://localhost:8000
```
