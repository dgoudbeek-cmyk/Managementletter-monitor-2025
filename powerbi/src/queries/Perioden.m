// Perioden-dimensie (boekjaar + periode). Volledig in Power Query gegenereerd,
// zodat er geen extra bron nodig is. Pas het bereik "Jaren" desgewenst aan.
let
    Jaren    = {2023 .. 2028},
    Perioden = {0 .. 15},                 // 0 = beginbalans, 1-12 = maanden, 13-15 = jaarafsluiting
    Kruis    = List.Combine(
        List.Transform(Jaren, (j) => List.Transform(Perioden, (p) => [Boekjaar = j, Periode = p]))
    ),
    Tabel    = Table.FromRecords(Kruis),
    MetKey   = Table.AddColumn(Tabel, "PeriodeKey", each [Boekjaar] * 100 + [Periode], Int64.Type),
    MetLabel = Table.AddColumn(
        MetKey,
        "PeriodeLabel",
        each Text.From([Boekjaar]) & "-P" & Text.PadStart(Text.From([Periode]), 2, "0"),
        type text
    ),
    Sorteer  = Table.AddColumn(MetLabel, "SorteerKey", each [PeriodeKey], Int64.Type),
    Types    = Table.TransformColumnTypes(Sorteer, {{"Boekjaar", Int64.Type}, {"Periode", Int64.Type}})
in
    Types
