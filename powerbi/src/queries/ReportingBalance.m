// Grootboeksaldi per periode (feit) uit Exact Online Premium.
// Verbinding via de Exact Online Premium-connector: ExactOnlinePremium.Contents().
// Bedrag = AmountDCDebit - AmountDCCredit (netto, debet positief). Koppeling via GLAccount (GUID).
let
    Bron             = ExactOnlinePremium.Contents(),
    dbo              = Bron{[Name = "dbo", Kind = "Schema"]}[Data],
    ReportingBalance = dbo{[Name = "ReportingBalance", Kind = "Table"]}[Data],
    Selectie         = Table.SelectColumns(
        ReportingBalance,
        {"Division", "ReportingYear", "ReportingPeriod", "GLAccount",
         "AmountDCDebit", "AmountDCCredit", "Count"}
    ),
    Types = Table.TransformColumnTypes(
        Selectie,
        {
            {"Division", Int64.Type},
            {"ReportingYear", Int64.Type},
            {"ReportingPeriod", Int64.Type},   // 0 = beginbalans, 1-12 = maanden, 13-15 = jaarafsluiting
            {"GLAccount", type text},          // GUID -> koppelt aan GLAccounts[ID]
            {"AmountDCDebit", type number},
            {"AmountDCCredit", type number},
            {"Count", Int64.Type}
        }
    ),
    // GUID uniform maken zodat hij koppelt met GLAccounts[ID] (zonder accolades, kleine letters)
    Sleutel = Table.TransformColumns(
        Types,
        {{"GLAccount", each if _ = null then null else Text.Lower(Text.Remove(_, {"{", "}"})), type text}}
    ),
    // Netto bedrag in eigen valuta: debet positief, credit negatief
    Bedrag = Table.AddColumn(Sleutel, "Amount", each [AmountDCDebit] - [AmountDCCredit], type number),
    // Koppelsleutel naar de Perioden-dimensie
    MetKey = Table.AddColumn(Bedrag, "PeriodeKey", each [ReportingYear] * 100 + [ReportingPeriod], Int64.Type)
in
    MetKey
