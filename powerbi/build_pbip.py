#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bouwt een Power BI Project (PBIP) voor de financiele managementrapportage.

PBIP is het officiele, tekst-gebaseerde bronformaat van Microsoft. Anders dan
een .pbit heeft het GEEN binair DataMashup-onderdeel nodig: de M-queries staan
in het model (SemanticModel/model.bim). Power BI Desktop opent de .pbip en bouwt
daar zelf een .pbix van.

Hergebruikt het model en de rapport-layout uit build_pbit.py, zodat er maar een
bron van waarheid is (src/*.m en src/measures.dax).

Gebruik:  python3 build_pbip.py
Resultaat: ./pbip/Managementrapportage.pbip (+ SemanticModel- en Report-mappen)
"""

import json
import os
import uuid

import build_pbit  # hergebruikt build_model() en build_layout()

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "pbip")
NAME = "Managementrapportage"
SM_DIR = os.path.join(ROOT, NAME + ".SemanticModel")
RP_DIR = os.path.join(ROOT, NAME + ".Report")


def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def platform(item_type, display):
    return {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
        "metadata": {"type": item_type, "displayName": display},
        "config": {"version": "2.0", "logicalId": str(uuid.uuid4())},
    }


def main():
    model = build_pbit.build_model()
    layout = build_pbit.build_layout()

    # --- .pbip ---
    write_json(os.path.join(ROOT, NAME + ".pbip"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json",
        "version": "1.0",
        "artifacts": [{"report": {"path": NAME + ".Report"}}],
        "settings": {"enableAutoRecovery": True},
    })

    # --- SemanticModel ---
    write_json(os.path.join(SM_DIR, ".platform"), platform("SemanticModel", NAME))
    write_json(os.path.join(SM_DIR, "definition.pbism"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json",
        "version": "1.0",
        "settings": {},
    })
    # model.bim = TMSL database-object (UTF-8, geen BOM in PBIP)
    write_json(os.path.join(SM_DIR, "model.bim"), model)

    # --- Report (klassiek report.json-formaat; GEEN $schema in definition.pbir,
    #     anders verwacht Power BI het nieuwe PBIR-mapformaat met losse artifacts) ---
    write_json(os.path.join(RP_DIR, ".platform"), platform("Report", NAME))
    write_json(os.path.join(RP_DIR, "definition.pbir"), {
        "version": "1.0",
        "datasetReference": {"byPath": {"path": "../" + NAME + ".SemanticModel"}},
    })
    write_json(os.path.join(RP_DIR, "report.json"), layout)

    print("PBIP geschreven onder: %s" % ROOT)
    for base, _, files in os.walk(ROOT):
        for fn in sorted(files):
            rel = os.path.relpath(os.path.join(base, fn), ROOT)
            print("  " + rel)


if __name__ == "__main__":
    main()
