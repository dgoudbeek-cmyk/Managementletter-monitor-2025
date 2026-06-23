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

`data.js` bevat de **vaste** inhoud (themas, deadlines, bevindingen, owners). De
**status, voortgangsnotities en gekoppelde documenten** worden real-time gedeeld
via een Supabase-database — wijzigingen zijn meteen voor alle kijkers zichtbaar,
zonder verversen en zonder commit.

## ✏️ Status bijwerken (real-time)

1. Open het dashboard en klik rechtsboven in de werkbalk op **“Bewerken”**.
2. Pas per actie de status aan (Niet gestart / Opgestart / Afgerond), vul een
   **voortgangsnotitie** in of koppel een document.
3. Klaar — meer niet. Elke wijziging wordt **automatisch opgeslagen** in de
   database en is direct zichtbaar voor iedereen die het dashboard openheeft.
   De badge rechtsboven toont **Live** als de verbinding actief is.

> “Back-up exporteren” downloadt desgewenst een momentopname als `data.js`.

## 🗄️ Database (Supabase)

De gedeelde status staat in de tabel `acties_status` in een gratis Supabase-
project. Configuratie (project-URL + publishable key) staat boven in het
`<script>` van `index.html`. De tabel:

| Kolom | Type | Betekenis |
|-------|------|-----------|
| `id` | text (PK) | Actie-id, bv. `P01`. |
| `status` | text | `Open` / `Opgestart` / `Afgerond`. |
| `notitie` | text | Voortgangsnotitie. |
| `links` | jsonb | Gekoppelde documenten `[{label,url}]`. |
| `bijgewerkt` | date | Datum laatste wijziging. |
| `updated_at` | timestamptz | Technische tijdstempel. |

Realtime staat aan op deze tabel; het dashboard valt terug op de laatst bekende
stand (lokale cache) als de verbinding wegvalt.

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
