# -*- coding: utf-8 -*-
#!/usr/bin/python

import csv
import json

def remove_duplicates(geolist):
    used_ids = set()
    new_geolist = []
    for entry in geolist:
        id = entry['properties']['id']
        if entry['properties']['id'] not in used_ids:
            new_geolist.append(entry)
            used_ids.add(id)

    return new_geolist


# Read CSV with geocodes and build a dictionary:
geocodes = {}
duplicates = []
for geocode_input_filename in ['data/80268-escuelas-segun-la-dne.capital.coords.csv', 'input/escuelas-DNE-con-GEO-del-MinEduc.csv']:
#for geocode_input_filename in ['data/80268-escuelas-segun-la-dne.capital.coords.csv']:
    #geocode_input_filename = 'data/locations.csv'
    #geocode_input_filename = 'data/80268-escuelas-segun-la-dne.capital.coords.csv'
    geocode_input_file = open(geocode_input_filename)
    geocode_csvreader = csv.reader(geocode_input_file)
    geocode_csvreader.next() # skip header
    for row in geocode_csvreader:
        id, latitude, longitude = row
        if int(id) in geocodes:
            duplicates.append(int(id))
        elif latitude and longitude:
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
        
        geocode_list.append(d2)

# Add dummy school:
dummy_school = {
                "type": "Feature", 
                "properties": { 
                    "id": 0, 
                    "mesa_desde": "0", 
                    "mesa_hasta": "0", 
                    #"codigo_dis": "4", 
                    #"codigo_pos": "5000", 
                    #"cant_mesas": "7", 
                    "direccion": "", 
                    "seccion": "", 
                    "circuito": "", 
                    #"localidad": "CAPITAL", 
                    #"distrito": "CÓRDOBA", 
                    "establecim": u"Escuelas sin geolocalización", 
                    #"dne_distri": 4, 
                    #"dne_seccio": 1, 
                    "score": 1.0 }, 
                "geometry": { 
                    "type": "Point", 
                    # Laguna Mar Chiquita :P
                    # http://maps.googleapis.com/maps/api/geocode/json?address=laguna+mar+chiquita&sensor=false&language=es&region=ar
                    "coordinates": [ -30.4963614, -62.7323884 ] 
                    #"coordinates": [ -64.189654456840955, -31.414637452814794 ]
                    } }
geocode_list.append(dummy_school)

# Integrate with existing JSON
#import codecs
#f = codecs.open('input/escuelas.final.972.json', encoding='utf8')
geojson_input_filename = 'input/escuelas.finales.972.json'
geojson_input_file = open(geojson_input_filename)
geojson_input = json.load(geojson_input_file)
geomanual_list = geojson_input[u'features']
known_idset = set(x['properties']['id'] for x in geomanual_list)

geomanual_list = remove_duplicates(geomanual_list)

unknown = set()
for entry in geocode_list:
    i = int(entry['properties']['id'])
    if i not in known_idset:
        unknown.add(i)
        geomanual_list.append(entry)
print 'Added new {0} entries (including the dummy school).'.format(len(unknown))

# Write new JSON
output_filename = 'input/locales_cordoba_geocode.geojson'
output_file = open(output_filename, 'w')
geojson_output = {'type': 'FeaturesCollection', 'features': geomanual_list }
#geojson_output = geojson_input
json.dump(geojson_output, output_file, indent=2)

output_file.close()
            
