# OVERALL APARTMENR BUILDING UNIT DATA STRUCTURE:

1. apartment_specs.csv defines all available apartment units by unit type.
The table has this schema:
Unit Description, Description, Unit Area,Ground,Floor 2 North,Floor 3 North,Floor 4 North,Floor 5 North,Floor 2 South,Floor 3 South,Floor 4 South,Floor 5 South,Total Units,Total Leasable Area,Percent,Totals by Unit Class

if Total Units is 0, that means the unit type is not needed for this project. Materials for this type of unit should be 0 for all materials.

# VALUE ENGINEERING FOR DOORS DATA STRUCTURE:

2. We also have data/schedule/schedule_unit_doors.tsv, which has the following column:
MARK	LOCATION	TYPE	WIDTH	HEIGHT	THICKNESS	MATERIAL	LABEL	HARDWARE SET	FRAME TYPE	FRAME MATERIAL

MARK is the door's id which is used as a unique identifier for the door type. 
This table is used to see the specifications for each door.

3. We also have the data/counts/count_unit_doors.tsv, which has the following column:
Unit Description	Description	Unit Area	1	2	3	4	5	6	7	8	9	10	11	12	13	14	15	16	17	18	19	20	21	22

This table describes what unit has what doors available.
The Unit Description is used to filter the apartment units available by checking the apartment_specs.csv table;
the nubmer columns 1 - 22 are the unit door mark (id).
You can sum up all the counts for each door mark, and get the total for each door mark.


# VALUE ENGINEERING FOR WINDOWS DATA STRUCTURE:

The window schedule data/schedule/schedule_window.tsv describes the specifications for each window type. The table schema is:
MARK	STYLE	UNIT SIZE WIDTH	UNIT SIZE HEIGHT	MATERIAL	HEAD HEIGHT (AFF)	SILL HEIGHT (AFF)	GLAZING INSUL	GLAZING LOW-E	GLAZING TINT	DETAIL	NATURAL VENTILATION CALCULATION FREE AREA PER FLOOR AREA PER TYPE 5A	NATURAL VENTILATION CALCULATION FREE AREA PER FLOOR AREA PER TYPE 5B	REMARKS

MARK is the unique identifier for the window. 

The data/counts/count_windows.tsv describes the number of windows available for each window type, i.e. the MARK, by building facade: Schema is:
MARK	North-outside	South-outside	West-outside	East-outside	North-inside	South-inside	West-inside	East-inside

Note that the total windows available for each window type (MARK) can be aggregated by the building facade.


# VALUE ENGINEERING FOR APPLICANCES DATA STRUCTURE:

The total needed appliaces are in data/counts/count_appliance.tsv. Columns are:
UNIT TYPE	Appliance	Manufacturer	Model	Finish	Notes	Count


# Now, you should have the cost data in data/rsmeans/ folder, which has the cost for :
1. windows, rsmeans_B2020_ext_windows_unit_cost.tsv, for all windows,
2. exterior doors rsmeans_B2030_110_ext_doors_unit_cost.tsv (for balcony doors only)
3. interior doors rsmeans_C1020_102_int_doors_unit_cost.tsv (for all other interior doors)
4. appliances, rsmeans_appliances_unit_cost.tsv, which has prices for appliances.

Note that when you quote prices, you quote the material, labor, and the total costs for each.

