#!/usr/bin/env python
# coding: utf-8

# In[ ]:


query_zip = """
SELECT *

FROM program

LEFT JOIN zipcode on program.state_id == zipcode.state_id

WHERE is_entire_state == 1
"""

query_city_zip = """
SELECT *

FROM program_city

LEFT JOIN program

on program_city.program_id == program.id

LEFT JOIN zipcode on program_city.city_id == zipcode.city_id

WHERE is_entire_state == 0
"""

query_county_zip = """
SELECT *

FROM program_county

LEFT JOIN program

on program_county.program_id == program.id

LEFT JOIN zipcode on program_county.county_id == zipcode.county_id

WHERE is_entire_state == 0
"""

query_utility_zip = """
SELECT *

FROM program_utility

LEFT JOIN program

on program_utility.program_id == program.id

LEFT JOIN utility_zipcode

on program_utility.utility_id == utility_zipcode.utility_id

LEFT JOIN zipcode on utility_zipcode.zipcode_id == zipcode.id

WHERE is_entire_state == 0
"""

query_zip_zip = """
SELECT *

FROM program_zipcode

LEFT JOIN program

on program_zipcode.program_id == program.id

INNER JOIN zipcode on program_zipcode.zipcode_id == zipcode.id

WHERE is_entire_state == 0
"""

query_tech = """
SELECT * 

FROM program_technology

WHERE program_technology.technology_id == 7
"""

query_sector = """
SELECT * 

FROM program_sector

"""

