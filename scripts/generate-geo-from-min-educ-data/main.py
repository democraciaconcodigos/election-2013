#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
This script uses data from the Ministerio de Educación de la Provincia de
Córdoba and data from the Dirección Nacional Electoral, and tries to assign
lat/lon coordinates to the schools in the DNE.

"""

__authors__ = 'Carlos de la Torre, Andrés Blanco'


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
    parser.add_argument("-r", "--report",
                        help="optional output csv filename, with a complete "
                             "report of the results")
    args = parser.parse_args()

    log_level = log._levelNames.get(args.log_level, log.INFO)
    log.basicConfig(format=DEBUG_MSG_FORMAT, level=log_level)

    geo_processor = MinEducHelper(args.MinEdu_data_fname)
    log.info("Loaded data from %s.", args.MinEdu_data_fname)

    com_nac_electoral_data = csv.reader(open(args.CNE_data_fname, 'rU'),
                                        delimiter=',')
    output_csv = csv.writer(open(args.output_csv_fname, 'w'), delimiter=',')
    output_csv.writerow(['dne_id', 'lat', 'lon'])

    voting_place = com_nac_electoral_data.next()  # Skip header
    for data in com_nac_electoral_data:
        # data[13]: dne_seccion_id. It is the ID of the area (departamento)
        area = ''
        if data[13]:
            area = normalize_str(DEPARTAMENTOS[int(data[13])])

        voting_place = School(
            name=data[11],  # establecimiento
            address=data[6],  # direccion
            city=data[9],  # localidad
            area=area,
            province=data[10],  # distrito
            postal_code=data[4],  # codigo_postal
            dne_id=data[0],  # D.N.E. ID
        )

        most_probable = geo_processor.get_most_probable(voting_place)
        schools_set = list(most_probable['schools_set'])
        if schools_set:
            if len(schools_set) == 1:
                school = schools_set[0]
            else:
                school = School.select_by_proximity(schools_set)
            if school:
                row = school.output_row(most_probable['match'])
                output_csv.writerow(row)

    sys.exit(0)
