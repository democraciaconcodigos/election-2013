#!/usr/bin/python
# -*- encoding: utf-8 -*-

"""
Convert CSV file with format:

"id","mesa_hasta","codigo_distrito","mesa_desde","codigo_postal","cant_mesas","direccion","seccion","circuito","localidad","distrito","establecimiento","dne_distrito_id","dne_seccion_id"

To output CSV file that only has schools from cities we know Google has the map:

  * Córdoba Capital
  * Rio Cuarto
  * Villa María
"""

import csv
import urllib2

def generateCapitalCSV(filepath):
    """
    only keep Córdoba Capital lines from input CSV
    """
    name = filepath
    if name.endswith('.csv'):
        name = name[:-4]
    outFile = name + '.capital.csv'

    csvList = fileToCSVListCapital(filepath)
    with open(outFile,'wb') as csvFile:
        writer = csv.writer(csvFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerows(csvList)

known = ['CAPITAL','RIO CUARTO','VILLA MARIA','RIO TERCERO','ONCATIVO','OLIVA','VILLA CARLOS PAZ',
         'UNQUILLO','MENDIOLAZA', 'MARCOS JUAREZ','LABOULAYE','VICUÑA MACKENNA',
         'MALVINAS ARGENTINAS','VILLA ALLENDE']:

def tieneMapa(city):
    if city in known:
        return True
    return False 

def fileToCSVListCapital(filepath):
    """
    filepath -> csv file with only Córdoba Capital lines
    """
    f = open(filepath)
    reader = csv.reader(f)
    primeraLinea = reader.next()     # title line
    result = [primeraLinea]
    for line in reader:
        if tieneMapa(line[9])
            result.append(line)
    f.close()
    return result

