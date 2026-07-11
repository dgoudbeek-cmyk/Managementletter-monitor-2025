#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bouwt een Power BI-template (.pbit) voor de financiele managementrapportage van
Concern voor Werk, gevoed vanuit Exact Online (Premium) via Invantive Bridge Online.

Het script stelt een geldig OPC/ZIP-pakket samen met de vier kernonderdelen:
  - [Content_Types].xml   (UTF-8)
  - Version               (UTF-16 LE)
  - DataModelSchema       (UTF-16 LE)  -> tabellen, M-queries, relaties, measures
  - Report/Layout         (UTF-16 LE)  -> rapportpagina's met visuals
Plus benigne, lege Settings/Metadata-onderdelen.

De M-queries en DAX-measures worden uit ./src ingelezen, zodat die bestanden de
enige bron van waarheid zijn (en los te (her)gebruiken zijn via de "plak"-methode
uit de README).

Gebruik:  python3 build_pbit.py
Resultaat: ./Managementrapportage-Exact-Online.pbit
"""

import codecs
import json
import os
import re
import uuid
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
OUT = os.path.join(HERE, "Managementrapportage-Exact-Online.pbit")

BOM = codecs.BOM_UTF16_LE


def read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def m_query(name):
    """Lees een .m-bestand en strip commentaarregels aan de kop (blijven leesbaar in PBI)."""
    return read(os.path.join(SRC, "queries", name + ".m")).rstrip("\n")


def parse_measures(text):
    """Parse measures.dax: blokken '// == <naam> | <formatstring>' gevolgd door DAX."""
    measures = []
    blocks = re.split(r"(?m)^//\s*==\s*", text)
    for block in blocks[1:]:
        header, _, body = block.partition("\n")
        name, _, fmt = header.partition("|")
        name = name.strip()
        fmt = fmt.strip()
        # Verwijder de 'Naam =' toewijzingsregel; PBI bewaart alleen de expressie.
        lines = body.split("\n")
        expr_lines = []
        started = False
        for ln in lines:
            if not started:
                if re.match(r"^\s*" + re.escape(name).replace(r"\ ", " ") + r"\s*=\s*$", ln) \
                        or re.match(r"^.*=\s*$", ln) and not expr_lines:
                    started = True
                    continue
            expr_lines.append(ln)
        expr = "\n".join(expr_lines).strip()
        if name and expr:
            measures.append((name, expr, fmt))
    return measures


# ---------------------------------------------------------------------------
# Bronnen inlezen
# ---------------------------------------------------------------------------
GL_M = m_query("GLAccounts")
RB_M = m_query("ReportingBalance")
PER_M = m_query("Perioden")
MEASURES = parse_measures(read(os.path.join(SRC, "measures.dax")))


# ---------------------------------------------------------------------------
# Parameters (worden bij openen van het template opgevraagd)
# ---------------------------------------------------------------------------
PARAM_BRIDGE_DEFAULT = "https://bridge-online.cloud/uwbedrijf"
PARAM_DIVISION_DEFAULT = "3000000"


def col(name, dtype, summarize="none", sort_by=None, hidden=False):
    c = {"name": name, "dataType": dtype, "sourceColumn": name, "summarizeBy": summarize}
    if sort_by:
        c["sortByColumn"] = sort_by
    if hidden:
        c["isHidden"] = True
    return c


# ---------------------------------------------------------------------------
# DataModelSchema (TMSL, enhanced metadata / powerBI_V3)
# ---------------------------------------------------------------------------
def build_model():
    tables = [
        {
            "name": "GLAccounts",
            "columns": [
                col("ID", "string", hidden=True),
                col("Code", "string"),
                col("Description", "string"),
                col("BalanceSide", "string"),
                col("BalanceType", "string"),
                col("Type", "int64"),
                col("TypeDescription", "string"),
            ],
            "partitions": [{
                "name": "GLAccounts",
                "mode": "import",
                "source": {"type": "m", "expression": GL_M},
            }],
            "annotations": [{"name": "PBI_ResultType", "value": "Table"}],
        },
        {
            "name": "Perioden",
            "columns": [
                col("Boekjaar", "int64"),
                col("Periode", "int64"),
                col("PeriodeKey", "int64", hidden=True),
                col("PeriodeLabel", "string", sort_by="SorteerKey"),
                col("SorteerKey", "int64", hidden=True),
            ],
            "partitions": [{
                "name": "Perioden",
                "mode": "import",
                "source": {"type": "m", "expression": PER_M},
            }],
            "annotations": [{"name": "PBI_ResultType", "value": "Table"}],
        },
        {
            "name": "ReportingBalance",
            "columns": [
                col("Division", "int64", hidden=True),
                col("GLAccountCode", "string"),
                col("ReportingYear", "int64"),
                col("ReportingPeriod", "int64"),
                col("Amount", "double", summarize="sum"),
                col("Count", "int64", summarize="sum"),
                col("PeriodeKey", "int64", hidden=True),
            ],
            "partitions": [{
                "name": "ReportingBalance",
                "mode": "import",
                "source": {"type": "m", "expression": RB_M},
            }],
            "measures": [
                {"name": n, "expression": e, "formatString": f or "#,0"}
                for (n, e, f) in MEASURES
            ],
            "annotations": [{"name": "PBI_ResultType", "value": "Table"}],
        },
    ]

    relationships = [
        {
            "name": str(uuid.uuid4()),
            "fromTable": "ReportingBalance", "fromColumn": "GLAccountCode",
            "toTable": "GLAccounts", "toColumn": "Code",
            "crossFilteringBehavior": "oneDirection",
        },
        {
            "name": str(uuid.uuid4()),
            "fromTable": "ReportingBalance", "fromColumn": "PeriodeKey",
            "toTable": "Perioden", "toColumn": "PeriodeKey",
            "crossFilteringBehavior": "oneDirection",
        },
    ]

    expressions = [
        {
            "name": "BridgeUrl",
            "kind": "m",
            "expression": ('"%s" meta [IsParameterQuery=true, Type="Text", '
                           "IsParameterQueryRequired=true]" % PARAM_BRIDGE_DEFAULT),
            "annotations": [{"name": "PBI_NavigationStepName", "value": "Navigation"},
                            {"name": "PBI_ResultType", "value": "Text"}],
        },
        {
            "name": "Division",
            "kind": "m",
            "expression": ('"%s" meta [IsParameterQuery=true, Type="Text", '
                           "IsParameterQueryRequired=true]" % PARAM_DIVISION_DEFAULT),
            "annotations": [{"name": "PBI_NavigationStepName", "value": "Navigation"},
                            {"name": "PBI_ResultType", "value": "Text"}],
        },
    ]

    model = {
        "culture": "nl-NL",
        "dataAccessOptions": {"legacyRedirects": True, "returnErrorValuesAsNull": True},
        "defaultPowerBIDataSourceVersion": "powerBI_V3",
        "sourceQueryCulture": "nl-NL",
        "tables": tables,
        "relationships": relationships,
        "expressions": expressions,
        "annotations": [
            {"name": "PBI_QueryOrder",
             "value": json.dumps(["BridgeUrl", "Division", "GLAccounts",
                                  "ReportingBalance", "Perioden"])},
            {"name": "__PBI_TimeIntelligenceEnabled", "value": "0"},
            {"name": "PBIDesktopVersion", "value": "2.130.0.0"},
        ],
    }

    return {
        "name": str(uuid.uuid4()),
        "compatibilityLevel": 1567,
        "model": model,
    }


# ---------------------------------------------------------------------------
# Report/Layout
# ---------------------------------------------------------------------------
def cfg(obj):
    """Serialiseer een visual-/sectie-config naar de vereiste JSON-string."""
    return json.dumps(obj, ensure_ascii=False)


def textbox(x, y, w, h, text, size="20pt", bold=True):
    name = str(uuid.uuid4())
    conf = {
        "name": name,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "z": 0, "width": w, "height": h}}],
        "singleVisual": {
            "visualType": "textbox",
            "drillFilterOtherVisuals": True,
            "objects": {"general": [{"properties": {"paragraphs": [{
                "textRuns": [{
                    "value": text,
                    "textStyle": {"fontSize": size, "fontWeight": "bold" if bold else "normal",
                                  "color": "#D92B4A" if bold else "#333333"},
                }],
            }]}}]},
        },
    }
    return {"x": x, "y": y, "z": 0, "width": w, "height": h,
            "config": cfg(conf), "filters": "[]"}


def card(x, y, w, h, table, measure, title):
    name = str(uuid.uuid4())
    ref = "%s.%s" % (table, measure)
    conf = {
        "name": name,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "z": 0, "width": w, "height": h}}],
        "singleVisual": {
            "visualType": "card",
            "projections": {"Values": [{"queryRef": ref}]},
            "prototypeQuery": {
                "Version": 2,
                "From": [{"Name": "r", "Entity": table, "Type": 0}],
                "Select": [{
                    "Measure": {"Expression": {"SourceRef": {"Source": "r"}}, "Property": measure},
                    "Name": ref,
                }],
            },
            "objects": {"labels": [{"properties": {"color": [{"solid": {"color": {"expr": {"Literal": {"Value": "'#333333'"}}}}}]}}]},
            "vcObjects": {"title": [{"properties": {
                "show": {"expr": {"Literal": {"Value": "true"}}},
                "text": {"expr": {"Literal": {"Value": "'%s'" % title.replace("'", "")}}},
            }}]},
            "drillFilterOtherVisuals": True,
        },
    }
    return {"x": x, "y": y, "z": 0, "width": w, "height": h,
            "config": cfg(conf), "filters": "[]"}


def column_chart(x, y, w, h, cat_table, cat_col, val_table, measure, title):
    name = str(uuid.uuid4())
    cref = "%s.%s" % (cat_table, cat_col)
    vref = "%s.%s" % (val_table, measure)
    conf = {
        "name": name,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "z": 0, "width": w, "height": h}}],
        "singleVisual": {
            "visualType": "clusteredColumnChart",
            "projections": {"Category": [{"queryRef": cref}], "Y": [{"queryRef": vref}]},
            "prototypeQuery": {
                "Version": 2,
                "From": [
                    {"Name": "c", "Entity": cat_table, "Type": 0},
                    {"Name": "v", "Entity": val_table, "Type": 0},
                ],
                "Select": [
                    {"Column": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": cat_col}, "Name": cref},
                    {"Measure": {"Expression": {"SourceRef": {"Source": "v"}}, "Property": measure}, "Name": vref},
                ],
                "OrderBy": [{"Direction": 1, "Expression": {"Column": {
                    "Expression": {"SourceRef": {"Source": "c"}}, "Property": cat_col}}}],
            },
            "vcObjects": {"title": [{"properties": {
                "show": {"expr": {"Literal": {"Value": "true"}}},
                "text": {"expr": {"Literal": {"Value": "'%s'" % title.replace("'", "")}}},
            }}]},
            "drillFilterOtherVisuals": True,
        },
    }
    return {"x": x, "y": y, "z": 0, "width": w, "height": h,
            "config": cfg(conf), "filters": "[]"}


def matrix(x, y, w, h, row_table, row_col, val_table, measures, title):
    name = str(uuid.uuid4())
    rref = "%s.%s" % (row_table, row_col)
    selects = [{"Column": {"Expression": {"SourceRef": {"Source": "g"}}, "Property": row_col}, "Name": rref}]
    values_proj = []
    for m in measures:
        vref = "%s.%s" % (val_table, m)
        selects.append({"Measure": {"Expression": {"SourceRef": {"Source": "v"}}, "Property": m}, "Name": vref})
        values_proj.append({"queryRef": vref})
    conf = {
        "name": name,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "z": 0, "width": w, "height": h}}],
        "singleVisual": {
            "visualType": "pivotTable",
            "projections": {"Rows": [{"queryRef": rref}], "Values": values_proj},
            "prototypeQuery": {
                "Version": 2,
                "From": [
                    {"Name": "g", "Entity": row_table, "Type": 0},
                    {"Name": "v", "Entity": val_table, "Type": 0},
                ],
                "Select": selects,
            },
            "vcObjects": {"title": [{"properties": {
                "show": {"expr": {"Literal": {"Value": "true"}}},
                "text": {"expr": {"Literal": {"Value": "'%s'" % title.replace("'", "")}}},
            }}]},
            "drillFilterOtherVisuals": True,
        },
    }
    return {"x": x, "y": y, "z": 0, "width": w, "height": h,
            "config": cfg(conf), "filters": "[]"}


def build_layout():
    # Pagina 1 — Managementoverzicht (W&V)
    page1 = {
        "name": "ReportSection_overzicht",
        "displayName": "Managementoverzicht",
        "filters": "[]",
        "ordinal": 0,
        "width": 1280,
        "height": 720,
        "displayOption": 1,
        "config": cfg({}),
        "visualContainers": [
            textbox(20, 12, 700, 44, "Managementrapportage — Concern voor Werk"),
            textbox(20, 52, 700, 28, "Resultaatontwikkeling · Exact Online (live)", size="11pt", bold=False),
            card(20, 96, 300, 120, "ReportingBalance", "Omzet", "Omzet"),
            card(330, 96, 300, 120, "ReportingBalance", "Kosten", "Kosten"),
            card(640, 96, 300, 120, "ReportingBalance", "Resultaat", "Resultaat"),
            card(950, 96, 310, 120, "ReportingBalance", "Resultaatmarge %", "Resultaatmarge"),
            column_chart(20, 232, 620, 460, "Perioden", "PeriodeLabel",
                         "ReportingBalance", "Resultaat", "Resultaat per periode"),
            matrix(660, 232, 600, 460, "GLAccounts", "TypeDescription",
                   "ReportingBalance", ["Omzet", "Kosten", "Resultaat"],
                   "Resultaat per grootboekcategorie"),
        ],
    }

    # Pagina 2 — Balans & liquiditeit
    page2 = {
        "name": "ReportSection_balans",
        "displayName": "Balans & liquiditeit",
        "filters": "[]",
        "ordinal": 1,
        "width": 1280,
        "height": 720,
        "displayOption": 1,
        "config": cfg({}),
        "visualContainers": [
            textbox(20, 12, 700, 44, "Balans & liquiditeit"),
            card(20, 80, 300, 120, "ReportingBalance", "Totaal activa", "Totaal activa"),
            card(330, 80, 300, 120, "ReportingBalance", "Totaal passiva", "Totaal passiva"),
            card(640, 80, 300, 120, "ReportingBalance", "Liquide middelen", "Liquide middelen"),
            card(950, 80, 310, 120, "ReportingBalance", "Aantal boekingen", "Aantal boekingen"),
            matrix(20, 216, 1240, 476, "GLAccounts", "Description",
                   "ReportingBalance", ["Totaal activa", "Totaal passiva"],
                   "Balansposten per grootboekrekening"),
        ],
    }

    return {
        "id": 0,
        "resourcePackages": [],
        "sections": [page1, page2],
        "config": cfg({
            "version": "5.43",
            "themeCollection": {"baseTheme": {"name": "CY24SU10"}},
            "activeSectionIndex": 0,
            "defaultDrillFilterOtherVisuals": True,
            "settings": {"useStylableVisualContainerHeader": True},
        }),
        "layoutOptimization": 0,
    }


# ---------------------------------------------------------------------------
# Pakket samenstellen
# ---------------------------------------------------------------------------
CONTENT_TYPES = (
    '<?xml version="1.0" encoding="utf-8"?>\r\n'
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    '<Default Extension="json" ContentType="" />'
    '<Override PartName="/Version" ContentType="" />'
    '<Override PartName="/DataModelSchema" ContentType="" />'
    '<Override PartName="/Report/Layout" ContentType="" />'
    '<Override PartName="/Settings" ContentType="" />'
    '<Override PartName="/Metadata" ContentType="" />'
    "</Types>"
)


def utf16(text):
    return BOM + text.encode("utf-16-le")


def main():
    model = build_model()
    layout = build_layout()

    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        # [Content_Types].xml -> UTF-8
        z.writestr("[Content_Types].xml", CONTENT_TYPES.encode("utf-8"))
        # Version -> UTF-16 LE
        z.writestr("Version", utf16("3.0"))
        # DataModelSchema -> UTF-16 LE
        z.writestr("DataModelSchema", utf16(json.dumps(model, ensure_ascii=False)))
        # Report/Layout -> UTF-16 LE
        z.writestr("Report/Layout", utf16(json.dumps(layout, ensure_ascii=False)))
        # Benigne, lege onderdelen
        z.writestr("Settings", utf16(json.dumps({})))
        z.writestr("Metadata", utf16(json.dumps({})))

    size = os.path.getsize(OUT)
    print("Geschreven: %s (%d bytes)" % (OUT, size))
    print("Measures: %s" % ", ".join(n for (n, _, _) in MEASURES))


if __name__ == "__main__":
    main()
