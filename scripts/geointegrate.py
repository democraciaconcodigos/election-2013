#!/usr/bin/python

import csv
import json

# Read CSV with geocodes and build a dictionary:
#geocode_input_filename = 'data/locations.csv'
geocode_input_filename = 'data/80268-escuelas-segun-la-dne.capital.coords.csv'
geocode_input_file = open(geocode_input_filename)
geocode_csvreader = csv.reader(geocode_input_file)
geocode_csvreader.next() # skip header
geocodes = {}
for row in geocode_csvreader:
    id, latitude, longitude = row
    geocodes[int(id)] = (float(latitude), float(longitude))


# Read voting locals
locals_input_filename ='data/80268-escuelas-segun-la-dne.csv'
locals_file = open(locals_input_filename)
#locals_csvreader = csv.reader(locals_file)
locals_csvreader = csv.DictReader(locals_file)

geocode_list = []
for d in locals_csvreader:
    id = int(d['id'])
    if id in geocodes:
        # only places with a geocode:
        latitude, longitude = geocodes[id]
        
        d2 = {}
        d2['type'] = 'Feature'
        d2['properties'] = {}
        d2['properties']['score'] = 1.0
        
        for k, v in d.items():
            # truncate key to 10 chars:
            d2['properties'][k[:10]] = v
        
        d2['geometry'] = {}
        d2['geometry']['type'] = 'Point'
        d2['geometry']['coordinates'] = [latitude, longitude]
        
        geocode_list += [d2]

# Integrate with existing JSON
#import codecs
#f = codecs.open('input/escuelas.final.972.json', encoding='utf8')
geojson_input_filename = 'input/escuelas.finales.972.json'
geojson_input_file = open(geojson_input_filename)
geojson_input = json.load(geojson_input_file)
geomanual_list = geojson_input[u'features']
known_idset = set(x['properties']['id'] for x in geomanual_list)

unknown = set()
for entry in geocode_list:
    i = int(entry['properties']['id'])
    if i not in known_idset:
        unknown.add(i)
        geomanual_list.append(entry)
print 'Added new {0} entries.'.format(len(unknown))

# Write new JSON
output_filename = 'input/locales_cordoba_geocode.geojson'
output_file = open(output_filename, 'w')
"""geojson = {'type': 'FeaturesCollection',
           'features': output_list }"""
geojson_output = geojson_input
json.dump(geojson_output, output_file)

output_file.close()

