# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url
from django.http import HttpResponse
from piston.resource import Resource
from apps.api.handlers import LineaHandler, RecorridoHandler

def api_welcome(request):
    msg = """

           .----------------.
           |_I_I_I_I_I_I_I_I]___
   .::.    |  _  CualBondi   _  )
   ':::'' ='-(_)----------=-(_)-'

   Bienvenido a la API CualBondi!

    """
    return HttpResponse(msg, content_type="text/plain")


lineas_handler = Resource(LineaHandler, authentication=None)
recorridos_handler = Resource(RecorridoHandler, authentication=None)

urlpatterns = patterns('',
    url(r'^$', api_welcome),

    url(r'^lineas/$', lineas_handler),
    url(r'^lineas/(?P<id_linea>\d+)/$', lineas_handler),

    url(r'^recorridos/$', recorridos_handler),
    url(r'^recorridos/(?P<id_recorrido>\d+)/$', recorridos_handler),
)
