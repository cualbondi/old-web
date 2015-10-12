# -*- coding: utf-8 -*-
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework import exceptions
from rest_framework import pagination
from rest_framework.response import Response

from apps.core.models import Recorrido
from django.contrib.gis.geos import GEOSGeometry
from base64 import b64encode
from django.contrib.gis.measure import D


class CBPagination(pagination.PageNumberPagination):
    page_size = 5


class RouterResultSerializer(serializers.Serializer):

    def to_representation(self, obj):
        if not hasattr(obj, 'id2'):
            return {
                "id": obj.id,
                "itinerario": [
                    {
                        "id": obj.id,
                        "ruta_corta": b64encode(obj.ruta_corta),
                        "long_bondi": obj.long_ruta,
                        "long_pata": obj.long_pata,
                        "color_polilinea": obj.color_polilinea,
                        "inicio": obj.inicio,
                        "fin": obj.fin,
                        "nombre": obj.nombre,
                        "foto": obj.foto,
                        "p1": getParada(obj.p1),
                        "p2": getParada(obj.p2),
                        "url": obj.get_absolute_url()
                    }
                ]
            }
        else:
            return {
                "id": str(obj.id) + str(obj.id2),
                "itinerario": [
                    {
                        "id": obj.id,
                        "ruta_corta": b64encode(obj.ruta_corta),
                        "long_bondi": obj.long_ruta,
                        "long_pata": obj.long_pata,
                        "color_polilinea": obj.color_polilinea,
                        "inicio": obj.inicio,
                        "fin": obj.fin,
                        "nombre": obj.nombre,
                        "foto": obj.foto,
                        "p1": getParada(obj.p11ll),
                        "p2": getParada(obj.p12ll),
                        "url": obj.get_absolute_url(None, None, obj.slug)
                    },
                    {
                        "id": obj.id2,
                        "ruta_corta": b64encode(obj.ruta_corta2),
                        "long_bondi": obj.long_ruta2,
                        "long_pata": obj.long_pata2,
                        "color_polilinea": obj.color_polilinea2,
                        "inicio": obj.inicio2,
                        "fin": obj.fin2,
                        "nombre": obj.nombre2,
                        "foto": obj.foto2,
                        "p1": getParada(obj.p21ll),
                        "p2": getParada(obj.p22ll),
                        "url": obj.get_absolute_url(None, None, obj.slug2)
                    }
                ]
            }


def getParada(parada_id):
    if parada_id is None:
        return None
    else:
        p = Parada.objects.get(pk=obj.parada_id)
        return {
            "latlng": p.latlng.geojson,
            "codigo": p.codigo,
            "nombre": p.nombre
        }


class RecorridoSerializer(serializers.Serializer):

    def to_representation(self, obj):
        return {
            'id': obj.id,
            'nombre': obj.nombre,
            'nombre_linea': obj.linea.nombre,
            'color_polilinea': obj.color_polilinea,
            'sentido': obj.sentido,
            'descripcion': obj.descripcion,
            'inicio': obj.inicio,
            'fin': obj.fin,
            'ruta': b64encode(obj.ruta.wkt),
        }


class RecorridoViewSet(viewsets.ModelViewSet):
    """
        Parametros querystring

         - `l` lista de puntos (lon,lat floats) y radio (int: metros) en orden
            por los cuales se busca que pase una ruta. Ejemplos a continuación:

            - `l=55.3324,-55.4433,200`
            - `l=55.3324,-55.4433,200|55.1112,-55.3334,300`
            - [live example](http://192.168.2.100/api/v2/recorrido/?l=-57.957258224487305,-34.92056351681724,200|-57.94755935668945,-34.92556010123052,200)

         - `t` true/false: buscar con transbordo (true). `false` por defecto.
         - `q` string: para búsqueda por nombre de recorrido (fuzzy search)
         - `c` string: ciudad-slug, requerido cuando se usa `q`
    """

    serializer_class = RecorridoSerializer
    queryset = Recorrido.objects.all()
    pagination_class = CBPagination

    def list(self, request):
        q = request.query_params.get('q', None)
        l = request.query_params.get('l', None)
        t = request.query_params.get('t', 'false')
        c = request.query_params.get('c', None)

        if (q is None) == (l is None):
            raise exceptions.ValidationError(
                {'detail': '\'q\' or \'l\' parameter expected (but not both)'}
            )

        if t == 'true':
            t = True
        elif t == 'false':
            t = False
        else:
            raise exceptions.ValidationError(
                {'detail': '\'t\' parameter malformed: Expected \'true\' or \'false\''}
            )

        if l is not None:
            try:
                lp = []  # lista de puntos
                for p in l.split('|'):
                    ps = p.split(',')
                    lp.append({'p': GEOSGeometry('POINT({} {})'.format(ps[0], ps[1]), srid=4326), 'r': int(ps[2])})
            except:
                raise exceptions.ValidationError(
                    {'detail': '\'l\' parameter malformed'}
                )
            if len(lp) > 2:
                raise exceptions.ValidationError(
                    {'detail': '\'l\' parameter accepts up to 2 points max.'}
                )

            if len(lp) == 1:
                page = self.paginate_queryset(Recorrido.objects.filter(ruta__distance_lte=(lp[0]['p'], D(m=lp[0]['r']))))
                if page is not None:
                    serializer = self.get_serializer(page, many=True)
                    return self.get_paginated_response(serializer.data)
                else:
                    return Response([])

            if not t:
                # sin transbordo
                routerResults = Recorrido.objects.get_recorridos(lp[0]['p'], lp[1]['p'], lp[0]['r'], lp[1]['r'])
            else:
                # con transbordo
                routerResults = Recorrido.objects.get_recorridos_combinados_sin_paradas(lp[0]['p'], lp[1]['p'], lp[0]['r'], lp[1]['r'], 500)

            page = self.paginate_queryset(routerResults)
            if page is not None:
                serializer = RouterResultSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            else:
                return Response([])

        if q is not None:
            if c is None:
                raise exceptions.ValidationError(
                    {'detail': '\'c\' parameter is required when using `q` parameter'}
                )
            page = self.paginate_queryset(list(Recorrido.objects.fuzzy_like_trgm_query(q, c)))
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            else:
                return Response([])
