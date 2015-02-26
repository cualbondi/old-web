from apps.catastro.models import Ciudad
from apps.core.models import Recorrido
from django.contrib.gis.geos import Point
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from django.conf import settings
from django.contrib.sites.models import Site

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET

@csrf_exempt
@require_GET
def v1_busqueda(request, extension):
    if request.GET.get("key") == '123456789':
        if extension == "html":
            if request.GET.get("ciudad"):
                ci = Ciudad.objects.get(slug=request.GET.get("ciudad"))
                ciudades = []
            else:
                ci = None
                ciudades = Ciudad.objects.all()
            return render_to_response('widget/v1/busqueda.html',
                { 'ciudades': ciudades,
                  'ciudad'  : ci      },
                context_instance=RequestContext(request))
        else:
            if extension == "js":
                current_site = Site.objects.get_current()
                try:
                    ci = Ciudad.objects.get(slug=request.GET.get("ciudad"))
                    ciudad_arg = "&ciudad="+ci.slug
                except:
                    ciudad_arg = ""
                return render_to_response('widget/v1/busqueda.js',
                    { 'current_site': current_site,
                      'ciudad_arg'  : ciudad_arg  },
                    context_instance=RequestContext(request), 
                    #content_type="application/x-JavaScript") #django => 1.5
                    mimetype="application/x-JavaScript") #django < 1.5
    else:
        return HttpResponse(status=403)


@csrf_exempt
@require_GET
def v1_lineas(request, extension):
    if request.GET.get("key") == '123456789':
        if extension == "html":
            try: 
                lat = float(request.GET.get("lat", "NaN"))
                lon = float(request.GET.get("lon", "NaN"))
                rad = int(request.GET.get("rad", "NaN"))
            except:
                return HttpResponse(status=501)
            print_ramales = request.GET.get("ramales") == "true"
            recorridos = Recorrido.objects.select_related('linea').filter(ruta__dwithin=(Point(lon, lat), 0.1), ruta__distance_lt=(Point(lon, lat), rad))
            if not print_ramales:
                recorridos = list(set([x.linea for x in recorridos]))
            return render_to_response('widget/v1/lineas.html',
                {
                    'listado': recorridos,
                    'print_ramales': print_ramales,
                },
                context_instance=RequestContext(request))
        else:
            if extension == "js":
                if request.GET.get("lat") and request.GET.get("lon") and request.GET.get("rad"):
                    current_site = Site.objects.get_current()
                    return render_to_response('widget/v1/lineas.js',
                        { 'current_site': current_site },
                        context_instance=RequestContext(request), 
                        #content_type="application/x-JavaScript") #django => 1.5
                        mimetype="application/x-JavaScript") #django < 1.5
                else:
                    return HttpResponse(status=501)
    else:
        return HttpResponse(status=403)
    

def not_found(request):
    return HttpResponse(status=404)

def test(request):
    return render_to_response('widget/test.html',
                        { 'current_site': Site.objects.get_current()})
