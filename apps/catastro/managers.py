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
