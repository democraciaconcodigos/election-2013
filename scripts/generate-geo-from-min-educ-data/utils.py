#!/usr/bin/python
# -*- coding: utf-8 -*-
__authors__ = 'Carlos de la Torre'

from math import sqrt, pow

DEPARTAMENTOS = {
    1: 'CAPITAL',
    2: 'CALAMUCHITA',
    3: 'COLON',
    4: 'CRUZ DEL EJE',
    5: 'GENERAL ROCA',
    6: 'GENERAL SAN MARTIN',
    7: 'ISCHILIN',
    8: 'JUAREZ CELMAN',
    9: 'MARCOS JUAREZ',
    10: 'MINAS',
    11: 'POCHO',
    12: 'PUNILLA',
    13: 'RIO CUARTO',
    14: 'RIO PRIMERO',
    15: 'RIO SECO',
    16: 'RIO SEGUNDO',
    17: 'PRESIDENTE ROQUE SAENZ PEÑA',
    18: 'SAN ALBERTO',
    19: 'SAN JAVIER',
    20: 'SAN JUSTO',
    21: 'SANTA MARIA',
    22: 'SOBREMONTE',
    23: 'TERCERO ARRIBA',
    24: 'TOTORAL',
    25: 'TULUMBA',
    26: 'UNION'
}


def normalize_str(s):
    return s.strip().lower()


def output_row(school):
    """Given a School instance, output the correct row format for geoloc file"""
    return [school.dne_id, school.lat, school.lon]


def report_row(voting_place, school, match_str, density_str):
    """Given two School instances, output a row for the report file"""
    return [
        voting_place.dne_id,
        voting_place.name,
        voting_place.address,
        voting_place.city,
        voting_place.area,
        school.min_edu_id,
        school.name,
        school.address,
        school.city,
        school.area,
        school.lat,
        school.lon,
        match_str,
        density_str,
        1,  # Useful flag
    ]


MAX_DISTANCE = float('inf')


def euclidean_distance(lat_x, lon_x, lat_y, lon_y):
    try:
        lat_x = float(lat_x)
        lon_x = float(lon_x)
        lat_y = float(lat_y)
        lon_y = float(lon_y)
    except ValueError:
        return MAX_DISTANCE
    return sqrt(pow(lat_x - lat_y, 2.0) + pow(lon_x - lon_y, 2.0))


def compute_proximity(schools):
    N = len(schools)
    min_distance = MAX_DISTANCE
    max_distance = 0.0
    sum_distances = 0.0
    furthest = (None, None)
    for i in range(N):
        origin = schools[i]
        o_lat = origin.lat
        o_lon = origin.lon
        for j in range(i+1, N):
            target = schools[j]
            t_lat = target.lat
            t_lon = target.lon
            d = euclidean_distance(o_lat, o_lon, t_lat, t_lon)
            sum_distances += d
            min_distance = min(d, min_distance)
            if d > max_distance:
                max_distance = d
                furthest = (origin, target)
    return {'num': N,
            'min': min_distance,
            'max': max_distance,
            'furthest': furthest,
            'avg': sum_distances / N}
