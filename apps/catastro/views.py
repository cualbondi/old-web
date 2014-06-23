# -*- coding: UTF-8 -*-
from django.shortcuts import (get_object_or_404, render_to_response,
                              redirect, render)
from django.http import HttpResponse
from django.template import RequestContext

from apps.catastro.models import Poi, Ciudad
from apps.core.models import Recorrido
from django.contrib.gis.measure import D


def poi(request, slug=None):
    if request.method == 'GET':
        poi = get_object_or_404(Poi, slug=slug)
        recorridos = Recorrido.objects.filter(ruta__dwithin=(poi.latlng, 0.00111)).select_related('linea').order_by('linea__nombre', 'nombre')
        pois = Poi.objects.filter(latlng__dwithin=(poi.latlng, 0.111)).exclude(id=poi.id)
        return render_to_response(
            'catastro/ver_poi.html',
            {
                'ciudad_actual': Ciudad.objects.filter(poligono__intersects=poi.latlng),
                'poi': poi,
                'recorridos': recorridos,
                'pois': pois
            },
            context_instance=RequestContext(request)
        )
    else:
        return HttpResponse(status=501)
    
def zona(request, slug=None):
    return HttpResponse(status=504)