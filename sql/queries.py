select_nsr_rows = """
SELECT date_time,
-- year, month, day, 
-- zipcode,
-- Clearsky_DHI, DHI,
Clearsky_DNI, DNI,
Clearsky_GHI, GHI,
Temperature,
Relative_Humidity,
Precipitable_Water,
-- Wind_Direction,
Wind_Speed
from nsrdb
where zipcode = :zipcode
-- and not (month = 2 and day = 29)
;
"""

select_locale_data = """
select city, county, state
from geo_zipcodes
where zipcode = :zipcode
;
"""

select_zipcode_geo = """
select "zipcode",
"lat_zc" as "lat",
"lon_zc" as "lon"
from geo_zipcodes
where "zipcode" = :zipcode
"""

select_distinct_zips = """
SELECT DISTINCT zipcode FROM nsrdb;
"""


select_zip_year = """
select count(zipcode) from nsrdb
where zipcode = :zipcode
and substr(date_time, 1, 4) in (:year);
"""

update_gzc_llltze = """
update geo_zipcodes
set location_id = :loc_id,
lat_nrel = :lat,
lon_nrel = :lon,
elevation = :elev,
time_zone = :tz
where zipcode = :zipcode;
"""


create_table_geo_zipcodes = """
create table if not exists geo_zipcodes(
'id' INTEGER PRIMARY KEY AUTOINCREMENT,
'zipcode' CHAR(10),
'location_id' INTEGER,
'land_area_msq' FLOAT,
'water_area_msq' FLOAT,
'land_area_sqmi' FLOAT,
'water_area_sqmi' FLOAT,
'lat_zc' FLOAT,
'lon_zc' FLOAT,
'lat_nrel' FLOAT,
'lon_nrel' FLOAT,
'elevation' FLOAT,
'time_zone' INTEGER,
'city' TEXT,
'county' TEXT,
'state' TEXT
);
"""


create_table_nsrdb = """
create table if not exists nsrdb(
'id' INTEGER PRIMARY KEY AUTOINCREMENT,
'location_id' INTEGER,
'zipcode' CHAR(10),
'date_time' CHAR(24),
'year' INTEGER,
'month' INTEGER,
'day' INTEGER,
'hour' INTEGER,
'Temperature' FLOAT,
'Clearsky_DHI' FLOAT,
'Clearsky_DNI' FLOAT,
'Clearsky_GHI' FLOAT,
'Cloud_Type' INTEGER,
'Dew_Point' FLOAT,
'DHI' FLOAT,
'DNI' FLOAT,
'Fill_Flag' INTEGER,
'GHI' FLOAT,
'Relative_Humidity' FLOAT,
'Solar_Zenith_Angle' FLOAT,
'Surface_Albedo' FLOAT,
'Pressure' FLOAT,
'Precipitable_Water' FLOAT,
'Wind_Direction' FLOAT,
'Wind_Speed' FLOAT,
'Global_Horizontal_UV_Irradiance_(280-400nm)' FLOAT,
'Global_Horizontal_UV_Irradiance_(295-385nm)' FLOAT);
"""

create_table_monthly_nsrdb = """
create table if not exists nsrdb(
'id' INTEGER PRIMARY KEY AUTOINCREMENT,
'location_id' INTEGER,
'zipcode' CHAR(10),
'date_time' CHAR(24),
'Temperature' FLOAT,
'Clearsky_DHI' FLOAT,
'DHI' FLOAT,
'Clearsky_DNI' FLOAT,
'DNI' FLOAT,
'Clearsky_GHI' FLOAT,
'GHI' FLOAT,
'Dew_Point' FLOAT,
'Relative_Humidity' FLOAT,
'Pressure' FLOAT,
'Precipitable_Water' FLOAT,
'Wind_Speed' FLOAT,
'GHI_UV_wd' FLOAT,
'GHI_UV_nw' FLOAT);
"""


# test query
select_zipcode = """
select * from geo_zipcodes
where zipcode = :zipcode;
"""
