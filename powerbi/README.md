# Power BI — Financiële managementrapportage (Exact Online Premium)

Model + rapport voor de live financiële managementrapportage van Concern voor
Werk, gevoed vanuit **Exact Online Premium** via de **Exact Online Premium-connector**
(`ExactOnlinePremium.Contents()`).

Je krijgt hetzelfde resultaat via twee routes:

1. **PBIP-project openen** (`pbip/Managementrapportage.pbip`) — aanbevolen; Power BI
   Desktop bouwt hier zelf een `.pbix` van.
2. **Plak-methode** — model in ~10 minuten handmatig opbouwen uit de bronbestanden
   in [`src/`](src/). Werkt gegarandeerd op elke Power BI Desktop-versie.

> **Waarom geen kant-en-klaar `.pbix` of `.pbit`?**
> Een `.pbix`/`.pbit` met ingebouwd datamodel bevat een binair *DataMashup*-onderdeel
> dat álléén Power BI Desktop zelf kan wegschrijven (Windows-only engine). Zonder dat
> onderdeel weigert Power BI het bestand ("versleuteld of beschadigd"). Daarom leveren
> we het model als **PBIP** (tekst-gebaseerd bronformaat, M-code zit ín het model) en
> als losse M/DAX-bronbestanden. Beide monden uit in een gewoon, live-verversbaar
> `.pbix` dat je zelf één keer opslaat.

## 📦 Wat zit erin

| Onderdeel | Inhoud |
|-----------|--------|
| **Bron** | Exact Online Premium-connector — `ExactOnlinePremium.Contents()`. Geen URL of parameters nodig; Power BI vraagt alleen éénmalig om in te loggen. |
| **Tabellen** | `GLAccounts` (grootboekrekeningen), `ReportingBalance` (saldi per periode) en `Perioden` (boekjaar/periode-dimensie). |
| **Relaties** | `ReportingBalance[GLAccount]` → `GLAccounts[ID]` (GUID) en `ReportingBalance[PeriodeKey]` → `Perioden[PeriodeKey]`. |
| **Measures** | Omzet, Kosten, Resultaat, Resultaatmarge %, Totaal activa, Totaal passiva, Liquide middelen, Aantal boekingen. |
| **Pagina's** | *Managementoverzicht* (KPI-kaarten, resultaat per periode, resultaat per categorie, administratie-slicer) en *Balans & liquiditeit*. |

Enkele keuzes die op de **Exact Online Premium**-inrichting zijn afgestemd:

- Het bedrag komt uit `AmountDCDebit − AmountDCCredit` (netto in eigen valuta, debet
  positief). De measures draaien opbrengsten en passiva met `-1` zodat ze positief tonen.
- Het rekeningnummer staat in `SearchCode`; de koppeling loopt via de GUID (`ID` /
  `GLAccount`).
- Premium heeft geen `TypeDescription`; er wordt een **Categorie** afgeleid
  (Opbrengsten / Kosten / Activa / Passiva) uit `BalanceType` + `BalanceSide`.
- De database bevat meerdere administraties (`Division`); daarom staat er een
  **Administratie-slicer** op pagina 1 om per administratie te filteren.

## 🚀 Route 1 — PBIP-project openen (aanbevolen)

1. Eenmalig in Power BI Desktop: **Bestand → Opties → Preview-functies →** zet
   **“Power BI Project (.pbip) opslagopties”** aan en herstart Desktop.
2. **Bestand → Openen** → kies [`pbip/Managementrapportage.pbip`](pbip/Managementrapportage.pbip).
3. Power BI vraagt om in te loggen bij de Exact Online Premium-connector (zoals je
   gewend bent). Dat is alles — er zijn geen parameters.
4. Het model laadt de data en de pagina's vullen zich. Kies eventueel een
   administratie in de slicer rechtsboven.
5. **Bestand → Opslaan als → `.pbix`**. Klaar — dit is je live rapport.
6. **Publiceren** naar de Power BI-service en daar een **geplande vernieuwing**
   instellen voor de live-actualisatie.

## 🩹 Route 2 — Plak-methode (gegarandeerd, ±10 min)

Alle logica staat kant-en-klaar in `src/`:

1. Nieuw, leeg `.pbix` → **Gegevens ophalen → Exact Online Premium** (jullie connector),
   inloggen, en desnoods één tabel laden om de verbinding te leggen.
2. Plak per query de inhoud van de `.m`-bestanden in de **Geavanceerde editor**
   (Start → Nieuwe bron → Lege query → Geavanceerde editor):
   [`src/queries/GLAccounts.m`](src/queries/GLAccounts.m),
   [`src/queries/ReportingBalance.m`](src/queries/ReportingBalance.m),
   [`src/queries/Perioden.m`](src/queries/Perioden.m).
3. **Sluiten & toepassen.** Leg in de modelweergave de twee relaties uit de tabel
   hierboven.
4. Neem de measures over uit [`src/measures.dax`](src/measures.dax) (naam +
   expressie + notatie).
5. Bouw de visuals; opslaan als `.pbix`.

## 🔧 Aanpassen aan jullie omgeving

De queries staan als leesbare bronbestanden in [`src/`](src/). Aandachtspunten:

- **Liquide middelen.** De measure filtert op Exact-rekeningtype `10` (kas) en `12`
  (bank). Kloppen die typecodes in jullie schema niet, pas dan het filter in
  `measures.dax` aan (bijv. op een reeks `SearchCode`-nummers).
- **Boekjaarbereik.** `Perioden.m` genereert de jaren `2023..2028`; pas dit bereik
  aan als je verder terug of vooruit wilt.
- **Consolidatie vs. één administratie.** Zonder selectie in de slicer tellen de
  measures álle administraties bij elkaar op. Wil je standaard één administratie,
  zet dan een filter op `Division`.

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
