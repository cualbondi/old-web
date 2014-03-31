from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from apps.core.models import Recorrido
from apps.editor.models import RecorridoProposed
from django.contrib.gis.geos import GEOSGeometry
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.contrib.auth.decorators import login_required, permission_required


@ensure_csrf_cookie
@csrf_protect
def editor_recorrido(request, id_recorrido):
    if request.method == 'GET':
        recorrido = get_object_or_404(Recorrido, pk=id_recorrido)
        return render_to_response(
            'editor/editor_recorrido.html',
            {'recorrido': recorrido},
            context_instance=RequestContext(request)
        )
    elif request.method == 'POST':
        # save anyway! all info is useful
        if request.POST.get("mode") == 'save':
            mode = "save"
        else:
            mode = "draft"
        # request.POST.get("id")
        recorrido = get_object_or_404(Recorrido, pk=id_recorrido)
        # sys.stderr.write(str(GEOSGeometry(request.POST.get("geojson"))))
        if (request.POST.get("uuid")):
            r = RecorridoProposed.objects.get(uuid=request.POST.get("uuid"))
        else:
            r = RecorridoProposed()
        r.recorrido = recorrido
        r.nombre = recorrido.nombre
        r.linea = recorrido.linea
        r.sentido         = recorrido.sentido
        r.inicio          = recorrido.inicio
        r.fin             = recorrido.fin
        r.semirrapido     = recorrido.semirrapido
        r.color_polilinea = recorrido.color_polilinea
        r.pois            = recorrido.pois
        r.descripcion     = recorrido.descripcion
        r.ruta = GEOSGeometry(request.POST.get("geojson"))
        r.user = request.user if request.user.is_authenticated() else None
        r.parent = recorrido.uuid
        # save anyway, but respond as forbidden if not auth ;)
        r.save()
        data = '{"uuid":"'+r.uuid+'"}'
        if request.user.is_authenticated():
            return HttpResponse(data)
        else:
            return HttpResponse(data, status=403)
    else:
        return HttpResponse(status=501)


@permission_required('editor.moderate_recorridos', login_url="/usuarios/login/", raise_exception=True)
def mostrar_ediciones(request):
    # chequear capability moderar_ediciones
    # por get, sin id: mostrar ultimos recorridos en la tabla de ediciones
    # por get con uuid: mostrar ese recorrido con diff con el parent o con el que esta publicado (recorrido_id)
    # por post con uuid: aceptar ese recorrido: mover de la tabla ediciones a la tabla posta con el recorrido_id
    if request.method == 'GET':
        ediciones = RecorridoProposed.objects.order_by('-date_update')[:50]
        return render_to_response(
            'editor/moderacion_listado.html',
            {'ediciones': ediciones},
            context_instance=RequestContext(request)
        )
    else:
        return HttpResponse(status=501)

@permission_required('editor.moderate_recorridos', login_url="/usuarios/login/", raise_exception=True)
def moderar_ediciones_id(request, id=None):
    # chequear capability moderar_ediciones
    # por get, sin id: mostrar ultimos recorridos en la tabla de ediciones
    # por get con uuid: mostrar ese recorrido con diff con el parent o con el que esta publicado (recorrido_id)
    # por post con uuid: aceptar ese recorrido: mover de la tabla ediciones a la tabla posta con el recorrido_id
    if request.method == 'GET':
        ediciones = RecorridoProposed.objects.filter(recorrido__id=id).order_by('-date_update')[:50]
        original = Recorrido.objects.get(id=id)
        return render_to_response(
            'editor/moderacion_id.html',
            {
                'ediciones': ediciones,
                'original': original
            },
            context_instance=RequestContext(request)
        )
    else:
        return HttpResponse(status=501)


@permission_required('editor.moderate_recorridos', login_url="/usuarios/login/", raise_exception=True)
def moderar_ediciones_uuid(request, uuid=None):
    # chequear capability moderar_ediciones
    # por get, sin id: mostrar ultimos recorridos en la tabla de ediciones
    # por get con uuid: mostrar ese recorrido con diff con el parent o con el que esta publicado (recorrido_id)
    # por post con uuid: aceptar ese recorrido: mover de la tabla ediciones a la tabla posta con el recorrido_id
    if request.method == 'GET':
        ediciones = RecorridoProposed.objects.filter(uuid=uuid).order_by('-date_update')[:50]
        original = Recorrido.objects.get(id=ediciones[0].recorrido.id)
        return render_to_response(
            'editor/moderacion_id.html',
            {
                'ediciones': ediciones,
                'original': original
            },
            context_instance=RequestContext(request)
        )
    else:
        return HttpResponse(status=501)


@permission_required('editor.moderate_recorridos', login_url="/usuarios/login/", raise_exception=True)
def moderar_ediciones_uuid_rechazar(request, uuid=None):
    RecorridoProposed.objects.get(uuid=uuid).logmoderacion_set.create(newStatus='N')
    # redirect('moderar_ediciones_uuid', uuid=uuid)
    return HttpResponseRedirect(request.GET.get("next"))


@permission_required('editor.moderate_recorridos', login_url="/usuarios/login/", raise_exception=True)
def moderar_ediciones_uuid_aprobar(request, uuid=None):
    proposed = RecorridoProposed.objects.get(uuid=uuid)
    r = proposed.recorrido
    if not r.uuid:
        rp = RecorridoProposed(
            recorrido       = r,
            nombre          = r.nombre,
            linea           = r.linea,
            ruta            = r.ruta,
            sentido         = r.sentido,
            slug            = r.slug,
            inicio          = r.inicio,
            fin             = r.fin,
            semirrapido     = r.semirrapido,
            color_polilinea = r.color_polilinea,
            pois            = r.pois,
            descripcion     = r.descripcion
        )
        rp.save()
        proposed.parent=rp.uuid
        proposed.save()

    r.recorrido       = proposed.recorrido
    r.nombre          = proposed.nombre
    r.linea           = proposed.linea
    r.ruta            = proposed.ruta
    r.sentido         = proposed.sentido
    r.inicio          = proposed.inicio
    r.fin             = proposed.fin
    r.semirrapido     = proposed.semirrapido
    r.color_polilinea = proposed.color_polilinea
    r.pois            = proposed.pois
    r.descripcion     = proposed.descripcion
    r.save()

    try:
        parent = RecorridoProposed.objects.get(uuid=proposed.parent)
        if parent:
            parent.logmoderacion_set.create(newStatus='R')
    except RecorridoProposed.DoesNotExist:
        pass
    for rp in RecorridoProposed.objects.filter(current_status='S', recorrido=r.recorrido).exclude(uuid=uuid):
        rp.logmoderacion_set.create(newStatus='R')
    proposed.logmoderacion_set.create(newStatus='S')
    return HttpResponseRedirect(request.GET.get("next"))