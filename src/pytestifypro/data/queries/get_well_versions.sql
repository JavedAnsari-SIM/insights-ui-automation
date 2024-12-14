#src/pytestifypro/data/queries/get_well_versions.sql
-- current_version
SELECT
    'current' AS version_type,
    NULL::timestamp with time zone AS start_period,
    NULL::timestamp with time zone AS end_period,
    w.*
FROM
    wells w
WHERE
    w.uwi = %s;

-- previous_versions
SELECT
    'historical' AS version_type,
    lower(wh.sys_period) AS start_period,
    upper(wh.sys_period) AS end_period,
    w.*
FROM
    wells_history wh
JOIN
    wells w ON wh.uwi = w.uwi
WHERE
    w.uwi = %s;
