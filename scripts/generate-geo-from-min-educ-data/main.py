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
from utils import (DEPARTAMENTOS, normalize_str, output_row, report_row,
                   compute_proximity)

MinEdu_arg_help = "path to the CSV file with data from the Ministerio de Educación de la Provincia de Córdoba"
DNE_arg_help = "path to the CSV file with data from the Comisión Nacional Electoral"
out_arg_help = "path to the desired output CSV file"

DEBUG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
DEBUG_MSG_FORMAT = '%(levelname)s\t%(message)s'

# How close should the schools be in order to be considered the same place?
# DISTANCE_THRESHOLD = 0.000931122  # Aprox. 100mts
DISTANCE_THRESHOLD = 0.004655608  # Aprox. 500mts

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
    log.info("Loaded data from %s", args.MinEdu_data_fname)

    com_nac_electoral_data = csv.reader(open(args.CNE_data_fname, 'rU'),
                                        delimiter=',')
    output_csv = csv.writer(open(args.output_csv_fname, 'w'), delimiter=',')
    output_csv.writerow(['dne_id', 'lat', 'lon'])

    report = None
    if args.report:
        report = csv.writer(open(args.report, 'w'), delimiter=',')
        report.writerow(['dne_id', 'dne name', 'dne address', 'dne city',
                         'dne area', 'min_edu_id', 'min edu name',
                         'min edu address', 'min edu city', 'min edu area',
                         'lat', 'lon', 'match_str', 'density_str', 'flag',
                         'max_distance', 'origin.lat', 'origin.lon',
                         'destiny.lat', 'destiny.lon'])

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
        density = 'probable'
        if schools_set:
            if len(schools_set) == 1:
                school = schools_set[0]
                density = 'only'
            else:
                stats = compute_proximity(schools_set)
                if stats['max'] < DISTANCE_THRESHOLD:
                    school = schools_set[0]

            if school:
                voting_place.lat = school.lat
                voting_place.lon = school.lon
                voting_place.min_edu_id = school.min_edu_id
                output_csv.writerow(output_row(school))

        if report:
            if density == 'only':
                row = report_row(voting_place, school, most_probable['match'],
                                 'only')
                report.writerow(row)
            elif schools_set:
                chosen_flag = False
                for probable in schools_set:
                    density = 'probable'
                    if probable.min_edu_id == voting_place.min_edu_id:
                        density = 'chosen'
                        chosen_flag = True
                    row = report_row(voting_place, probable,
                                     most_probable['match'], density)
                    report.writerow(row)
                if not chosen_flag:
                    # No school chosen because proximity threshold is broke.
                    row = report_row(voting_place, School(),
                                     most_probable['match'], 'no chosen')
                    origin, destiny = stats['furthest']
                    row += [stats['max'], origin.lat, origin.lon, destiny.lat,
                            destiny.lon]
                    report.writerow(row)
            else:
                row = report_row(voting_place, School(), 'no match', 'no match')
                report.writerow(row)
    log.info("Generated geoloc file %s", args.output_csv_fname)
    if report:
        log.info("Generated report file %s", args.report)

    sys.exit(0)
