# Lehrstellen-Matching (Demo)

Portfolio-Projekt: Jugendliche auf Lehrstellensuche (Batch) werden mit laufend eintreffenden Lehrstellen (Stream) abgeglichen.
Alle Daten sind synthetisch.

**Stack:** Google Cloud (Cloud Storage, BigQuery, Pub/Sub) · dbt (BigQuery) · Airflow (lokal in Docker) · Looker Studio

## Architektur

```
schueler.csv ──► GCS ──► BigQuery raw.schueler ─┐
                                                ├─► dbt staging ─► dbt marts (Matching) ─► Looker Studio
Generator ──► Pub/Sub ──► BigQuery raw.lehrstellen ┘
                    (Airflow orchestriert Batch-Load + dbt build)
```

## Struktur

```
data/raw/            schueler.csv (generiert)
scripts/             Datengeneratoren
dbt/seeds/           berufe.csv (Referenz: Beruf -> Berufsfeld, Mindest-Schultyp)
dbt/                 dbt-Projekt (folgt)
airflow/dags/        DAGs (folgt)
docs/                datenfehler.md (Spoiler!)
```

## Daten

`schueler.csv`: ~2000 Jugendliche + eingebaute Datenfehler (Duplikate, Komma-Noten, ungültige Werte, ...).
Listen-Spalten (`lieblingsfaecher`, `interessen`) sind mit `;` getrennt.

Neu generieren: `python scripts/generate_schueler.py --n 2000 --out data/raw/schueler.csv`

## Governance-Hinweis

Die Daten imitieren Personendaten von Minderjährigen. Name, E-Mail und Adresse werden in BigQuery
mit Policy Tags geschützt; Marts enthalten nur pseudonymisierte IDs. Region: `europe-west6` (Zürich).
