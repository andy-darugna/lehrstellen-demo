"""
Generiert einen synthetischen Datensatz von Jugendlichen auf Lehrstellensuche.

Alle Daten sind frei erfunden. Verteilungen (z.B. Interessen nach Geschlecht)
sind grobe Annahmen für eine Demo, keine echten Statistiken.

Bewusst eingebaute Datenfehler (für dbt-Tests) sind in docs/datenfehler.md
beschrieben. Ohne Python-Abhängigkeiten ausser der Standardbibliothek.

Aufruf:  python scripts/generate_schueler.py --n 2000 --out data/raw/schueler.csv
"""
import argparse
import csv
import random
from datetime import date, datetime, timedelta

SEED = 42
STICHTAG = date(2026, 10, 1)

VORNAMEN_W = ["Lea", "Mia", "Lara", "Emma", "Sara", "Elena", "Lina", "Nina", "Alina", "Laura",
              "Anna", "Julia", "Leonie", "Chiara", "Selina", "Noemi", "Jana", "Elin", "Aline", "Ronja"]
VORNAMEN_M = ["Noah", "Luca", "Leon", "Elias", "Levin", "Nico", "Jan", "Matteo", "Gian", "David",
              "Liam", "Samuel", "Tim", "Fabio", "Nevio", "Joel", "Ben", "Dario", "Lio", "Robin"]
VORNAMEN_D = ["Kim", "Robin", "Alex", "Noa", "Sascha"]
NACHNAMEN = ["Müller", "Meier", "Schmid", "Keller", "Weber", "Huber", "Schneider", "Meyer",
             "Steiner", "Fischer", "Gerber", "Brunner", "Baumann", "Frei", "Zimmermann",
             "Moser", "Widmer", "Wyss", "Graf", "Roth", "Bianchi", "Rossi", "Krasniqi",
             "Berisha", "Da Silva", "Ferreira", "Yilmaz", "Nguyen", "Bühler", "Suter"]
STRASSEN = ["Bahnhofstrasse", "Dorfstrasse", "Hauptstrasse", "Schulstrasse", "Kirchweg",
            "Lindenstrasse", "Gartenstrasse", "Rosenweg", "Feldstrasse", "Seestrasse",
            "Bergstrasse", "Industriestrasse", "Mühleweg", "Sonnenbergstrasse", "Wiesenstrasse"]

# (PLZ, Ort, Kanton, Gewicht)
ORTE = [
    ("8001", "Zürich", "ZH", 10), ("8400", "Winterthur", "ZH", 6), ("8620", "Wetzikon", "ZH", 3),
    ("8600", "Dübendorf", "ZH", 2), ("8952", "Schlieren", "ZH", 2), ("8610", "Uster", "ZH", 3),
    ("8800", "Thalwil", "ZH", 2), ("8180", "Bülach", "ZH", 2),
    ("3011", "Bern", "BE", 7), ("2502", "Biel/Bienne", "BE", 3), ("3600", "Thun", "BE", 3),
    ("4051", "Basel", "BS", 5), ("4410", "Liestal", "BL", 2),
    ("5000", "Aarau", "AG", 3), ("5400", "Baden", "AG", 3), ("5600", "Lenzburg", "AG", 2),
    ("6003", "Luzern", "LU", 5), ("6210", "Sursee", "LU", 2), ("6300", "Zug", "ZG", 3),
    ("9000", "St. Gallen", "SG", 4), ("8640", "Rapperswil-Jona", "SG", 2), ("9500", "Wil", "SG", 2),
    ("8500", "Frauenfeld", "TG", 2), ("8280", "Kreuzlingen", "TG", 2),
    ("8200", "Schaffhausen", "SH", 2), ("7000", "Chur", "GR", 2),
    ("4500", "Solothurn", "SO", 2), ("4600", "Olten", "SO", 2),
    ("6430", "Schwyz", "SZ", 1), ("8750", "Glarus", "GL", 1),
]

SCHULTYPEN = [("Sek A", 45), ("Sek B", 33), ("Sek C", 10), ("Bezirksschule", 7), ("10. Schuljahr", 5)]

# Berufsfelder angelehnt an die Gliederung von berufsberatung.ch
BERUFSFELDER = [
    "Natur", "Ernährung", "Gastgewerbe", "Schönheit, Sport", "Gestaltung, Kunst",
    "Druck", "Bau", "Gebäudetechnik", "Holz, Innenausbau", "Fahrzeuge",
    "Elektrotechnik", "Metall, Maschinen", "Chemie, Physik", "Planung, Konstruktion",
    "Verkauf, Einkauf", "Wirtschaft, Verwaltung", "Verkehr, Logistik", "Informatik",
    "Gesundheit", "Bildung, Soziales",
]
# Grobe, erfundene Neigungen für die Demo (Multiplikator auf Grundgewicht 1)
NEIGUNG_W = {"Gesundheit": 3, "Bildung, Soziales": 3, "Schönheit, Sport": 2.5,
             "Gestaltung, Kunst": 1.8, "Wirtschaft, Verwaltung": 1.6, "Verkauf, Einkauf": 1.5}
NEIGUNG_M = {"Informatik": 2.5, "Elektrotechnik": 2.5, "Metall, Maschinen": 2.5,
             "Fahrzeuge": 2.5, "Bau": 2, "Gebäudetechnik": 2, "Holz, Innenausbau": 1.8,
             "Verkehr, Logistik": 1.6, "Wirtschaft, Verwaltung": 1.4}

FAECHER = ["Mathematik", "Deutsch", "Englisch", "Französisch", "Natur und Technik",
           "Räume, Zeiten, Gesellschaften", "Bildnerisches Gestalten", "Textiles und Technisches Gestalten",
           "Musik", "Sport", "Medien und Informatik", "Wirtschaft, Arbeit, Haushalt"]
FACH_ZU_FELD = {  # leichte Korrelation Fach -> Interesse
    "Mathematik": ["Informatik", "Planung, Konstruktion", "Wirtschaft, Verwaltung"],
    "Natur und Technik": ["Chemie, Physik", "Gesundheit", "Natur", "Elektrotechnik"],
    "Medien und Informatik": ["Informatik", "Druck", "Gestaltung, Kunst"],
    "Bildnerisches Gestalten": ["Gestaltung, Kunst", "Druck", "Schönheit, Sport"],
    "Textiles und Technisches Gestalten": ["Holz, Innenausbau", "Metall, Maschinen", "Gestaltung, Kunst"],
    "Sport": ["Schönheit, Sport", "Bildung, Soziales"],
    "Wirtschaft, Arbeit, Haushalt": ["Ernährung", "Gastgewerbe", "Verkauf, Einkauf"],
    "Deutsch": ["Wirtschaft, Verwaltung", "Bildung, Soziales"],
    "Englisch": ["Wirtschaft, Verwaltung", "Gastgewerbe", "Verkehr, Logistik"],
    "Französisch": ["Wirtschaft, Verwaltung", "Verkauf, Einkauf"],
}


def wchoice(items_with_weights):
    items, weights = zip(*[(i[:-1] if len(i) > 2 else i[0], i[-1]) for i in items_with_weights])
    return random.choices(items, weights=weights, k=1)[0]


def geburtsdatum():
    # Alter am Stichtag: meist 14-16, einige älter (Zwischenjahr, Lehrabbruch)
    alter = random.choices([14, 15, 16, 17, 18, 19, 20], weights=[18, 40, 22, 9, 6, 3, 2])[0]
    start = STICHTAG.replace(year=STICHTAG.year - alter - 1) + timedelta(days=1)
    return start + timedelta(days=random.randint(0, 364))


def notenschnitt(schultyp):
    basis = {"Sek A": 4.9, "Bezirksschule": 5.0, "Sek B": 4.6, "Sek C": 4.3, "10. Schuljahr": 4.5}[schultyp]
    return round(min(6.0, max(3.0, random.gauss(basis, 0.4))), 1)


def interessen(geschlecht, faecher):
    neigung = NEIGUNG_W if geschlecht == "w" else NEIGUNG_M if geschlecht == "m" else {}
    gewichte = {f: neigung.get(f, 1.0) for f in BERUFSFELDER}
    for fach in faecher:
        for feld in FACH_ZU_FELD.get(fach, []):
            gewichte[feld] += 1.0
    anzahl = random.choices([1, 2, 3], weights=[30, 45, 25])[0]
    gewaehlt = []
    while len(gewaehlt) < anzahl:
        f = random.choices(list(gewichte), weights=list(gewichte.values()))[0]
        if f not in gewaehlt:
            gewaehlt.append(f)
    return gewaehlt


def schueler(i):
    geschlecht = random.choices(["w", "m", "d"], weights=[48, 50, 2])[0]
    vorname = random.choice({"w": VORNAMEN_W, "m": VORNAMEN_M, "d": VORNAMEN_D}[geschlecht])
    nachname = random.choice(NACHNAMEN)
    plz, ort, kanton = wchoice(ORTE)
    schultyp = wchoice(SCHULTYPEN)
    faecher = random.sample(FAECHER, k=random.choice([1, 2, 3]))
    registriert = datetime(2026, 3, 1) + timedelta(minutes=random.randint(0, 60 * 24 * 210))
    mail_name = f"{vorname}.{nachname}".lower().replace(" ", "").replace("ü", "ue").replace("ä", "ae").replace("ö", "oe")
    return {
        "schueler_id": f"S{i:06d}",
        "vorname": vorname,
        "nachname": nachname,
        "email": f"{mail_name}{random.randint(1, 99)}@example.ch",
        "geburtsdatum": geburtsdatum().isoformat(),
        "geschlecht": geschlecht,
        "strasse": f"{random.choice(STRASSEN)} {random.randint(1, 120)}",
        "plz": plz,
        "ort": ort,
        "kanton": kanton,
        "schultyp": schultyp,
        "notenschnitt": f"{notenschnitt(schultyp):.1f}",
        "lieblingsfaecher": ";".join(faecher),
        "interessen": ";".join(interessen(geschlecht, faecher)),
        "registriert_am": registriert.strftime("%Y-%m-%d %H:%M:%S"),
    }


def verschmutzen(rows):
    """Baut realistische Datenfehler ein (siehe docs/datenfehler.md)."""
    n = len(rows)
    # 1) Gleiche schueler_id, spätere Version (Profil aktualisiert)
    for r in random.sample(rows[:n], k=15):
        neu = dict(r)
        neu["interessen"] = ";".join(random.sample(BERUFSFELDER, k=2))
        neu["registriert_am"] = (datetime.fromisoformat(r["registriert_am"]) + timedelta(days=random.randint(5, 60))).strftime("%Y-%m-%d %H:%M:%S")
        rows.append(neu)
    # 2) Noten mit Komma statt Punkt (Excel-Export)
    for r in random.sample(rows[:n], k=10):
        r["notenschnitt"] = r["notenschnitt"].replace(".", ",")
    # 3) Ungültige Noten (ausserhalb 1-6)
    for r in random.sample(rows[:n], k=3):
        r["notenschnitt"] = random.choice(["7.0", "0.0", "55"])
    random.shuffle(rows)
    return rows


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=2000)
    p.add_argument("--out", default="data/raw/schueler.csv")
    p.add_argument("--clean", action="store_true", help="ohne eingebaute Datenfehler")
    a = p.parse_args()
    random.seed(SEED)
    rows = [schueler(i + 1) for i in range(a.n)]
    if not a.clean:
        rows = verschmutzen(rows)
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} Zeilen -> {a.out}")


if __name__ == "__main__":
    main()
