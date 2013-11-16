#!/usr/bin/python
# -*- coding: utf-8 -*-
__authors__ = 'Carlos de la Torre, Andrés Blanco'

"""
This script uses data from the Ministerio de Educación de la Provincia de
Córdoba and data from the Dirección Nacional Electoral, and tries to assign
lat/lon coordinates to the schools in the DNE.

"""

import argparse
import logging as log
import sys

from geo_from_min_edu_data import *


MinEdu_arg_help = "path to the CSV file with data from the Ministerio de Educación de la Provincia de Córdoba"
DNE_arg_help = "path to the CSV file with data from the Comisión Nacional Electoral"
out_arg_help = "path to the desired output CSV file"

DEBUG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
DEBUG_MSG_FORMAT = '%(levelname)s\t%(message)s'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("MinEdu_data_fname", help=MinEdu_arg_help)
    parser.add_argument("CNE_data_fname", help=DNE_arg_help)
    parser.add_argument("output_csv_fname", help=out_arg_help)
    parser.add_argument("-l", "--log-level", choices=DEBUG_LEVELS,
                        help="set the output verbosity level")
    args = parser.parse_args()

    log_level = log._levelNames.get(args.log_level, log.DEBUG)
    log.basicConfig(format=DEBUG_MSG_FORMAT, level=log_level)

    geo_processor = MinEducHelper(args.MinEdu_data_fname)
    log.info("Data from %s loaded.", args.MinEdu_data_fname)

    com_nac_electoral_data = csv.reader(open(args.CNE_data_fname, 'rU'),
                                        delimiter=',')
    output_report = csv.writer(open(args.output_csv_fname, 'w'), delimiter=',')
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
                    output_report.writerow(row)

    sys.exit(0)
