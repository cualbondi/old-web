from apps.core.models import Ciudad, Poi, Linea, Recorrido
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.http import HttpResponse
from django.template import RequestContext, Context
from django.template.defaultfilters import slugify
from apps.core.forms import LineaForm, RecorridoForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core import serializers


def index(request):
    """ TODO: Aca hay que checkear si tiene seteada una
        cookie con la ciudad predeterminada.
        Si no la tiene redirect a "seleccionar_ciudad"
    """
    id_ciudad = request.COOKIES.get('default_city', None)
    if id_ciudad:
        ciudad = get_object_or_404(Ciudad, id=id_ciudad)
        url = '/{0}/'.format(ciudad.slug)
    else:
        url = '/seleccionar-ciudad/'
    return redirect(url)

def seleccionar_ciudad(request):
    if request.method == 'GET':
        return render_to_response('core/seleccionar_ciudad.html',
                                  {'ciudad_actual': None},
                                  context_instance=RequestContext(request))
    elif request.method == 'POST':
        id_ciudad = request.POST.get('ciudad', None)
        predeterminada = request.POST.get('predeterminada', False)

        ciudad = get_object_or_404(Ciudad, id=id_ciudad)
        response = redirect('/{0}/'.format(ciudad.slug))
        if predeterminada:
            response.set_cookie('default_city', ciudad.id)
        return response


def ver_ciudad(request, nombre_ciudad):
    slug_ciudad = slugify(nombre_ciudad)
    ciudad_actual = get_object_or_404(Ciudad, slug=slug_ciudad, activa=True)

    lineas = ciudad_actual.lineas.all()

    return render_to_response('core/ver_ciudad.html',
                              {'lineas': lineas},
                              context_instance=RequestContext(request))


def ver_mapa_ciudad(request, nombre_ciudad):
    slug_ciudad = slugify(nombre_ciudad)
    ciudad_actual = get_object_or_404(Ciudad, slug=slug_ciudad, activa=True)

#    pois = Poi.objects.filter(ciudad=ciudad_actual)
#    comercios = Comercio.objects.filter(ciudad=ciudad_actual)

    return render_to_response('core/ver_mapa_ciudad.html',
                              {'es_vista_mapa': True,
                               'ciudad_actual': ciudad_actual},
                              context_instance=RequestContext(request))


def ver_linea(request, nombre_ciudad, nombre_linea):
    slug_ciudad = slugify(nombre_ciudad)
    slug_linea = slugify(nombre_linea)

    ciudad_actual = get_object_or_404(Ciudad, slug=slug_ciudad, activa=True)
    """ TODO: Buscar solo lineas activas """
    linea_actual = get_object_or_404(Linea,
                                     slug=slug_linea,
                                     ciudad=ciudad_actual)
    recorridos = Recorrido.objects.filter(linea=linea_actual)
    return render_to_response('core/ver_linea.html',
                              {'ciudad_actual': ciudad_actual,
                               'linea_actual': linea_actual,
                               'recorridos': recorridos},
                              context_instance=RequestContext(request))


def ver_recorrido(request, nombre_ciudad, nombre_linea, nombre_recorrido):
    slug_ciudad = slugify(nombre_ciudad)
    slug_linea = slugify(nombre_linea)
    slug_recorrido = slugify(nombre_recorrido)

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
                               'linea_actual': linea_actual,
                               'recorrido_actual': recorrido_actual},
                              context_instance=RequestContext(request))


@login_required(login_url="/usuarios/login/")
def agregar_linea(request, nombre_ciudad):
    slug_ciudad = slugify(nombre_ciudad)
    ciudad_actual = get_object_or_404(Ciudad, slug=slug_ciudad, activa=True)

    if request.method == 'POST':
        form = LineaForm(request.POST)
        if form.is_valid():
            linea = form.save(commit=True)
            msg = 'La linea {0} se ha agregado correctamente'
            messages.add_message(request,
                            messages.SUCCESS,
                            msg.format(linea))
        else:
            msg = 'La operacion no pudo realizarse con exito'
            messages.add_message(request,
                            messages.ERROR,
                            msg)
        return render_to_response('core/agregar_linea.html',
                                 {'form': form,
                                  'ciudad_actual': ciudad_actual},
                              context_instance=RequestContext(request))
    elif request.method == 'GET':
        linea_form = LineaForm()
        return render_to_response('core/agregar_linea.html',
                                  {'form': linea_form,
                                   'ciudad_actual': ciudad_actual},
                                  context_instance=RequestContext(request))


@login_required(login_url="/usuarios/login/")
def agregar_recorrido(request, nombre_ciudad):
    slug_ciudad = slugify(nombre_ciudad)
    ciudad_actual = get_object_or_404(Ciudad, slug=slug_ciudad, activa=True)

    if request.method == 'POST':
        pass
    elif request.method == 'GET':
        recorrido_form = RecorridoForm()
        return render_to_response('core/agregar_recorrido.html',
                                  {'form': recorrido_form,
                                   'ciudad_actual': ciudad_actual},
                                    context_instance=RequestContext(request))
