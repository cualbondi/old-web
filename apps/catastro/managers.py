# -*- coding: UTF-8 -*-
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
        result = []
        result += self._buscar_calles(query)
        result += self._buscar_comercios(query)
        return result

    def interseccion(self, calle1, calle2):
        params = {'calle1':calle1, 'calle2':calle2}
        query = """
            SELECT DISTINCT
                SEL1.nom as nom1,
                SEL2.nom as nom2,
                SEL2.similarity + SEL1.similarity as total_similarity,
                SEL1.similarity as s1,
                SEL2.similarity as s2,
                ST_AsText(ST_Intersection(SEL1.way, SEL2.way)) as int
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
                on ( ST_Intersects(SEL1.way, SEL2.way) )
            ORDER BY
                SEL2.similarity + SEL1.similarity DESC
            LIMIT 10
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
