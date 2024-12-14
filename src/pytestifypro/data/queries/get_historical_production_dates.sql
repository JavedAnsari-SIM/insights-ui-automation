--src/pytestifypro/data/queries/get_historical_production_dates.sql

-- first_production_date
SELECT MIN(ja.date) AS first_production_date
FROM (
    SELECT well_id, "date"
    FROM public.well_production_records
    WHERE well_id IN (SELECT id FROM wells WHERE uwi = %s)
      AND LOWER(sys_period) <= %s
    UNION ALL
    SELECT well_id, "date"
    FROM public.well_production_records_history
    WHERE well_id IN (SELECT id FROM wells WHERE uwi = %s)
      AND LOWER(sys_period) <= %s
      AND UPPER(sys_period) >= %s
) AS ja
GROUP BY ja.well_id;


-- last_production_date
SELECT MAX(ja.date) AS last_production_date
FROM (
    SELECT well_id, "date"
    FROM public.well_production_records
    WHERE well_id IN (SELECT id FROM wells WHERE uwi = %s)
      AND LOWER(sys_period) <= %s
    UNION ALL
    SELECT well_id, "date"
    FROM public.well_production_records_history
    WHERE well_id IN (SELECT id FROM wells WHERE uwi = %s)
      AND LOWER(sys_period) <= %s
      AND UPPER(sys_period) >= %s
) AS ja
GROUP BY ja.well_id;


