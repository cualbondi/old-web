from apps.core.models import Ciudad, Poi, Linea, Recorrido
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext, Context
from django.template.defaultfilters import slugify


def index(request):
    """ TODO: Aca hay que checkear si tiene seteada una
        cookie con la ciudad predeterminada.
        Si no la tiene redirect a "seleccionar_ciudad"
    """
    return redirect("/seleccionar-ciudad")

def seleccionar_ciudad(request):
    ciudades = Ciudad.objects.filter(activa=True)
    return render_to_response('core/seleccionar_ciudad.html',
                              {'ciudad_actual': None,
                               'ciudades': ciudades},
                              context_instance=RequestContext(request))


def ver_ciudad(request, nombre_ciudad):
    slug_ciudad = slugify(nombre_ciudad)
    ciudad_actual = get_object_or_404(Ciudad, slug=slug_ciudad, activa=True)

    ciudades = Ciudad.objects.filter(activa=True)
    lineas = ciudad_actual.lineas.all()

    return render_to_response('core/ver_ciudad.html',
                              {'ciudad_actual': ciudad_actual,
                               'ciudades': ciudades,
                               'lineas': lineas},
                              context_instance=RequestContext(request))


def ver_mapa_ciudad(request, nombre_ciudad):
    slug_ciudad = slugify(nombre_ciudad)
    ciudad_actual = get_object_or_404(Ciudad, slug=slug_ciudad, activa=True)

    ciudades = Ciudad.objects.filter(activa=True)
#    pois = Poi.objects.filter(ciudad=ciudad_actual)
#    comercios = Comercio.objects.filter(ciudad=ciudad_actual)

    return render_to_response('core/ver_mapa_ciudad.html',
                              {'es_vista_mapa': True,
                               'ciudad_actual': ciudad_actual,
                               'ciudades': ciudades},
                              context_instance=RequestContext(request))


def ver_linea(request, nombre_ciudad, nombre_linea):
    slug_ciudad = slugify(nombre_ciudad)
    slug_linea = slugify(nombre_linea)

    ciudades = Ciudad.objects.filter(activa=True)
    ciudad_actual = get_object_or_404(Ciudad, slug=slug_ciudad, activa=True)
    """ TODO: Buscar solo lineas activas """
    linea_actual = get_object_or_404(Linea,
                                     slug=slug_linea,
                                     ciudad=ciudad_actual)
    recorridos = Recorrido.objects.filter(linea=linea_actual)
    return render_to_response('core/ver_linea.html',
                              {'ciudad_actual': ciudad_actual,
                               'ciudades': ciudades,
                               'linea_actual': linea_actual,
                               'recorridos': recorridos},
                              context_instance=RequestContext(request))


def ver_recorrido(request, nombre_ciudad, nombre_linea, nombre_recorrido):
    slug_ciudad = slugify(nombre_ciudad)
    slug_linea = slugify(nombre_linea)
    slug_recorrido = slugify(nombre_recorrido)

    ciudades = Ciudad.objects.filter(activa=True)
    ciudad_actual = get_object_or_404(Ciudad, slug=slug_ciudad, activa=True)
    """ TODO: Buscar solo lineas activas """
    linea_actual = get_object_or_404(Linea,
                                     slug=slug_linea,
                                     ciudad=ciudad_actual)
    """ TODO: Buscar solo recorridos activos """
    recorrido_actual = get_object_or_404(Recorrido,
                                         slug=slug_recorrido,
                                         linea=linea_actual)

    return render_to_response('core/ver_recorrido.html',
                              {'ciudad_actual': ciudad_actual,
                               'ciudades': ciudades,
                               'linea_actual': linea_actual,
                               'recorrido_actual': recorrido_actual},
                              context_instance=RequestContext(request))
