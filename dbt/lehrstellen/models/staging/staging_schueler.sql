select 
    schueler_id,
    email_key,
    geschlecht,
    cast(
        date_diff(current_date(), geburtsdatum, year)
         as int)                       as alter_jahre,         
    plz,
    ort,
    kanton,
    schultyp,
    notenschnitt,
    lieblingsfaecher,
    interessen,
    registriert_am
from {{ ref('base_schueler') }}