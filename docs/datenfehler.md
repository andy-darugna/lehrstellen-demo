# Eingebaute Datenfehler in `schueler.csv`

Spoiler-Datei: Erst lesen, nachdem du versucht hast, die Fehler mit dbt-Tests selbst zu finden.

| # | Fehler | Anzahl | Passender Test / Fix in Staging |
|---|--------|--------|--------------------------------|
| 1 | Gleiche `schueler_id`, spätere Version (anderes `registriert_am`, andere Interessen) | 15 Zeilen | `unique` auf schueler_id schlägt an → ROW_NUMBER() OVER (PARTITION BY schueler_id ORDER BY registriert_am DESC) = 1 |
| 2 | Notenschnitt mit Komma statt Punkt | 10 Zeilen | REPLACE(',', '.') vor SAFE_CAST |
| 3 | Ungültige Noten (7.0, 0.0, 55) | 3 Zeilen | Test: Wert zwischen 1 und 6 (`dbt_utils.accepted_range`) |

Mit `python scripts/generate_schueler.py --clean` entsteht eine Version ohne Fehler.

Hinweis: Alle Personen sind erfunden. Interessen sind leicht nach Geschlecht gewichtet (eigene, grobe Annahme), damit im Dashboard eine Auswertung nach Geschlecht etwas zeigt. Das ist keine echte Statistik.
