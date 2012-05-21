# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url
from django.http import HttpResponse
from piston.resource import Resource
from apps.api.handlers import CiudadHandler, CiudadLineaHandler, CiudadRecorridoHandler, LineaHandler, LineaRecorridoHandler, RecorridoHandler

def api_welcome(request):
    msg = """

           .----------------.
           |_I_I_I_I_I_I_I_I]___
   .::.    |  _  CualBondi   _  )
   ':::'' ='-(_)----------=-(_)-'

   Bienvenido a la API CualBondi!

    """
    return HttpResponse(msg, content_type="text/plain")


ciudades_handler = Resource(CiudadHandler, authentication=None)
ciudades_lineas_handler = Resource(CiudadLineaHandler, authentication=None)
ciudades_recorridos_handler = Resource(CiudadRecorridoHandler, authentication=None)
lineas_handler = Resource(LineaHandler, authentication=None)
lineas_recorridos_handler = Resource(LineaRecorridoHandler, authentication=None)
recorridos_handler = Resource(RecorridoHandler, authentication=None)

urlpatterns = patterns('',
    url(r'^$', api_welcome),

    url(r'^ciudades/$', ciudades_handler),
    url(r'^ciudades/(?P<id_ciudad>\d+)/$', ciudades_handler),
    url(r'^ciudades/(?P<id_ciudad>\d+)/lineas/$', ciudades_lineas_handler),
    url(r'^ciudades/(?P<id_ciudad>\d+)/recorridos/$', ciudades_recorridos_handler),

    url(r'^lineas/$', lineas_handler),
    url(r'^lineas/(?P<id_linea>\d+)/$', lineas_handler),
    url(r'^lineas/(?P<id_linea>\d+)/recorridos/$', lineas_recorridos_handler),

    url(r'^recorridos/$', recorridos_handler),
    url(r'^recorridos/(?P<id_recorrido>\d+)/$', recorridos_handler),
)


"""
ESTRUCTURA DE LAS URLs

[DONE].com/api/ciudades/
[DONE].com/api/ciudades/<id-ciudad>/
[DONE].com/api/ciudades/<id-ciudad>/lineas/
[DONE].com/api/ciudades/<id-ciudad>/recorridos/
.com/api/ciudades/<id-ciudad>/comercios/
.com/api/ciudades/<id-ciudad>/pois/

[DONE].com/api/lineas/
[DONE].com/api/lineas/<id-linea>/
[DONE].com/api/lineas/<id-linea>/recorridos/

.com/api/recorridos/
    GET:    origen (40.737102,-73.990318)   \   Buscar recorridos que vayan de "origen" a "destino"
            destino (40.737102,-73.990318)  /
            radio_origen (200)  \   Tolerancia a caminar, tanto al subir como al bajar
            radio_destino (350) /
            combinar (True) => Si es True buscar con transbordo
            --->query (Oeste 10 desde Olmos hasta centro)   =>  Busqueda de recorridos por nombre o lugares por dnd pasa
                tendria que ser una .com/api/catastro/?query=olmos
                y la query en recorridos solo hacerse con origen y destino en latlng
            pagina (4)  =>  Dada una busqueda, los resultados se paginan y se devuelve la pagina "pagina"
[DONE].com/api/recorridos/<id-recorrido>/
.com/api/recorridos/<id-recorrido>/paradas/
.com/api/recorridos/<id-recorrido>/paradas/<id-parada>/
.com/api/recorridos/<id-recorrido>/paradas/<id-parada>/horarios/
.com/api/recorridos/
    GET:    q (string de busqueda difusa)

.com/api/usuarios/
.com/api/usuarios/<id-usuario>/
.com/api/usuarios/<id-usuario>/custom_pois/
.com/api/usuarios/<id-usuario>/recorridos_favoritos/

"""


