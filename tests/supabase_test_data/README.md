This directory contains CSVs to be imported into the Supabase dev environment for testing. 

To insert data from any csv into the relevant table, go to the table editor section of the Supabase dashboard, click "Insert-> Import data from CSV", and select the relevant csv.

Note that when importing data, Supabase may identify some columns not specified in the CSV for import -- these columns will show up with null values. This can cause the import to fail. To avoid this, select the "Configure Import Data" option and deselect the columns that are not specified in the CSV. 