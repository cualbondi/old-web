# -*- coding: UTF-8 -*-
from django.db.models import get_model
from django.contrib.gis.db import models
import re

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
            pass

    def interseccion(self, calle1, calle2):
        params = {'calle1':calle1, 'calle2':calle2}
        query = """
            SELECT DISTINCT
                SEL1.nom || ' y ' || SEL2.nom as nombre,
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
            ORDER BY
                precision DESC
            LIMIT 5
        ;"""
        query_set = self.raw(query, params)
        return list(query_set)


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
