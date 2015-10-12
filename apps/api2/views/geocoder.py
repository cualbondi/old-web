# -*- coding: utf-8 -*-
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework import exceptions
from rest_framework.response import Response

from apps.catastro.models import PuntoBusqueda
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.gis.geos import GEOSGeometry
import json


class GeocoderSerializer(serializers.Serializer):
    nombre = serializers.ReadOnlyField()
    geom = serializers.SerializerMethodField()
    precision = serializers.ReadOnlyField()
    tipo = serializers.ReadOnlyField()

    def get_geom(self, obj):
        return json.loads(GEOSGeometry(obj['geom'], srid=4326).geojson)


class GeocoderViewSet(viewsets.GenericViewSet):
    """
        Parámetros querystring

         - `q` obligatorio: string a geobuscar
         - `ciudad` opcional: slug de la ciudad donde buscar

        Busca el valor del parámetro `q`
        usando varias fuentes según el formato del string de búsqueda

         - **Geocoder** [Google] (ej: [12 1234](/api/v2/geocoder/?q=12%201234&ciudad=la-plata) / [12 n 1234](/api/v2/geocoder/?q=12%20n%201234&ciudad=la-plata) / [centenario 1234](/api/v2/geocoder/?q=centenario%20n%201234&ciudad=la-plata))
         - **Intersección de calles** [OSM] (ej: [12 y 62](/api/v2/geocoder/?q=12%20y%2062&ciudad=la-plata) / perón y alvarez)
         - **POI (Point Of Interest)** [OSM y Cualbondi] (ej: plaza rocha / hospital)
         - **Zona (Barrio / Ciudad)** [Cualbondi] (ej: berisso / colegiales) (devuelve geocentro)

        El geocoder usa varias fuentes y técnicas, entre ellas fuzzy search.
        Por esto, devuelve un valor de "precision" para cada registro.

        Utiliza el parámetro `ciudad` para dar mas contexto al lugar
        donde se está buscando. Esto ayuda a evitar ambigüedad en la búsqueda
        ya que puede haber dos calles que se llamen igual en distintas ciudades
        pero no restringe la búsqueda a esa ciudad (sólo altera la precisión)
    """
    serializer_class = GeocoderSerializer

    def list(self, request):
        q = request.query_params.get('q', None)
        ciudad_actual_slug = request.query_params.get('ciudad', None)
        if q is None:
            raise exceptions.ValidationError(
                {'detail': 'expected \'q\' parameter'}
            )
        else:
            try:
                return Response(
                    GeocoderSerializer(
                        PuntoBusqueda.objects.buscar(q, ciudad_actual_slug),
                        many=True
                    ).data
                )
            except ObjectDoesNotExist:
                return Response([])
