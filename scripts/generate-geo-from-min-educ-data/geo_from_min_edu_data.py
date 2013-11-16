#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv
import logging as log
import math

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


class School(object):
    def __init__(self, name='', address='', city='', area='', province='CORDOBA', postal_code='', dne_id=None,
                 min_edu_id=None, lat=None, lon=None):
        self.name = name
        self.address = address
        self.city = city
        self.area = area  # Departamento
        self.province = province # Always CORDOBA in Min. Edu. data
        self.postal_code = postal_code
        self.dne_id = dne_id
        self.min_edu_id = min_edu_id
        self.lat = lat
        self.lon = lon

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
                    # The distance between the origin and target schools is higher
                    # than the acceptable threshold.
                    return None
        # If this point is reached, then all the given schools are within the given threshold
        # then we just return a 'random' one.
        if cnt:
            log.debug("Avg distance: %f (%i) points", s*1.0 / cnt, cnt)
        return schools[0]

    def __str__(self):
        return "%s" % (self.name)


class MinEducHelper(object):
    def __init__(self, data_fname):
        self.csv_reader = csv.reader(open(data_fname, 'rU'), delimiter=',')
        self.schools = []
        for school_data in self.csv_reader:
            lat = school_data[10]
            lon = school_data[11]
            if lat and lon:
                school = School(
                    min_edu_id=school_data[0],  # Min. Edu. ID
                    name=school_data[1],  # nombre
                    address=school_data[4],  # domicilio
                    city=school_data[7],  # localidad
                    area=school_data[8], # departamento
                    postal_code=school_data[5],  # cp
                    lat=school_data[10],  # lat
                    lon=school_data[11],  # lon
                )
                self.schools.append(school)
            else:
                log.warning("Invalid lat/lon data: %s (id %s)",
                            school_data[1], school_data[0])

        self.schools_by_city = {}
        self.schools_by_area = {}
        for school in self.schools:
            school_city = school.city.lower().strip()
            if school_city == 'cordoba':
                school_city = 'capital'
            if school_city not in self.schools_by_city:
               self.schools_by_city[school_city] = [school]
            else:
                self.schools_by_city[school_city].append( school )

            school_area = school.area.lower().strip()
            if school_area not in self.schools_by_area:
               self.schools_by_area[school_area] = [school]
            else:
                self.schools_by_area[school_area].append( school )


    def guess_geo(self, data):
        """Try and guess the geolocation of the given data"""
        # DNE data[13] is called dne_seccion_id and is the ID of the 'area' (departamento).
        dne_place_id = data[0]
        voting_place = School(
            name=data[11],  # establecimiento
            address=data[6],  # direccion
            city=data[9],  # localidad
            area=data[13],  # dne_seccion_id
            province=data[10],  # distrito
            postal_code=data[4],  # codigo_postal
            dne_id=data[0],  # D.N.E. ID
        )

        results = self.match_name(voting_place)
        voting_place.applied_filters['name'] = results

        results = self.match_address(voting_place)
        voting_place.applied_filters['address'] = results

        #results = self.match_area(voting_place)
        #voting_place.applied_filters['area'] = results
        #
        #results = self.match_city(voting_place)
        #voting_place.applied_filters['city'] = results

        return voting_place

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
