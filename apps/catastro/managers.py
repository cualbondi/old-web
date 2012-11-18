# -*- coding: UTF-8 -*-
import re
from django.db.models import get_model
from django.contrib.gis.db import models


class PuntoBusquedaManager(models.Manager):
    """ Este manager se encarga de convertir una query tipo texto
    en una lista de puntos geográficos que pueden ser usados como origen
    o destino de una búsqueda. Los datos tenidos en cuenta son:
    **Interseccion de calles
    **Comercios
    **Pois
    **CustomPois
    **Google Geocoder

    A futuro puede sumarse:
    **Paradas

    """

    def buscar(self, query):
        if query is not None:
            calles = re.split(' y ', query)
            if len(calles) == 2:
                return self.interseccion(calles[0], calles[1])
            else:
                direccion = re.split(' n ', query)
                if len(direccion) == 2:
                    return self.direccionPostal(direccion[0], direccion[1])
                else:
                    return self.poi(query)
        else:
            pass

    def interseccion(self, calle1, calle2):
        params = {'calle1': calle1, 'calle2': calle2}
#            SELECT nombre || ", " ci.nombre
        query = """
                SELECT DISTINCT
                    SEL1.nom || ' y ' || SEL2.nom || coalesce(', ' || z.name, '') as nombre,
                    ST_AsText(ST_Intersection(SEL1.way, SEL2.way)) as geom,
                    ( SEL2.similarity + SEL1.similarity ) / 2 as precision,
                    'interseccion' as tipo
                FROM
                    (
                        SELECT
                            nom,
                            similarity(nom_normal, %(calle1)s) as similarity,
                            way
                        FROM
                            catastro_calle as c
                        WHERE
                            nom_normal %% %(calle1)s
                    ) AS SEL1
                    join
                    (
                        SELECT
                            nom,
                            similarity(nom_normal, %(calle2)s) as similarity,
                            way
                        FROM
                            catastro_calle as c
                        WHERE
                            nom_normal %% %(calle2)s
                    ) AS SEL2
                    on ( ST_Intersects(SEL1.way, SEL2.way)
                        and ST_GeometryType(ST_Intersection(SEL1.way, SEL2.way)::Geometry)='ST_Point')

                    left outer join
                        catastro_zona as z
                        on ST_Intersects(z.geo, ST_Intersection(SEL1.way, SEL2.way))

                ORDER BY
                    precision DESC
                LIMIT 5
        ;"""
        query_set = self.raw(query, params)
        return list(query_set)

    def poi(self, nombre):
        params = {'nombre': nombre}
        query = """
            SELECT
                nom as nombre,
                similarity(nom_normal, %(nombre)s) as precision,
                ST_AsText(latlng) as geom,
                'interseccion' as tipo
            FROM
                catastro_poi as p
            WHERE
                nom_normal %% %(nombre)s
            ORDER BY
                precision DESC
            LIMIT 5
        ;"""
        query_set = self.raw(query, params)
        return list(query_set)

    def direccionPostal(self, calle, numero):
        # http://stackoverflow.com/questions/9884475/using-google-maps-geocoder-from-python-with-urllib2
        import urllib2
        import json
        add = calle + " " + numero + ", La Plata, Argentina"
        add = urllib2.quote(add)
        geocode_url = "http://maps.googleapis.com/maps/api/geocode/json?address=%s&sensor=false" % add
        req = urllib2.urlopen(geocode_url)
        res = json.loads(req.read())
        # comprehension para parsear lo devuelto por el google geocoder
        ret = [{'nombre': i["address_components"][1]["long_name"] + u" N°" + i["address_components"][0]["long_name"] + ", " + i["address_components"][2]["long_name"],
                  'precision': "1",
                  'geom': "POINT(" + str(i["geometry"]["location"]["lng"]) + " " + str(i["geometry"]["location"]["lat"]) + ")",
                  'tipo': "direccionPostal"}
                for i in res["results"]
                    if "street_address" in i["types"]
              ]
        return ret

    def _buscar_calles(self, query):
        calle_model = get_model('catastro', 'Calle')
        return calle_model.objects.all()

    def _buscar_comercios(self, query):
        comercio_model = get_model('core', 'Comercio')
        return comercio_model.objects.all()

    def _buscar_pois(self, query):
        pass

    def _buscar_custom_pois(self, query):
        pass

    def _buscar_google_geocoder(self, query):
        pass
