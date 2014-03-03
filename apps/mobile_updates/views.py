from django.http import HttpResponse
import json
from apps.catastro.models import Ciudad
from apps.core.models import Recorrido
from apps.mobile_updates.models import Version
from django.db.models import Max
from django.shortcuts import get_object_or_404

def json_response(func):
    """
    A decorator thats takes a view response and turns it
    into json. If a callback is added through GET or POST
    the response is JSONP.
    """
    def decorator(request, *args, **kwargs):
        objects = func(request, *args, **kwargs)
        if isinstance(objects, HttpResponse):
            return objects
        try:
            data = json.dumps(objects)
            if 'callback' in request.REQUEST:
                # a jsonp response!
                data = '%s(%s);' % (request.REQUEST['callback'], data)
                return HttpResponse(data, "text/javascript")
        except:
            data = json.dumps(str(objects))
        return HttpResponse(data, "application/json")
    return decorator


@json_response
def ciudades_package(request):
    return [
        {
            'slug'  : c.slug,
            'nombre': c.nombre,
            'latlng': list(c.centro.coords)
        } 
        for c in Ciudad.objects.all()
    ]

@json_response
def recorridos_package(request):
    ci_sl = request.GET.get("ciudad", "")
    ci = get_object_or_404(Ciudad, slug=ci_sl)
    return [
        {
            'li': r.linea.nombre,
            're': r.nombre,
            'id': r.id
        }
        for r in Recorrido.objects.all().select_related('linea__ciudad').filter(linea__ciudad=ci)
    ]

@json_response
def versiones(request):
#    return [
#        {
#            'tipo'     : v.tipo,
#            'timestamp': v.timestamp,
#            'name'     : v.name,
#            'noticia'  : v.noticia
#        }
#        for v in 
	return Version.objects.values('tipo').annotate(timestamp_max=Max('timestamp'))
#    ]
