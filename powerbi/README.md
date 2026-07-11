# Power BI — Financiële managementrapportage (Exact Online via Invantive)

Model + rapport voor de live financiële managementrapportage van Concern voor
Werk, gevoed vanuit **Exact Online (Premium)** via de **Invantive Bridge
Online**-connector.

Je krijgt hetzelfde resultaat via twee routes:

1. **PBIP-project openen** (`pbip/Managementrapportage.pbip`) — aanbevolen; Power BI
   Desktop bouwt hier zelf een `.pbix` van.
2. **Plak-methode** — model in ~10 minuten handmatig opbouwen uit de bronbestanden
   in [`src/`](src/). Werkt gegarandeerd op elke Power BI Desktop-versie.

> **Waarom geen kant-en-klaar `.pbix` of `.pbit`?**
> Een `.pbix`/`.pbit` met ingebouwd datamodel bevat een binair *DataMashup*-onderdeel
> dat álléén Power BI Desktop zelf kan wegschrijven (Windows-only engine). Zonder dat
> onderdeel weigert Power BI het bestand ("versleuteld of beschadigd"). Daarom leveren
> we het model als **PBIP** (tekst-gebaseerd bronformaat, M-code zit ín het model —
> géén DataMashup nodig) en als losse M/DAX-bronbestanden. Beide monden uit in een
> gewoon, live-verversbaar `.pbix` dat je zelf één keer opslaat.

## 📦 Wat zit erin

| Onderdeel | Inhoud |
|-----------|--------|
| **Parameters** | `BridgeUrl` (OData-URL van je Invantive Bridge Online) en `Division` (Exact administratie-/divisiecode). Worden bij openen gevraagd. |
| **Tabellen** | `GLAccounts` (grootboekrekeningen), `ReportingBalance` (saldi per periode) en `Perioden` (boekjaar/periode-dimensie). |
| **Relaties** | `ReportingBalance` → `GLAccounts` (op rekeningcode) en `ReportingBalance` → `Perioden` (op periode-sleutel). |
| **Measures** | Omzet, Kosten, Resultaat, Resultaatmarge %, Totaal activa, Totaal passiva, Liquide middelen, Aantal boekingen. |
| **Pagina's** | *Managementoverzicht* (KPI-kaarten, resultaat per periode, resultaat per grootboekcategorie) en *Balans & liquiditeit*. |

Waarom `ReportingBalance` en niet `TransactionLines`? `ReportingBalance` is in Exact
al voorgeaggregeerd tot één saldo per rekening/jaar/periode — ordes van grootte
lichter dan alle journaalregels en ruim voldoende voor een management-dashboard.

## 🚀 Route 1 — PBIP-project openen (aanbevolen)

1. Eenmalig in Power BI Desktop: **Bestand → Opties → Preview-functies →** zet
   **“Power BI Project (.pbip) opslagopties”** aan en herstart Desktop.
2. **Bestand → Openen** → kies [`pbip/Managementrapportage.pbip`](pbip/Managementrapportage.pbip).
3. Vul de parameters in:
   - **BridgeUrl** — de OData-URL van jullie Invantive Bridge Online, bijv.
     `https://bridge-online.cloud/uwbedrijf`.
   - **Division** — de Exact Online administratie-/divisiecode (bijv. `3000000`).
4. Power BI vraagt om inloggegevens voor de bron. Kies de methode die bij jullie
   Bridge hoort (meestal **Basic** of **Web API / OAuth**) en log in.
5. Het model laadt de data en de pagina's vullen zich.
6. **Bestand → Opslaan als → `.pbix`**. Klaar — dit is je live rapport.
7. **Publiceren** naar de Power BI-service en daar een **geplande vernieuwing**
   instellen voor de live-actualisatie.

## 🩹 Route 2 — Plak-methode (gegarandeerd, ±10 min)

Alle logica staat kant-en-klaar in `src/`:

1. Nieuw, leeg `.pbix` → **Gegevens ophalen → Lege query**.
2. **Beheer parameters** → maak `BridgeUrl` en `Division` aan (beide type tekst).
3. Plak per query de inhoud van de `.m`-bestanden in de **Geavanceerde editor**
   (Start → Nieuwe bron → Lege query → Geavanceerde editor):
   [`src/queries/GLAccounts.m`](src/queries/GLAccounts.m),
   [`src/queries/ReportingBalance.m`](src/queries/ReportingBalance.m),
   [`src/queries/Perioden.m`](src/queries/Perioden.m).
4. **Sluiten & toepassen.** Leg in de modelweergave de twee relaties uit de tabel
   hierboven.
5. Neem de measures over uit [`src/measures.dax`](src/measures.dax) (naam +
   expressie + notatie).
6. Bouw de visuals; opslaan als `.pbix`.

## 🔧 Aanpassen aan jullie omgeving

De queries staan als leesbare bronbestanden in [`src/`](src/). Let op deze punten,
die per Exact/Invantive-inrichting kunnen verschillen:

- **Entiteitsnamen.** De queries navigeren naar `GLAccounts` en `ReportingBalance`
  in de OData-feed. Heten die entiteiten in jullie Bridge anders (bijv.
  `ExactOnlineREST.Financial.ReportingBalance`), pas dan de regel
  `Bron{[Name="…"]}[Data]` aan.
- **Divisiefilter.** Bakent jullie Bridge de administratie al af, dan is de kolom
  `Division` er mogelijk niet en kun je de `Administratie`-stap weglaten.
- **Liquide middelen.** De measure filtert op Exact-rekeningtype `10` (kas) en `12`
  (bank). Wijkt jullie rekeningschema af, pas dan het filter in `measures.dax` aan.
- **Tekenconventie.** Exact boekt debet positief en credit negatief. De measures
  draaien opbrengsten en passiva daarom met `-1` zodat ze positief tonen.

Na het wijzigen van een bronbestand herbouw je het PBIP-project met:

```bash
python3 build_pbip.py
```

## 🗂️ Bestanden

| Bestand | Doel |
|---------|------|
| `pbip/Managementrapportage.pbip` | Het PBIP-project (openen in Power BI Desktop). |
| `pbip/Managementrapportage.SemanticModel/` | Het datamodel (model.bim = tabellen, M-queries, relaties, measures). |
| `pbip/Managementrapportage.Report/` | De rapportpagina's. |
| `build_pbip.py` | Stelt het PBIP-project reproduceerbaar samen uit `src/`. |
| `build_pbit.py` | Bouwt het model/rapport (wordt door `build_pbip.py` hergebruikt). |
| `src/queries/*.m` | De Power Query (M) bronqueries. |
| `src/measures.dax` | De DAX-measures. |
