-- src/pytestifypro/data/queries/get_well_header_details.sql
SELECT
    w.lease_name || ' #' || w.well_number AS srp_well_name,
    w.current_operator,
    w.hole_direction,
    INITCAP(w."status") AS srp_well_status,
    TO_CHAR(w.permit_date, 'MM/DD/YYYY') AS permit_date,
    TO_CHAR(w.spud_date, 'MM/DD/YYYY') AS spud_date,
    COALESCE(TO_CHAR(w.rig_release_date, 'MM/DD/YYYY'), '–') AS rig_release_date,
    TO_CHAR(w.completion_date, 'MM/DD/YYYY') AS completion_date,
    TO_CHAR(MIN(wpr.date), 'MM/DD/YYYY') AS first_production_date,
    TO_CHAR(MAX(wpr.date), 'MM/DD/YYYY') AS last_production_date
FROM
    wells w
LEFT JOIN
    well_production_records wpr ON w.id = wpr.well_id
WHERE
    w.uwi = %s
GROUP BY
    w.lease_name,
    w.well_number,
    w.current_operator,
    w.hole_direction,
    w."status",
    w.permit_date,
    w.spud_date,
    w.rig_release_date,
    w.completion_date;

