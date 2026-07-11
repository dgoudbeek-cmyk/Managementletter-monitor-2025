// Grootboekrekeningen (dimensie) uit Exact Online via Invantive Bridge Online.
// Verbinding loopt via de OData-feed van Invantive Bridge Online (parameter BridgeUrl).
// Als jouw Bridge de administratie al afbakent, mag je de "Administratie"-stap weglaten.
let
    Bron          = OData.Feed(BridgeUrl, null, [Implementation = "2.0"]),
    GLAccounts    = Bron{[Name = "GLAccounts"]}[Data],
    Administratie = Table.SelectRows(GLAccounts, each [Division] = Number.FromText(Division)),
    Selectie      = Table.SelectColumns(
        Administratie,
        {"ID", "Code", "Description", "BalanceSide", "BalanceType", "Type", "TypeDescription"}
    ),
    Types = Table.TransformColumnTypes(
        Selectie,
        {
            {"Code", type text},
            {"Description", type text},
            {"BalanceSide", type text},       // "D" = debet, "C" = credit
            {"BalanceType", type text},       // "B" = balans, "W" = winst & verlies
            {"Type", Int64.Type},             // Exact-classificatie (10 = kas, 12 = bank, ...)
            {"TypeDescription", type text}
        }
    )
in
    Types
