// Grootboeksaldi per periode (feit) uit Exact Online via Invantive Bridge Online.
// ReportingBalance is voorgeaggregeerd (saldo per rekening/jaar/periode) en daardoor
// veel lichter dan TransactionLines — ideaal voor een management-dashboard.
let
    Bron          = OData.Feed(BridgeUrl, null, [Implementation = "2.0"]),
    RB            = Bron{[Name = "ReportingBalance"]}[Data],
    Administratie = Table.SelectRows(RB, each [Division] = Number.FromText(Division)),
    Selectie      = Table.SelectColumns(
        Administratie,
        {"Division", "GLAccountCode", "ReportingYear", "ReportingPeriod", "Amount", "Count"}
    ),
    Types = Table.TransformColumnTypes(
        Selectie,
        {
            {"Division", Int64.Type},
            {"GLAccountCode", type text},
            {"ReportingYear", Int64.Type},
            {"ReportingPeriod", Int64.Type},  // 0 = beginbalans, 1-12 = maanden, 13-15 = jaarafsluiting
            {"Amount", type number},          // debet positief, credit negatief (Exact-conventie)
            {"Count", Int64.Type}
        }
    ),
    // Koppelsleutel naar de Perioden-dimensie
    MetKey = Table.AddColumn(Types, "PeriodeKey", each [ReportingYear] * 100 + [ReportingPeriod], Int64.Type)
in
    MetKey
