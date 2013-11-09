#!/usr/bin/python

import csv
import json
import urllib2

"""
Convert CSV file with format:

"id","mesa_hasta","codigo_distrito","mesa_desde","codigo_postal","cant_mesas","direccion","seccion","circuito","localidad","distrito","establecimiento","dne_distrito_id","dne_seccion_id"

To output CSV file:

"Id","Lat","Lng"

Using Google Geocoding HTTP API to get GPS coordinates.
"""


def convertCSV(filepath):
    """
    does the whole conversion from full csv to id-lat-lng csv
    """
    csvList = fileToCSVList(filepath)
    name = filepath
    if filepath.endswith('.csv'):
        name = name[:-4]
    outFile = filepath.rstrip('.csv') + '.coords.csv'

    with open(outFile,'wb') as csvFile:
        writer = csv.writer(csvFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(['Id','Lat','Lng'])
        writer.writerows(csvList)
 
def makeGoogleUrl(address):
    a = address.replace(" ","+")
    url = 'https://maps.googleapis.com/maps/api/geocode/json?address=' + a + '&sensor=false'
    return url

def queryGeocode(address):
    """
    returns (latitude,longitude)
    """
    f = urllib2.urlopen( makeGoogleUrl(address) )
    x = f.read()
    j = json.loads(x)
    lat = j['results'][0]['geometry']['location']['lat']
    lng = j['results'][0]['geometry']['location']['lng']
    return (lat,lng)


def fileToCSVList(filepath):
    """
    filepath: csv file

    returns list of tuples (id,lat,lng)
    """
    f = open(filepath)
    reader = csv.reader(f)
    reader.next()     # drops title line
    result = []
    for line in reader:
        addr = lineToAddress(line)
        id   = line[0]
        (lat,lng) = queryGeocode(addr)
        result.append((id,lat,lng))
    f.close()
    return result

def lineToAddress(listLine):
    """
    Grabs a line from a csv file in the format of 80268-escuelas-segun-la-dne.csv

    returns address
    """
    address = listLine[6]
    city = listLine[9]
    if city == "CAPITAL":
        city = "CORDOBA CAPITAL"
    result = address + " , " + city + " , " + "CORDOBA, ARGENTINA"
    return result
