"""
"features": [ {
    "type": "Feature", 
    "properties": {
        "id": 6089,         <- 'id'
        "mesa_hasta": "7",  <- 'mesa_hasta'
        "codigo_dis": "4",  <- 'codigo_distrito'
        "mesa_desde": "1",  <- 'mesa_desde'
        "codigo_pos": #"5000", <- 'codig_postal'
        "cant_mesas": "7",  <- 'cant_mesas'
        "direccion": "DEAN FUNES 417", <- 'direccion'
        "seccion": "1", <- 'seccion'
        "circuito": "00001",  <- 'circuito'
        "localidad": "CAPITAL", <- 'localidad'
        "distrito": "CÓRDOBA", <- 'distrito'
        "establecim": "CENTRO EDUC.NIVEL MEDIO ADULTO", <- 'establecimiento'
        "dne_distri": 4,  <- 'dne_distrito_id'
        "dne_seccio": 1,  <- 'dne_seccion_id'
        "score": 1.0 <- 1.0
    },
    "geometry": { 
            "type": "Point", <- "Point"
            "coordinates": [ -64.189654456840955, -31.414637452814794 ] <- latitude, longitude
    }
}
"""

import codecs
f = codecs.open('input/escuelas.final.972.json', encoding='utf8')
j = json.load(f)
g = codecs.open('output.csv', 'w', encoding='utf8')
fieldnames = [u'latitude', u'longitude'] + j['features'][0]['properties'].keys()
writer = csv.DictWriter(g, fieldnames)

for d in j['features']:
    d2 = {}
    for p in props:
        d2[p] = d['properties'][p]
    d2[u'longitude'] = d['geometry']['coordinates'][1]
    d2[u'latitude'] = d['geometry']['coordinates'][0]
    d3 = {}
    for x in d2:
        if isinstance(d2[x], unicode):
            d3[x] = codecs.encode(d2[x], 'utf8')
        else:
            d3[x] = d2[x]
            
    writer.writerow(d3)

