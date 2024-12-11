-- src/pytestifypro/data/queries/get_well_header_details.sql

SELECT
  name AS srp_well_name,
  current_operator,
  hole_direction,
  status AS srp_well_status,
  TO_CHAR(permit_date, 'MM/DD/YYYY') AS permit_date,
  TO_CHAR(spud_date, 'MM/DD/YYYY') AS spud_date,
  COALESCE(TO_CHAR(rig_release_date, 'MM/DD/YYYY'), '–') AS rig_release_date,
  TO_CHAR(completion_date, 'MM/DD/YYYY') AS completion_date,
  TO_CHAR(first_production_date, 'MM/DD/YYYY') AS first_production_date,
  TO_CHAR(last_production_date, 'MM/DD/YYYY') AS last_production_date
FROM wells
WHERE uwi = '{{uwi}}';
