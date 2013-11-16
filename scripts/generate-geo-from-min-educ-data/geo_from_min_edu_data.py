#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv
import logging as log
import math
from collections import defaultdict


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

MAX_DISTANCE = 1000

def euclidean_distance(lat_x, lon_x, lat_y, lon_y):
    try:
        lat_x = float(lat_x)
        lon_x = float(lon_x)
        lat_y = float(lat_y)
        lon_y = float(lon_y)
    except ValueError, e:
        return MAX_DISTANCE
    return math.sqrt( math.pow(lat_x + lat_y, 2.0) + math.pow(lon_x + lon_y, 2.0))


def normalize_str(s):
    return s.strip().lower()


class School(object):
    def __init__(self, name='', address='', city='', area='', postal_code='',
                 province='CORDOBA', dne_id=None, min_edu_id=None, lat=None,
                 lon=None):
        self.name = normalize_str(name)
        self.address = normalize_str(address)
        self.city = normalize_str(city)
        self.area = normalize_str(area)  # Departamento
        self.province = normalize_str(province)  # Always CORDOBA in MinEdu.data
        self.postal_code = normalize_str(postal_code)
        self.dne_id = dne_id
        self.min_edu_id = min_edu_id
        self.lat = lat and float(lat)
        self.lon = lon and float(lon)

        self.applied_filters = {}

    def output_row(self, notes):
        return [self.dne_id, self.lat, self.lon]

    @classmethod
    def select_by_proximity(cls, schools, threshold=145.0):
        s = 0
        cnt = 0
        N = len(schools)
        for i in range(N):
            origin = schools[i]
            o_lat = origin.lat
            o_lon = origin.lon
            for j in range(i+1, N):
                target = schools[j]
                t_lat = target.lat
                t_lon = target.lon
                d = euclidean_distance(o_lat, o_lon, t_lat, t_lon)
                s += d
                cnt += 1
                if d > threshold:
                    # The distance between the origin and target schools is
                    # higher than the acceptable threshold.
                    return None
        # If this point is reached, then all the given schools are within the
        # given threshold then we just return a 'random' one.
        if cnt:
            log.debug("Avg distance: %f (%i) points", s*1.0 / cnt, cnt)
        return schools[0]

    def __str__(self):
        return "%s" % (self.name)


class MinEducHelper(object):
    def __init__(self, data_fname):

        self.schools = []
        self.schools_by_city = defaultdict(list)
        self.schools_by_area = defaultdict(list)

        self.csv_reader = csv.reader(open(data_fname, 'rU'), delimiter=',')
        self.csv_reader.next()  # Skip header
        for school_data in self.csv_reader:
            lat = school_data[10]
            lon = school_data[11]
            if not (lat and lon):
                log.debug("Invalid lat/lon data: %s (id %s)", school_data[1],
                          school_data[0])
                continue

            city = normalize_str(school_data[7])
            if city == 'cordoba':
                city = 'capital'  # DNE data says city='capital'
            school = School(
                min_edu_id=school_data[0],  # Min. Edu. ID
                name=school_data[1],  # nombre
                address=school_data[4],  # domicilio
                city=city,  # localidad
                area=school_data[8], # departamento
                postal_code=school_data[5],  # cp
                lat=school_data[10],  # lat
                lon=school_data[11],  # lon
            )
            self.schools.append(school)
            self.schools_by_city[school.city].append(school)
            self.schools_by_area[school.area].append(school)

    def get_most_probable(self, school):
        """
        Try and guess a geolocation for the given school.

        First, try to subset the schools set where to check: keep those with
        the same city only. If there's no match in the city, keep those in the
        same area.

        Next, filter the resulting set with two criterias:
            - A) Keep those with "similar" name, or
            - B) Keep those with "similar" address.

        Next, keep only the intersection of A and B. If it is empty,
        keep the union.

        Finally, in the resulting set of probable schools, compute the
        geographic distance between all of them. If the max distance is
        lower than some threshold, then just pick a random sample from the
        set (we assume that all of them represent the same school).
        """
        school_set = self.schools
        check_area = True
        if school.city and school.city in self.schools_by_city:
                school_set = self.schools_by_city[school.city]
                # If we have the city, no need to check by the area
                check_area = False

        if check_area:
            if school.area and school.area in self.schools_by_area:
                    school_set = self.schools_by_area[school.area]

        same_name = self.match_name(school, school_set)
        same_address = self.match_address(school, school_set)

        same_name = set(same_name)
        same_address = set(same_address)
        intersection = set(same_name).intersection(same_address)
        if intersection:
            schools_set = intersection
            match = 'name AND address'
        else:
            schools_set = same_name.union(same_address)
            match = 'name OR address'

        return {'schools_set': schools_set, 'match': match}

    def match_name(self, target_place, school_set):
        results = []
        name = target_place.name
        if name:
            name = name.strip().lower()
            name_set = set(map(str.strip, name.split()))
            for school in school_set:
                school_name = school.name.strip().lower()
                school_name_set = set(map(str.strip, school_name.split()))
                #print name_set, school_name_set
                if school_name_set.issubset(name_set) or name_set.issubset(school_name_set):
                    school.dne_id = target_place.dne_id
                    results.append(school)
        return results

    def match_address(self, target_place, school_set):
        results = []
        address = target_place.address
        if address:
            address = address.strip().lower()
            address_set = set(map(str.strip, address.split()))
            for school in school_set:
                school_address = school.address.strip().lower()
                school_address_set = set(map(str.strip, school_address.split()))
                #print name_set, school_name_set
                if school_address_set.issubset(address_set) or address_set.issubset(school_address_set):
                    school.dne_id = target_place.dne_id
                    results.append(school)
        return results



    def match_area(self, target_place):
        results = []
        area = target_place.area
        if area:
            area = area.strip()
            area_name = DEPARTAMENTOS[int(area)]
            for school in self.schools:
                school_area = school.area.strip().upper()
                #print area_name, school_area
                if area_name == school_area:
                    results.append(school)
        return results

    def match_city(self, target_place):
        results = []
        city = target_place.city
        print city
        if city:
            city = city.strip().upper()
            for school in self.schools:
                school_city = school.city.strip().upper()
                if school_city == 'CORDOBA':
                    school_city = 'CAPITAL'
                print school_city
                if city == school_city:
                    results.append(school)
        return results
