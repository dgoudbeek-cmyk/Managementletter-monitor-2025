# Power BI — Financiële managementrapportage (Exact Online via Invantive)

Een **Power BI-template** (`.pbit`) voor de live financiële managementrapportage van
Concern voor Werk, gevoed vanuit **Exact Online (Premium)** via de **Invantive
Bridge Online**-connector.

> **Waarom een `.pbit` en geen `.pbix`?**
> Een volledig `.pbix` met ingebouwd (gecomprimeerd) datamodel kan alléén Power BI
> Desktop zelf wegschrijven — die engine is Windows-only. Een `.pbit` bevat exact
> hetzelfde model (queries, relaties, measures) en dezelfde rapportpagina's, maar
> nog zónder ingeladen data. Je opent het template één keer in Power BI Desktop,
> vult je gegevens in, en slaat het op als `.pbix`. Vanaf dat moment is het een
> gewoon, live-verversbaar rapport.

## 📦 Wat zit erin

| Onderdeel | Inhoud |
|-----------|--------|
| **Parameters** | `BridgeUrl` (OData-URL van je Invantive Bridge Online) en `Division` (Exact administratie-/divisiecode). Worden bij openen gevraagd. |
| **Tabellen** | `GLAccounts` (grootboekrekeningen), `ReportingBalance` (saldi per periode) en `Perioden` (boekjaar/periode-dimensie). |
| **Relaties** | `ReportingBalance` → `GLAccounts` (op rekeningcode) en `ReportingBalance` → `Perioden` (op periode-sleutel). |
| **Measures** | Omzet, Kosten, Resultaat, Resultaatmarge %, Totaal activa, Totaal passiva, Liquide middelen, Aantal boekingen. |
| **Pagina's** | *Managementoverzicht* (KPI-kaarten, resultaat per periode, resultaat per grootboekcategorie) en *Balans & liquiditeit*. |

Waarom `ReportingBalance` en niet `TransactionLines`? `ReportingBalance` is in Exact
al voorgeaggregeerd tot één saldo per rekening/jaar/periode. Dat is ordes van
grootte lichter dan alle journaalregels en ruim voldoende voor een
management-dashboard. Wil je later inzoomen op detail, dan voeg je `TransactionLines`
toe als extra tabel.

## 🚀 Openen en als `.pbix` opslaan

1. Open `Managementrapportage-Exact-Online.pbit` in **Power BI Desktop**.
2. Vul de parameters in:
   - **BridgeUrl** — de OData-URL van jullie Invantive Bridge Online, bijv.
     `https://bridge-online.cloud/uwbedrijf`.
   - **Division** — de Exact Online administratie-/divisiecode (bijv. `3000000`).
3. Power BI vraagt om inloggegevens voor de bron. Kies de authenticatiemethode die
   bij jullie Invantive Bridge hoort (meestal **Basic** of **Web API / OAuth**) en
   log in.
4. Het model laadt de data en de rapportpagina's vullen zich.
5. **Bestand → Opslaan als → `.pbix`**. Klaar — dit is je live rapport.
6. Publiceren naar de Power BI-service kan daarna via **Publiceren**; stel daar een
   geplande vernieuwing (scheduled refresh) in voor de live-actualisatie.

## 🔧 Aanpassen aan jullie omgeving

De queries staan als leesbare bronbestanden in [`src/`](src/):

- [`src/queries/GLAccounts.m`](src/queries/GLAccounts.m)
- [`src/queries/ReportingBalance.m`](src/queries/ReportingBalance.m)
- [`src/queries/Perioden.m`](src/queries/Perioden.m)
- [`src/measures.dax`](src/measures.dax)

Let op deze punten, die per Exact/Invantive-inrichting kunnen verschillen:

- **Entiteitsnamen.** De queries navigeren naar `GLAccounts` en `ReportingBalance`
  in de OData-feed. Heten die entiteiten in jullie Bridge anders (bijv.
  `ExactOnlineREST.Financial.ReportingBalance`), pas dan de regel
  `Bron{[Name="…"]}[Data]` aan.
- **Divisiefilter.** Bakent jullie Bridge de administratie al af, dan is de kolom
  `Division` er mogelijk niet en kun je de `Administratie`-stap weglaten.
- **Liquide middelen.** De measure filtert op Exact-rekeningtype `10` (kas) en `12`
  (bank). Wijkt jullie rekeningschema af, pas dan het filter in `measures.dax` aan
  (bijv. op een reeks rekeningcodes).
- **Tekenconventie.** Exact boekt debet positief en credit negatief. De measures
  draaien opbrengsten en passiva daarom met `-1` zodat ze positief tonen.

Na het wijzigen van een bronbestand herbouw je het template met:

```bash
python3 build_pbit.py
```

## 🩹 Fallback — het model in 10 minuten handmatig opbouwen

Weigert jouw Power BI Desktop-versie het template te openen? Dan bouw je hetzelfde
model rechtstreeks op; alle logica staat kant-en-klaar in `src/`:

1. Nieuw, leeg `.pbix` → **Gegevens ophalen → Lege query**.
2. Maak twee parameters aan (**Beheer parameters**): `BridgeUrl` en `Division` (tekst).
3. Plak per query de inhoud van de `.m`-bestanden in de **Geavanceerde editor**
   (Start → Nieuwe bron → Lege query → Geavanceerde editor).
4. **Sluiten & toepassen.** Leg in de modelweergave de twee relaties uit de tabel
   hierboven.
5. Maak de measures aan door de blokken uit `measures.dax` over te nemen (naam +
   expressie + notatie).
6. Bouw de visuals; opslaan als `.pbix`.

## 🗂️ Bestanden

| Bestand | Doel |
|---------|------|
| `Managementrapportage-Exact-Online.pbit` | Het Power BI-template (openen in Power BI Desktop). |
| `build_pbit.py` | Stelt het `.pbit` reproduceerbaar samen uit `src/`. |
| `src/queries/*.m` | De Power Query (M) bronqueries. |
| `src/measures.dax` | De DAX-measures. |
