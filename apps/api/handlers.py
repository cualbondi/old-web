from hashlib import sha1
from base64 import b64encode

from piston.handler import BaseHandler
from piston.utils import rc
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.gis.geos import Point
from django.core.cache import cache

from apps.core.models import Linea, Recorrido, Parada, Posicion
from apps.catastro.models import Ciudad, PuntoBusqueda
from settings import (RADIO_ORIGEN_DEFAULT, RADIO_DESTINO_DEFAULT,
                      CACHE_TIMEOUT, LONGITUD_PAGINA, USE_CACHE)

try:
    import json
except ImportError:
    from django.utils import simplejson as json



class CiudadHandler(BaseHandler):
    allowed_methods = ['GET']
    model = Ciudad
    exclude = ()

    def read(self, request, id_ciudad=None):
        if id_ciudad is None:
            return Ciudad.objects.all()
        else:
            try:
                return Ciudad.objects.get(id=id_ciudad)
            except ObjectDoesNotExist:
                return rc.NOT_FOUND


class CiudadLineaHandler(BaseHandler):
    allowed_methods = ['GET']
    exclude = ()

    def read(self, request, id_ciudad=None):
        if id_ciudad is None:
            return rc.BAD_REQUEST
        else:
            try:
                return Ciudad.objects.get(id=id_ciudad).lineas.all()
            except ObjectDoesNotExist:
                return rc.NOT_FOUND


class CiudadRecorridoHandler(BaseHandler):
    allowed_methods = ['GET']
    exclude = ()

    def read(self, request, id_ciudad=None):
        if id_ciudad is None:
            return rc.BAD_REQUEST
        else:
            try:
                return Ciudad.objects.get(id=id_ciudad).recorridos.all()
            except ObjectDoesNotExist:
                return rc.NOT_FOUND


class PosicionHandler(BaseHandler):
    allowed_methods = ['POST']

    def create(self, request, id_recorrido):
        try:
            recorrido = Recorrido.objects.get(id=id_recorrido)
        except Recorrido.DoesNotExist:
            return rc.NOT_FOUND

        lat = request.POST.get('lat')
        lng = request.POST.get('lng')
        if not all([lat, lng]):
            return rc.BAD_REQUEST

        try:
            lat = float(lat)
            lng = float(lng)
        except ValueError:
            return rc.BAD_REQUEST

        point = 'POINT({lng} {lat})'.format(lat=lat, lng=lng)

        uuid = request.POST.get('uuid')

        Posicion.objects.create(
            recorrido=recorrido,
            dispositivo_uuid=uuid,
            latlng=point
        )

        return rc.ALL_OK


class LineaHandler(BaseHandler):
    allowed_methods = ['GET']
    model = Linea
    exclude = ()

    def read(self, request, id_linea=None):
        if id_linea is None:
            # Devolver la lista completa de Lineas
            return Linea.objects.all()
        else:
            try:
                response = Linea.objects.get(id=id_linea)
                return response
            except ObjectDoesNotExist:
                return rc.NOT_FOUND


class LineaRecorridoHandler(BaseHandler):
    allowed_methods = ['GET']
    exclude = ()

    def read(self, request, id_linea=None):
        if id_linea is None:
            return rc.BAD_REQUEST
        else:
            try:
                l = Linea.objects.get(id=id_linea)
                response = Recorrido.objects.filter(linea=l)
                return response
            except ObjectDoesNotExist:
                return rc.NOT_FOUND


class RecorridoHandler(BaseHandler):
    allowed_methods = ['GET']
    model = Recorrido
    exclude = ()

    def _get_response_from_cache(self, origen, destino, radio_origen, radio_destino, combinar):
        concat = str(origen) + str(destino) + str(radio_origen) + str(radio_destino) + str(combinar)
        key = sha1(concat).hexdigest()
        response = cache.get(key)
        if not response:
            # No se encontro la response en la cache
            return None
        return response

    def _save_in_cache(self, origen, destino, radio_origen, radio_destino, combinar, recorridos):
        concat = str(origen) + str(destino) + str(radio_origen) + str(radio_destino) + str(combinar)
        key = sha1(concat).hexdigest()
        cache.set(key, recorridos, CACHE_TIMEOUT)

    def _paginar(self, recorridos, pagina):
        desde = (pagina - 1) * LONGITUD_PAGINA
        hasta = desde + LONGITUD_PAGINA
        return recorridos[desde:hasta]

    def _encriptar(self, response):
        for res in response.get('resultados'):
            for it in res.get('itinerario'):
                it['ruta_corta'] = b64encode(it['ruta_corta'])
        return response

    def read(self, request, id_recorrido=None):
        response = {'long_pagina': LONGITUD_PAGINA, 'cached': False}

        pagina = request.GET.get('p', 1)
        try:
            pagina = int(pagina)
        except ValueError:
            return rc.BAD_REQUEST
        response['p'] = pagina

        query = request.GET.get('q', None)
        ciudad_slug = request.GET.get('c', None)
        response['c'] = ciudad_slug

        if query is not None:
            qs = Recorrido.objects.fuzzy_like_trgm_query(query, ciudad_slug)
            recorridos = [
                {"id": r.id,
                  "itinerario": [
                        {
                            "id": r.id,
                            "ruta_corta": r.ruta_corta,
                            "long_bondi": r.long_ruta,
                            "long_pata": None,
                            "color_polilinea": r.color_polilinea,
                            "inicio": r.inicio,
                            "fin": r.fin,
                            "nombre": r.nombre,
                            "foto": r.foto,
                            "url": r.get_absolute_url(ciudad_slug)
                        }
                    ]
                }
                for r in list(qs)
            ]
            response['cant'] = len(recorridos)
            #if pagina >= response['cant_total']/LONGITUD_PAGINA+1:
            #    return rc.BAD_REQUEST
            # Filtrar todos los recorridos y devolver solo la pagina pedida
            response['resultados'] = self._paginar(recorridos, pagina)
            response['q'] = query
            return self._encriptar(response)

        elif id_recorrido is not None:
            # Me mandaron "id_recorrido", tengo que devolver ese solo recorrido.
            try:
                recorrido = Recorrido.objects.get(id=id_recorrido)
                response = {
                    'id': recorrido.id,
                    'nombre': recorrido.nombre,
                    'nombre_linea': recorrido.linea.nombre,
                    'color_polilinea': recorrido.color_polilinea,
                    'sentido': recorrido.sentido,
                    'descripcion': recorrido.descripcion,
                    'inicio': recorrido.inicio,
                    'fin': recorrido.fin,
                    'ruta': b64encode(recorrido.ruta.wkt),
                }
                return response
            except ObjectDoesNotExist:
                return rc.NOT_FOUND

        else:
            origen = request.GET.get('origen', None)
            destino = request.GET.get('destino', None)
            radio_origen = request.GET.get('radio_origen', RADIO_ORIGEN_DEFAULT)
            radio_destino = request.GET.get('radio_destino', RADIO_DESTINO_DEFAULT)
            query = request.GET.get('query', None)

            combinar = request.GET.get('combinar', 'false')
            if combinar == 'true':
                combinar = True
            elif combinar == 'false':
                combinar = False
            else:
                return rc.BAD_REQUEST

            if origen is not None and destino is not None:
                # Buscar geograficamente en base a origen y destino
                origen = str(origen).split(",")
                try:
                    latitud_origen = float(origen[1])
                    longitud_origen = float(origen[0])
                except ValueError:
                    return rc.BAD_REQUEST
                origen = Point(longitud_origen, latitud_origen)

                destino = str(destino).split(",")
                try:
                    latitud_destino = float(destino[1])
                    longitud_destino = float(destino[0])
                except ValueError:
                    return rc.BAD_REQUEST
                destino = Point(longitud_destino, latitud_destino)

                if USE_CACHE:
                    recorridos = self._get_response_from_cache(origen, destino,
                                    radio_origen, radio_destino, combinar)
                else:
                    recorridos = None

                if recorridos is not None:
                    response['cached'] = True
                else:
                    # No se encontro en la cache, hay que buscarlo en la DB.
                    if not combinar:
                        # Buscar SIN transbordo
                        recorridos = [
                            {"id": r.id,
                              "itinerario": [
                                    {
                                        "id": r.id,
                                        "ruta_corta": r.ruta_corta,
                                        "long_bondi": r.long_ruta,
                                        "long_pata": r.long_pata,
                                        "color_polilinea": r.color_polilinea,
                                        "inicio": r.inicio,
                                        "fin": r.fin,
                                        "nombre": r.nombre,
                                        "foto": r.foto,
                                        "p1": None if r.p1 == None else (lambda p:{"latlng": p.latlng.wkt, "codigo": p.codigo, "nombre": p.nombre } ) (Parada.objects.get(pk=r.p1)),
                                        "p2": None if r.p1 == None else (lambda p:{"latlng": p.latlng.wkt, "codigo": p.codigo, "nombre": p.nombre } ) (Parada.objects.get(pk=r.p2)),
                                        "url": r.get_absolute_url(ciudad_slug, r.lineaslug)
                                    }
                                ]
                            }
                            for r in Recorrido.objects.get_recorridos(origen, destino, radio_origen, radio_destino)
                        ]
                    else:
                        # Buscar CON transbordo
                        recorridos = [
                            {"id": str(r.id) + str(r.id2),
                              "itinerario": [
                                    {
                                        "id": r.id,
                                        "ruta_corta": r.ruta_corta,
                                        "long_bondi": r.long_ruta,
                                        "long_pata": r.long_pata,
                                        "color_polilinea": r.color_polilinea,
                                        "inicio": r.inicio,
                                        "fin": r.fin,
                                        "nombre": r.nombre,
                                        "foto": r.foto,
                                        "p1": None if r.p11ll == None else (lambda p:{"latlng": p.latlng.wkt, "codigo": p.codigo, "nombre": p.nombre } ) (Parada.objects.get(pk=r.p11ll)),
                                        "p2": None if r.p12ll == None else (lambda p:{"latlng": p.latlng.wkt, "codigo": p.codigo, "nombre": p.nombre } ) (Parada.objects.get(pk=r.p12ll)),
                                        "url": r.get_absolute_url(ciudad_slug, r.lineaslug, r.slug1)
                                    },
                                    {
                                        "id": r.id2,
                                        "ruta_corta": r.ruta_corta2,
                                        "long_bondi": r.long_ruta2,
                                        "long_pata": r.long_pata2,
                                        "color_polilinea": r.color_polilinea2,
                                        "inicio": r.inicio2,
                                        "fin": r.fin2,
                                        "nombre": r.nombre2,
                                        "foto": r.foto2,
                                        "p1": None if r.p21ll == None else (lambda p:{"latlng": p.latlng.wkt, "codigo": p.codigo, "nombre": p.nombre } ) (Parada.objects.get(pk=r.p21ll)),
                                        "p2": None if r.p22ll == None else (lambda p:{"latlng": p.latlng.wkt, "codigo": p.codigo, "nombre": p.nombre } ) (Parada.objects.get(pk=r.p22ll)),
                                        "url": r.get_absolute_url(ciudad_slug, r.lineaslug2, r.slug2)
                                    }
                                ]
                            }
                            for r in Recorrido.objects.get_recorridos_combinados_sin_paradas(origen, destino, radio_origen, radio_destino, 500)
                        ]
                        #for rec in recorridos
						#	rec["itinerario"][0]["p1"] = rec["itinerario"][0]["ruta_corta"] #parada mas cercana que se encuentre a menos de 100 metros del ultimo punto del recorrido 1
						#	rec["itinerario"][0]["p2"]
						#	rec["itinerario"][1]["p1"]
						#	rec["itinerario"][2]["p2"]

                    # Guardar los resultados calculados en memcached
                    if USE_CACHE:
                        self._save_in_cache(origen, destino, radio_origen, radio_destino, combinar, recorridos)
                response['cant'] = len(recorridos)
                #if pagina > response['cant']/LONGITUD_PAGINA:
                #    return rc.BAD_REQUEST
                # Filtrar todos los recorridos y devolver solo la pagina pedida
                response['resultados'] = self._paginar(recorridos, pagina)
                return self._encriptar(response)


class CatastroHandler(BaseHandler):
    allowed_methods = ['GET']
    #model = Calle
    exclude = ()

    def read(self, request):
        q = request.GET.get('query', None)
        ciudad_actual_slug = request.GET.get('ciudad', None)
        if q is None:
            return rc.BAD_REQUEST
        else:
            try:
                response = [
                    {
                        'nombre'    : r['nombre'],
                        'precision' : r['precision'],
                        'geom'      : r['geom'],
                        'tipo'      : r['tipo'],
                    }
                    for r in PuntoBusqueda.objects.buscar(q, ciudad_actual_slug)
                ]
                return response
            except ObjectDoesNotExist:
                return []


class CalleHandler(BaseHandler):
    allowed_methods = ['GET']
    #model = Calle
    exclude = ()

    def read(self, request):
        calle1 = request.GET.get('calle1', None)
        calle2 = request.GET.get('calle2', None)
        if calle1 is None or calle2 is None:
            return rc.BAD_REQUEST
        else:
            try:
                response = PuntoBusqueda.objects.interseccion(calle1, calle2)
                return response
            except ObjectDoesNotExist:
                return rc.NOT_FOUND
