// Grootboekrekeningen (dimensie) uit Exact Online Premium.
// Verbinding via de Exact Online Premium-connector: ExactOnlinePremium.Contents().
// In Premium staat het rekeningnummer in SearchCode; de koppelsleutel is ID (GUID).
let
    Bron       = ExactOnlinePremium.Contents(),
    dbo        = Bron{[Name = "dbo", Kind = "Schema"]}[Data],
    GLAccounts = dbo{[Name = "GLAccounts", Kind = "Table"]}[Data],
    Selectie   = Table.SelectColumns(
        GLAccounts,
        {"ID", "Division", "SearchCode", "Description", "BalanceType", "BalanceSide", "Type"}
    ),
    Types = Table.TransformColumnTypes(
        Selectie,
        {
            {"ID", type text},
            {"Division", Int64.Type},
            {"SearchCode", type text},        // rekeningnummer
            {"Description", type text},
            {"BalanceType", type text},       // "B" = balans, "W" = winst & verlies
            {"BalanceSide", type text},       // "D" = debet, "C" = credit
            {"Type", Int64.Type}              // Exact-classificatie (10 = kas, 12 = bank, ...)
        }
    ),
    // Afgeleide categorie voor rapportage (Premium heeft geen TypeDescription-kolom)
    Categorie = Table.AddColumn(
        Types,
        "Categorie",
        each
            if [BalanceType] = "W" and [BalanceSide] = "C" then "Opbrengsten"
            else if [BalanceType] = "W" then "Kosten"
            else if [BalanceType] = "B" and [BalanceSide] = "D" then "Activa"
            else "Passiva",
        type text
    )
in
    Categorie
