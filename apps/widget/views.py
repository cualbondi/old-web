from apps.catastro.models import Ciudad
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from django.conf import settings
from django.contrib.sites.models import Site

def v1_busqueda(request, extension):
    if request.method == 'GET':
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
                        content_type="application/x-JavaScript")                
        else:
            return HttpResponse(status=403)
    else:
        return HttpResponse(status=501)

def not_found(request):
    return HttpResponse(status=404)

def test(request):
    return render_to_response('widget/test.html',
                        { 'current_site': Site.objects.get_current()})
