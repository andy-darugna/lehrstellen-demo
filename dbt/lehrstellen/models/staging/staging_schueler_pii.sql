{{ config(schema='staging_pii')}}
select 
    schueler_id,
    email_key,
    email,
    vorname,
    nachname,
    geburtsdatum,
    geschlecht,
    strasse, 
    plz,
    ort
from {{ ref('base_schueler') }}