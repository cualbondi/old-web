# -*- coding: UTF-8 -*-
from django.shortcuts import (get_object_or_404, render_to_response,
                              redirect, render)
from django.http import HttpResponse
from django.template import RequestContext

from apps.catastro.models import Poi
from apps.core.models import Recorrido
from django.contrib.gis.measure import D


def poi(request, slug=None):
    if request.method == 'GET':
        poi = get_object_or_404(Poi, slug=slug)
        recorridos = Recorrido.objects.filter(ruta__dwithin=(poi.latlng, 0.001)).select_related('linea').order_by('linea__nombre', 'nombre')
        return render_to_response(
            'catastro/ver_poi.html',
            {
                'poi': poi,
                'recorridos': recorridos,
            },
            context_instance=RequestContext(request)
        )
    else:
        return HttpResponse(status=501)
    
def zona(request, slug=None):
    return HttpResponse(status=504)