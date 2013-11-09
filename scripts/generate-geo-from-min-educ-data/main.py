#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'Andrés Blanco'

import sys
from geo_from_min_edu_data import *

#min_educ_fname = sys.argv[1]
#com_nac_electoral_fname = sys.argv[2]
#output = sys.argv[3]

min_educ_fname = 'test_data/80269-escuelas-de-cordoba-geolocalizadas.csv'
com_nac_electoral_fname = 'test_data/80268-escuelas-segun-la-dne.csv'
output = 'out.csv'

geo_processor = MinEducHelper(min_educ_fname)
com_nac_electoral_data = csv.reader(open(com_nac_electoral_fname, 'rU'), delimiter=',')
output_report = csv.writer(open(output, 'w'), delimiter=',')
output_report.writerow(['dne_id', 'lat', 'lon'])

voting_place = com_nac_electoral_data.next()
com_nac_electoral_data.next()
for data in com_nac_electoral_data:
    voting_place = School(
        name=data[11],  # establecimiento
        address=data[6],  # direccion
        city=data[9],  # localidad
        area=data[13],  # dne_seccion_id
        province=data[10],  # distrito
        postal_code=data[4],  # codigo_postal
        dne_id=data[0],  # D.N.E. ID
    )

    check_area = True
    school_set = geo_processor.schools
    if voting_place.city:
        city = voting_place.city.lower().strip()
        if city in geo_processor.schools_by_city:
            school_set = geo_processor.schools_by_city[city]
            check_area = False

    if check_area:
        if voting_place.area:
            area = DEPARTAMENTOS[int(voting_place.area)].lower().strip()
            if area in geo_processor.schools_by_area:
                school_set = geo_processor.schools_by_area[area]

    same_name = geo_processor.match_name(voting_place, school_set)
    same_address = geo_processor.match_address(voting_place, school_set)

    #import ipdb; ipdb.set_trace()
    same_name = set(same_name)
    same_address = set(same_address)
    intersection = set(same_name).intersection(same_address)
    if intersection:
        school = School.select_by_proximity(list(intersection))
        if school:
            row = school.output_row("Match name and address")
            output_report.writerow( row )
    else:
        schools_set = list(same_name.union(same_address))
        if schools_set:
            school = School.select_by_proximity(schools_set)
            if school:
                row = school.output_row("Only name or address")
                output_report.writerow( row )

sys.exit(0)