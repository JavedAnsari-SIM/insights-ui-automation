--src/pytestifypro/data/queries/get_production_volume_data.sql
----date field is used to plot the graph
select date, liquid, water, gas
from well_production_records_history
where well_id = (select id from wells where uwi = '4231742813')
order by date asc;