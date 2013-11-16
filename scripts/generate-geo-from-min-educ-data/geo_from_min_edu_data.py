#!/usr/bin/python
# -*- coding: utf-8 -*-
__authors__ = 'Carlos de la Torre, Andrés Blanco'


import csv
import logging as log
from collections import defaultdict

from utils import normalize_str


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
                area=school_data[8],  # departamento
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

    def match_by_field(self, target_place, school_set, field_name):
        results = []
        field_value = getattr(target_place, field_name)
        if field_value:
            field_value_set = set(field_value.split())
            for school in school_set:
                school_field_val_set = set(getattr(school, field_name).split())
                if (school_field_val_set.issubset(field_value_set) or
                        field_value_set.issubset(school_field_val_set)):
                    results.append(school)
        return results

    def match_name(self, target_place, school_set):
        return self.match_by_field(target_place, school_set, 'name')

    def match_address(self, target_place, school_set):
        return self.match_by_field(target_place, school_set, 'address')

