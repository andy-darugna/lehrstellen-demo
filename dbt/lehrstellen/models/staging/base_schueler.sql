{{ config(materialized = 'ephemeral') }}

select 
    cast(schueler_id as string)        as schueler_id,
    cast(vorname as string)            as vorname,
    cast(nachname as string)           as nachname,
    cast(email as string)              as email,
    to_hex(sha256(lower(trim(email)))) as email_key,
    cast(geburtsdatum as date)         as geburtsdatum,
    cast(
        (case when geschlecht = 'w' then 'weiblich' 
              when geschlecht = 'm' then 'männlich'
              when geschlecht = 'd' then 'divers'
              else NULL END)
                    as string)         as geschlecht,
    cast(strasse as string)            as strasse,
    cast(plz as string)                as plz,
    cast(ort as string)                as ort,
    cast(kanton as string)             as kanton,
    cast(schultyp as string)           as schultyp,
    safe_cast(replace(
        notenschnitt,',', '.'
        ) as float64)                  as notenschnitt,
    cast(lieblingsfaecher as string)   as lieblingsfaecher,
    cast(interessen as string)         as interessen,
    cast(registriert_am as datetime)   as registriert_am
from {{ source('raw', 'schueler') }}
qualify row_number() over (partition by schueler_id order by cast(registriert_am as datetime) desc) = 1